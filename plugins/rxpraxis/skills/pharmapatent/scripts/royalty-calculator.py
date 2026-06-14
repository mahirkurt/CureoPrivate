#!/usr/bin/env python3
"""
royalty-calculator.py — Lisans Müzakeresi için NPV + IRR + Milestone Calculator

Bir patent/asset lisans anlaşması için finansal modelleme:
- Upfront + milestone payments + tiered royalty stream
- NPV (Net Present Value) - farklı discount rate senaryoları
- IRR (Internal Rate of Return)
- Relief-from-Royalty (RFR) değerleme
- Royalty stack analizi (birden fazla lisans burden'ı)
- Comparable transactions benchmarks

Kullanım:
    python3 royalty-calculator.py                    # interactive
    python3 royalty-calculator.py --example          # ADC lisans örneği
    python3 royalty-calculator.py --rfr              # Relief-from-Royalty modu

Yazar: pharmapatent skill v1.3.0
Lisans: Internal use.
Bağımlılık: python-dateutil, numpy (opsiyonel, yoksa math kullanılır)
"""

import sys
from datetime import date
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Milestone:
    """Development veya sales milestone."""
    label: str
    year: int
    amount_usd: float
    probability: float = 1.0  # 0-1 arası; risk-adjusted için


@dataclass
class RevenueTier:
    """Tiered royalty için revenue dilimi."""
    lower_bound_usd: float  # annual revenue lower bound
    upper_bound_usd: Optional[float]  # None = unlimited
    royalty_rate: float  # 0-1 arası (örn. 0.08 = %8)


@dataclass
class LicenseDeal:
    """Lisans anlaşması tam tanımı."""
    name: str
    upfront_usd: float
    milestones: List[Milestone] = field(default_factory=list)
    royalty_tiers: List[RevenueTier] = field(default_factory=list)
    annual_revenue_projection: List[float] = field(default_factory=list)  # yıl bazlı
    deal_start_year: int = 0  # year 0 baseline
    discount_rate: float = 0.12  # %12 default
    tax_rate: float = 0.20  # %20 KVK Türkiye


# --- Benchmark data (comparable transactions — industry averages) ---
BENCHMARKS = {
    "small_molecule_onco_P3": {
        "upfront_range": (200_000_000, 1_500_000_000),
        "milestones_total": (500_000_000, 3_000_000_000),
        "royalty_range": (0.10, 0.25),
    },
    "mab_P3": {
        "upfront_range": (150_000_000, 1_200_000_000),
        "milestones_total": (400_000_000, 2_500_000_000),
        "royalty_range": (0.08, 0.18),
    },
    "adc_P2": {
        "upfront_range": (100_000_000, 600_000_000),
        "milestones_total": (300_000_000, 1_800_000_000),
        "royalty_range": (0.15, 0.25),
    },
    "car_t_P2": {
        "upfront_range": (80_000_000, 400_000_000),
        "milestones_total": (200_000_000, 1_200_000_000),
        "royalty_range": (0.20, 0.35),
    },
    "mrna_lnp_preclinical": {
        "upfront_range": (10_000_000, 100_000_000),
        "milestones_total": (100_000_000, 800_000_000),
        "royalty_range": (0.10, 0.18),
    },
    "gene_therapy_P1": {
        "upfront_range": (50_000_000, 300_000_000),
        "milestones_total": (200_000_000, 1_000_000_000),
        "royalty_range": (0.10, 0.20),
    },
    "platform_preclinical": {
        "upfront_range": (5_000_000, 50_000_000),
        "milestones_total": (50_000_000, 500_000_000),
        "royalty_range": (0.03, 0.08),
    },
}


