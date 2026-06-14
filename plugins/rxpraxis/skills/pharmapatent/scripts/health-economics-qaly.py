#!/usr/bin/env python3
"""
health-economics-qaly.py — Sağlık Ekonomisi QALY + ICER + HTA Threshold Değerlendirme

İlaç değerleme + fiyatlandırma + SGK/HTA müzakere için temel farmakoekonomi
hesaplayıcısı. QALY (Quality-Adjusted Life Year) + ICER (Incremental
Cost-Effectiveness Ratio) + budget impact + HTA threshold karşılaştırması.

Thresholds (2024-2026 güncel):
    NICE (UK)      £20,000-30,000 / QALY   (standard)
    NICE (UK)      £50,000 / QALY          (end-of-life)
    ICER (US)      $100,000-150,000 / QALY (standard)
    ICER (US)      $200,000 / QALY         (ultra-rare)
    WHO            1-3× GDP per capita / QALY
    Türkiye        ~₺500K / QALY (2024 WHO-aligned, informal — kesin threshold yok)
    Almanya (IQWiG)  Relative benefit (no fixed threshold)
    Fransa (HAS)     ASMR seviye yaklaşımı
    Çin (CDE)        ~3× GDP per capita (yaklaşık ¥250K-300K / QALY)

QALY metodolojisi:
    QALY = Σ (yaşam yılı × HRQoL utility) — utility [0, 1] ölçek
    ICER = (Cost_new - Cost_comparator) / (QALY_new - QALY_comparator)

Kullanım:
    python3 health-economics-qaly.py --example pembrolizumab
    python3 health-economics-qaly.py --example car-t
    python3 health-economics-qaly.py --example resmetirom
    python3 health-economics-qaly.py --interactive
    python3 health-economics-qaly.py --threshold-table

Yazar: pharmapatent skill v1.8.0
"""

import sys
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


# --- HTA thresholds ---

HTA_THRESHOLDS = {
    "NICE_standard": {"low": 20000, "high": 30000, "currency": "GBP", "country": "UK", "note": "Standard cost-per-QALY"},
    "NICE_eol": {"low": 50000, "high": 50000, "currency": "GBP", "country": "UK", "note": "End-of-life"},
    "NICE_severity": {"low": 30000, "high": 50000, "currency": "GBP", "country": "UK", "note": "2022 severity modifier"},
    "ICER_standard": {"low": 100000, "high": 150000, "currency": "USD", "country": "US", "note": "Standard"},
    "ICER_ultra_rare": {"low": 150000, "high": 200000, "currency": "USD", "country": "US", "note": "Ultra-rare / orphan"},
    "WHO_1xGDP": {"low": 14000, "high": 14000, "currency": "USD", "country": "Global", "note": "WHO 1× GDP (TR GDP 2024 est)"},
    "WHO_3xGDP": {"low": 42000, "high": 42000, "currency": "USD", "country": "Global", "note": "WHO 3× GDP (TR)"},
    "Türkiye_informal": {"low": 500000, "high": 500000, "currency": "TRY", "country": "TR", "note": "Informal WHO-aligned (~3× GDP)"},
    "Germany_IQWiG": {"low": None, "high": None, "currency": "EUR", "country": "DE", "note": "No fixed threshold — relative benefit"},
    "France_HAS": {"low": None, "high": None, "currency": "EUR", "country": "FR", "note": "ASMR hiyerarşi + AMM"},
    "China_CDE": {"low": 150000, "high": 250000, "currency": "CNY", "country": "CN", "note": "~3× GDP per capita"},
    "Japan_MHLW": {"low": 5000000, "high": 7500000, "currency": "JPY", "country": "JP", "note": "Cost-effectiveness assessment since 2019"},
}


@dataclass
class HealthState:
    """Sağlık durumu — utility değeri + süre."""
    name: str          # "progression-free", "post-progression", "stable"
    utility: float     # 0.0-1.0 HRQoL
    duration_months: float


