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


if __name__ == "__main__":
    unittest.main()