def calculate_tiered_royalty(revenue: float, tiers: List[RevenueTier]) -> float:
    """Bir yıl için tiered royalty ödemesini hesapla."""
    if not tiers:
        return 0.0
    total = 0.0
    remaining = revenue
    for t in sorted(tiers, key=lambda x: x.lower_bound_usd):
        if remaining <= 0:
            break
        tier_top = t.upper_bound_usd if t.upper_bound_usd else float('inf')
        tier_bottom = t.lower_bound_usd
        # Bu tiere ne kadar revenue düşüyor?
        if revenue > tier_bottom:
            slice_amount = min(revenue, tier_top) - tier_bottom
            slice_amount = max(0, slice_amount)
            total += slice_amount * t.royalty_rate
    return total


def calculate_npv(cash_flows: List[float], discount_rate: float) -> float:
    """NPV hesapla. cash_flows[0] = year 0."""
    npv = 0.0
    for t, cf in enumerate(cash_flows):
        npv += cf / ((1 + discount_rate) ** t)
    return npv


def calculate_irr(cash_flows: List[float], tolerance: float = 0.0001, max_iter: int = 1000) -> Optional[float]:
    """IRR hesapla — Newton-Raphson / bisection."""
    if not cash_flows or all(cf >= 0 for cf in cash_flows):
        return None
    if sum(cash_flows) < 0:
        return None  # positive return imkansız

    # Bisection — güvenilir
    low, high = -0.99, 10.0
    for _ in range(max_iter):
        mid = (low + high) / 2
        npv = calculate_npv(cash_flows, mid)
        if abs(npv) < tolerance:
            return mid
        if npv > 0:
            low = mid
        else:
            high = mid
    return mid


def build_deal_cash_flows(deal: LicenseDeal, horizon_years: int = 20) -> List[float]:
    """Yıl-yıl net cash flow listesi inşa et (licensor perspektifinden)."""
    cash_flows = [0.0] * horizon_years

    # Year 0: upfront
    cash_flows[0] += deal.upfront_usd

    # Milestones
    for m in deal.milestones:
        if 0 <= m.year < horizon_years:
            cash_flows[m.year] += m.amount_usd * m.probability

    # Royalty — revenue projection üzerinden
    for yr, rev in enumerate(deal.annual_revenue_projection):
        actual_year = yr + (1 if deal.upfront_usd > 0 else 0)  # upfront sonrası 1. yıl revenue başlasın
        if 0 <= actual_year < horizon_years:
            royalty = calculate_tiered_royalty(rev, deal.royalty_tiers)
            cash_flows[actual_year] += royalty

    # After-tax (licensor için)
    cash_flows = [cf * (1 - deal.tax_rate) for cf in cash_flows]

    return cash_flows


def build_licensee_cash_flows(deal: LicenseDeal, horizon_years: int = 20) -> List[float]:
    """Licensee (lisans alan) perspektifinden: outflows (lisans ödemeleri) negatif."""
    cash_flows = [0.0] * horizon_years

    # Year 0: upfront ödeme
    cash_flows[0] -= deal.upfront_usd

    # Milestone ödemeleri
    for m in deal.milestones:
        if 0 <= m.year < horizon_years:
            cash_flows[m.year] -= m.amount_usd * m.probability

    # Royalty ödemeleri
    for yr, rev in enumerate(deal.annual_revenue_projection):
        actual_year = yr + (1 if deal.upfront_usd > 0 else 0)
        if 0 <= actual_year < horizon_years:
            royalty = calculate_tiered_royalty(rev, deal.royalty_tiers)
            cash_flows[actual_year] -= royalty

    return cash_flows


