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
MCP_PROTOCOL_VERSION = "2024-11-05"
DOCTOR_CLIENT_VERSION = "3.0.0"
DEVARSIV_EXPECTED_TOOLS = 22
DEVARSIV_VNC_URL = "https://devarsiv-vnc.cureonics.com/vnc.html"

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
    ServerSpec("resmigazete", "Yasama/mevzuat", "env", "erken-Cumhuriyet RG arsivi; rg-ocr cift-motor"),
    ServerSpec("mevzuat", "Yasama/mevzuat", "env", "TR mevzuat + mulga + gerekce + RG capraz-referans"),
    ServerSpec("tbmm", "Yasama/mevzuat", "env", "TBMM yasama tarihcesi + Acik Erisim DSpace"),
    ServerSpec("yok-akademik", "Destekleyici", "env", "uzman/ekol haritasi"),
    ServerSpec("detsis", "Destekleyici", "env", "kurumsal prosopografi; Cumhuriyet-sinirli"),
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


def curl_head(url: str, timeout: int) -> tuple[int, str]:
    """HEAD-only probe (no MCP envelope). Mirrors curl_post_json's subprocess pattern."""
    cmd = [
        "curl",
        "-sS",
        "--max-time",
        str(timeout),
        "-o",
        "/dev/null",
        "-w",
        "%{http_code}",
        "-I",
        url,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return 0, "curl executable not found"

    if result.returncode != 0:
        return 0, result.stderr.strip() or f"curl exit {result.returncode}"

    stdout = result.stdout.strip()
    try:
        status_code = int(stdout)
    except ValueError:
        status_code = 0
    return status_code, ""


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
            "clientInfo": {"name": "vekayinuvis-doctor", "version": DOCTOR_CLIENT_VERSION},
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


def envanter_line(content: dict[str, Any]) -> str:
    """[envanter] line: devarsiv_server_info tool-count drift check (K1: 22 tools)."""
    tools = content.get("tools")
    if isinstance(tools, list):
        count = len(tools)
    elif isinstance(tools, int):
        count = tools
    else:
        return "[envanter] SORUN: devarsiv_server_info yanitinda tools alani yok"
    if count != DEVARSIV_EXPECTED_TOOLS:
        return (
            f"[envanter] DRIFT: {count}/{DEVARSIV_EXPECTED_TOOLS} — "
            "claude.ai connector'ını yeniden bağlayın"
        )
    return f"[envanter] OK ({count}/{DEVARSIV_EXPECTED_TOOLS})"


def engine_lines(content: dict[str, Any]) -> list[str]:
    """[engines] lines: transkribus/escriptorium status strings from ocr.engines."""
    ocr = content.get("ocr")
    engines = ocr.get("engines") if isinstance(ocr, dict) else None
    if not isinstance(engines, dict):
        return ["[engines] SORUN: devarsiv_server_info yanitinda ocr.engines alani yok"]
    lines = []
    for name in ("transkribus", "escriptorium"):
        status = engines.get(name)
        lines.append(f"[engines] {name}: {status if status is not None else 'bilinmiyor'}")
    return lines


def devarsiv_envanter_engines_lines(config: dict, timeout: int) -> list[str]:
    """Run the devarsiv_server_info tools/call (same initialize/initialized/tools_call
    HTTP+JSON-RPC pattern as devarsiv_live_status) and format [envanter]+[engines] lines."""
    url = config.get("url")
    if not isinstance(url, str) or not url:
        reason = "live devarsiv_server_info icin MCP URL yok"
        return [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]

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
            "clientInfo": {"name": "vekayinuvis-doctor", "version": DOCTOR_CLIENT_VERSION},
        },
    }
    code, response_headers, _body, error = curl_post_json(
        url,
        headers,
        init_payload,
        timeout=timeout,
    )
    if error:
        reason = f"live initialize curl_failed ({error})"
        return [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]
    if code != 200:
        reason = f"live initialize http {code}"
        return [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]

    session_id = header_value(response_headers, "mcp-session-id")
    if not session_id:
        reason = "live initialize mcp-session-id dondurmedi"
        return [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]

    initialized_payload = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    code, _, _, error = curl_post_json(
        url,
        headers,
        initialized_payload,
        session_id=session_id,
        timeout=timeout,
    )
    if error:
        reason = f"live initialized notification curl_failed ({error})"
        return [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]
    if code not in {200, 202, 204}:
        reason = f"live initialized notification http {code}"
        return [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]

    call_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": "devarsiv_server_info", "arguments": {}},
    }
    code, _, body, error = curl_post_json(
        url,
        headers,
        call_payload,
        session_id=session_id,
        timeout=timeout,
    )
    if error:
        reason = f"live devarsiv_server_info curl_failed ({error})"
        return [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]
    if code != 200:
        reason = f"live devarsiv_server_info http {code}"
        return [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]

    response = mcp_response_json(body)
    if response is None:
        reason = "live devarsiv_server_info parse_failed"
        return [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]
    if response.get("error"):
        reason = "live devarsiv_server_info jsonrpc_error"
        return [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]

    result = response.get("result")
    if isinstance(result, dict) and result.get("isError") is True:
        reason = "live devarsiv_server_info tool_error"
        return [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]

    content = structured_content(response)
    return [envanter_line(content), *engine_lines(content)]


