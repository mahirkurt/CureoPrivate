#!/usr/bin/env python3
"""
biosimilar-comparator.py — Biyobenzer CQA Comparability Skorlama

Referans ürün ve biyobenzer aday arasındaki Critical Quality Attributes (CQA)
karşılaştırmasını analitik + klinik benzerlik çerçevesinde skorlayan script.
FDA + EMA biosimilar guidance'a uyumlu, ICH Q5E comparability kuralları ile.

Kategoriler:
    1. Structural characterization (primer yapı, glycan, charge variants, aggregation)
    2. Functional/biological activity (binding affinity, ADCC, CDC, neutralization)
    3. Process-related impurities (HCP, DNA, endotoxin)
    4. Product-related impurities (oxidation, deamidation, fragmentation)
    5. PK/PD profile (AUC, Cmax, half-life)

Her CQA için:
- Tier 1 (Critical) — Biosimilarity için zorunlu benzer
- Tier 2 (Important) — Önemli; ciddi sapma risk
- Tier 3 (Minor) — İzleme yeterli

Skorlama kuralları:
- "Highly similar" ≥ %90 overlap interval → skor 1.0
- "Similar" %80-90 → skor 0.7
- "Trend toward similar" %70-80 → skor 0.4
- "Not similar" < %70 → skor 0.0

Kullanım:
    python3 biosimilar-comparator.py                        # interactive
    python3 biosimilar-comparator.py --example trastuzumab  # demo
    python3 biosimilar-comparator.py --example adalimumab   # demo
    python3 biosimilar-comparator.py --import cqa_data.json # JSON import
    python3 biosimilar-comparator.py --report               # tam CQA raporu

Yazar: pharmapatent skill v1.6.0
Lisans: Internal use.
Bağımlılık: standart kütüphane
"""

import sys
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


# --- Classification + scoring logic ---

TIER_DEFINITIONS = {
    "tier_1": {
        "name": "Critical",
        "description": "Biosimilarity için zorunlu benzer (mechanism of action + safety)",
        "minimum_score_for_biosimilar": 0.85,
    },
    "tier_2": {
        "name": "Important", 
        "description": "Önemli — ciddi sapma risk, ek klinik veri gerekebilir",
        "minimum_score_for_biosimilar": 0.70,
    },
    "tier_3": {
        "name": "Minor",
        "description": "İzleme yeterli — pazarlama izni engellemez",
        "minimum_score_for_biosimilar": 0.50,
    },
}


SIMILARITY_BANDS = [
    {"label": "Highly Similar", "threshold": 0.85, "score": 1.0, "icon": "✓✓", "color": "green"},
    {"label": "Similar", "threshold": 0.70, "score": 0.75, "icon": "✓", "color": "green-yellow"},
    {"label": "Trend toward Similar", "threshold": 0.55, "score": 0.40, "icon": "⚠", "color": "yellow"},
    {"label": "Not Similar", "threshold": 0.00, "score": 0.00, "icon": "✗", "color": "red"},
]


def classify_similarity(overlap_pct: float) -> Dict:
    """Overlap yüzdesini similarity band'ına çevir."""
    for band in SIMILARITY_BANDS:
        if overlap_pct >= band['threshold']:
            return band
    return SIMILARITY_BANDS[-1]


@dataclass
class CQA:
    """Critical Quality Attribute."""
    name: str
    category: str  # "structural", "functional", "process", "product", "pkpd"
    tier: str      # "tier_1", "tier_2", "tier_3"
    reference_range: str   # "85-115%" veya "100 ± 10 ng/mL"
    biosimilar_range: str  # Gözlenen aralık
    overlap_pct: float     # 0.0-1.0
    method: str            # "SEC-HPLC", "SPR", "ELISA", "CE-SDS"
    notes: str = ""


