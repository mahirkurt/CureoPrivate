#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
carbon-edupedia · Modül Kalite Kapısı Doğrulayıcı (validate_module.py)
====================================================================
Üretilen bir etkileşimli öğrenim modülü HTML'ini SKILL.md §12 kalite
kapılarına göre denetler. Salt-metin (regex/heuristik) denetimdir;
tarayıcı gerektirmez. Çıkış kodu: 0 = tüm FAIL kapıları geçti, 1 = ihlal.

Kullanım:
    python scripts/validate_module.py <modul.html> [--strict]

Kapılar:
    G-EMOJI         (FAIL) — çıktıda emoji bulunmamalı
    G-CARBON        (FAIL) — IBM Plex yüklü; çekirdek --cds-* token'ları tanımlı/kullanımda
    G-A11Y          (FAIL) — lang, <title>, reduced-motion, ARIA, odak görünürlüğü
    G-INTERACT      (FAIL) — her quiz sorusunda correctIndex; (WARN) explanation
    G-SELFCONTAINED (FAIL) — yerel/harici dosya bağımlılığı yok (yalnız https/inline)
    G-CONTRAST      (WARN) — metin rengi token'ı; aksanın küçük metinde kullanımı uyarısı
    G-WELLBEING     (FAIL) — cezalandırıcı/süre-baskısı dili yok; (WARN) uzun modülde mola/azaltılmış hareket
    G-SVG           (FAIL) — figür SVG'leri role="img"+başlık; (WARN) ham-hex yerine token renk
    G-AUDIO         (FAIL) — ses varsa: susturulabilir + reduced-motion + otomatik-oynatma/döngü yok
    G-TOKEN         (WARN) — çekirdek --cds-* değerleri @carbon/themes otoritesiyle birebir; white support-info regresyonu FAIL
    G-CURRICULUM    (FAIL) — koşullu: CURRICULUM modu/curriculum bloğu varsa kazanım→segment izlenebilirliği