@dataclass
class Intervention:
    """İntervansiyon (yeni tedavi veya comparator)."""
    name: str
    cost_per_cycle: float           # Para birimi intervention'a göre
    cycles: int                     # Tedavi döngü sayısı
    cost_currency: str
    health_states: List[HealthState]
    additional_costs: float = 0.0   # Monitoring + AE + ikincil işlem
    
    def total_cost(self) -> float:
        return (self.cost_per_cycle * self.cycles) + self.additional_costs
    
    def total_qaly(self) -> float:
        qaly = 0.0
        for hs in self.health_states:
            years = hs.duration_months / 12.0
            qaly += years * hs.utility
        return qaly
    
    def total_life_years(self) -> float:
        return sum(hs.duration_months for hs in self.health_states) / 12.0


@dataclass
class HEAnalysis:
    """Karşılaştırmalı farmakoekonomi analizi."""
    disease: str
    population: str
    time_horizon_years: float
    discount_rate: float     # 0.03 (3%) standart
    new_intervention: Intervention
    comparator: Intervention
    perspective: str = "payer"   # payer / societal
    
    def incremental_cost(self) -> float:
        return self.new_intervention.total_cost() - self.comparator.total_cost()
    
    def incremental_qaly(self) -> float:
        return self.new_intervention.total_qaly() - self.comparator.total_qaly()
    
    def incremental_ly(self) -> float:
        return self.new_intervention.total_life_years() - self.comparator.total_life_years()
    
    def icer(self) -> Optional[float]:
        dqaly = self.incremental_qaly()
        if abs(dqaly) < 0.001:
            return None
        return self.incremental_cost() / dqaly
    
    def cost_per_ly(self) -> Optional[float]:
        dly = self.incremental_ly()
        if abs(dly) < 0.001:
            return None
        return self.incremental_cost() / dly
    
    def dominated_status(self) -> str:
        """Dominance analizi."""
        dc = self.incremental_cost()
        dq = self.incremental_qaly()
        if dc < 0 and dq > 0:
            return "dominant (yeni tedavi daha ucuz + daha etkili)"
        if dc > 0 and dq < 0:
            return "dominated (yeni tedavi daha pahalı + daha az etkili)"
        if dc > 0 and dq > 0:
            return "trade-off (yeni tedavi daha pahalı + daha etkili)"
        if dc < 0 and dq < 0:
            return "cost-saving (yeni tedavi daha ucuz + daha az etkili)"
        return "equivalent"
    
    def check_thresholds(self) -> List[Dict]:
        """HTA threshold'larına karşı değerlendirme."""
        icer_val = self.icer()
        currency = self.new_intervention.cost_currency
        
        results = []
        for th_name, th_info in HTA_THRESHOLDS.items():
            if th_info["low"] is None:
                results.append({
                    "threshold": th_name,
                    "country": th_info["country"],
                    "threshold_range": "n/a (no fixed threshold)",
                    "verdict": "N/A",
                    "note": th_info["note"],
                })
                continue
            
            # Currency match check
            if th_info["currency"] != currency:
                results.append({
                    "threshold": th_name,
                    "country": th_info["country"],
                    "threshold_range": f"{th_info['low']:,}-{th_info['high']:,} {th_info['currency']}",
                    "verdict": f"⚠ Currency mismatch ({currency} vs {th_info['currency']})",
                    "note": th_info["note"],
                })
                continue
            
            if icer_val is None:
                verdict = "N/A (ICER hesaplanamadı)"
            elif icer_val < 0:
                verdict = "🟢 DOMINANT / COST-SAVING"
            elif icer_val <= th_info["low"]:
                verdict = "🟢 HIGHLY COST-EFFECTIVE"
            elif icer_val <= th_info["high"]:
                verdict = "🟡 COST-EFFECTIVE (borderline)"
            else:
                pct_over = (icer_val / th_info["high"] - 1) * 100
                verdict = f"🔴 NOT COST-EFFECTIVE (%{pct_over:.0f} üstünde)"
            
            results.append({
                "threshold": th_name,
                "country": th_info["country"],
                "threshold_range": f"{th_info['low']:,}-{th_info['high']:,} {th_info['currency']}",
                "verdict": verdict,
                "note": th_info["note"],
            })
        
        return results


# --- Örnek vaka analizleri ---

