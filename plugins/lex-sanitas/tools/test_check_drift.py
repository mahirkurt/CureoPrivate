#!/usr/bin/env python3
"""check_drift birim testleri — AĞ ERİŞİMİ YOK.

Koşum:  cd plugins/lex-sanitas && python3 tools/test_check_drift.py -v
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_drift  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


class TestDriftGate(unittest.TestCase):
    def test_yanlis_sayiyi_yakalar(self):
        hits = check_drift.scan_text(
            "wire edilmiş 14 hukuk/regülasyon MCP her sorguda çalışır", expected=19)
        self.assertTrue(hits, "'14 … MCP' ifadesi yakalanmalıydı")

    def test_dogru_sayiyi_gecirir(self):
        self.assertFalse(
            check_drift.scan_text("wire edilmiş 19 hukuk/regülasyon MCP", expected=19))

    def test_alakasiz_sayiyi_yakalamaz(self):
        """5210 sayılı Yönetmelik, Md.90/5, 21-nokta rubrik → false positive olmamalı."""
        for s in ("5210 sayılı Yönetmelik (RG 24/2/2022, 31760)",
                  "Anayasa Md.90/5 usulüne uygun andlaşma",
                  "R6b 21-nokta yürütülebilir rubrik",
                  "G0-G9 kalite kapıları; 27 kalem anti-pattern",
                  "TBMM İçtüzüğü Md.74-91",
                  "yürürlükten 12-36 ay sonra"):
            self.assertFalse(check_drift.scan_text(s, expected=19), s)

    def test_sahada_yakalanan_yanlis_pozitifler(self):
        """İlk canlı koşumda çıkan üç yanlış-pozitif sınıfı — regresyon koruması.

        Bunlar plugin metninde GERÇEKTEN geçen ifadelerdir; regex daraltılmazsa
        kapı her koşumda gürültü üretir ve güvenilirliğini yitirir.
        """
        for s in ("`references/00-mod-pipelines.md` Mod 1 server-listesini ver",
                  "Tasarım spec §8a VERIFY policy + §4 server-side quality gate",
                  "SKILL §3 companion↔kapı bağı; composition-contract §3 tablo."):
            self.assertFalse(check_drift.scan_text(s, expected=19, companions=5), s)

    def test_test_dosyalari_taranmaz(self):
        """test_* dosyaları kasten yanlış sayı içerir (regex sınaması) → atlanmalı."""
        self.assertTrue(check_drift.SKIP_PREFIXES)
        self.assertTrue("test_check_drift.py".startswith(check_drift.SKIP_PREFIXES))

    def test_companion_sayisini_dogrular(self):
        self.assertTrue(
            check_drift.scan_text("6 companion tam-filonun zorunlu üyesi",
                                  expected=19, companions=5))
        self.assertFalse(
            check_drift.scan_text("5 companion tam-filonun zorunlu üyesi",
                                  expected=19, companions=5))

    def test_hook_kapsam_acigi_tespiti(self):
        """session_start.py lock okumalı; hardcoded GATED kalmışsa yakalanmalı."""
        gap = check_drift.hook_coverage_gap(ROOT)
        self.assertIsInstance(gap, str)

    def test_repo_temiz(self):
        """Bütünleşik: plan tamamlandığında repo sürüklenmesiz olmalı."""
        self.assertEqual(check_drift.main(["--quiet"]), 0)


if __name__ == "__main__":
    unittest.main()