"""
import sys, re, argparse

# ---- Emoji aralıkları (yaygın bloklar) ----
EMOJI_RE = re.compile(
    "[" 
    "\U0001F300-\U0001FAFF"   # semboller, piktograflar, ek semboller
    "\U00002600-\U000027BF"   # çeşitli semboller + dingbats
    "\U0001F000-\U0001F0FF"   # mahjong/domino/playing cards
    "\U0001F1E6-\U0001F1FF"   # bölgesel bayrak harfleri
    "\U00002190-\U000021FF"   # oklar (bazı emoji oklar) — yanlış pozitifi azaltmak için VS16 ile birlikte aranır
    "\U0000FE0F"              # variation selector-16 (emoji sunum)
    "\U00002028-\U00002029"   # line/para separators (zararsız ama temizlik)
    "\U0001F004\U0001F0CF\U0000203C\U00002049"
    "]"
)
# Daha güvenli emoji yakalama: VS16 veya ana emoji blokları
CORE_EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000026FF\U00002700-\U000027BF\U0001F1E6-\U0001F1FF]"
    "|\U0000FE0F"
)

RESET="\033[0m"; RED="\033[31m"; GRN="\033[32m"; YEL="\033[33m"; BOLD="\033[1m"; DIM="\033[2m"

class Result:
    def __init__(self):
        """Boş bulgu listesi ve fail bayrağı başlatır."""
        self.rows=[]; self.fail=False
    def add(self, gate, status, msg):
        """Bir kapı sonucunu (PASS|FAIL|WARN) kaydeder; FAIL ise fail bayrağını kaldırır."""
        self.rows.append((gate,status,msg))
        if status=="FAIL": self.fail=True
    def report(self):
        """Renkli, hizalı denetim raporunu stdouta basar."""
        print(f"\n{BOLD}carbon-edupedia · Modül Doğrulama Raporu{RESET}")
        print("="*64)
        for gate,status,msg in self.rows:
            c={"PASS":GRN,"FAIL":RED,"WARN":YEL}[status]
            tag={"PASS":"GEÇTİ","FAIL":"İHLAL","WARN":"UYARI"}[status]
            print(f"  {c}{tag:5}{RESET}  {BOLD}{gate:16}{RESET} {msg}")
        print("="*64)
        n_fail=sum(1 for _,s,_ in self.rows if s=="FAIL")
        n_warn=sum(1 for _,s,_ in self.rows if s=="WARN")
        verdict = f"{RED}{n_fail} İHLAL{RESET}" if n_fail else f"{GRN}TÜM FAIL KAPILARI GEÇTİ{RESET}"
        print(f"  Sonuç: {verdict}  ·  {YEL}{n_warn} uyarı{RESET}\n")

def gate_emoji(html, R):
    """G-EMOJI: çıktıda emoji bulunmadığını doğrular (FAIL kapısı)."""
    hits=CORE_EMOJI_RE.findall(html)
    # VS16 tek başına bazen meşru olabilir; emoji bloğuyla birlikteyse kesin emoji
    real=[h for h in hits if h!="\ufe0f"] or hits
    if real:
        sample=", ".join(sorted(set(real))[:6])
        R.add("G-EMOJI","FAIL", f"{len(real)} emoji bulundu (örn: {sample}). Carbon ikon/piktogram/SVG kullanın.")
    else:
        R.add("G-EMOJI","PASS","Emoji yok.")

def gate_carbon(html, R):
    """G-CARBON: IBM Plex ve çekirdek --cds-* token kullanımını doğrular (FAIL)."""
    issues=[]
    if "IBM Plex Sans" not in html: issues.append("IBM Plex Sans yüklü değil")
    core=["--cds-text-primary","--cds-background","--cds-interactive",
          "--cds-support-success","--cds-support-error"]
    missing=[t for t in core if t not in html]
    if missing: issues.append("eksik token: "+", ".join(missing))
    # token kullanımı: var(--cds-text-primary) gerçekten kullanılıyor mu
    if "var(--cds-text-primary)" not in html and "var(--accent" not in html:
        issues.append("token'lar tanımlı ama kullanımda görünmüyor")
    if issues:
        R.add("G-CARBON","FAIL","; ".join(issues))
    else:
        R.add("G-CARBON","PASS","IBM Plex + çekirdek Carbon token'ları tanımlı ve kullanımda.")

def gate_a11y(html, R):
    """G-A11Y: lang, title, reduced-motion, aria-live, odak ve görsel rollerini denetler (FAIL)."""
    issues=[]
    if not re.search(r'<html[^>]*\blang=', html): issues.append("<html lang> yok")
    if not re.search(r'<title>.*?</title>', html, re.S): issues.append("<title> yok")
    if "prefers-reduced-motion" not in html: issues.append("reduced-motion bloğu yok")
    if "aria-live" not in html: issues.append("aria-live (anlık geri bildirim) yok")
    # outline:none kötüye kullanımı (odak halkası kaldırılmış mı)
    bad_outline = re.findall(r'outline\s*:\s*none', html)
    if bad_outline and "focus-visible" not in html:
        issues.append("outline:none var ama :focus-visible yedeği yok")
    if "role=\"img\"" not in html and "aria-hidden" not in html:
        issues.append("görsel rolleri (role=img / aria-hidden) yok")
    if issues:
        R.add("G-A11Y","FAIL","; ".join(issues))
    else:
        R.add("G-A11Y","PASS","lang, title, reduced-motion, aria-live, odak ve görsel rolleri tamam.")

def gate_interact(html, R):
    """G-INTERACT: her quiz sorusunda correctIndex; explanation eksikse WARN (FAIL)."""
    # MODULE_DATA içindeki quiz bütünlüğü (heuristik)
    stems=len(re.findall(r'\bstem\s*:', html))
    correct=len(re.findall(r'\bcorrectIndex\s*:', html))
    expl=len(re.findall(r'\bexplanation\s*:', html))
    if stems==0:
        R.add("G-INTERACT","WARN","MODULE_DATA'da quiz sorusu (stem) bulunamadı (mod quiz değilse normal).")
        return
    if correct < stems:
        R.add("G-INTERACT","FAIL",
              f"{stems} soru var ama {correct} correctIndex; her soruda doğru cevap zorunlu.")
    else:
        R.add("G-INTERACT","PASS", f"{stems} sorunun her birinde correctIndex mevcut.")
    if expl < stems:
        R.add("G-INTERACT","WARN",
              f"{stems} sorudan {expl} tanesinde açıklama (explanation) var; her soruya açıklama önerilir.")

def gate_selfcontained(html, R):
    """G-SELFCONTAINED: yerel harici dosya bağımlılığı olmadığını doğrular (FAIL)."""
    # relatif src/href (http olmayan, # olmayan, data: olmayan)
    refs=re.findall(r'(?:src|href)\s*=\s*["\']([^"\']+)["\']', html)
    bad=[r for r in refs if not (r.startswith("http") or r.startswith("#")
         or r.startswith("data:") or r.startswith("//"))]
    if bad:
        R.add("G-SELFCONTAINED","FAIL","yerel dosya bağımlılığı: "+", ".join(bad[:5]))
    else:
        R.add("G-SELFCONTAINED","PASS","Tüm varlıklar satır içi veya CDN; harici yerel bağımlılık yok.")

def gate_contrast(html, R):
    """G-CONTRAST: gövde metni text-primary, aksanın küçük metinde kullanımını uyarır (WARN)."""
    # heuristik: gövde metni aksan rengiyle mi boyanmış? (küçük metinde aksan riski)
    warn=[]
    # body color aksan değil text-primary olmalı
    if re.search(r'body\s*\{[^}]*color\s*:\s*var\(--accent', html):
        warn.append("gövde metni aksan rengiyle boyanmış (kontrast riski)")
    if not re.search(r'color\s*:\s*var\(--cds-text-primary\)', html):
        warn.append("--cds-text-primary metin rengi olarak kullanılmamış")
    if warn:
        R.add("G-CONTRAST","WARN","; ".join(warn)+" — küçük metin daima text-primary olmalı.")
    else:
        R.add("G-CONTRAST","PASS","Metin rengi token'ı uygun; aksan büyük/dolgu öğelerinde.")

def gate_wellbeing(html, R):
    """G-WELLBEING: DEHB klinik kanıtına dayalı sorumlu/etik kullanım kapısı.

    - Cezalandırıcı / süre-baskısı dili → FAIL. DEHB'de duygu-düzenleme kırılganlığı
      (Groves 2021) ve oyun-bağımlılığı yatkınlığı (Rodrigo-Yanguas 2022) nedeniyle
      başarısızlık/zaman baskısı dili kullanılmaz.
    - >=6 segmentlik modülde beyin molası yoksa → WARN (Zhu 2023 NMA; ped §4).
    - prefers-reduced-motion yoksa → WARN (aşırı-uyarım; A11Y ile örtüşür).
    """
    punitive = re.compile(
        r"(kaybettin|kaybettiniz|s\u00fcre doldu|s\u00fcren doldu|s\u00fcreniz doldu|"
        r"zaman doldu|game over|oyun bitti|ba\u015far\u0131s\u0131z oldun)", re.IGNORECASE)
    hits = sorted(set(m.group(0).lower() for m in punitive.finditer(html)))
    warns = []
    types = re.findall(r'type\s*:\s*"([a-z]+)"', html)
    total = len(types); breaks = types.count("brainbreak")
    if total >= 6 and breaks == 0:
        warns.append(f"{total} segmentte beyin molası yok — uzun modülde en az 1 brainbreak önerilir")
    if "prefers-reduced-motion" not in html:
        warns.append("prefers-reduced-motion bildirimi yok")
    if hits:
        R.add("G-WELLBEING","FAIL","cezalandırıcı/süre-baskısı dili: "+", ".join(hits))
    elif warns:
        R.add("G-WELLBEING","WARN","; ".join(warns))
    else:
        R.add("G-WELLBEING","PASS","Cezalandırıcı/süre-baskısı dili yok; mola ritmi ve hareket-azaltma uygun.")

SVG_BLOCK_RE = re.compile(r"<svg\b[^>]*>.*?</svg>", re.S | re.I)
def _svg_decorative(open_tag):
    """Sprite / @carbon ikon / piktogram gibi salt-dekor SVG mi?"""
    return ('aria-hidden="true"' in open_tag or "display:none" in open_tag
            or "cds-icon" in open_tag or 'class="pic"' in open_tag)

def _svg_accessible(block, open_tag):
    """Figür SVG erişilebilir mi: role=\"img\" + başlık/etiket."""
    has_role  = 'role="img"' in open_tag
    has_label = ("<title" in block) or ("aria-label=" in open_tag) or ("aria-labelledby=" in open_tag)
    return has_role and has_label

