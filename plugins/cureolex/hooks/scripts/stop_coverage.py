#!/usr/bin/env python3
"""cureolex Stop hook — G0 kapsam manifestosu + confidence_label bütünlük kapısı.

Bir cureolex reform modu (DRAFT/AMEND/ANALYZE/COMPLY/OPINE/RIA/COMPARATIVE/TBMM/EX_POST)
koştuğunda çıktı ZORUNLU olarak (a) tam-filo kanıtı olan **kapsam manifestosu (G0)** ve
(b) **confidence_label**'ı taşımalıdır (SKILL §7). Bu hook son asistan mesajını inceler:
cureolex mod-çıktısı imzası varsa AMA manifesto/label eksikse, turu bloklamadan devam
ettirir ve eksiği tamamlatır. cureolex ile ilgisiz turlarda SESSİZ. Fail-open;
stop_hook_active döngüyü kırar.

KAPSAM (2026-09-07 daraltması). Tetikleme artık metinden **davranışa** bağlıdır ve bölüşüm
üç kardeş plugin'de aynıdır (vekayinuvis `fleet_data_tool_invoked`, historia-medicinae
`turn_called_mcp`; cureolex tek istisnaydı):

  * Transkript VARSA — birincil kapı `fleet_data_tool_invoked()`: bu turda gerçekten bir
    cureolex filo veri-aracı çağrıldı mı? Filo hakkında KOD/PLAN konuşmak araç çağırmaz →
    sessiz. Saf teşhis uçları (`*_server_info`, `*_session_status`) kapıyı açmaz.
  * Transkript YOKSA — davranış kapısına güvenilmez; metin-sezgisi yedeği çalışır:
    meta-tur baskılayıcı + (1 GÜÇLÜ sinyal VEYA 2 ZAYIF sinyal).

Neden gerekti (ölçüldü): üç MCP sunucusunun mühendislik denetim raporu, yalnız "gerekçe" ve
"madde 4.3" kelimeleri yüzünden reform çıktısı sanılıp G0 manifestosu istendi — ortada tek bir
hukuk normu yoktu. Eski mod jetonları ayrıca IGNORECASE ve sonda sınırsızdı, yani "draft",
"analyze", "comply", "amendment" gibi sıradan İngilizce kelimeler mod bildirimi sayılıyordu.

Stop sözleşmesi: {"decision":"block","reason":...} turu reddetmez — verilen gerekçeyle devam ettirir.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _turn_tools import (  # noqa: E402
    fleet_data_tool_invoked,
    mode_invoked,
    transcript_available,
)

# ── Reform-modu imzası: GÜÇLÜ / ZAYIF ayrımı ────────────────────────────────
# Eski tasarım altı GEVŞEK sinyalden ikisinin eşleşmesini "mod çıktısı" sayıyordu.
# 2026-09-07'de üç ayrı yanlış-pozitif kaynağı ÖLÇÜLDÜ (üç MCP sunucusunun denetim
# raporu reform çıktısı sanıldı; ortada tek bir hukuk normu yoktu):
#   1. `gerekçe` — Türkçe teknik metnin sıradan kelimesi ("reddetme gerekçesi").
#   2. `\bMADDE\s+\d+` IGNORECASE — "madde 4.3" gibi bir PLAN maddesi atfını yasama
#      maddesi sanıyordu.
#   3. Mod jetonları IGNORECASE ve SONDA `\b` YOK: `\bDRAFT`→"draft",
#      `\bANALYZE`→"analyze", `\bCOMPLY`→"comply", `\bAMEND`→"amendment" — yani
#      sıradan İngilizce kelimeler mod bildirimi sayılıyordu. `DEA` da sınırsızdı.
# Düzeltme: mod jetonları BÜYÜK-HARF DUYARLI + tam sınırlı; "MADDE" yasama başlığı
# olarak büyük harfle aranır; `gerekçe` yalnız yasama eş-dizimiyle GÜÇLÜ sayılır.
STRONG_SIGNALS = [
    re.compile(r"\bMADDE\s+\d+"),                       # yasama madde başlığı (BÜYÜK harf)
    re.compile(r"\b(DRAFT|AMEND|ANALYZE|COMPLY|OPINE|RIA|COMPARATIVE_LAW|"
               r"TBMM_KANUN_TEKLIFI|EX_POST)\b"),        # mod bildirimi (büyük-harf duyarlı)
    re.compile(r"(yönetmelik|tebliğ|kanun teklifi|CBK|genelge)\s+(taslağı|metni|değişik)",
               re.IGNORECASE),
    re.compile(r"(genel|madde)\s+gerekçe|gerekçe\s+(metni|bölümü)", re.IGNORECASE),
    re.compile(r"karşılaştırma cetveli", re.IGNORECASE),
    re.compile(r"\b\d{3,5}\s+sayılı\b", re.IGNORECASE),  # TR mevzuat atfı
]
# Tek başına yetmez — güçlü sinyal yokken en az İKİSİ gerekir.
WEAK_SIGNALS = [
    re.compile(r"\bgerekçe", re.IGNORECASE),
    re.compile(r"\b5210\b"),
    re.compile(r"\b(DEA|BEF|R6b)\b"),
    re.compile(r"belirlilik ilkes", re.IGNORECASE),
    re.compile(r"düzenleyici etki analizi", re.IGNORECASE),
]
# Plugin-iç öz-referans: reform ÇIKTISINDA görünmez, mühendislik/inceleme turunda görünür.
META_MARKERS = re.compile(
    r"hooks/scripts|stop_coverage|scope_guard|anamnesis_guard|fleet_probe|test_hooks|"
    r"plugins/cureolex|fleet\.lock\.json|plugin\.json|\.mcp\.json|MODE_SIGNALS",
    re.IGNORECASE,
)


def is_meta_turn(text):
    """Filo/mod ADINI anan ama üretmeyen tur mu? (inceleme/dokümantasyon/mühendislik)

    Yalnız transkript-YOK yedeğinde uygulanır; transkript varken davranış kapısı zaten
    kesindir — vekayinuvis'teki aynı bölüşüm.
    """
    return bool(META_MARKERS.search(text or ""))


# Zorunlu çıktı bileşenleri.
HAS_MANIFEST = re.compile(r"(kapsam manifesto|coverage manifest|\bG0\b|hit \d|skipped:|empty\b)", re.IGNORECASE)
HAS_CONFIDENCE = re.compile(r"(confidence[_ ]?label|combined_confidence|human_review_required|güven etiketi)", re.IGNORECASE)
# Manifesto varsa içinde görünmesi ZORUNLU satırlar — companion'lar + delegasyon
# plugin'leri (durum ne olursa olsun: hit/empty/degraded/skipped-with-reason).
# v3.5.0'da liste HARDCODE DEĞİL, fleet.lock.json'dan türetilir: yoktez
# wire'landığı için companion olmaktan çıktı. 2026-08-08'de AYNI geçiş
# Fedlex Swiss'te yaşandı — companion'dan wire'lı sunucuya geçti.
# Zorunlu satır = companions + delegations (şu an 3 + 2 = 5).
_TOKEN_RX = {
    "Yargı": r"\bYarg",
    "Open Law": r"Open[_ ]?Law",
    "Ansvar": r"\bAnsvar",
    "evidentia": r"\bevidentia",
    "sci-audit": r"\bsci[- ]?audit",
}

# Lock okunamazsa kullanılacak asgari liste (fail-open) — 3 companion + 2 delegasyon.
_FALLBACK_ROWS = {
    "Yargı (companion — G5 içtihat)": re.compile(_TOKEN_RX["Yargı"], re.IGNORECASE),
    "Open Law (companion — UK birincil metin)": re.compile(_TOKEN_RX["Open Law"], re.IGNORECASE),
    "Ansvar (companion — Mod7 58-yargı)": re.compile(_TOKEN_RX["Ansvar"], re.IGNORECASE),
    "evidentia (klinik delegasyon)": re.compile(_TOKEN_RX["evidentia"], re.IGNORECASE),
    "sci-audit (çıktı-QA delegasyonu)": re.compile(_TOKEN_RX["sci-audit"], re.IGNORECASE),
}


def _load_lock():
    """fleet.lock.json'u stdlib json ile okur; okunamazsa None (fail-open)."""
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "..", "..", "fleet.lock.json")
        with open(os.path.normpath(path), encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def mandatory_rows(lock=None):
    """Manifestoda BULUNMASI ZORUNLU satırları lock'tan türetir.

    Yalnız companion (wire edilemez dış connector) + delegasyon plugin'leri
    denetlenir. Wire'lı 22 server için satır-satır regex denetimi YAPILMAZ —
    kırılgan olur ve yanlış-pozitif üretir; onların kanıtı G0 manifestosunun
    varlığıdır. Bilinmeyen ad için ada dayalı jenerik desen üretilir.
    """
    if lock is None:
        lock = _load_lock()
    if not lock:
        return dict(_FALLBACK_ROWS)
    rows = {}
    for item in list(lock.get("companions", [])) + list(lock.get("delegations", [])):
        name = item.get("name", "")
        row = item.get("manifest_row") or name
        pattern = _TOKEN_RX.get(name)
        if pattern is None:  # fleet.yaml'e yeni ad eklenirse sessizce düşmesin
            pattern = re.escape(name).replace(r"\ ", r"[_ ]?").replace(r"\-", r"[- ]?")
        rows[row] = re.compile(pattern, re.IGNORECASE)
    return rows or dict(_FALLBACK_ROWS)


def last_assistant_message(event):
    msg = event.get("last_assistant_message")
    if isinstance(msg, str) and msg.strip():
        return msg
    path = event.get("transcript_path") or ""
    if not path or not os.path.exists(path):
        return ""
    try:
        last = ""
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except Exception:
                    continue
                if rec.get("type") == "assistant" or rec.get("role") == "assistant":
                    content = rec.get("message", {}).get("content", rec.get("content", ""))
                    if isinstance(content, list):
                        content = " ".join(
                            b.get("text", "") for b in content if isinstance(b, dict)
                        )
                    if isinstance(content, str) and content.strip():
                        last = content
        return last
    except Exception:
        return ""


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    if event.get("stop_hook_active"):
        sys.exit(0)  # döngü koruması

    text = last_assistant_message(event)
    if not text:
        sys.exit(0)

    # DAVRANIŞ KAPISI (birincil, transkript varsa) — yer gerçeği: bu turda gerçekten bir
    # cureolex filo veri-aracı çağrıldı mı? Filo hakkında KOD/PLAN konuşmak (sunucu adlarını
    # port tablosunda/.mcp.json'da anmak, hook'un kendi kodunu düzenlemek) araç ÇAĞIRMAZ
    # → kapı kapalı → sessiz. Saf teşhis uçları (`*_server_info`) da kapıyı açmaz.
    # Transkript YOKSA davranış kapısına güvenilmez (araç seti boş görünür ama bu transkript
    # yokluğundan olabilir) → metin-sezgisi yedeğine düşülür ki invaryant sessizce kaybolmasın.
    # Bölüşüm vekayinuvis/stop_coverage.py ile birebir; üç kardeş plugin ayrışmasın.
    if transcript_available(event):
        # MOD KAPISI (davranış kapısından önce) — G0 sözleşmesi cureolex *mod çıktısı*
        # içindir. Davranış kapısı tek başına yetmiyor: `literatur` hem bu filonun üyesi
        # hem de bağımsız bir MCP paketi, dolayısıyla o paketin KODUNU ölçen bir tur
        # filo aracı çağırmış görünür. Modun bu oturumda gerçekten açılmış olması şart.
        if not mode_invoked(event):
            sys.exit(0)
        if not fleet_data_tool_invoked(event):
            sys.exit(0)
    else:
        if is_meta_turn(text):
            sys.exit(0)  # filo/mod adını anan ama üretmeyen mühendislik turu → sessiz
        strong = any(rx.search(text) for rx in STRONG_SIGNALS)
        weak = sum(1 for rx in WEAK_SIGNALS if rx.search(text))
        if not (strong or weak >= 2):
            sys.exit(0)  # cureolex mod-çıktısı değil → sessiz

    missing = []
    if not HAS_MANIFEST.search(text):
        missing.append("kapsam manifestosu (G0 — wire'lı tüm MCP'lerin hit/empty/degraded/skipped-with-reason kanıtı)")
    else:
        # Manifesto var → companion + delegasyon satırları da mevcut olmalı (SKILL §7 / coverage-manifest.md).
        absent_rows = [label for label, rx in mandatory_rows().items()
                       if not rx.search(text)]
        if absent_rows:
            missing.append(
                "manifestoda zorunlu satır(lar): " + ", ".join(absent_rows)
                + " (her biri hit/empty/degraded/skipped-with-reason olarak yazılmalı; "
                "companion skip'i ilgili kapıyı CONDITIONAL yapar)"
            )
    if not HAS_CONFIDENCE.search(text):
        missing.append("confidence_label (mod + combined_confidence + human_review_required:true + scope_disclaimer)")

    if not missing:
        sys.exit(0)  # tam → sessiz

    reason = (
        "[cureolex G0/çıktı-sözleşmesi] Bu reform-modu çıktısı şu ZORUNLU bileşen(ler)i "
        "taşımıyor: " + "; ".join(missing) + ". SKILL §7 gereği bunları ekleyerek tamamla. "
        "Manifesto biçimi: shared/coverage-manifest.md. Tam-filo iddiası (hepsi her sorguda "
        "çalıştı) manifesto olmadan doğrulanamaz. Herhangi bir server atlandıysa gerekçesi "
        "('anahtar yok' / 'mod için N/A') yazılmalı — sessiz atlama yasak."
    )
    sys.stdout.write(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


if __name__ == "__main__":
    main()
