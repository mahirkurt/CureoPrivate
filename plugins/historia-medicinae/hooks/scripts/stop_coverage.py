#!/usr/bin/env python3
"""Stop — substantif çıktı G0 kapsam manifestosu taşıyor mu. Fail-open."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit_block, load_lock, read_payload, transcript_text  # noqa: E402

# Substantif araştırma sinyali: mod adı veya en az iki alan terimi
MODES = ("SOURCE_HUNT", "MORBUS", "INSTITUTIO", "CONCEPTUS", "ETHICA", "PROSOPOGRAPHIA",
         "THERAPEUTICA", "SANITAS_PUBLICA", "HISTORIOGRAPHIA", "EDITIO", "RELATIO")
DOMAIN = ("tıp tarihi", "history of medicine", "salgın tarihi", "tarihyazımı",
          "birincil kaynak", "retrospektif tanı", "historiograph")

MANIFEST_RX = re.compile(r"kapsam\s+manifesto", re.I)
STATUS_RX = re.compile(r"\b(hit\s+\d+|empty|degraded|skipped)\b", re.I)


def main():
    payload = read_payload()
    if payload.get("stop_hook_active"):
        return  # döngü koruması

    text = transcript_text(payload)
    if not text or len(text) < 1200:
        return  # kısa/etkileşimli yanıt — manifesto gerekmez

    hits = sum(1 for m in MODES if m in text) + sum(1 for d in DOMAIN if d.lower() in text.lower())
    if hits < 2:
        return  # substantif araştırma çıktısı değil

    if MANIFEST_RX.search(text) and len(STATUS_RX.findall(text)) >= 8:
        return  # manifesto var

    lock = load_lock()
    n = lock.get("counts", {}).get("servers", 25)
    emit_block(
        "G0 İHLALİ — bu substantif tıp tarihi çıktısı kapsam manifestosu taşımıyor.\n"
        f"Çıktıyı tamamla: {n} wire'lı server + 3 companion + 3 delegasyon için BİRER satır, "
        "her biri `hit N` / `empty` / `degraded: <gerekçe>` / `skipped: <gerekçe>` durumuyla. "
        "Gerekçesiz skip yasaktır; bağlı bir connector'ın tetiklenmiş bağlamda atlanması G0 "
        "ihlalidir. Biçim: shared/coverage-manifest.md. Dosya raporunda manifesto "
        "`<!-- OPS: ... -->` bloğunun içinde yaşar."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