def _svg_report(R, checked, fails, warns):
    """G-SVG sonucunu Result'a yazar."""
    if checked == 0:
        R.add("G-SVG","PASS","Figür SVG yok; yalnız dekoratif ikon/sprite mevcut.")
    elif fails:
        R.add("G-SVG","FAIL", f"{len(fails)} figür SVG erişilemez: " + "; ".join(fails[:3]))
    elif warns:
        R.add("G-SVG","WARN", "; ".join(sorted(set(warns))) + f" ({checked} figür SVG denetlendi)")
    else:
        R.add("G-SVG","PASS", f"{checked} figür SVG erişilebilir ve tema-duyarlı (role+başlık, token renk).")

def gate_svg(html, R):
    """Figür SVG'leri erişilebilir (role=img + başlık) ve tema-duyarlı (token renk) olmalı.

    Dekoratif SVG'ler (sprite, @carbon ikon/piktogram) aria-hidden / cds-icon / class=pic
    ile dışlanır; yalnız diyagram ve grafik figürleri denetlenir.
    """
    fails=[]; warns=[]; checked=0
    for b in SVG_BLOCK_RE.findall(html):
        open_tag = b[:b.find(">")+1]
        if _svg_decorative(open_tag):
            continue
        checked += 1
        if not _svg_accessible(b, open_tag):
            fails.append('role="img"+<title>/aria eksik (' + re.sub(r"\s+", " ", open_tag)[:60] + "…)")
        if re.search(r'(?:fill|stroke)="#', b):
            warns.append('ham hex renk (fill/stroke="#…") yerine var(--…)/currentColor kullanın')
    _svg_report(R, checked, fails, warns)

