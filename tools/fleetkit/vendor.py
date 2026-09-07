#!/usr/bin/env python3
"""Kanonik runtime bileşenlerini hook'lu plugin'lere BİREBİR vendor eder.

Neden vendor: plugin'ler marketplace'ten TEK DİZİN olarak kurulur; repo kökündeki
paylaşılan kod kurulu kopyaya GİTMEZ. Runtime bileşenleri (hook'ların import
ettiği prob) bu yüzden plugin içinde yaşamak zorunda. Kopyaların ayrışmaması
`check_drift.py [3]` ile bayt-özdeşlik denetlenerek sağlanır — edupedia'nın
`app/gates/` vendor'lı validator deseninin aynısı.

İki küme vendor edilir:
  · fleet_probe.py        — hooks/ + fleet.yaml olan HER plugin'e
  · anamnesis çekirdeği   — YALNIZ ANAMNESIS_PLUGINS'e (4 dosya)

Anamnesis çekirdeği neden yalnız iki plugin'e: evidentia ve cureolex aynı
sözleşmenin AYRI implementasyonlarını taşıyor (ölçüldü 2026-09-07: saf kod
benzerliği ~%56, docstring/yorum hariç), yani onlar kopya değil. vekayinuvis ↔
historia-medicinae ise %98.7 aynıydı — tek gerçek kopya buydu ve birleştirildi.
Kimlik her plugin'in kendi `anamnesis_config.py`'sinde kalır, çekirdek jenerik.

Kullanım:  python3 tools/fleetkit/vendor.py [--check]
"""
import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CANONICAL = HERE / "fleet_probe.py"
ANAMNESIS_DIR = HERE / "vendor" / "anamnesis"
ANAMNESIS_FILES = (
    "anamnesis_run.py",
    "anamnesis_guard.py",
    "anamnesis_ledger.py",
    "anamnesis_lifecycle.py",
)
#: Yalnız gerçek ikizler. Bir plugin eklemeden ÖNCE koduna bak: bu liste
#: "aynı sözleşmeyi kullananlar" değil, "aynı KODU çalıştıranlar" listesidir.
ANAMNESIS_PLUGINS = ("vekayinuvis", "historia-medicinae")


def targets():
    """hooks/ dizini OLAN her plugin — prob'u ancak bir hook tüketebilir."""
    for d in sorted((REPO / "plugins").iterdir()):
        if (d / "hooks").is_dir() and (d / "fleet.yaml").is_file():
            yield d / "hooks" / "scripts" / "fleet_probe.py"


def anamnesis_pairs():
    """(kanonik, hedef) — anamnesis çekirdeğinin ikizlere vendor'lanması."""
    for plugin in ANAMNESIS_PLUGINS:
        for name in ANAMNESIS_FILES:
            yield ANAMNESIS_DIR / name, REPO / "plugins" / plugin / "hooks" / "scripts" / name


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="fleet_probe vendor")
    ap.add_argument("--check", action="store_true", help="yazma; sapma varsa exit 1")
    a = ap.parse_args(argv)
    pairs = [(CANONICAL, t) for t in targets()] + list(anamnesis_pairs())
    drift = []
    for canonical, t in pairs:
        src = canonical.read_bytes()
        if t.is_file() and t.read_bytes() == src:
            print(f"  = {t.relative_to(REPO)}")
            continue
        drift.append(str(t.relative_to(REPO)))
        if not a.check:
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(canonical, t)
            print(f"  → {t.relative_to(REPO)}")
    if a.check and drift:
        print("VENDOR SAPMASI:", file=sys.stderr)
        for d in drift:
            print(f"  · {d}", file=sys.stderr)
        print("  Çözüm: python3 tools/fleetkit/vendor.py", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
