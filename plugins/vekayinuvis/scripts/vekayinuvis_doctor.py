#!/usr/bin/env python3
"""Vekayinüvis fleet doctor.

This script is intentionally offline-first so it works inside Claude marketplace
installs before any remote MCP tool is called. It checks the packaged .mcp.json,
classifies credential/session prerequisites, and can emit the G0 coverage
manifest skeleton required by the runtime hooks.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
MCP_PATH = PLUGIN_ROOT / ".mcp.json"
DEFAULT_MANIFEST_PATH = Path.cwd() / "shared" / "coverage-manifest.md"
MCP_PROTOCOL_VERSION = "2024-11-05"

ENV_RE = re.compile(r"\$\{([A-Z0-9_]+)\}")
USER_CONFIG_RE = re.compile(r"\$\{user_config\.([a-zA-Z0-9_]+)\}")


@dataclass(frozen=True)
class ServerSpec:
    name: str
    group: str
    auth: str
    note: str


FLEET: tuple[ServerSpec, ...] = (
    ServerSpec("ottoman-archives", "Cekirdek arsiv", "env", "IIIF, takvim, HTR, TDV IA"),
    ServerSpec(
        "devlet-arsivleri",
        "Cekirdek arsiv",
        "env+session",
        "resmi katalog; devarsiv_session_status gerekli",
    ),
    ServerSpec("yoktez", "Cekirdek arsiv", "authless", "YOK Tez transkripsiyon katmani"),
    ServerSpec("literatur", "Akademik", "authless", "DergiPark tam-metin"),
    ServerSpec("consensus", "Akademik", "oauth", "hakemli sentez; /mcp login gerekebilir"),
    ServerSpec("scholar-gateway", "Akademik", "oauth", "pasaj-duzeyi akademik arama"),
    ServerSpec("exa", "Akademik", "oauth_or_key", "Exa remote; OAuth veya opsiyonel API key"),
    ServerSpec("tavily", "Akademik", "oauth_or_key", "Tavily remote; OAuth veya API key"),
    ServerSpec("paper-search", "Akademik", "user_config", "Smithery userConfig"),
    ServerSpec("openathens", "Tam-metin", "env", "lisansli tam-metin Tier 3"),
    ServerSpec("annas-reader", "Tam-metin", "env", "son-care tam-metin Tier 4"),
    ServerSpec("yok-akademik", "Destekleyici", "env", "uzman/ekol haritasi"),
    ServerSpec("anamnesis", "Buyuk-veri substrati", "env", "RAG/GraphRAG ingest ve bounded query"),
)


def load_mcp_servers() -> dict:
    data = json.loads(MCP_PATH.read_text(encoding="utf-8"))
    return data.get("mcpServers", data)


def env_refs(obj: object) -> list[str]:
    text = json.dumps(obj, ensure_ascii=False)
    return sorted(set(ENV_RE.findall(text)))


def user_config_refs(obj: object) -> list[str]:
    text = json.dumps(obj, ensure_ascii=False)
    return sorted(set(USER_CONFIG_RE.findall(text)))


def expand_env_template(value: str) -> str:
    return ENV_RE.sub(lambda match: os.environ.get(match.group(1), ""), value)


def header_value(headers: str, name: str) -> str | None:
    target = name.lower()
    for line in headers.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip().lower() == target:
            return value.strip()
    return None


def mcp_response_json(body: str) -> dict[str, Any] | None:
    for line in body.splitlines():
        if not line.startswith("data:"):
            continue
        data = line.removeprefix("data:").strip()
        if not data or data == "[DONE]":
            continue
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    try:
        parsed = json.loads(body)
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def structured_content(response: dict[str, Any]) -> dict[str, Any]:
    result = response.get("result")
    if not isinstance(result, dict):
        return {}

    structured = result.get("structuredContent")
    if isinstance(structured, dict):
        return structured

    content = result.get("content")
    if not isinstance(content, list):
        return {}
    for item in content:
        if not isinstance(item, dict) or item.get("type") != "text":
            continue
        text = item.get("text")
        if not isinstance(text, str):
            continue
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return {}


def curl_post_json(
    url: str,
    headers: list[str],
    payload: dict[str, Any],
    *,
    session_id: str | None = None,
    timeout: int = 20,
) -> tuple[int, str, str, str]:
    request_headers = [
        *headers,
        "Content-Type: application/json",
        "Accept: application/json, text/event-stream",
    ]
    if session_id:
        request_headers.append(f"Mcp-Session-Id: {session_id}")

    with tempfile.NamedTemporaryFile("r+", encoding="utf-8") as body_file, tempfile.NamedTemporaryFile(
        "r+",
        encoding="utf-8",
    ) as header_file:
        cmd = [
            "curl",
            "-sS",
            "--max-time",
            str(timeout),
            "-D",
            header_file.name,
            "-o",
            body_file.name,
            "-w",
            "%{http_code}",
            "-X",
            "POST",
            url,
        ]
        for header in request_headers:
            cmd.extend(["-H", header])
        cmd.extend(["--data", json.dumps(payload, ensure_ascii=False)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        except FileNotFoundError:
            return 0, "", "", "curl executable not found"
        body_file.seek(0)
        header_file.seek(0)
        body = body_file.read()
        response_headers = header_file.read()

    if result.returncode != 0:
        return 0, response_headers, body, result.stderr.strip() or f"curl exit {result.returncode}"

    stdout = result.stdout.strip()
    try:
        status_code = int(stdout)
    except ValueError:
        status_code = 0
    return status_code, response_headers, body, ""


def devarsiv_live_status(config: dict, timeout: int) -> tuple[str, str]:
    url = config.get("url")
    if not isinstance(url, str) or not url:
        return "degraded", "live devarsiv_session_status icin MCP URL yok"

    headers = []
    for key, value in config.get("headers", {}).items():
        if isinstance(value, str):
            headers.append(f"{key}: {expand_env_template(value)}")

    init_payload: dict[str, Any] = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "vekayinuvis-doctor", "version": "2.5.0"},
        },
    }
    code, response_headers, _body, error = curl_post_json(
        url,
        headers,
        init_payload,
        timeout=timeout,
    )
    if error:
        return "degraded", f"live initialize curl_failed ({error})"
    if code != 200:
        return "degraded", f"live initialize http {code}"

    session_id = header_value(response_headers, "mcp-session-id")
    if not session_id:
        return "degraded", "live initialize mcp-session-id dondurmedi"

    initialized_payload = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    code, _, _, error = curl_post_json(
        url,
        headers,
        initialized_payload,
        session_id=session_id,
        timeout=timeout,
    )
    if error:
        return "degraded", f"live initialized notification curl_failed ({error})"
    if code not in {200, 202, 204}:
        return "degraded", f"live initialized notification http {code}"

    call_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "devarsiv_session_status", "arguments": {}},
    }
    code, _, body, error = curl_post_json(
        url,
        headers,
        call_payload,
        session_id=session_id,
        timeout=timeout,
    )
    if error:
        return "degraded", f"live devarsiv_session_status curl_failed ({error})"
    if code != 200:
        return "degraded", f"live devarsiv_session_status http {code}"

    response = mcp_response_json(body)
    if response is None:
        return "degraded", "live devarsiv_session_status parse_failed"
    if response.get("error"):
        return "degraded", "live devarsiv_session_status jsonrpc_error"

    result = response.get("result")
    if isinstance(result, dict) and result.get("isError") is True:
        content = structured_content(response)
        status = content.get("status")
        if status == "session_required":
            return "degraded", "session_required (HP noVNC re-login gerekiyor)"
        return "degraded", "live devarsiv_session_status tool_error"

    content = structured_content(response)
    status = content.get("status")
    session = content.get("session") if isinstance(content.get("session"), dict) else {}
    alive = session.get("alive") if isinstance(session, dict) else None
    if status == "ok" and alive is True:
        return "hit 1", "credential present; live devarsiv_session_status ok (session alive)"
    if status == "session_required" or alive is False:
        return "degraded", "session_required (HP noVNC re-login gerekiyor)"
    return "degraded", f"live devarsiv_session_status unexpected status={status or 'unknown'}"


def classify(
    spec: ServerSpec,
    config: dict | None,
    *,
    live: bool = False,
    timeout: int = 20,
) -> tuple[str, str]:
    if config is None:
        return "skipped", "not wired in .mcp.json"

    refs = env_refs(config)
    missing = [name for name in refs if not os.environ.get(name)]
    if missing:
        return "skipped", "anahtar yok (" + ", ".join(f"${name}" for name in missing) + ")"

    uc_refs = user_config_refs(config)
    if uc_refs:
        return "degraded", "userConfig runtime'da dogrulanmali (" + ", ".join(uc_refs) + ")"

    if spec.auth == "authless":
        return "hit 1", "configured; authless transport; live tool smoke run edilmedi"
    if spec.auth == "env":
        return "hit 1", "configured; credential present; live tool smoke run edilmedi"
    if spec.auth == "env+session":
        if live and spec.name == "devlet-arsivleri":
            return devarsiv_live_status(config, timeout)
        return "degraded", "credential present; devarsiv_session_status runtime'da dogrulanmali"
    if spec.auth in {"oauth", "oauth_or_key"}:
        return "degraded", "OAuth/login durumu runtime'da /mcp ile dogrulanmali"
    return "degraded", "configured; runtime durumu bilinmiyor"


def rows(topic: str, *, live: bool = False, timeout: int = 20) -> list[str]:
    servers = load_mcp_servers()
    out = [
        f"### Kapsam Manifestosu (G0) - Doctor preflight - Konu: {topic}",
        "",
    ]
    current_group = None
    for spec in FLEET:
        if spec.group != current_group:
            current_group = spec.group
            out.append(current_group)
        status, reason = classify(spec, servers.get(spec.name), live=live, timeout=timeout)
        out.append(f"  {spec.name:<19} -> {status:<8} ({reason}; {spec.note})")
    out.extend(
        [
            "",
            "No-fabrication notu: Bu doctor preflight'i belge goruntusu, OCR/HTR veya tam metin",
            "uretmez; yalnizca connector wiring, credential ve runtime-oncesi G0 kapsam",
            "durumunu beyan eder. Arsiv belge atfinda gercek kosumda fon/kutu/gomlek +",
            "orijinal takvim + Miladi cift-tarih + katalog URL gerekir. Format ornegi:",
            "H-27-12-1337 (M. 1919); katalog URL ornegi:",
            "https://katalog.devletarsivleri.gov.tr/.../BelgeGoster.aspx?ItemId=...",
            "Belge goruntusu/OCR iddiasinda provenance ornegi:",
            "devarsiv_ocr_belge page=1 engine=Transkribus model=56496 mean_confidence=<deger>.",
        ]
    )
    return out


def json_report(topic: str, *, live: bool = False, timeout: int = 20) -> dict:
    servers = load_mcp_servers()
    entries = []
    for spec in FLEET:
        status, reason = classify(spec, servers.get(spec.name), live=live, timeout=timeout)
        entries.append(
            {
                "server": spec.name,
                "group": spec.group,
                "status": status,
                "reason": reason,
                "note": spec.note,
            }
        )
    return {"topic": topic, "mcp_path": str(MCP_PATH), "live": live, "entries": entries}


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vekayinüvis G0 fleet doctor")
    parser.add_argument("--topic", default="preflight", help="Manifest topic label")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run live MCP probe for env+session servers such as devlet-arsivleri",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=20,
        help="Per-request timeout in seconds for --live probes",
    )
    parser.add_argument(
        "--write-manifest",
        action="store_true",
        help="Write preflight manifest to the current workspace shared/coverage-manifest.md",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Output path used with --write-manifest",
    )
    return parser.parse_args(argv)


def main() -> int:
    args = parse_args()
    if args.json:
        print(
            json.dumps(
                json_report(args.topic, live=args.live, timeout=args.timeout),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    text = "\n".join(rows(args.topic, live=args.live, timeout=args.timeout)) + "\n"
    if args.write_manifest:
        output = Path(args.output).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"wrote {output}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