def print_summary(deal: LicenseDeal, horizon: int = 20):
    """Deal özetini yazdır."""
    print()
    print("═" * 72)
    print(f"  LİSANS DEAL ÖZET: {deal.name}")
    print("═" * 72)

    # Licensor perspektifi
    lcf = build_deal_cash_flows(deal, horizon)
    npv_licensor = calculate_npv(lcf, deal.discount_rate)
    irr_licensor = calculate_irr(lcf)

    # Licensee perspektifi
    lecf = build_licensee_cash_flows(deal, horizon)

    # Toplam nominal ödemeler
    total_upfront = deal.upfront_usd
    total_milestones = sum(m.amount_usd * m.probability for m in deal.milestones)
    total_royalty = sum(
        calculate_tiered_royalty(rev, deal.royalty_tiers)
        for rev in deal.annual_revenue_projection
    )
    total_nominal = total_upfront + total_milestones + total_royalty

    print(f"\n  📊 NOMİNAL DEĞERLER (Licensor'a ödenecek)")
    print(f"     Upfront:              USD {total_upfront:>15,.0f}")
    print(f"     Milestones (toplam):  USD {total_milestones:>15,.0f}")
    print(f"     Royalty (toplam):     USD {total_royalty:>15,.0f}")
    print(f"     ─────────────────────────────────────────")
    print(f"     TOPLAM NOMİNAL:       USD {total_nominal:>15,.0f}")

    print(f"\n  💰 İSKONTOLU DEĞER (Licensor perspektifi)")
    print(f"     Discount rate:        {deal.discount_rate:.1%}")
    print(f"     Tax rate:             {deal.tax_rate:.1%}")
    print(f"     NPV (after-tax):      USD {npv_licensor:>15,.0f}")
    if irr_licensor:
        print(f"     IRR:                  {irr_licensor:.1%}")

    # Duyarlılık
    print(f"\n  📉 DİSCOUNT RATE DUYARLILIĞI (Licensor NPV)")
    rates = [0.08, 0.10, 0.12, 0.15, 0.18, 0.25]
    npvs = [calculate_npv(lcf, r) for r in rates]
    max_npv = max(abs(n) for n in npvs) if npvs else 1
    for r, npv_r in zip(rates, npvs):
        bar_len = int(abs(npv_r) / max_npv * 40) if max_npv > 0 else 0
        bar = "█" * bar_len
        print(f"     r={r:.0%}:  USD {npv_r:>14,.0f}  {bar}")

    print("═" * 72)
    print()


def print_cash_flow_table(deal: LicenseDeal, horizon: int = 10):
    """Yıl-yıl cash flow tablosu."""
    lcf = build_deal_cash_flows(deal, horizon)
    lecf = build_licensee_cash_flows(deal, horizon)

    print(f"\n  📅 YILLIK NAKİT AKIŞI (İLK {horizon} YIL)")
    print(f"     {'Yıl':<5} {'Revenue':<15} {'Licensor':<15} {'Licensee':<15}")
    print(f"     {'-'*5} {'-'*15} {'-'*15} {'-'*15}")
    for yr in range(horizon):
        rev_idx = yr - (1 if deal.upfront_usd > 0 else 0)
        rev = deal.annual_revenue_projection[rev_idx] if 0 <= rev_idx < len(deal.annual_revenue_projection) else 0
        print(f"     {yr:<5} USD {rev:>11,.0f}  USD {lcf[yr]:>10,.0f}  USD {lecf[yr]:>10,.0f}")