EXAMPLES = {
    "pembrolizumab": HEAnalysis(
        disease="Metastatik non-small cell lung cancer (1L, PD-L1 TPS ≥50%)",
        population="Adult NSCLC, no EGFR/ALK",
        time_horizon_years=10,
        discount_rate=0.03,
        new_intervention=Intervention(
            name="Pembrolizumab (Keytruda) monoterapi",
            cost_per_cycle=9500,
            cycles=35,      # Up to 2 yıl (3-haftalık)
            cost_currency="USD",
            health_states=[
                HealthState("progression-free on pembro", 0.80, 24),
                HealthState("post-progression (survivor)", 0.55, 18),
                HealthState("terminal", 0.35, 3),
            ],
            additional_costs=45000,  # AE + monitoring
        ),
        comparator=Intervention(
            name="Platin doublet kemoterapi (pemetrexed+carboplatin)",
            cost_per_cycle=2200,
            cycles=4,        # 4 siklus standart
            cost_currency="USD",
            health_states=[
                HealthState("progression-free on chemo", 0.65, 6),
                HealthState("post-progression", 0.50, 10),
                HealthState("terminal", 0.30, 3),
            ],
            additional_costs=25000,
        ),
    ),
    "car-t": HEAnalysis(
        disease="Relapsed/refractory large B-cell lymphoma (3L+)",
        population="Adult DLBCL, 2+ prior lines",
        time_horizon_years=15,
        discount_rate=0.03,
        new_intervention=Intervention(
            name="Axicabtagene ciloleucel (Yescarta) CAR-T",
            cost_per_cycle=373000,     # Single infusion pricing
            cycles=1,
            cost_currency="USD",
            health_states=[
                HealthState("complete response (sustained)", 0.85, 90),   # 7.5 yıl durable
                HealthState("partial response / stable", 0.60, 18),
                HealthState("relapsed / progression", 0.40, 9),
            ],
            additional_costs=150000,   # Hastane + lymphodepletion + AE (CRS, neurotoxicity)
        ),
        comparator=Intervention(
            name="Salvage kemoterapi (DHAP/ICE + stem cell transplant kısmen)",
            cost_per_cycle=15000,
            cycles=6,
            cost_currency="USD",
            health_states=[
                HealthState("response on salvage", 0.50, 12),
                HealthState("refractory / progression", 0.35, 12),
                HealthState("terminal", 0.20, 6),
            ],
            additional_costs=80000,
        ),
    ),
    "resmetirom": HEAnalysis(
        disease="Metabolic-Associated Steatohepatitis (MASH) F2-F3 fibrozis",
        population="Non-cirrhotic MASH with F2-F3",
        time_horizon_years=20,
        discount_rate=0.03,
        new_intervention=Intervention(
            name="Resmetirom (Rezdiffra) + SoC",
            cost_per_cycle=4000,
            cycles=60,        # 5 yıl (aylık)
            cost_currency="USD",
            health_states=[
                HealthState("F2 stable on resmetirom", 0.78, 84),
                HealthState("improved to F0-F1", 0.85, 60),
                HealthState("F3 progressed", 0.65, 36),
                HealthState("cirrhosis (F4)", 0.55, 60),
            ],
            additional_costs=30000,   # Monitoring + liver biopsies
        ),
        comparator=Intervention(
            name="Standard of Care (lifestyle + comorbidity management)",
            cost_per_cycle=120,
            cycles=240,       # 20 yıl aylık
            cost_currency="USD",
            health_states=[
                HealthState("F2 on SoC", 0.72, 60),
                HealthState("F3 progressed", 0.62, 48),
                HealthState("cirrhosis", 0.52, 84),
                HealthState("decompensated / HCC / LT", 0.40, 48),
            ],
            additional_costs=50000,
        ),
    ),
}


# --- Çıktı fonksiyonları ---

