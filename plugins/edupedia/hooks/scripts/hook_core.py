#!/usr/bin/env python3
"""edupedia Claude/Cursor hook'larının paylaştığı çekirdek yardımcılar."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

PATH_FIELDS = ("file_path", "path", "target_file", "target_path")
NESTED_PATH_CONTAINERS = ("arguments", "input")
MAX_MODULE_BYTES = 8 * 1024 * 1024


def resolve_plugin_root(env_name: str, script_file: str) -> Path:
    """Host plugin kökünü güvenle çöz; eksik/geçersiz env'de dosya konumuna dön."""
    fallback = Path(script_file).resolve().parents[2]
    raw = os.environ.get(env_name, "")
    if not raw:
        return fallback
    try:
        candidate = Path(raw).expanduser()
        if not candidate.is_absolute():
            return fallback
        candidate = candidate.resolve()
        if (candidate / "hooks" / "scripts").is_dir():
            return candidate
    except (OSError, RuntimeError, ValueError):
        pass
    return fallback


def conventions(lock: dict | None) -> str:
    """Çekirdek invaryantlar — sayılar lock'tan türetilir."""
    counts = (lock or {}).get("counts", {})
    n_srv = counts.get("servers", 2)
    return (
        f"[edupedia] MEB Türkiye Yüzyılı Maarif Modeli Etkileşimli Öğrenim Modülü Süiti aktif. "
        f"Çekirdek invaryantlar: "
        f"(1) İKİ MCP CONNECTOR — {n_srv} sunucu: maarif-mufredat (OTORİTE — 105 MEB ders kitabı tam metni, "
        f"10.855 kazanım, 22.414 figür, 13 çerçeve; Bearer) · egitim-kaynak (tamamlayıcı OER RAG içerik-zenginleştirme, "
        f"124 doğrulanmış kategori, PhET 175 simülasyon, OAuth 2.1 / Bearer; display adı 'Eğitim Kaynakları'). "
        f"Olgusal çelişkide ders kitabı KAZANIR. "
        f"(2) YEREL ÇIKTI — teslim yerel bağımsız tek-dosya HTML'dir (IBM Carbon v11, IBM Plex, "
        f"WCAG 2.1 AA, EMOJİSİZ, offline çalışır). Plugin yayınlamaz (/edupedia:yayinla emekli). "
        f"(3) 16 KALİTE KAPISI — yerel `scripts/validate_module.py` otoritedir: G-EMOJI, G-CARBON, "
        f"G-A11Y, G-INTERACT, G-SELFCONTAINED, G-CONTRAST, G-WELLBEING, G-VOICE, G-SVG, G-AUDIO, "
        f"G-TOKEN, G-CURRICULUM, G-VERIFY, G-FLOW, G-CARBON-GRID, G-EXAM. "
        f"(4) GÖRÜNTÜ-DAYANAK — Tier-1 (yazar-üretimli tema-duyarlı SVG) GARANTİ; Tier-2 (get_figure "
        f"ders kitabı görseli) BEST-EFFORT. "
        f"(5) KANONİK ÖNBELLEK — Tek-sefer disiplini (subject_registry, outcomes_extract, framework_map, "
        f"figure_probe) ve run-manifest yazımı (canonical-cache-contract.md). "
        f"(6) ZARİF DEGRADE — MCP erişilemezse offline yola dönülür (asla uydurma kaynak)."
    )


def build_context(lock: dict | None, probe: dict) -> str:
    """Konvansiyonlar + yalnız sağlıksız prob satırları."""
    ctx = conventions(lock)

    broken = [r for r in probe.values() if r.get("status") == "unauthorized"]
    missing = [r for r in probe.values() if r.get("status") == "auth_missing"]
    down = [r for r in probe.values() if r.get("status") in ("unreachable", "error")]

    if broken:
        ctx += (
            "\n⚠ YAPILANDIRMA ARIZASI — şu connector(lar) canlı prob'da 401/403 verdi: "
            + ", ".join(f"{r['name']} (HTTP {r.get('http')})" for r in broken)
            + ". Bu bir degrade DEĞİL, düzeltilebilir bir wiring hatasıdır: connector "
            "Authorization yapılandırması eksik/yanlış veya anahtar geçersiz. "
            "Onarım: fleet.yaml'i düzelt → `python3 tools/fleetkit/gen_fleet.py`."
        )

    if missing:
        ctx += (
            "\nGated connector key(ler)i süreç ortamında YOK: "
            + ", ".join(
                f"{r['name']} (${r.get('auth_env') or (r.get('detail', '').split(' ')[0].strip('${}'))})"
                for r in missing
            )
            + " → ilgili connector çağrıları 401 döner. Çözüm: gerekli anahtarları "
            "host süreç ortamına güvenli secret enjeksiyonuyla sağla (repo dosyasına yazma). "
            "Manifestoda 'skipped: anahtar yok' beyan edilir (meşru degrade — "
            "çıktı durmaz, veri boşluğu doldurulmaz)."
        )

    if down:
        ctx += (
            "\nŞu connector(lar)a erişilemedi: "
            + ", ".join(f"{r['name']} ({r.get('detail') or r.get('http')})" for r in down)
            + " → offline yola düşülür; konunun yokluk kanıtı DEĞİLDİR."
        )

    return ctx