def benchmark_check(deal: LicenseDeal, category: str):
    """Deal'ı sektörel benchmark'larla karşılaştır."""
    if category not in BENCHMARKS:
        print(f"\n  ⚠ Bilinmeyen kategori: {category}")
        print(f"  Mevcut kategoriler: {list(BENCHMARKS.keys())}")
        return

    bm = BENCHMARKS[category]
    print(f"\n  📈 SEKTÖREL KARŞILAŞTIRMA: {category}")
    print(f"     {'Metrik':<25} {'Deal':<20} {'Benchmark (range)':<30}")
    print(f"     {'-'*25} {'-'*20} {'-'*30}")

    # Upfront
    up_low, up_high = bm["upfront_range"]
    up_ok = "✓" if up_low <= deal.upfront_usd <= up_high else "⚠"
    print(f"     {'Upfront':<25} USD {deal.upfront_usd/1e6:>8.1f}M      USD {up_low/1e6:.0f}M-{up_high/1e9:.1f}B  {up_ok}")

    # Milestones
    ms_total = sum(m.amount_usd for m in deal.milestones)
    ms_low, ms_high = bm["milestones_total"]
    ms_ok = "✓" if ms_low <= ms_total <= ms_high else "⚠"
    print(f"     {'Milestones total':<25} USD {ms_total/1e6:>8.1f}M      USD {ms_low/1e6:.0f}M-{ms_high/1e9:.1f}B  {ms_ok}")

    # Royalty (ortalama tier)
    if deal.royalty_tiers:
        avg_royalty = sum(t.royalty_rate for t in deal.royalty_tiers) / len(deal.royalty_tiers)
        r_low, r_high = bm["royalty_range"]
        r_ok = "✓" if r_low <= avg_royalty <= r_high else "⚠"
        print(f"     {'Royalty (ort.)':<25} {avg_royalty:>8.1%}          {r_low:.0%}-{r_high:.0%}      {r_ok}")


def print_rfr_analysis(annual_revenue: List[float], royalty_rate: float, discount_rate: float = 0.12, tax_rate: float = 0.20):
    """Relief-from-Royalty değerleme (patent sahibi olmasaydı ödeyeceği royalty'den kurtarılan değer)."""
    print()
    print("═" * 72)
    print(f"  RELIEF-FROM-ROYALTY (RFR) DEĞERLEMESİ")
    print("═" * 72)
    print(f"  Prensip: Patent sahibi olmasaydı, aynı teknolojiyi üçüncü taraftan")
    print(f"  lisansla alacaktı. Kaçınılan royalty → patent değeri.")
    print()
    print(f"  Royalty rate:    {royalty_rate:.1%}")
    print(f"  Discount rate:   {discount_rate:.1%}")
    print(f"  Tax rate:        {tax_rate:.1%}")
    print()

    # Yıllık kaçınılan royalty ödemeleri
    cash_flows = [rev * royalty_rate * (1 - tax_rate) for rev in annual_revenue]
    npv = calculate_npv(cash_flows, discount_rate)

    print(f"  {'Yıl':<5} {'Revenue':<20} {'Kaçınılan Royalty':<25}")
    print(f"  {'-'*5} {'-'*20} {'-'*25}")
    for yr, rev in enumerate(annual_revenue):
        print(f"  {yr:<5} USD {rev:>15,.0f}  USD {cash_flows[yr]:>15,.0f}")
    print(f"  {'-'*5} {'-'*20} {'-'*25}")
    total = sum(cash_flows)
    print(f"  {'TOT':<5} {'':<20} USD {total:>15,.0f}")
    print()
    print(f"  🎯 RFR Değerleme (NPV): USD {npv:,.0f}")
    print("═" * 72)


def example_adc_deal():
    """ADC lisans örneği — hipotetik anti-HER2 ADC."""
    return LicenseDeal(
        name="Hipotetik Anti-HER2 ADC Lisans (Faz II)",
        upfront_usd=200_000_000,
        milestones=[
            Milestone("Faz III başlangıç", 2, 100_000_000, 0.7),
            Milestone("BLA submission", 5, 150_000_000, 0.55),
            Milestone("FDA onay", 6, 250_000_000, 0.6),
            Milestone("EMA onay", 7, 100_000_000, 0.7),
            Milestone("TİTCK onay", 7, 20_000_000, 0.8),
            Milestone("İlk $500M satış", 9, 200_000_000, 0.85),
            Milestone("İlk $1B satış", 11, 300_000_000, 0.75),
            Milestone("İlk $2B satış", 13, 500_000_000, 0.55),
        ],
        royalty_tiers=[
            RevenueTier(0, 500_000_000, 0.12),         # İlk $500M için %12
            RevenueTier(500_000_000, 1_500_000_000, 0.15),   # $500M-$1.5B için %15
            RevenueTier(1_500_000_000, None, 0.18),    # $1.5B üstü için %18
        ],
        annual_revenue_projection=[
            0, 0, 0, 0, 0, 0,  # Y0-Y5: geliştirme dönemi
            100_000_000,   # Y6: launch yılı
            400_000_000,   # Y7
            900_000_000,   # Y8
            1_500_000_000, # Y9
            2_200_000_000, # Y10
            2_800_000_000, # Y11 — peak
            2_800_000_000, # Y12
            2_500_000_000, # Y13
            2_000_000_000, # Y14 — erozyon başlar (ADC biosimilar beklentisi)
            1_400_000_000, # Y15
            900_000_000,   # Y16
            500_000_000,   # Y17
            300_000_000,   # Y18
            200_000_000,   # Y19
        ],
        discount_rate=0.12,
        tax_rate=0.20,
    )