def print_analysis_report(analysis: HEAnalysis):
    print()
    print("═" * 90)
    print(f"  SAĞLIK EKONOMİSİ ANALİZİ")
    print("═" * 90)
    print(f"  Hastalık: {analysis.disease}")
    print(f"  Popülasyon: {analysis.population}")
    print(f"  Zaman ufku: {analysis.time_horizon_years} yıl · Discount rate: {analysis.discount_rate*100}%")
    print(f"  Perspektif: {analysis.perspective}")
    print()
    
    currency = analysis.new_intervention.cost_currency
    
    # Tedavi karşılaştırması
    print(f"  ┌─ KARŞILAŞTIRMA ─────────────────────────────────────────────┐")
    print(f"  │  {'':38} {'Yeni':>12} {'Comparator':>14}")
    print(f"  │  {'Tedavi':<38} {analysis.new_intervention.name[:12]:>12} {analysis.comparator.name[:14]:>14}")
    print(f"  │  {'Total Cost (' + currency + ')':<38} {analysis.new_intervention.total_cost():>12,.0f} {analysis.comparator.total_cost():>14,.0f}")
    print(f"  │  {'Total QALY':<38} {analysis.new_intervention.total_qaly():>12.3f} {analysis.comparator.total_qaly():>14.3f}")
    print(f"  │  {'Total Life Years':<38} {analysis.new_intervention.total_life_years():>12.3f} {analysis.comparator.total_life_years():>14.3f}")
    print(f"  └──────────────────────────────────────────────────────────────┘")
    print()
    
    # Incremental
    dc = analysis.incremental_cost()
    dq = analysis.incremental_qaly()
    dly = analysis.incremental_ly()
    icer = analysis.icer()
    cost_per_ly = analysis.cost_per_ly()
    
    print(f"  ┌─ INCREMENTAL ───────────────────────────────────────────────┐")
    print(f"  │  ΔCost:       {dc:>15,.0f} {currency}")
    print(f"  │  ΔQALY:       {dq:>15.3f}")
    print(f"  │  ΔLY:         {dly:>15.3f}")
    if icer is not None:
        print(f"  │  ICER:        {icer:>15,.0f} {currency} / QALY")
    if cost_per_ly is not None:
        print(f"  │  Cost/LY:     {cost_per_ly:>15,.0f} {currency} / LY")
    print(f"  │  Status:      {analysis.dominated_status()}")
    print(f"  └──────────────────────────────────────────────────────────────┘")
    print()
    
    # Threshold karşılaştırma
    print(f"  ┌─ HTA THRESHOLD DEĞERLENDİRMESİ ─────────────────────────────┐")
    thresholds = analysis.check_thresholds()
    for t in thresholds:
        print(f"  │  {t['country']:<3} {t['threshold']:<20} {t['threshold_range']:<30} {t['verdict']}")
    print(f"  └──────────────────────────────────────────────────────────────┘")
    print()


def print_markdown_report(analysis: HEAnalysis):
    print()
    print(f"# Farmakoekonomi Analizi — {analysis.new_intervention.name}")
    print()
    print(f"**Hastalık**: {analysis.disease}")
    print(f"**Popülasyon**: {analysis.population}")
    print(f"**Zaman ufku**: {analysis.time_horizon_years} yıl")
    print(f"**Discount rate**: {analysis.discount_rate*100}%")
    print(f"**Perspektif**: {analysis.perspective}")
    print()
    
    currency = analysis.new_intervention.cost_currency
    
    print("## Tedavi Karşılaştırması")
    print()
    print("| Metrik | Yeni Tedavi | Comparator |")
    print("|---|---|---|")
    print(f"| Tedavi adı | {analysis.new_intervention.name} | {analysis.comparator.name} |")
    print(f"| Total Cost ({currency}) | {analysis.new_intervention.total_cost():,.0f} | {analysis.comparator.total_cost():,.0f} |")
    print(f"| Total QALY | {analysis.new_intervention.total_qaly():.3f} | {analysis.comparator.total_qaly():.3f} |")
    print(f"| Total Life Years | {analysis.new_intervention.total_life_years():.2f} | {analysis.comparator.total_life_years():.2f} |")
    print()
    
    dc = analysis.incremental_cost()
    dq = analysis.incremental_qaly()
    icer = analysis.icer()
    
    print("## Incremental Sonuçlar")
    print()
    print(f"- **ΔCost**: {dc:,.0f} {currency}")
    print(f"- **ΔQALY**: {dq:.3f}")
    print(f"- **ICER**: {icer:,.0f} {currency} / QALY" if icer else "- **ICER**: N/A")
    print(f"- **Durum**: {analysis.dominated_status()}")
    print()
    
    print("## HTA Threshold Değerlendirmesi")
    print()
    print("| Ülke | Threshold | Aralık | Verdict |")
    print("|---|---|---|---|")
    for t in analysis.check_thresholds():
        print(f"| {t['country']} | {t['threshold']} | {t['threshold_range']} | {t['verdict']} |")
    print()


