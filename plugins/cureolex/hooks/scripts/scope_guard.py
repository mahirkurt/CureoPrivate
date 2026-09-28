#!/usr/bin/env python3
"""cureolex UserPromptSubmit Scope Guard — kapsam-drift erken uyarısı.

cureolex YALNIZ mevzuat reformu içindir (SKILL §6). Bireysel hak-arama (ödeme reddi davası,
AYM bireysel başvuru, dava dilekçesi, malpraktis) ve promosyonel materyal denetimi kapsam
DIŞIDIR. Hook yalnız KULLANICININ KENDİ TALEBİNE bakar: çitli kod blokları, satır içi kod,
`>` alıntı satırları ve çift tırnaklı parçalar ("…", "…", «…») çıkarılır; belge biçimli
istemde (≥2 markdown başlığı ya da tablo) yalnız ilk düzyazı paragrafı değerlendirilir.
Bağlam + kapsam-dışı sinyal birlikteyse kısa bir uyarı enjekte eder ve HİÇBİR skill'e
yönlendirmez; aksi halde sessizdir. Asla blok değil. Fail-open.

Tek tırnak ÇIKARILMAZ: Türkçe ek kesme işareti (SGK'nın) yanlış bir alıntı açardı.
"""
import json
import re
import sys

# Sağlık/hukuk bağlam sinyali (en az biri) — aksi halde cureolex ile ilgisiz, sessiz kal.
CONTEXT = re.compile(
    r"(mevzuat|yönetmelik|tebliğ|kanun|genelge|reform|TİTCK|titck|SGK|sağlık bakanlığı|"
    r"ilaç|tıbbi cihaz|ruhsat|SUT|geri[- ]?ödeme|regülasyon|hukuk|dava|başvuru|malpraktis|"
    r"promosyon|reçete|endikasyon)",
    re.IGNORECASE,
)

# Kapsam-dışı sinyal → uyarıdaki kategori adı (skill adı DEĞİL).
OUT_OF_SCOPE = [
    (re.compile(r"(bireysel başvuru|AYM.{0,20}başvuru|SGK.{0,20}(red|ödeme reddi|itiraz)|"
                r"ödeme reddi.{0,20}dava|kompasyon|compassionate|malpraktis|tazminat dava|"
                r"hasta.{0,10}dava|dava dilekçe)", re.IGNORECASE),
     "bireysel hak-arama / dava"),
    (re.compile(r"(detail aid|leave[- ]?behind|promosyon.{0,15}(materyal|denetim)|MLR|"
                r"speaker bureau|tanıtım malzeme|reklam.{0,10}uyum|CME.{0,15}uyum)", re.IGNORECASE),
     "promosyon materyali denetimi"),
]

_FENCE = re.compile(r"```.*?```", re.S)
_INLINE = re.compile(r"`[^`\n]*`")
_DQUOTE = re.compile(r"\"[^\"\n]*\"|“[^”\n]*”|«[^»\n]*»")
_HEADING = re.compile(r"(?m)^\s{0,3}#{1,6}\s")
# [ \t]* (NOT \s*) içinde: \s bir satır-içi karakter sınıfında yeni satırı da yutar —
# tablo başlığından sonra gelen büyük bir boş-satır bloğu, motorun her konumda
# `[\s:|-]+` ile geri-izleme (backtracking) yapmasına yol açar (ölçüldü: 40 KB boş
# satır → 15.6 sn, hook zaman aşımı 10 sn). Yatay boşlukla sınırlamak satır atlamayı
# engeller ve tek-geçişli (lineer) eşleşmeyi geri getirir.
_TABLE = re.compile(r"(?m)^[ \t]*\|.*\|[ \t]*$\n^[ \t]*\|[ \t:|-]+\|[ \t]*$")
_NON_PROSE = re.compile(r"^\s*(#{1,6}\s|\||[-*+]\s|\d+[.)]\s)")


def _document_shaped(text: str) -> bool:
    return len(_HEADING.findall(text)) >= 2 or bool(_TABLE.search(text))


def _first_prose_paragraph(text: str) -> str:
    for block in re.split(r"\n\s*\n", text):
        lines = [ln for ln in block.splitlines() if ln.strip()]
        if lines and not any(_NON_PROSE.match(ln) for ln in lines):
            return block
    return ""


def own_request_text(prompt: str) -> str:
    """İstemden kullanıcının KENDİ talebini ayıkla (alıntı / kod / belge gövdesi hariç)."""
    t = _FENCE.sub(" ", prompt)
    t = _INLINE.sub(" ", t)
    t = "\n".join(ln for ln in t.splitlines() if not ln.lstrip().startswith(">"))
    t = _DQUOTE.sub(" ", t)
    # Çit-ayıklanmış (fence-stripped) `t` üzerinde karar ver — ham `prompt` üzerinde
    # karar verirse bir kod bloğu İÇİNDEKİ `##` satırları belge-biçimli sanılır ve
    # asıl istem `_first_prose_paragraph` tarafından yanlışlıkla atlanabilir.
    if _document_shaped(t):
        t = _first_prose_paragraph(t)
    return t


def warning_for(prompt: str):
    # Patolojik girdi savunması: yapıştırılan raporlar/belgeler onlarca KB olabilir;
    # kullanıcının KENDİ talebi her zaman kısadır. Aşağıdaki regex'ler düzeltilmiş
    # olsa da (bkz. _TABLE), tek regex'i unutmak veya yeni bir kalıp eklemek yine
    # geri-izleme patlamasına yol açabilir — bu yüzden regex işinden ÖNCE sabit bir
    # tavan uygula (savunma-derinliği, ölçülen sınırların çok üstünde).
    prompt = prompt[:20000]
    own = own_request_text(prompt)
    if not own.strip() or not CONTEXT.search(own):
        return None
    hits = [label for rx, label in OUT_OF_SCOPE if rx.search(own)]
    if not hits:
        return None
    return ("[cureolex Scope Guard] Bu talep kapsam dışı bir sinyal taşıyor olabilir: "
            + "; ".join(hits)
            + ". cureolex yalnız mevzuat REFORMU/üretimi içindir (DRAFT/AMEND/analiz/uyum/"
              "görüş/RIA/karşılaştırmalı/TBMM/ex-post). Talep gerçekten bireysel hak-arama/"
              "dava ya da promosyon materyali denetimiyse cureolex çıktısı ÜRETME ve bunun "
              "kapsam dışı olduğunu kullanıcıya söyle. Reform bağlamıysa (mevzuatın kendisini "
              "değiştirmek/yazmak) devam et. Bağlam karar verir — bu yalnız uyarıdır.")


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    ctx = warning_for(str(data.get("prompt", "")))
    if ctx:
        sys.stdout.write(json.dumps({"hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit", "additionalContext": ctx}}))
    sys.exit(0)


if __name__ == "__main__":
    main()