def _audio_earcon_issues(html):
    """Earcon/ses-efekti katmanının güvenlik ihlallerini toplar (susturma, autoplay, loop)."""
    issues=[]
    if not re.search(r'state\.sound|toggleSound|id="soundBtn"', html):
        issues.append("earcon: susturma kontrolü yok (state.sound/toggleSound/#soundBtn)")
    if re.search(r"<audio[^>]*\bautoplay", html) or re.search(r"<video[^>]*\bautoplay", html):
        issues.append("earcon: autoplay ile otomatik ses")
    if re.search(r"\bloop\s*[:=]\s*true", html) or re.search(r"\.loop\s*=\s*true", html):
        issues.append("earcon: döngülü (loop) ses — sürekli arka plan sesi yasak")
    return issues


def _audio_tts_issues(html):
    """Sesli-okuma/TTS katmanının güvenlik ihlallerini toplar (kontrol, durdurma, varsayılan kapalı)."""
    issues=[]
    if not re.search(r'toggleTTS|id="ttsBtn"|#ttsBtn|state\.tts', html):
        issues.append("TTS: kullanıcı kontrolü yok (toggleTTS/#ttsBtn/state.tts)")
    if ".cancel(" not in html:
        issues.append("TTS: konuşma durdurma yok (speechSynthesis.cancel)")
    if not re.search(r'data-tts["\']\s*,\s*["\']off', html):
        issues.append('TTS: varsayılan kapalı değil (init data-tts="off" ayarı bulunamadı)')
    return issues


def _audio_pass_msg(uses_earcon, uses_tts):
    """G-AUDIO başarı mesajını üretir (kullanılan katmanlara göre)."""
    layers=[]
    if uses_earcon: layers.append("earcon susturulabilir")
    if uses_tts: layers.append("TTS kullanıcı-denetimli/durdurulabilir, varsayılan kapalı")
    return ("İşitsel katman(lar) güvenli ("+", ".join(layers)
            +"); reduced-motion duyarlı, otomatik-oynatma/döngü yok.")


