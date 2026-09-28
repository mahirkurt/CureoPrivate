#!/usr/bin/env python3
"""check_drift [5]: `scan_prose` (server/companion SAYI iddiası) CHANGELOG.md'yi
taramamalı.

CHANGELOG.md tarihseldir — geçmiş bir satırın anlattığı sayı ("→ 21 server") o
GÜNKÜ filo boyutunu doğru şekilde kaydeder ve filo o tarihten sonra büyüyüp
küçüldükçe sayı kaçınılmaz olarak "yanlış" görünür. `scan_prose` bunu ayırt
edemez ve fleet her değiştiğinde geçmiş kayıtları düzyazı sürüklenmesi sanıp
kapıyı düşürür — yazarı ya tarihi metni günün sayısına göre yeniden yazmaya
(kaynağı bozar) ya da regex'i atlatacak şekilde kelime oyunuyla eğip bükmeye
zorlar. Doğru çözüm: CHANGELOG.md'yi SAYI taramasından tamamen muaf tutmak.

`scan_server_ids` (kimlik ataması) BAŞKA bir denetim ve bu istisnadan
etkilenmemeli — CHANGELOG.md'de filoda olmayan bir sunucu kimliğine atıf hâlâ
yakalanmalı (ölçüldü: 2026-09-28 itibariyle hiçbir plugin'in CHANGELOG.md'si
böyle bir atıf taşımıyor, ama kapının kendisi bunu YAKALAYABİLMELİ).
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import check_drift  # noqa: E402

WRONG_COUNT_LINE = "Sürüm 9.9.9: filo büyüdü → 99 server.\n"


def _make_root() -> Path:
    root = Path(tempfile.mkdtemp())
    (root / "CHANGELOG.md").write_text(WRONG_COUNT_LINE, encoding="utf-8")
    (root / "README.md").write_text(WRONG_COUNT_LINE, encoding="utf-8")
    return root


class ChangelogProseExemptionTests(unittest.TestCase):
    def test_changelog_wrong_count_not_flagged(self):
        root = _make_root()
        hits = check_drift.scan_prose(root, expected=1, companions=0)
        changelog_hits = [h for h in hits if h[0] == "CHANGELOG.md"]
        self.assertEqual(changelog_hits, [], changelog_hits)

    def test_same_wrong_count_in_readme_is_still_flagged(self):
        """İstisna DAR: yalnız CHANGELOG.md. Aynı satır README.md'de olsaydı
        kapı yine yakalamalı — istisna kapıyı genel olarak körleştirmemeli."""
        root = _make_root()
        hits = check_drift.scan_prose(root, expected=1, companions=0)
        readme_hits = [h for h in hits if h[0] == "README.md"]
        self.assertTrue(readme_hits, f"README.md'deki '99 server' yakalanmalıydı, hits={hits}")


if __name__ == "__main__":
    unittest.main()
