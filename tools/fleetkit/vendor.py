#!/usr/bin/env python3
"""Kanonik fleet_probe.py'yi hook'lu plugin'lere BİREBİR vendor eder.

Neden vendor: plugin'ler marketplace'ten TEK DİZİN olarak kurulur; repo kökündeki
paylaşılan kod kurulu kopyaya GİTMEZ. Runtime bileşenleri (hook'ların import
ettiği prob) bu yüzden plugin içinde yaşamak zorunda. Kopyaların ayrışmaması
`check_drift.py [3]` ile bayt-özdeşlik denetlenerek sağlanır — edupedia'nın
`app/gates/` vendor'lı validator deseninin aynısı.

Kullanım:  python3 tools/fleetkit/vendor.py [--check]
"""
import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
CANONICAL = HERE / "fleet_probe.py"


def targets():
    """hooks/ dizini OLAN her plugin — prob'u ancak bir hook tüketebilir."""
    for d in sorted((REPO / "plugins").iterdir()):
        if (d / "hooks").is_dir() and (d / "fleet.yaml").is_file():
            yield d / "hooks" / "scripts" / "fleet_probe.py"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="fleet_probe vendor")
    ap.add_argument("--check", action="store_true", help="yazma; sapma varsa exit 1")
    a = ap.parse_args(argv)
    src = CANONICAL.read_bytes()
    drift = []
    for t in targets():
        same = t.is_file() and t.read_bytes() == src
        if same:
            print(f"  = {t.relative_to(REPO)}")
            continue
        drift.append(str(t.relative_to(REPO)))
        if not a.check:
            t.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(CANONICAL, t)
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