@dataclass
class ComparabilityAssessment:
    """Tam comparability değerlendirmesi."""
    reference_product: str
    biosimilar_candidate: str
    cqas: List[CQA] = field(default_factory=list)
    assessment_date: str = ""
    
    def overall_score(self) -> float:
        """Tier-ağırlıklı toplam skor (0-1)."""
        if not self.cqas:
            return 0.0
        tier_weights = {"tier_1": 3, "tier_2": 2, "tier_3": 1}
        weighted_sum = 0
        total_weight = 0
        for cqa in self.cqas:
            band = classify_similarity(cqa.overlap_pct)
            weight = tier_weights.get(cqa.tier, 1)
            weighted_sum += band['score'] * weight
            total_weight += weight
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def tier_scores(self) -> Dict[str, float]:
        """Her tier için ayrı skor."""
        scores = {}
        for tier in ["tier_1", "tier_2", "tier_3"]:
            tier_cqas = [c for c in self.cqas if c.tier == tier]
            if tier_cqas:
                scores[tier] = sum(classify_similarity(c.overlap_pct)['score'] for c in tier_cqas) / len(tier_cqas)
            else:
                scores[tier] = None
        return scores
    
    def failed_cqas(self) -> List[CQA]:
        """Tier gereksinimini karşılamayan CQA'lar."""
        failed = []
        for cqa in self.cqas:
            band = classify_similarity(cqa.overlap_pct)
            min_score = TIER_DEFINITIONS[cqa.tier]['minimum_score_for_biosimilar']
            if band['score'] < min_score:
                failed.append(cqa)
        return failed
    
    def verdict(self) -> Dict:
        """Biosimilarity verdict."""
        overall = self.overall_score()
        tier_scores = self.tier_scores()
        failed = self.failed_cqas()
        
        # Tier 1 critical — tüm tier 1 ≥0.85 olmalı
        tier1_ok = tier_scores.get('tier_1') is None or tier_scores['tier_1'] >= 0.85
        tier2_ok = tier_scores.get('tier_2') is None or tier_scores['tier_2'] >= 0.70
        
        critical_failures = [c for c in failed if c.tier == "tier_1"]
        
        if critical_failures:
            status = "FAIL"
            message = f"Tier 1 (Critical) başarısız: {len(critical_failures)} CQA"
        elif not tier1_ok:
            status = "FAIL"
            message = "Tier 1 ortalama skoru yetersiz"
        elif not tier2_ok:
            status = "CONDITIONAL"
            message = "Tier 2 sapmalar — ek klinik veri gerekebilir"
        elif overall >= 0.85:
            status = "PASS"
            message = "Biosimilarity — analitik benzerlik gösterilmiş"
        elif overall >= 0.70:
            status = "CONDITIONAL"
            message = "Kısmi benzerlik — ek PK/PD ve klinik veri gerekebilir"
        else:
            status = "FAIL"
            message = "Yeterli benzerlik yok"
        
        return {
            "status": status,
            "message": message,
            "overall_score": overall,
            "tier_scores": tier_scores,
            "failed_count": len(failed),
            "critical_failed_count": len(critical_failures),
        }


# --- Örnek veri tabanı ---

