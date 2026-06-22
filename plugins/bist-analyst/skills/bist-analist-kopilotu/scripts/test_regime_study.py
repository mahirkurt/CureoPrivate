#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""regime_study.py birim testleri (stdlib unittest)."""
import math
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regime_study as rs


class PriceStatsTest(unittest.TestCase):
    def test_log_returns_basic(self):
        out = rs._log_returns([100.0, 105.0])
        self.assertEqual(len(out), 1)
        self.assertAlmostEqual(out[0], math.log(1.05), places=7)

    def test_log_returns_nonpositive_is_none(self):
        self.assertIsNone(rs._log_returns([100.0, 0.0, 100.0]))

    def test_realized_vol_known(self):
        # ln(1.1)=0.0953102, ln(0.9)=-0.1053605 → std(ddof=1) ≈ 0.141896
        v = rs._realized_vol([100.0, 110.0, 99.0])
        self.assertAlmostEqual(v, 0.141896, places=5)

    def test_realized_vol_too_short_is_none(self):
        self.assertIsNone(rs._realized_vol([100.0]))

    def test_realized_vol_invalid_is_none(self):
        self.assertIsNone(rs._realized_vol([100.0, 0.0, 100.0]))

    def test_efficiency_ratio_pure_trend(self):
        self.assertAlmostEqual(rs._efficiency_ratio([10, 11, 12, 13]), 1.0, places=7)

    def test_efficiency_ratio_choppy(self):
        self.assertAlmostEqual(rs._efficiency_ratio([10, 11, 10, 11]), 1.0 / 3.0, places=7)

    def test_efficiency_ratio_flat_is_none(self):
        self.assertIsNone(rs._efficiency_ratio([10, 10, 10]))  # sıfır yol


class CorrStatsTest(unittest.TestCase):
    def test_partial_spearman_degenerate_control_is_none(self):
        # y == z → ρ_yz=1 → payda 0 → None
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 1.0, 4.0, 3.0, 5.0]
        self.assertIsNone(rs._partial_spearman(x, y, y))

    def test_partial_spearman_matches_formula(self):
        x = [1.0, 2.0, 3.0, 4.0, 5.0]
        y = [2.0, 1.0, 4.0, 3.0, 5.0]
        z = [5.0, 3.0, 4.0, 1.0, 2.0]
        rxy = rs._spearman(x, y); rxz = rs._spearman(x, z); ryz = rs._spearman(y, z)
        expect = (rxy - rxz * ryz) / math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
        self.assertAlmostEqual(rs._partial_spearman(x, y, z), expect, places=9)

    def test_partial_spearman_too_few_is_none(self):
        self.assertIsNone(rs._partial_spearman([1, 2, 3], [3, 2, 1], [1, 1, 2]))

    def test_chi2_sf_df2_closed_form(self):
        # df=2 → SF(x)=exp(-x/2)
        self.assertAlmostEqual(rs._chi2_sf(2.0, 2), math.exp(-1.0), places=6)
        self.assertAlmostEqual(rs._chi2_sf(0.0, 2), 1.0, places=6)

    def test_kruskal_wallis_known(self):
        # [1,2,3],[4,5,6],[7,8,9] → H=7.2, eta2≈0.8667, p=exp(-3.6)
        out = rs._kruskal_wallis([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        self.assertAlmostEqual(out["H"], 7.2, places=4)
        self.assertAlmostEqual(out["eta2"], 5.2 / 6.0, places=4)
        self.assertAlmostEqual(out["p"], math.exp(-3.6), places=4)

    def test_kruskal_wallis_one_group_is_none(self):
        self.assertIsNone(rs._kruskal_wallis([[1, 2, 3]]))

    def test_sidak(self):
        self.assertAlmostEqual(rs._sidak(0.05, 3), 1 - 0.95 ** 3, places=9)
        self.assertIsNone(rs._sidak(None, 3))


if __name__ == "__main__":
    unittest.main()