def session_context(root: Path, env: dict[str, str], fleet_probe: Any) -> str:
    """SessionStart bağlamını her iki host için tek kez üret."""
    lock = fleet_probe.load_lock(root) if fleet_probe else None
    probe = {}
    if fleet_probe and not env.get("EDUPEDIA_PREFLIGHT_NO_PROBE"):
        probe = fleet_probe.cached_probe(root, env)
    return build_context(lock, probe)


def extract_write_path(data: dict) -> str:
    """Write girdisinden yalnız belgelenmiş dar alan/kapsayıcı listesini tara."""
    tool_input = data.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""

    scopes = [tool_input]
    for container in NESTED_PATH_CONTAINERS:
        nested = tool_input.get(container)
        if isinstance(nested, dict):
            scopes.append(nested)

    for scope in scopes:
        for field in PATH_FIELDS:
            value = scope.get(field)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _trusted_roots(data: dict, plugin_root: Path) -> list[Path]:
    """Yalnız host zarfı ve wrapper'ın plugin kökünden kanonik mevcut dizinler."""
    raw_roots = []
    cwd = data.get("cwd")
    if isinstance(cwd, str) and cwd.strip():
        raw_roots.append(cwd)
    workspace_roots = data.get("workspace_roots")
    if isinstance(workspace_roots, list):
        raw_roots.extend(root for root in workspace_roots if isinstance(root, str))
    raw_roots.append(str(plugin_root))

    roots = []
    for raw in raw_roots:
        try:
            candidate = Path(raw).expanduser()
            if not candidate.is_absolute():
                continue
            resolved = candidate.resolve(strict=True)
            if resolved.is_dir() and resolved not in roots:
                roots.append(resolved)
        except (OSError, RuntimeError, ValueError):
            continue
    return roots


def resolve_written_html(
    data: dict,
    plugin_root: Path,
    allowed_tool_names: frozenset[str],
) -> Path | None:
    """Yazılan HTML'i kanonikleştir ve yalnız açık güven kökleri içinde kabul et."""
    if data.get("tool_name") not in allowed_tool_names:
        return None

    raw = extract_write_path(data)
    if not raw or "\x00" in raw:
        return None

    try:
        candidate = Path(raw).expanduser()
        roots = _trusted_roots(data, plugin_root)
        if not roots:
            return None
        if candidate.is_absolute():
            candidates = [candidate.resolve(strict=True)]
        else:
            candidates = []
            for root in roots:
                try:
                    candidates.append((root / candidate).resolve(strict=True))
                except (OSError, RuntimeError, ValueError):
                    continue

        for resolved in candidates:
            if not any(_is_within(resolved, root) for root in roots):
                continue
            if resolved.suffix.lower() == ".html" and resolved.is_file():
                return resolved
        return None
    except (OSError, RuntimeError, ValueError):
        return None


def _module_gate_advisory(path: Path, plugin_root: Path) -> str:
    if path.stat().st_size > MAX_MODULE_BYTES:
        return ""
    content = path.read_text(encoding="utf-8", errors="ignore")
    if "MODULE_DATA" not in content:
        return ""

    root = plugin_root.resolve()
    validator = (
        root / "skills" / "carbon-edupedia" / "scripts" / "validate_module.py"
    ).resolve()
    if not _is_within(validator, root) or not validator.is_file():
        return ""

    result = subprocess.run(
        [sys.executable, str(validator), str(path), "--json"],
        capture_output=True,
        text=True,
        timeout=25,
        check=False,
    )
    if not result.stdout.strip():
        return ""
    try:
        gates = json.loads(result.stdout)
    except json.JSONDecodeError:
        return ""
    if not isinstance(gates, dict):
        return ""

    failed = [
        name
        for name, value in gates.items()
        if isinstance(value, dict) and value.get("status") == "FAIL"
    ]
    warned = [
        name
        for name, value in gates.items()
        if isinstance(value, dict) and value.get("status") == "WARN"
    ]
    if not failed and not warned:
        return ""

    parts = []
    if failed:
        parts.append(f"FAIL Kapıları: {', '.join(failed)}")
    if warned:
        parts.append(f"WARN Kapıları: {', '.join(warned)}")
    return (
        f"[edupedia modül kalite denetimi] {path.name}: "
        + " · ".join(parts)
        + ". scripts/validate_module.py ile ayrıntıları inceleyin (advisory, bloklamaz)."
    )


def module_advisory(
    data: dict,
    plugin_root: Path,
    allowed_tool_names: frozenset[str],
) -> str:
    """Write zarfını güvenli çöz ve deterministik gate advisory'sini üret."""
    try:
        path = resolve_written_html(data, plugin_root, allowed_tool_names)
        return _module_gate_advisory(path, plugin_root) if path else ""
    except Exception:
        return ""