def gate_audio(html, R):
    """G-AUDIO: işitsel katmanlar (earcon + sesli-okuma/TTS) opsiyonel, susturulabilir/durdurulabilir,
    reduced-motion duyarlı ve varsayılan kapalı olmalı; sürekli arka plan sesi (autoplay/loop) yasak (FAIL).

    DEHB'de sürekli/alakasız işitsel uyaran dağıtıcıdır; kısa olay-earcon'ları geçici uyarıcı etki
    sağlayabilir, metin-konuşma (TTS) ise kod-çözme yükünü azaltıp dinleme-anlama ile okumayı eşleştirir
    — ANCAK her iki katman da opsiyonel, kullanıcı-denetimli ve varsayılan kapalı olmalı; otomatik-oynatma,
    döngü ve istem-dışı otomatik okuma yasaktır. İki katman ayrı ayrı denetlenir.
    """
    uses_earcon = bool(re.search(r"\b(?:webkit)?AudioContext\b", html)) or ("<audio" in html)
    uses_tts    = bool(re.search(r"\bspeechSynthesis\b", html)) or ("SpeechSynthesisUtterance" in html)
    if not uses_earcon and not uses_tts:
        R.add("G-AUDIO","PASS","İşitsel katman kullanılmıyor (uygulanmaz).")
        return
    issues=[]
    if "prefers-reduced-motion" not in html:
        issues.append("prefers-reduced-motion referansı yok")
    if uses_earcon:
        issues += _audio_earcon_issues(html)
    if uses_tts:
        issues += _audio_tts_issues(html)
    if issues:
        R.add("G-AUDIO","FAIL","; ".join(issues))
    else:
        R.add("G-AUDIO","PASS",_audio_pass_msg(uses_earcon, uses_tts))

def _curriculum_collect(block, html):
    """curriculum bloğundan kazanım kodlarını, text sayısını ve mappedTo→segment
    eşleme durumunu toplar. (gate_curriculum karmaşıklığını düşürmek için ayrıldı.)

    Döndürür: (codes, n_texts, mapped_ids, missing_ids)
    """
    codes = re.findall(r'\bcode\s*:\s*["\']([^"\']+)["\']', block)
    n_texts = len(re.findall(r'\btext\s*:', block))
    mapped_ids = set()
    for arr in re.findall(r'mappedTo\s*:\s*\[([^\]]*)\]', block):
        mapped_ids |= set(re.findall(r'["\']([^"\']+)["\']', arr))
    all_ids = set(re.findall(r'\bid\s*:\s*["\']([^"\']+)["\']', html))
    missing = [mid for mid in sorted(mapped_ids) if mid not in all_ids]
    return codes, n_texts, mapped_ids, missing


def _curriculum_cite_ok(html):
    """meta.sourceCitation kazanım kodu (FB.5.3.1.1) veya korpus/MCP anahtarı içeriyor mu."""
    cite_m = re.search(r'sourceCitation\s*:\s*["\']?(.*?)["\']?\s*\n', html, re.S)
    cite = cite_m.group(1) if cite_m else ""
    return bool(re.search(r'[A-ZÇĞİÖŞÜ]{1,4}\.\d', cite)) or \
           bool(re.search(r'(?i)(müfredat|maarif|corpus|kazanım|tymm)', cite))


def _curriculum_eval(codes, n_texts, mapped_ids, missing, cite_ok):
    """Toplanan sinyallerden (issues, warns) listelerini üretir. Saf karar mantığı."""
    issues=[]; warns=[]
    if not codes:
        issues.append("curriculum.outcomes[] boş veya `code` içermiyor")
    if n_texts < len(codes):
        warns.append(f"{len(codes)} kazanımdan {n_texts} tanesinde `text` var (her kazanımda metin önerilir)")
    if mapped_ids and missing:
        issues.append("mappedTo segment id'si segments[]'te yok: "+", ".join(missing[:5]))
    if not mapped_ids and codes:
        warns.append("hiçbir kazanım segmente bağlanmamış (mappedTo eksik) — izlenebilirlik zayıf")
    if not cite_ok:
        warns.append("meta.sourceCitation kazanım kodu/korpus referansı içermiyor")
    return issues, warns