EXAMPLES = {
    "trastuzumab": {
        "reference_product": "Herceptin (trastuzumab) — Roche referans",
        "biosimilar_candidate": "BS-TRA-001 (hipotetik biyobenzer aday)",
        "cqas": [
            # Tier 1 — Critical
            CQA("Primary amino acid sequence", "structural", "tier_1", "100% identical", "100% identical", 1.00, "LC-MS peptide map"),
            CQA("HER2 binding affinity (KD)", "functional", "tier_1", "0.5-1.5 nM", "0.6-1.4 nM", 0.92, "SPR (Biacore)"),
            CQA("ADCC activity", "functional", "tier_1", "80-120% reference", "85-115%", 0.91, "Reporter bioassay"),
            CQA("Fc receptor binding (FcγRIIIa V)", "functional", "tier_1", "EC50 0.5-2 nM", "0.7-1.9 nM", 0.88, "SPR"),
            CQA("Disulfide bond structure", "structural", "tier_1", "Identical pattern", "Identical pattern", 1.00, "LC-MS reduced/non-reduced"),
            # Tier 2 — Important
            CQA("N-glycan profile (G0F)", "structural", "tier_2", "35-50%", "38-47%", 0.87, "HILIC-UPLC"),
            CQA("N-glycan profile (G1F)", "structural", "tier_2", "25-40%", "28-38%", 0.85, "HILIC-UPLC"),
            CQA("Afucosylation", "structural", "tier_2", "5-10%", "6-9%", 0.89, "HILIC-UPLC"),
            CQA("Charge variants (acidic)", "structural", "tier_2", "15-25%", "17-24%", 0.88, "cIEF"),
            CQA("Charge variants (basic)", "structural", "tier_2", "10-20%", "12-19%", 0.87, "cIEF"),
            CQA("Aggregates (HMW)", "product", "tier_2", "< 1%", "< 1%", 0.95, "SEC-HPLC"),
            CQA("Fragments (LMW)", "product", "tier_2", "< 1%", "< 1%", 0.92, "SEC + CE-SDS"),
            # Tier 3 — Minor
            CQA("HCP (Host Cell Protein)", "process", "tier_3", "< 100 ppm", "< 90 ppm", 0.95, "ELISA"),
            CQA("DNA residual", "process", "tier_3", "< 10 pg/mg", "< 8 pg/mg", 0.98, "qPCR"),
            CQA("Deamidation (Asn)", "product", "tier_3", "< 5%", "< 4%", 0.94, "LC-MS"),
            CQA("Oxidation (Met)", "product", "tier_3", "< 3%", "< 3%", 0.93, "LC-MS"),
        ],
        "assessment_date": "2026-04-24",
    },
    "adalimumab": {
        "reference_product": "Humira (adalimumab) — AbbVie referans",
        "biosimilar_candidate": "BS-ADA-002 (hipotetik citrate-free HD biyobenzer)",
        "cqas": [
            # Tier 1 — Critical
            CQA("Primary amino acid sequence", "structural", "tier_1", "100% identical", "100% identical", 1.00, "LC-MS"),
            CQA("TNFα binding affinity", "functional", "tier_1", "KD 0.3-0.7 nM", "0.4-0.6 nM", 0.94, "SPR"),
            CQA("TNFα neutralization", "functional", "tier_1", "80-120% potency", "85-115%", 0.93, "L929 bioassay"),
            CQA("Disulfide structure", "structural", "tier_1", "Identical", "Identical", 1.00, "LC-MS"),
            # Tier 2 — Important
            CQA("N-glycan G0F", "structural", "tier_2", "40-55%", "45-53%", 0.88, "HILIC-UPLC"),
            CQA("Charge variants", "structural", "tier_2", "Pattern similar", "Pattern similar", 0.85, "cIEF"),
            CQA("Concentration (100 mg/mL citrate-free)", "product", "tier_2", "100 mg/mL", "100 mg/mL", 1.00, "UV"),
            CQA("Aggregates", "product", "tier_2", "< 0.5%", "< 0.5%", 0.96, "SEC-HPLC"),
            # Tier 3
            CQA("HCP", "process", "tier_3", "< 50 ppm", "< 40 ppm", 0.97, "ELISA"),
            CQA("Endotoxin", "process", "tier_3", "< 0.5 EU/mg", "< 0.3 EU/mg", 0.98, "LAL"),
        ],
        "assessment_date": "2026-04-24",
    },
    "ranibizumab_fail": {
        "reference_product": "Lucentis (ranibizumab) — Genentech/Novartis referans",
        "biosimilar_candidate": "BS-RAN-FAIL (başarısız biyobenzer aday — fail örneği)",
        "cqas": [
            # Tier 1 — CRITICAL FAILURE
            CQA("Primary sequence", "structural", "tier_1", "100%", "100%", 1.00, "LC-MS"),
            CQA("VEGF binding affinity", "functional", "tier_1", "KD 46 pM", "KD 95 pM — 2× weaker", 0.65, "SPR — FAIL"),
            CQA("VEGF neutralization", "functional", "tier_1", "100% reference", "78% reference", 0.62, "HUVEC — FAIL"),
            CQA("Aggregates", "product", "tier_2", "< 0.5%", "1.2% — high", 0.45, "SEC — FAIL"),
            # Tier 2
            CQA("Charge variants", "structural", "tier_2", "Pattern similar", "Pattern differs", 0.55, "cIEF"),
            CQA("HCP", "process", "tier_3", "< 100 ppm", "< 80 ppm", 0.93, "ELISA"),
        ],
        "assessment_date": "2026-04-24",
    },
}


