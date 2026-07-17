"""Provenance kapısı — jenerik kelime provenance DEĞİLDİR.

Bu kapının işi 'belge görüntüsü/OCR/HTR iddiası varsa gerçek araç izi göster' demektir.
Bugün 'page' kelimesi tek başına yeterli sayılıyor → uydurulmuş bir okuma kapıyı geçiyor.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    # citation_discipline.py kardeş modülü `from _signals import ...` ile içe aktarır.
    # importlib.util.module_from_spec dosya yolundan yüklerken sys.path'i otomatik
    # güncellemez (script'i __main__ olarak çalıştırmaktan farklı) — elle ekliyoruz.
    sys.path.insert(0, str(_SCRIPTS_DIR))

_spec = importlib.util.spec_from_file_location(
    "citation_discipline", _SCRIPTS_DIR / "citation_discipline.py")
cd = importlib.util.module_from_spec(_spec)
sys.modules["citation_discipline"] = cd
_spec.loader.exec_module(cd)

REAL = [
    "devarsiv_ocr_archive_pages page=1 engine=transleyt engine_chain=['transleyt:hit']",
    "devarsiv_get_belge_image ile çekildi, engine=transleyt",
    "devarsiv_ocr_belge page=1 engine=Transkribus model=56496 mean_confidence=71.2",
    "devarsiv_ocr_submit job_id=abc123 → devarsiv_ocr_result",
]
FAKE = [
    "page 3 diyor",
    "the engine of reform",
    "canvas üzerine yazılmış",
    "Belgede vali şöyle yazar: …",
]


def test_real_provenance_passes():
    for text in REAL:
        assert cd.HAS_IMAGE_OR_OCR_PROVENANCE.search(text), f"gerçek provenance reddedildi: {text!r}"


def test_generic_words_are_not_provenance():
    """'page'/'engine'/'canvas' tek başına provenance değildir — kapıyı delerler."""
    for text in FAKE:
        m = cd.HAS_IMAGE_OR_OCR_PROVENANCE.search(text)
        assert not m, f"jenerik kelime provenance sayıldı: {text!r} → {m.group(0)!r}"


def test_every_engine_name_is_recognised():
    """Motor adları ocr.ENGINES ile hizalı olmalı — yeni motor sessizce düşmesin."""
    for engine in ("transleyt", "transkribus", "escriptorium", "tesseract"):
        text = f"devarsiv_ocr_belge page=1 engine={engine}"
        assert cd.HAS_IMAGE_OR_OCR_PROVENANCE.search(text), f"{engine} tanınmıyor"