_CARBON_AUTHORITY = {
    # @carbon/themes 11.75.0 — çekirdek token otorite haritası (white | g100).
    # Kaynak: assets/carbon-v11-authority.json (scripts/sync_carbon_tokens.py üretir).
    "white": {
        "--cds-background":"#ffffff","--cds-layer-01":"#f4f4f4","--cds-layer-02":"#ffffff",
        "--cds-layer-03":"#f4f4f4","--cds-border-subtle-00":"#e0e0e0","--cds-border-subtle-01":"#c6c6c6",
        "--cds-border-strong":"#8d8d8d","--cds-text-primary":"#161616","--cds-text-secondary":"#525252",
        "--cds-interactive":"#0f62fe","--cds-link-primary":"#0f62fe","--cds-focus":"#0f62fe",
        "--cds-button-primary":"#0f62fe","--cds-button-primary-hover":"#0050e6",
        "--cds-button-primary-active":"#002d9c","--cds-support-success":"#24a148",
        "--cds-support-error":"#da1e28","--cds-support-warning":"#f1c21b","--cds-support-info":"#0043ce",
    },
    "g100": {
        "--cds-background":"#161616","--cds-layer-01":"#262626","--cds-layer-02":"#393939",
        "--cds-layer-03":"#525252","--cds-border-subtle-00":"#393939","--cds-border-subtle-01":"#525252",
        "--cds-border-strong":"#6f6f6f","--cds-text-primary":"#f4f4f4","--cds-text-secondary":"#c6c6c6",
        "--cds-interactive":"#4589ff","--cds-link-primary":"#78a9ff","--cds-focus":"#ffffff",
        "--cds-button-primary":"#0f62fe","--cds-button-primary-hover":"#0050e6",
        "--cds-button-primary-active":"#002d9c","--cds-support-success":"#42be65",
        "--cds-support-error":"#fa4d56","--cds-support-warning":"#f1c21b","--cds-support-info":"#4589ff",
    },
}

def _theme_block(html, selector):
    """Verilen tema seçicisinin ilk CSS bloğunu döndürür (yoksa '')."""
    i = html.find(selector)
    if i < 0: return ""
    j = html.find("{", i); k = html.find("}", j)
    return html[j+1:k] if j >= 0 and k >= 0 else ""

def _classify_token(theme, tok, val, block, norm):
    """Tek bir --cds-* token'ını otoriteyle karşılaştırır.

    Döndürür: (drift_item, fail_item). Token tanımsız, alias (var(...)) veya
    otoriteyle birebirse her ikisi de None'dur. white/support-info #4589ff
    bilinen AA-kontrast regresyonu fail_item olarak işaretlenir.
    """
    m = re.search(re.escape(tok) + r"\s*:\s*([^;}]+)", block)
    if not m:
        return None, None  # tanımsız token denetlenmez (eksiklik G-CARBON'un işi)
    got = norm(m.group(1))
    if got.startswith("var("):
        return None, None  # alias kabul
    if got == norm(val):
        return None, None
    item = f"{theme} {tok}: {m.group(1).strip()} (otorite: {val})"
    if theme == "white" and tok == "--cds-support-info" and got == "#4589ff":
        return None, item + " — AA kontrast regresyonu"
    return item, None


def gate_token_authority(html, R):
    """G-TOKEN: tanımlı çekirdek --cds-* token'larının @carbon/themes otorite
    değerleriyle eşleştiğini denetler. Sapma = WARN (eski modüllerle geriye uyum);
    bilinen AA regresyonu (white'ta support-info #4589ff) = FAIL."""
    drift, fail = [], []
    blocks = {"white": _theme_block(html, '[data-theme="white"]') or _theme_block(html, ":root"),
              "g100":  _theme_block(html, '[data-theme="g100"]')}
    norm = lambda v: re.sub(r"\s+", "", v).lower().replace("0.", ".")
    for theme, expect in _CARBON_AUTHORITY.items():
        block = blocks.get(theme, "")
        if not block: continue
        for tok, val in expect.items():
            d, f = _classify_token(theme, tok, val, block, norm)
            if d: drift.append(d)
            if f: fail.append(f)
    if fail:
        R.add("G-TOKEN","FAIL","otorite ihlali: " + "; ".join(fail))
    elif drift:
        R.add("G-TOKEN","WARN", f"{len(drift)} token otoriteden sapıyor: " + "; ".join(drift[:4]) +
              (" …" if len(drift) > 4 else "") + " — scripts/sync_carbon_tokens.py --check ile ayrıntı.")
    else:
        R.add("G-TOKEN","PASS","Çekirdek --cds-* token'ları @carbon/themes 11.75.0 ile birebir.")

