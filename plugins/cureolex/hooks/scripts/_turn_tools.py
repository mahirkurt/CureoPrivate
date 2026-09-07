#!/usr/bin/env python3
"""cureolex Stop-hook ortak yardımcısı — "bu turda gerçekten hangi araçlar çağrıldı?"

`stop_coverage` eskiden YALNIZ son asistan **metnini** tarıyordu. Bu, cureolex'i üç kardeş
plugin arasında tek istisna bırakıyordu: vekayinuvis (`fleet_data_tool_invoked`) ve
historia-medicinae (`turn_called_mcp`) tetiklemeyi çoktan metinden **davranışa** taşımıştı.
Sonuç ölçüldü (2026-09-07): filo hakkında KOD/PLAN konuşan bir mühendislik turu — üç MCP
sunucusunun denetim raporu — "gerekçe" ve "madde 4.3" kelimeleri yüzünden reform-modu çıktısı
sanıldı ve G0 manifestosu istendi. Hiçbir hukuk normu üretilmemişti.

Bu modül tetiklemeyi yer gerçeğine bağlar: transkriptte son gerçek kullanıcı prompt'undan bu
yana asistanın çağırdığı `tool_use` adlarını toplar. Bir cureolex filo veri-aracı gerçekten
çağrılmadıysa G0 kapısı N/A'dır ve hook sessiz kalır.

Transkript yoksa/okunamıyorsa araç seti boş döner. Çağıran bunu `transcript_available()` ile
ayırt eder: transkript YOKSA davranış kapısına GÜVENİLMEZ (araç seti boş görünür ama bu
transkript yokluğundan olabilir) → metin-sezgisi yedeğine düşülür, böylece invaryant sessizce
kaybolmaz. Desen vekayinuvis/_turn_tools.py'den portlanmıştır; ayrışmasınlar diye API adları
birebir korunmuştur.
"""
import json
import os
import re

# cureolex'in wire'lı 22 sunucusu + 3 companion. Araç adı yüzeye göre
# `mcp__mevzuat__…`, `mcp__plugin_cureolex_mevzuat__…` veya `mcp__claude_ai_Mevzuat__…`
# biçiminde gelebilir; bu yüzden sunucu-adı ALT DİZGESİ aranır, tam ad değil.
# TİTCK claude.ai yüzeyinde `T_TCK` olarak görünür (görünen-ad bozulması) → ikisi de var.
_FLEET_NAMES = (
    r"mevzuat|mevzuat[-_]bilgisi|resmi[-_]?gazete|saglikbakanligi|saglik[-_]mcp|"
    r"titck|t_tck|tbmm|detsis|"
    r"health[-_]?policy|german[-_]?law|eurlex|fedlex|uk[-_]?legal|ich[-_]?guidelines|"
    r"intl[-_]?treaty|international[-_]?treaty|eudamed|oecd|"
    r"yok[-_]?akademik|yoktez|yok_tez|literatur|"
    r"openathens|annas|anamnesis|"
    # NOT: `\bYarg` KULLANILMAZ — araç adı `mcp__Yarg__…` biçiminde gelir ve `_`
    # kelime karakteri olduğu için "Yarg" öncesinde SINIR OLUŞMAZ (ölçüldü: test FAIL).
    r"yarg|open[-_]?law|ansvar"
)
# Saf teşhis/kimlik uçları RETRIEVAL DEĞİLDİR: bir sunucunun canlılığını yoklamak
# (ör. bu denetimde `oa_server_info`) substantif hukuk araştırması başlatmaz ve G0
# manifestosu gerektirmez. Bunlar kapıyı AÇMAZ.
_DIAGNOSTIC_ONLY = re.compile(
    r"(server_info|session_status|verify_access|_probe$|__probe|health|list_databases|"
    r"describe_capabilities|get_my_capabilities|jurisdiction_sources|list_jurisdictions)",
    re.IGNORECASE,
)
FLEET_DATA_TOOL = re.compile(r"mcp__.*(?:" + _FLEET_NAMES + r")", re.IGNORECASE)


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
        return any(
            isinstance(b, dict) and b.get("type") == "text" and str(b.get("text", "")).strip()
            for b in content
        )
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


def fleet_data_tool_invoked(event):
    """Bu turda substantif bir cureolex filo veri-aracı çağrıldı mı?

    Saf teşhis uçları (`*_server_info`, `*_session_status`, …) sayılmaz — bir sunucuyu
    yoklamak hukuk araştırması değildir.
    """
    return any(
        FLEET_DATA_TOOL.search(n) and not _DIAGNOSTIC_ONLY.search(n)
        for n in tools_since_last_prompt(event)
    )


def transcript_available(event):
    """Transkript dosyası var ve en az bir kayıt okunabiliyor mu?

    Davranış kapısı YALNIZ True iken uygulanır; False ise metin-sezgisi yedeğine düşülür.
    """
    path = event.get("transcript_path") or ""
    return bool(path and os.path.exists(path) and _records(path))