def main():
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.3.0 — Royalty + NPV + IRR Calculator               ║")
    print("║  Lisans müzakeresi finansal modellemesi                             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    if '--example' in sys.argv:
        print("\n📄 Örnek: Hipotetik Anti-HER2 ADC Lisansı (Faz II)\n")
        deal = example_adc_deal()
        print_summary(deal, horizon=20)
        print_cash_flow_table(deal, horizon=15)
        benchmark_check(deal, "adc_P2")
        return

    if '--rfr' in sys.argv:
        print("\n📄 Relief-from-Royalty Örnek Hesabı\n")
        # Küçük molekül onkoloji Faz III
        annual_rev = [
            50_000_000,    # launch
            200_000_000,
            500_000_000,
            800_000_000,
            1_000_000_000,  # peak
            1_000_000_000,
            900_000_000,
            700_000_000,   # LOE başlar
            200_000_000,
            50_000_000,    # erode
        ]
        print_rfr_analysis(annual_rev, royalty_rate=0.08, discount_rate=0.12, tax_rate=0.20)
        return

    # Interactive mod — basit prompt
    print("\n🎯 Interactive Mode (basit sorular)\n")
    try:
        name = input("Deal adı: ").strip() or "Untitled Deal"
        upfront = float(input("Upfront (USD, milyon olarak): ") or "0") * 1e6
        discount = float(input("Discount rate (%, örn 12): ") or "12") / 100

        print("\nMilestone ekleme (boş bırakılırsa biter):")
        milestones = []
        while True:
            ms_label = input("  Milestone açıklama (boş=bitir): ").strip()
            if not ms_label:
                break
            ms_year = int(input(f"    {ms_label} - yıl (0=bugün): ") or "0")
            ms_amount = float(input(f"    {ms_label} - miktar (USD, milyon): ") or "0") * 1e6
            ms_prob = float(input(f"    {ms_label} - olasılık (0-1): ") or "1.0")
            milestones.append(Milestone(ms_label, ms_year, ms_amount, ms_prob))

        # Basit flat royalty tek tier
        royalty_rate = float(input("\nRoyalty rate (%, tek tier için): ") or "10") / 100

        print("\nYıllık revenue projeksiyonu (USD milyon, 10-15 yıl tavsiyesi):")
        print("  Virgülle ayrılmış: örn 0,0,0,100,400,900,1500...")
        rev_raw = input("Revenue: ").strip()
        annual_rev = [float(x) * 1e6 for x in rev_raw.split(',')] if rev_raw else []

        deal = LicenseDeal(
            name=name,
            upfront_usd=upfront,
            milestones=milestones,
            royalty_tiers=[RevenueTier(0, None, royalty_rate)],
            annual_revenue_projection=annual_rev,
            discount_rate=discount,
        )

        print_summary(deal, horizon=20)
        if annual_rev:
            print_cash_flow_table(deal, horizon=15)

    except (ValueError, KeyboardInterrupt) as e:
        print(f"\n⏹ İşlem sonlandı. {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()