def gate_curriculum(html, R):
    """G-CURRICULUM (koşullu): Müfredat-temelli modüllerde kazanım izlenebilirliği.

    Yalnız mod CURRICULUM ise veya bir `curriculum` bloğu varsa tetiklenir; aksi
    halde atlanır (geriye dönük uyum — mevcut MCP'siz modüller etkilenmez).

    Denetler:
    - mode:"CURRICULUM" ise `curriculum` bloğu zorunlu (yoksa FAIL).
    - `curriculum.outcomes[]` boş olmamalı; her öğede `code` ve `text` (FAIL/WARN).
    - Her `outcomes[].mappedTo` segment id'si `segments[]` içinde tanımlı bir
      id'ye karşılık gelmeli (kazanım→segment izlenebilirliği; eksikse FAIL).
    - meta.sourceCitation kazanım kodu/korpus referansı içermeli (eksikse WARN).

    Not: Salt-metin (regex/heuristik) denetimdir; MODULE_DATA JS nesnesi parse
    edilmez. `curriculum` ve `mode` sinyalleri metin örüntüsüyle tespit edilir.
    """
    is_curr_mode = bool(re.search(r'\bmode\s*:\s*["\']CURRICULUM["\']', html))
    has_curr_block = bool(re.search(r'\bcurriculum\s*:\s*\{', html))
    if not is_curr_mode and not has_curr_block:
        R.add("G-CURRICULUM","PASS","Müfredat-temelli modül değil (uygulanmaz).")
        return
    if is_curr_mode and not has_curr_block:
        R.add("G-CURRICULUM","FAIL",
              "mode CURRICULUM ama `curriculum` bloğu yok; kazanım provenansı zorunlu.")
        return

    block_m = re.search(r'curriculum\s*:\s*\{(.*?)\n\s*\}\s*,?\s*\n', html, re.S)
    block = block_m.group(1) if block_m else html
    codes, n_texts, mapped_ids, missing = _curriculum_collect(block, html)
    issues, warns = _curriculum_eval(codes, n_texts, mapped_ids, missing,
                                     _curriculum_cite_ok(html))

    if issues:
        R.add("G-CURRICULUM","FAIL","; ".join(issues))
    elif warns:
        R.add("G-CURRICULUM","WARN","; ".join(warns)
              + f" ({len(codes)} kazanım, {len(mapped_ids)} segment-eşleme denetlendi)")
    else:
        R.add("G-CURRICULUM","PASS",
              f"{len(codes)} kazanım segmente izlenebilir; kaynak damgalı.")

def main():
    """CLI giriş noktası: HTML yolunu alır, kapıları çalıştırır, rapor basar, çıkış kodu döndürür."""
    ap=argparse.ArgumentParser(description="carbon-edupedia modül doğrulayıcı")
    ap.add_argument("html", help="modül HTML dosyası")
    ap.add_argument("--strict", action="store_true", help="WARN'ları da ihlal say")
    args=ap.parse_args()
    try:
        html=open(args.html, encoding="utf-8").read()
    except OSError as e:
        print(f"{RED}Dosya okunamadı:{RESET} {e}"); sys.exit(2)

    R=Result()
    gate_emoji(html,R)
    gate_carbon(html,R)
    gate_a11y(html,R)
    gate_interact(html,R)
    gate_selfcontained(html,R)
    gate_contrast(html,R)
    gate_wellbeing(html,R)
    gate_svg(html,R)
    gate_audio(html,R)
    gate_token_authority(html,R)
    gate_curriculum(html,R)
    R.report()

    if R.fail or (args.strict and any(s=="WARN" for _,s,_ in R.rows)):
        sys.exit(1)
    sys.exit(0)

if __name__=="__main__":
    main()