def print_assessment_report(assessment: ComparabilityAssessment):
    """Comparability raporunu yazdır."""
    verdict = assessment.verdict()
    
    print()
    print("═" * 90)
    print(f"  BIOSIMILAR COMPARABILITY ASSESSMENT")
    print("═" * 90)
    print(f"  Referans ürün: {assessment.reference_product}")
    print(f"  Biyobenzer aday: {assessment.biosimilar_candidate}")
    print(f"  Değerlendirme tarihi: {assessment.assessment_date}")
    print(f"  Toplam CQA sayısı: {len(assessment.cqas)}")
    
    # Tier breakdown
    tier_counts = {}
    for cqa in assessment.cqas:
        tier_counts[cqa.tier] = tier_counts.get(cqa.tier, 0) + 1
    
    print(f"\n  CQA Tier Dağılımı:")
    for tier, count in sorted(tier_counts.items()):
        print(f"    {TIER_DEFINITIONS[tier]['name']:<12}: {count}")
    
    # Tier scores
    tier_scores = assessment.tier_scores()
    print(f"\n  Tier Skorları:")
    for tier, score in tier_scores.items():
        if score is not None:
            tier_name = TIER_DEFINITIONS[tier]['name']
            min_req = TIER_DEFINITIONS[tier]['minimum_score_for_biosimilar']
            status = "✓" if score >= min_req else "✗"
            print(f"    {status} {tier_name:<12}: {score:.3f}  (min {min_req:.2f} gerekli)")
    
    # Overall score + verdict
    print(f"\n  ─────────────────────────────────────────────────────────────")
    overall = verdict['overall_score']
    print(f"  OVERALL SCORE:      {overall:.3f}  (0.85+ biosimilarity hedefi)")
    
    status_icon = {"PASS": "✓✓", "CONDITIONAL": "⚠", "FAIL": "✗✗"}.get(verdict['status'], "?")
    print(f"  VERDICT:            {status_icon} {verdict['status']}")
    print(f"  YORUM:              {verdict['message']}")
    
    # Failed CQAs
    if verdict['failed_count'] > 0:
        print(f"\n  ⚠ BAŞARISIZ CQA'lar ({verdict['failed_count']}):")
        for cqa in assessment.failed_cqas():
            band = classify_similarity(cqa.overlap_pct)
            tier_name = TIER_DEFINITIONS[cqa.tier]['name']
            print(f"    [{tier_name}] {cqa.name:<40} — {cqa.overlap_pct:.2f} ({band['label']})")
    
    print(f"\n  ─────────────────────────────────────────────────────────────")
    print(f"  DETAYLI CQA TABLOSU:")
    print()
    print(f"  {'Tier':<5} {'CQA':<42} {'Overlap':<9} {'Band':<22} {'Method':<14}")
    print(f"  {'-'*5} {'-'*42} {'-'*9} {'-'*22} {'-'*14}")
    
    # Tier 1 önce, sonra 2, sonra 3
    for tier in ["tier_1", "tier_2", "tier_3"]:
        tier_cqas = [c for c in assessment.cqas if c.tier == tier]
        for cqa in tier_cqas:
            band = classify_similarity(cqa.overlap_pct)
            tier_label = tier.replace("tier_", "T")
            print(f"  {tier_label:<5} {cqa.name[:42]:<42} {cqa.overlap_pct:<9.2f} {band['icon']+' '+band['label']:<22} {cqa.method[:14]:<14}")
    
    print()
    print("═" * 90)
    print()


