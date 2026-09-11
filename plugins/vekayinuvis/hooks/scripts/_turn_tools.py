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
#
# KAPSAM KASITLIDIR — yasama/mevzuat (mevzuat/tbmm/resmigazete) ve saf-akademik (paper-search/
# consensus) BİLEREK DIŞARIDA: citation_discipline'ın uyguladığı disiplin ARŞİV-özeldir (orijinal
# takvim + Miladî çift-tarih, BOA fon/kutu/gömlek künyesi, katalog URL'i). Bir Cumhuriyet kanununa
# veya bir DOI'li makaleye Hicrî çift-tarih dayatmak YANLIŞ olur. Bu tool'ları buraya eklemeyin;
# yasama-atıf disiplini (kanun no + madde + Resmî Gazete tarih/sayı) KANUN_GEREKÇESİ modunun prose
# sorumluluğudur (kanun-gerekcesi-workflow.md), hook'la değil. G0 KAPSAM tarafı ise FLEET_DATA_TOOL
# ile tüm filoyu (mevzuat/tbmm/resmigazete/paper-search dahil) zaten yakalar — orada boşluk yok.
ARCHIVE_DATA_TOOL = re.compile(
    r"mcp__.*(?:"
    r"devarsiv_(?:search|detailed_search|semantic_search|deep_search|deep_result|get_belge|"
    r"get_belge_image|ocr_belge|ocr_belge_pages|get_archive_page|get_archive_pdf|"
    r"ocr_archive_pages|ocr_submit|ocr_result|list_archive|list_purchased)"
    r"|ottoman[-_]archives|__ottoman|yoktez|yok_tez|__literatur"
    r")",
    re.IGNORECASE,
)
# NOT: deep_search/deep_result RETRIEVAL'dir (deep_result kayıt yüzeyler) → citation kapsamı.
# `coverage` (store hasat defteri) ve `rebuild_archive` (yerel arşiv bakımı) BİLEREK DIŞARIDA —
# ledger/bakım, belge KAYIT iddiası değil (session_status/server_info/list_fon_categories gibi).
# G0 KAPSAM tarafı ise FLEET_DATA_TOOL'daki bare `devarsiv_` ile hepsini zaten yakalar.

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


#: Bu plugin'in kendi skill/komut ad alanı. Slash biçimi `/vekayinuvis:arsiv-dalis`,
#: Skill-aracı biçimi `{"skill": "vekayinuvis:arsiv-dalis"}` — ikisi de bu önekle başlar.
MODE_NAMESPACE = "vekayinuvis"
_COMMAND_RX = re.compile(
    r"<command-name>\s*/" + MODE_NAMESPACE + r"\b", re.IGNORECASE
)


def _message_text(rec):
    msg = rec.get("message", rec)
    content = msg.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(
            str(b.get("text", ""))
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


def _skill_invocations(rec):
    msg = rec.get("message", rec)
    content = msg.get("content", [])
    if not isinstance(content, list):
        return []
    out = []
    for b in content:
        if not isinstance(b, dict) or b.get("type") != "tool_use":
            continue
        if str(b.get("name", "")) != "Skill":
            continue
        skill = str((b.get("input") or {}).get("skill", ""))
        if skill:
            out.append(skill)
    return out


def mode_invoked(event):
    """Bu OTURUMDA vekayinüvis'in kendi skill'i veya slash komutu çalıştırıldı mı?

    G0 sözleşmesi vekayinüvis *araştırma çıktısı* içindir. Davranış kapısı tek başına bunu
    ayırt edemiyordu: `literatur` (DergiPark tam metni) hem bu filonun üyesidir hem de
    bağımsız bir MCP paketidir, dolayısıyla o paketin KODUNU ölçen bir mühendislik turu
    `mcp__…tr_literatur_get_journal` çağırır ve kapı açılır. 2026-09-10'da birebir
    yaşandı: tr-literatur lisans ayrıştırıcısı onarılırken hiçbir arşiv iddiası
    üretilmemişken G0 manifestosu istendi.

    Mod kapısı bu eksik boyutu ekler: filo aracına dokunmak yetmez, vekayinüvis modu bu
    oturumda gerçekten açılmış olmalıdır.

    Tarama OTURUM GENELİDİR (davranış kapısının aksine tur-başı değil): mod bir kez
    açıldıktan sonra takip turları da mod çıktısıdır. Eşleşme YAPISALDIR — düzyazıda
    "vekayinuvis" kelimesini anmak kapıyı açmaz; yalnız `<command-name>/vekayinuvis…` bloğu
    veya `Skill` aracının `skill` girdisi sayılır.
    """
    path = event.get("transcript_path") or ""
    if not path or not os.path.exists(path):
        return False
    for rec in _records(path):
        if _COMMAND_RX.search(_message_text(rec)):
            return True
        for skill in _skill_invocations(rec):
            if skill.lower().startswith(MODE_NAMESPACE):
                return True
    return False
