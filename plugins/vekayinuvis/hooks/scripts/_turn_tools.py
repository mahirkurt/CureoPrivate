#!/usr/bin/env python3
"""vekayinuvis Stop-hook ortak yardımcısı — "bu turda gerçekten hangi araçlar çağrıldı?"

İki Stop hook'u (stop_coverage, citation_discipline) eskiden yalnız son asistan **metnini**
tarıyordu; `devarsiv` / `mevzuat` / `tbmm` gibi kelimeler bir araç-adı, connector-adı, port
tablosu veya `.mcp.json` bağlamında geçtiğinde de tetikleniyorlardı (ops/altyapı turlarında
kör yanlış-pozitif). Bu modül tetiklemeyi metinden **davranışa** taşır: transkriptte son gerçek
kullanıcı prompt'undan bu yana asistanın çağırdığı `tool_use` adlarını toplar. Bir vekayinüvis
veri-aracı gerçekten çağrılmadıysa disiplin/manifesto kapısı N/A'dır ve hook sessiz kalır.

Transkript yoksa/okunamıyorsa araç seti boş döner. Hook'lar bunu transcript_available() ile
ayırt eder: transkript YOKSA davranış kapısına güvenmez, metin-sezgisi yedeğine düşer
(invaryant sessizce kaybolmasın — kullanıcı sertleştirmesi 2026-07-17).
"""
import json
import os
import re

# Gerçek RETRIEVAL yapan devlet-arsivleri + Osmanlı/tez arşiv veri-araçları.
# (session_status / server_info / list_fon_categories retrieval değildir → atıf disiplini gerektirmez.)
ARCHIVE_DATA_TOOL = re.compile(
    r"mcp__.*(?:"
    r"devarsiv_(?:search|detailed_search|semantic_search|get_belge|get_belge_image|"
    r"ocr_belge|ocr_belge_pages|get_archive_page|get_archive_pdf|ocr_archive_pages|"
    r"ocr_submit|ocr_result|list_archive|list_purchased)"
    r"|ottoman[-_]archives|__ottoman|yoktez|yok_tez|__literatur"
    r")",
    re.IGNORECASE,
)

# Tüm tam-filo veri-araçları (substantif araştırma başladı sinyali → G0 manifesto beklenir).
FLEET_DATA_TOOL = re.compile(
    r"mcp__.*(?:"
    r"devarsiv_|devlet[-_]arsivleri|ottoman|yoktez|yok_tez|literatur|dergipark|"
    r"resmigazete|rg_get|rg_search|rg_list|mevzuat|tbmm|detsis|anamnesis|annas|"
    r"openathens|yok[-_]akademik|consensus|scholar[-_]gateway|__exa|tavily|paper[-_]search"
    r")",
    re.IGNORECASE,
)


def _records(path):
    out = []
    try:
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        return []
    return out


def _is_user_prompt(rec):
    """Gerçek kullanıcı prompt'u mu? (tool_result taşıyıcı user kaydı DEĞİL)."""
    if rec.get("type") != "user" and rec.get("role") != "user":
        return False
    msg = rec.get("message", rec)
    content = msg.get("content", "")
    if isinstance(content, str):
        return bool(content.strip())
    if isinstance(content, list):
        has_text = any(
            isinstance(b, dict) and b.get("type") == "text" and str(b.get("text", "")).strip()
            for b in content
        )
        return has_text
    return False


def _tool_uses(rec):
    if rec.get("type") != "assistant" and rec.get("role") != "assistant":
        return []
    msg = rec.get("message", rec)
    content = msg.get("content", [])
    if not isinstance(content, list):
        return []
    return [
        str(b.get("name", ""))
        for b in content
        if isinstance(b, dict) and b.get("type") == "tool_use"
    ]


def tools_since_last_prompt(event):
    """Son gerçek kullanıcı prompt'undan bu yana çağrılan araç adlarının kümesi."""
    path = event.get("transcript_path") or ""
    if not path or not os.path.exists(path):
        return set()
    recs = _records(path)
    last_prompt = -1
    for i, r in enumerate(recs):
        if _is_user_prompt(r):
            last_prompt = i
    names = set()
    for r in recs[last_prompt + 1:]:
        names.update(_tool_uses(r))
    return names


def archive_data_tool_invoked(event):
    """Bu turda gerçek bir arşiv-belge veri-aracı (arama/belge/OCR/tez) çağrıldı mı?"""
    return any(ARCHIVE_DATA_TOOL.search(n) for n in tools_since_last_prompt(event))


def fleet_data_tool_invoked(event):
    """Bu turda herhangi bir tam-filo veri-aracı çağrıldı mı? (substantif araştırma sinyali)"""
    return any(FLEET_DATA_TOOL.search(n) for n in tools_since_last_prompt(event))


def transcript_available(event):
    """Transkript dosyası var ve en az bir kayıt okunabiliyor mu?

    SERTLEŞTİRME (kullanıcı 2026-07-17): davranış kapısı yalnız transcript_available() True iken
    UYGULANIR. False ise hook, davranış kapısına GÜVENMEZ (araç seti boş görünür ama bu transkript
    yokluğundan olabilir) → metin-sezgisi yedeğine düşer. Böylece: transkript varken KESİNLİK
    (araç çağrılmadıysa sessiz), transkript yokken ESKİ DAVRANIŞ (manifesto/disiplin invaryantı
    sessizce kaybolmaz).
    """
    path = event.get("transcript_path") or ""
    return bool(path and os.path.exists(path) and _records(path))