def devarsiv_vnc_line(timeout: int) -> str:
    """[vnc] line: HEAD probe against the noVNC login surface.

    302 (Cloudflare Access redirect) = OK; timeout/5xx (or any other unexpected
    response) = SORUN — the noVNC surface is only ever fronted by an Access
    redirect, so anything else signals a problem.
    """
    code, error = curl_head(DEVARSIV_VNC_URL, timeout)
    if error or code == 0:
        return "[vnc] SORUN"
    if code == 302:
        return "[vnc] OK (Access-gated)"
    return "[vnc] SORUN"


def live_extra_checks(servers: dict, timeout: int) -> list[str]:
    """Task 8 --live additions: [envanter]/[engines] (devarsiv_server_info) + [vnc] (HEAD)."""
    config = servers.get("devlet-arsivleri")
    if config is None:
        reason = "devlet-arsivleri .mcp.json'da tanimli degil"
        lines = [f"[envanter] SORUN: {reason}", f"[engines] SORUN: {reason}"]
    else:
        lines = devarsiv_envanter_engines_lines(config, timeout)
    lines.append(devarsiv_vnc_line(timeout))
    return lines


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
    if live:
        out.append("")
        out.append("Canli ek kontroller (devlet-arsivleri: envanter/engines/vnc)")
        out.extend(f"  {line}" for line in live_extra_checks(servers, timeout))
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
    report = {"topic": topic, "mcp_path": str(MCP_PATH), "live": live, "entries": entries}
    if live:
        report["live_checks"] = live_extra_checks(servers, timeout)
    return report


def out_dir() -> Path:
    """Base directory for --write-manifest output.

    Single helper for the output-home decision (Task 8 Step 3): honors
    ``CLAUDE_PLUGIN_DATA`` (Claude Code's per-plugin persistent data dir) when
    set; otherwise preserves the pre-v3 default of the invoking workspace's
    ``shared/`` directory — fully backward-compatible.
    """
    plugin_data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if plugin_data:
        return Path(plugin_data).expanduser() / "shared"
    return Path.cwd() / "shared"


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
        help="Write preflight manifest to out_dir()/coverage-manifest.md",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output path used with --write-manifest (default: out_dir()/coverage-manifest.md; "
            "out_dir() = $CLAUDE_PLUGIN_DATA/shared if set, else <cwd>/shared)"
        ),
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
        output = Path(args.output).expanduser() if args.output else out_dir() / "coverage-manifest.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"wrote {output}")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
