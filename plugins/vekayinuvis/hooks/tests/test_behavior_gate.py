"""Davranış kapısı — Stop hook'ları yer-gerçeğine (araç çağrıldı mı?) bağlar.

Metin-eşleşmesinin kör noktası: `devarsiv`/`mevzuat`/`tbmm` adları bir araç ÇAĞRISI olarak değil,
metinde (port tablosu, .mcp.json, altyapı sohbeti) geçtiğinde de hook'lar tetikleniyordu —
ops turlarında kör yanlış-pozitif. `_turn_tools` bunu davranışa taşır: transkriptte son kullanıcı
prompt'undan bu yana gerçekten çağrılan tool_use adlarına bakar.

SERTLEŞTİRME (kullanıcı 2026-07-17): transkript varsa davranış kapısı KESİN; transkript yoksa
hook metin-sezgisi yedeğine düşer (invaryant sessizce kaybolmasın).
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

HOOKS = Path(__file__).resolve().parents[1] / "scripts"

_OPS = "devarsiv ve mevzuat MCP'lerini .mcp.json'da yapılandırdık; port tablosu 8301/8303 sohbeti."
_RESEARCH = "II. Mahmud dönemi tımar sistemi üzerine arşiv taraması yaptım, birçok bulgu var."
_ARCHIVE_CLAIM = "BOA HR.UHM.00048.00035 gömleğinde vali şöyle yazıyor: mühimme kaydı."


def _transcript(tool_calls, assistant_text):
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "user", "message": {"content": "kullanıcı sorusu"}}) + "\n")
        for tc in tool_calls:
            f.write(json.dumps({"type": "assistant",
                                "message": {"content": [{"type": "tool_use", "name": tc}]}}) + "\n")
        f.write(json.dumps({"type": "assistant",
                            "message": {"content": [{"type": "text", "text": assistant_text}]}}) + "\n")
    return path


def _run(hook, event):
    p = subprocess.run(["python3", str(HOOKS / f"{hook}.py")],
                       input=json.dumps(event), capture_output=True, text=True)
    return bool(p.stdout.strip() or p.returncode != 0)


def _fires_with_transcript(hook, tool_calls, text):
    tp = _transcript(tool_calls, text)
    try:
        return _run(hook, {"transcript_path": tp, "last_assistant_message": text})
    finally:
        os.unlink(tp)


# --- Davranış kapısı: transkript VAR ---------------------------------------------

def test_ops_turn_no_tool_call_is_silent_stop_coverage():
    """Filo adları metinde ama araç ÇAĞRILMADI (ops turu) → G0 manifesto N/A → sessiz."""
    assert _fires_with_transcript("stop_coverage", [], _OPS) is False


def test_ops_turn_no_tool_call_is_silent_citation():
    """Aynı ops turu → atıf disiplini N/A → sessiz."""
    assert _fires_with_transcript("citation_discipline", [], _OPS) is False


def test_real_research_fires_stop_coverage():
    """Filo veri-aracı çağrıldı + manifesto yok → yanar (künyesiz-tarama açığı kapandı)."""
    assert _fires_with_transcript(
        "stop_coverage", ["mcp__devlet-arsivleri__devarsiv_search"], _RESEARCH) is True


def test_real_archive_claim_fires_citation():
    """Arşiv-veri aracı çağrıldı + çift-tarih/URL eksik → yanar."""
    assert _fires_with_transcript(
        "citation_discipline", ["mcp__devlet-arsivleri__devarsiv_ocr_belge"], _ARCHIVE_CLAIM) is True


def test_non_data_tool_does_not_trip_gate():
    """session_status / server_info retrieval DEĞİL → atıf disiplini beklenmez → sessiz."""
    assert _fires_with_transcript(
        "citation_discipline", ["mcp__devlet-arsivleri__devarsiv_session_status"], _ARCHIVE_CLAIM) is False


# --- Metin yedeği: transkript YOK ------------------------------------------------

def test_no_transcript_falls_back_to_text_citation():
    """Transkript yok + somut künye → metin yedeği yanar (invaryant korunur)."""
    ev = {"last_assistant_message": _ARCHIVE_CLAIM}
    assert _run("citation_discipline", ev) is True


def test_no_transcript_silent_without_record_locator():
    """Transkript yok + salt isim geçişi (künye yok) → sessiz (isim geçişi atıf değil)."""
    ev = {"last_assistant_message": _OPS}
    assert _run("citation_discipline", ev) is False