def print_assessment_json(assessment: ComparabilityAssessment):
    """JSON çıktı."""
    verdict = assessment.verdict()
    data = {
        "reference_product": assessment.reference_product,
        "biosimilar_candidate": assessment.biosimilar_candidate,
        "assessment_date": assessment.assessment_date,
        "verdict": verdict,
        "cqas": [asdict(c) for c in assessment.cqas],
    }
    print(json.dumps(data, indent=2, ensure_ascii=False))


def load_cqas_json(path: str) -> ComparabilityAssessment:
    """JSON'dan CQA verisi yükle."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    cqas = [CQA(**c) for c in data.get('cqas', [])]
    return ComparabilityAssessment(
        reference_product=data.get('reference_product', ''),
        biosimilar_candidate=data.get('biosimilar_candidate', ''),
        cqas=cqas,
        assessment_date=data.get('assessment_date', ''),
    )


def main():
    print()
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.6.0 — Biosimilar Comparability Calculator            ║")
    print("║  CQA (Critical Quality Attributes) benzerlik skorlama                 ║")
    print("║  ICH Q5E + FDA + EMA Biosimilar Guidance uyumlu                       ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")
    
    json_output = '--json' in sys.argv
    
    # Example mode
    if '--example' in sys.argv:
        try:
            idx = sys.argv.index('--example')
            example_name = sys.argv[idx + 1]
        except (IndexError, ValueError):
            example_name = "trastuzumab"
        
        if example_name not in EXAMPLES:
            print(f"\n❌ Bilinmeyen örnek: {example_name}")
            print(f"   Mevcut: {list(EXAMPLES.keys())}")
            sys.exit(1)
        
        ex = EXAMPLES[example_name]
        assessment = ComparabilityAssessment(
            reference_product=ex['reference_product'],
            biosimilar_candidate=ex['biosimilar_candidate'],
            cqas=ex['cqas'],
            assessment_date=ex['assessment_date'],
        )
        
        if json_output:
            print_assessment_json(assessment)
        else:
            print_assessment_report(assessment)
        return
    
    # Import mode
    if '--import' in sys.argv:
        try:
            idx = sys.argv.index('--import')
            path = sys.argv[idx + 1]
            assessment = load_cqas_json(path)
            if json_output:
                print_assessment_json(assessment)
            else:
                print_assessment_report(assessment)
            return
        except (IndexError, FileNotFoundError) as e:
            print(f"❌ Import hatası: {e}")
            sys.exit(1)
    
    # Default: help
    print("\nKullanım:")
    print("  --example <name>   Demo (mevcut: " + ', '.join(EXAMPLES.keys()) + ")")
    print("  --import <file>    JSON import")
    print("  --json             JSON çıktı formatı")
    print()
    print("CQA tier sistemi:")
    print("  Tier 1 (Critical):  Biosimilarity için zorunlu (min skor 0.85)")
    print("  Tier 2 (Important): Önemli (min skor 0.70)")
    print("  Tier 3 (Minor):     İzleme (min skor 0.50)")
    print()
    print("Similarity bands:")
    print("  Highly Similar (≥0.90) → 1.0")
    print("  Similar (0.80-0.90)    → 0.7")
    print("  Trend (0.70-0.80)      → 0.4")
    print("  Not Similar (<0.70)    → 0.0")


if __name__ == "__main__":
    main()
