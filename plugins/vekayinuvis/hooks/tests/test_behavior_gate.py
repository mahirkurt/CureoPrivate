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


def _transcript(tool_calls, assistant_text, mode=True):
    """`mode=True` transkriptin başına bir `/vekayinuvis:…` komutu koyar.

    Davranış kapısı tek başına yetmiyor: `literatur` hem bu filonun üyesi hem de bağımsız
    bir MCP paketi, dolayısıyla o paketin KODUNU ölçen bir mühendislik turu da filo aracı
    çağırmış görünür ve G0 manifestosu istenir.
    """
    fd, path = tempfile.mkstemp(suffix=".jsonl")
    os.close(fd)
    with open(path, "w", encoding="utf-8") as f:
        if mode:
            f.write(json.dumps({"type": "user", "message": {
                "content": "<command-name>/vekayinuvis:arsiv-dalis</command-name>"}}) + "\n")
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


def _fires_with_transcript(hook, tool_calls, text, mode=True):
    tp = _transcript(tool_calls, text, mode=mode)
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


# --- F9: metin-yedeği META-TUR baskılayıcı (transkript YOK) -----------------------
# Filo/mod adlarını ANAN ama araç ÇAĞIRMAYAN turlar (mimari inceleme, dokümantasyon,
# hook'un kendi kodu) metin-yedeğinde mode_hit üzerinden yanlış-pozitif üretiyordu.

_META_REVIEW = (
    "Vekayinüvis mimari incelemesi: SOURCE_HUNT, ARCHIVE_DEEP_DIVE ve HISTORIOGRAPHY "
    "modlarını inceledim. plugins/vekayinuvis/skills/start/SKILL.md ve "
    "hooks/scripts/stop_coverage.py bulguları: kapsam manifestosu doğru yazılmış."
)
_META_MODES_ONLY = (
    "Üç mod — SOURCE_HUNT, HISTORIOGRAPHY ve ACADEMIC_REPORT — nasıl ayrışıyor diye "
    "düşündüm; herhangi bir arşiv taraması veya connector çağrısı yapmadım."
)
_REAL_SINGLE_MODE = (
    "PROSOPOGRAPHY modunda Mustafa Behçet Efendi'nin biyografisini derledim. Yaşam "
    "çizelgesi ve atama-azil zinciri hazır ama G0 kapsam manifestosu eklemedim."
)
_REAL_MULTIPHASE_WITH_LOCATOR = (
    "ACADEMIC_REPORT: SOURCE_HUNT + ARCHIVE_DEEP_DIVE + HISTORIOGRAPHY birleşimi. "
    "Kaynak: BOA, HAT 1234/56; II. Mahmud dönemi tıbbiye. Manifesto eklenmedi."
)


def test_no_transcript_meta_review_turn_silent():
    """Plugin-iç dosya/hook adları taşıyan inceleme turu → meta → sessiz (F9)."""
    assert _run("stop_coverage", {"last_assistant_message": _META_REVIEW}) is False


def test_no_transcript_many_modes_no_locator_silent():
    """≥3 mod anan ama künyesiz düşünme turu → meta → sessiz (F9)."""
    assert _run("stop_coverage", {"last_assistant_message": _META_MODES_ONLY}) is False


def test_no_transcript_single_mode_output_still_fires():
    """Tek gerçek mod çıktısı + manifesto yok → invaryant korunur, yanar."""
    assert _run("stop_coverage", {"last_assistant_message": _REAL_SINGLE_MODE}) is True


def test_no_transcript_multiphase_with_locator_still_fires():
    """Çok-fazlı gerçek rapor + arşiv künyesi (meta değil) + manifesto yok → yanar."""
    assert _run("stop_coverage", {"last_assistant_message": _REAL_MULTIPHASE_WITH_LOCATOR}) is True


# --- Mod kapısı ------------------------------------------------------------------

_LICENSE_FIX = (
    "tr-literatur paketinin lisans ayrıştırıcısını onardım; CC URI biçimleri artık tanınıyor."
)


def test_engineering_turn_on_a_fleet_package_is_silent():
    """Ölçülen yanlış-pozitif (2026-09-10).

    `literatur` bu filonun üyesidir *ve* bağımsız bir MCP paketidir. O paketin kodunu
    onarırken aracı ölçmek için `tr_literatur_*` çağrıldı; davranış kapısı açıldı ve
    ortada tek bir arşiv iddiası yokken G0 manifestosu istendi. Eksik boyut moddu.
    """
    assert _fires_with_transcript(
        "stop_coverage",
        ["mcp__claude_ai_TR_Dizin__tr_literatur_get_journal"],
        _LICENSE_FIX,
        mode=False,
    ) is False


def test_same_call_inside_a_research_session_still_fires():
    """Mod kapısı invaryantı öldürmemeli: mod açıksa aynı çağrı manifesto bekletir."""
    assert _fires_with_transcript(
        "stop_coverage",
        ["mcp__claude_ai_TR_Dizin__tr_literatur_get_journal"],
        _RESEARCH,
        mode=True,
    ) is True


def test_prose_mention_does_not_open_the_mode_gate():
    """Eşleşme yapısaldır — düzyazıda adı anmak modu açmaz."""
    tp = _transcript(["mcp__devlet-arsivleri__devarsiv_search"], _RESEARCH, mode=False)
    try:
        with open(tp, "r+", encoding="utf-8") as f:
            body = f.read()
            f.seek(0)
            f.write(json.dumps({"type": "user", "message": {
                "content": "vekayinuvis plugin'ini konuşalım"}}) + "\n")
            f.write(body)
        assert _run("stop_coverage",
                    {"transcript_path": tp, "last_assistant_message": _RESEARCH}) is False
    finally:
        os.unlink(tp)
