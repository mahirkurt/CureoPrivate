#!/usr/bin/env python3
"""Stop — işaretsiz retro-tanı, teleoloji ve çift-tarih eksiği taraması. Fail-open."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit_block, read_payload, transcript_text  # noqa: E402

# Teleolojik / presentist kalıplar (Türkçe + İngilizce)
TELEOLOGY = [
    r"henüz\s+\w+\s*(teorisini|bilgisini|yöntemini)?\s*(bul|keşfet|bil)\w*\s*(a?mamış|madık)",
    r"nihayet\s+\w+\s*(ulaş|keşfet|bul)\w*",
    r"\bilkel\s+(bir\s+)?(yöntem|teknik|anlayış|tıp)",
    r"yanlış(ı?)\s+biçimde\s+inan\w+",
    r"\bhad\s+not\s+yet\s+discovered\b",
    r"\bprimitive\s+(method|technique|medicine)\b",
]

# Modern tanı etiketleri — işaretsiz kullanım şüphesi
MODERN_DX = [
    "tüberküloz", "tuberculosis", "şizofreni", "schizophrenia", "depresyon", "depression",
    "tifüs", "typhus", "tifo", "typhoid", "sıtma", "malaria", "sifiliz", "syphilis",
    "difteri", "diphtheria", "kolera", "cholera", "veba", "plague", "yersinia pestis",
    "kızamık", "measles", "çiçek hastalığı", "smallpox", "menenjit", "meningitis",
]

# Hipotez işareti sayılan ifadeler
HEDGE = [
    "hipotez", "hypothesis", "retro-hipotez", "uyumlu okunabilir", "ayırıcı tanı",
    "kesin değildir", "retrospektif tanı", "olası", "compatible with", "differential",
]

# Miladî-olmayan takvim işaretleri
NONGREG = re.compile(r"\b(H\.\s*\d{3,4}|Hicr[iî]|Rum[iî]|hicri|rumi)\b", re.I)
GREG_PAIR = re.compile(r"\b(M\.\s*\d{4}|\d{4}[-–]\d{2,4}|\(\s*\d{4}\s*\))")

HIST_SIGNAL = ("tıp tarihi", "history of medicine", "yüzyıl", "century", "dönem",
               "salgın", "epidemic", "arşiv", "archive")


def main():
    payload = read_payload()
    if payload.get("stop_hook_active"):
        return

    text = transcript_text(payload)
    if not text or len(text) < 1200:
        return
    low = text.lower()
    if sum(1 for s in HIST_SIGNAL if s in low) < 2:
        return  # tıp tarihi çıktısı değil

    findings = []

    for rx in TELEOLOGY:
        m = re.search(rx, text, re.I)
        if m:
            findings.append(
                f"PRESENTİZM/TELEOLOJİ — \"{m.group(0).strip()}\" kalıbı. Dönem aktörlerinin "
                "kendi gerekçelerini kendi mantığı içinde kur; sonuca göre yazma."
            )
            break

    dx_found = [d for d in MODERN_DX if d in low]
    hedged = any(h in low for h in HEDGE)
    if dx_found and not hedged:
        findings.append(
            f"İŞARETSİZ RETROSPEKTİF TANI ŞÜPHESİ — modern tanı etiketi geçiyor "
            f"({', '.join(dx_found[:4])}) ama hipotez/ayırıcı-tanı işareti yok. "
            "Dört kapıyı işlet (gereklilik · kanıt türü · ayırıcı tanı · işaretleme) veya "
            "kaynağın kendi terimine dön. Bkz. skills/retrodiagnoz."
        )

    if NONGREG.search(text) and not GREG_PAIR.search(text):
        findings.append(
            "ÇİFT TARİH EKSİK — Miladî olmayan takvim geçiyor ama Miladî karşılık yok. "
            "Her Hicrî/Rumî tarih `özgün (Miladî)` biçiminde çift yazılır; Hicrî yıl iki "
            "Miladî yıla yayılabilir, tek yıla indirgemek veri uydurmaktır."
        )

    if findings:
        emit_block(
            "ANAKRONİZM DENETİMİ — düzeltme gerekli:\n· " + "\n· ".join(findings) +
            "\n\nDüzeltip çıktıyı tamamla. Şüphede kalırsan `anakronizm-denetcisi` alt-ajanını "
            "çağır."
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