def print_json(analysis: HEAnalysis):
    data = {
        "analysis": asdict(analysis),
        "results": {
            "incremental_cost": analysis.incremental_cost(),
            "incremental_qaly": analysis.incremental_qaly(),
            "incremental_life_years": analysis.incremental_ly(),
            "icer": analysis.icer(),
            "cost_per_ly": analysis.cost_per_ly(),
            "status": analysis.dominated_status(),
        },
        "threshold_check": analysis.check_thresholds(),
    }
    print(json.dumps(data, indent=2, ensure_ascii=False))


def print_threshold_table():
    print()
    print("═" * 90)
    print("  HTA COST-PER-QALY THRESHOLDS (2024-2026 güncel)")
    print("═" * 90)
    print(f"  {'Kısaltma':<22} {'Ülke':<8} {'Aralık':<30} {'Note':<30}")
    print(f"  {'-'*22} {'-'*8} {'-'*30} {'-'*30}")
    for name, info in HTA_THRESHOLDS.items():
        if info['low'] is None:
            rng = "n/a"
        elif info['low'] == info['high']:
            rng = f"{info['low']:,} {info['currency']}"
        else:
            rng = f"{info['low']:,}-{info['high']:,} {info['currency']}"
        print(f"  {name:<22} {info['country']:<8} {rng:<30} {info['note']:<30}")
    print("═" * 90)
    print()
    print("  Notlar:")
    print("  - Türkiye'de resmi threshold yoktur; SGK Ödeme Komisyonu case-by-case değerlendirir")
    print("  - WHO-CHOICE 2001: 1× GDP/capita çok maliyet-etkin; 3× GDP/capita maliyet-etkin")
    print("  - NICE 2022 severity modifier: 1.2× (orta), 1.7× (yüksek) fatör uygulanır")
    print("  - ICER (US) 2023: modifier sistemi (ultra-rare + societal perspective)")
    print()


def main():
    parser = argparse.ArgumentParser(description="Health Economics QALY/ICER Calculator v1.8.0")
    parser.add_argument('--example', type=str, help="Örnek: pembrolizumab, car-t, resmetirom")
    parser.add_argument('--format', default='ascii', choices=['ascii', 'markdown', 'json'])
    parser.add_argument('--threshold-table', action='store_true')
    parser.add_argument('--list-examples', action='store_true')
    
    args = parser.parse_args()
    
    if args.threshold_table:
        print_threshold_table()
        return
    
    if args.list_examples:
        print("\nMevcut örnekler:")
        for name, a in EXAMPLES.items():
            print(f"  {name:<18} {a.disease[:60]}")
        return
    
    if not args.example:
        print()
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║  pharmapatent v1.8.0 — Health Economics QALY + ICER + HTA         ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print()
        print("Kullanım:")
        print("  --example pembrolizumab     NSCLC 1L PD-L1 high")
        print("  --example car-t             r/r DLBCL 3L+")
        print("  --example resmetirom        MASH F2-F3")
        print("  --threshold-table           Tüm HTA threshold'ları göster")
        print("  --format ascii|markdown|json")
        return
    
    if args.example not in EXAMPLES:
        print(f"❌ Bilinmeyen örnek: {args.example}")
        sys.exit(1)
    
    analysis = EXAMPLES[args.example]
    
    if args.format == 'json':
        print_json(analysis)
    elif args.format == 'markdown':
        print_markdown_report(analysis)
    else:
        print_analysis_report(analysis)


if __name__ == "__main__":
    main()
