#!/usr/bin/env python3
"""
evidence-ranker.py — GRADE + Oxford CEBM Kanıt Seviyesi Otomatik Sınıflandırma

Klinik çalışmaları ve yayınları GRADE (Grading of Recommendations Assessment,
Development and Evaluation) ve Oxford CEBM (Centre for Evidence-Based Medicine)
hiyerarşilerine göre sınıflandırır.

GRADE sınıflandırması:
    HIGH:     Yüksek kalite — gerçek etki tahmine yakın (örn. iyi yapılandırılmış RCT)
    MODERATE: Orta kalite — gerçek etki muhtemelen tahmine yakın, ama bazı kısıtlar
    LOW:      Düşük kalite — gerçek etki tahminden farklı olabilir
    VERY LOW: Çok düşük — tahmin çok belirsiz

Oxford CEBM 2011 hiyerarşisi:
    Level 1: Systematic review of RCTs
    Level 2: Randomized trial or observational study with dramatic effect
    Level 3: Non-randomized controlled cohort/follow-up study
    Level 4: Case series, case-control, or historically controlled studies
    Level 5: Mechanism-based reasoning

Downgrade kriterleri (GRADE):
    - Risk of bias (RoB): -1 ciddi, -2 çok ciddi
    - Inconsistency: -1 ciddi, -2 çok ciddi
    - Indirectness: -1 ciddi, -2 çok ciddi
    - Imprecision: -1 ciddi, -2 çok ciddi
    - Publication bias: -1 ciddi

Upgrade kriterleri (observational için):
    - Large effect (RR > 2 veya < 0.5): +1
    - Very large effect (RR > 5 veya < 0.2): +2
    - Dose-response gradient: +1
    - All plausible confounders decrease observed effect: +1

Kullanım:
    python3 evidence-ranker.py --example            # 5 farklı çalışma demo
    python3 evidence-ranker.py --import studies.json
    python3 evidence-ranker.py --format markdown | json

Yazar: pharmapatent skill v1.7.0
"""

import sys
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from enum import Enum


class StudyDesign(str, Enum):
    SR_RCT = "systematic_review_of_rcts"
    META_ANALYSIS = "meta_analysis"
    RCT = "randomized_controlled_trial"
    CLUSTER_RCT = "cluster_randomized_trial"
    NONRAND_CONTROLLED = "non_randomized_controlled_trial"
    COHORT_PROSP = "prospective_cohort"
    COHORT_RETR = "retrospective_cohort"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"
    CASE_SERIES = "case_series"
    CASE_REPORT = "case_report"
    MECHANISM = "mechanism_based_reasoning"
    ANIMAL = "animal_preclinical"
    IN_VITRO = "in_vitro"
    EXPERT_OPINION = "expert_opinion"


@dataclass
class Study:
    id: str
    title: str
    design: str           # StudyDesign enum value
    year: int
    n_subjects: Optional[int] = None
    primary_endpoint_met: Optional[bool] = None
    blinding: str = "double_blind"    # open_label / single_blind / double_blind / triple_blind
    allocation_concealment: str = "yes"  # yes / no / unclear
    
    # GRADE downgrades
    risk_of_bias: int = 0           # 0 / -1 / -2
    inconsistency: int = 0          # 0 / -1 / -2
    indirectness: int = 0           # 0 / -1 / -2
    imprecision: int = 0            # 0 / -1 / -2
    publication_bias: int = 0       # 0 / -1
    
    # GRADE upgrades (observasyonel için)
    large_effect: int = 0           # 0 / +1 / +2
    dose_response: int = 0          # 0 / +1
    plausible_confounders_reduce: int = 0  # 0 / +1
    
    notes: str = ""


# --- GRADE + CEBM logic ---

def oxford_level(design: str) -> int:
    """Oxford CEBM 2011 level."""
    level_map = {
        StudyDesign.SR_RCT.value: 1,
        StudyDesign.META_ANALYSIS.value: 1,
        StudyDesign.RCT.value: 2,
        StudyDesign.CLUSTER_RCT.value: 2,
        StudyDesign.NONRAND_CONTROLLED.value: 3,
        StudyDesign.COHORT_PROSP.value: 3,
        StudyDesign.COHORT_RETR.value: 3,
        StudyDesign.CASE_CONTROL.value: 4,
        StudyDesign.CROSS_SECTIONAL.value: 4,
        StudyDesign.CASE_SERIES.value: 4,
        StudyDesign.CASE_REPORT.value: 4,
        StudyDesign.MECHANISM.value: 5,
        StudyDesign.ANIMAL.value: 5,
        StudyDesign.IN_VITRO.value: 5,
        StudyDesign.EXPERT_OPINION.value: 5,
    }
    return level_map.get(design, 5)


def baseline_grade(design: str) -> str:
    """Başlangıç GRADE — tasarıma göre."""
    if design in (StudyDesign.SR_RCT.value, StudyDesign.META_ANALYSIS.value):
        return "HIGH"
    if design in (StudyDesign.RCT.value, StudyDesign.CLUSTER_RCT.value):
        return "HIGH"
    # Observasyonel
    if design in (StudyDesign.COHORT_PROSP.value, StudyDesign.COHORT_RETR.value,
                  StudyDesign.CASE_CONTROL.value, StudyDesign.NONRAND_CONTROLLED.value):
        return "LOW"
    # Diğer
    return "VERY LOW"


def compute_grade(study: Study) -> Dict:
    """Çalışma için GRADE hesapla."""
    level_values = {"HIGH": 4, "MODERATE": 3, "LOW": 2, "VERY LOW": 1}
    value_levels = {v: k for k, v in level_values.items()}
    
    base = baseline_grade(study.design)
    level = level_values[base]
    
    # Downgrades
    downgrades = [
        ("Risk of Bias", study.risk_of_bias),
        ("Inconsistency", study.inconsistency),
        ("Indirectness", study.indirectness),
        ("Imprecision", study.imprecision),
        ("Publication Bias", study.publication_bias),
    ]
    
    # Upgrades (observasyonel için; bazen RCT için de)
    upgrades_applied = []
    # Sadece baseline LOW ise upgrade uygulanabilir
    if base in ("LOW", "VERY LOW"):
        if study.large_effect > 0:
            level += study.large_effect
            upgrades_applied.append(f"Large effect (+{study.large_effect})")
        if study.dose_response > 0:
            level += study.dose_response
            upgrades_applied.append(f"Dose-response (+1)")
        if study.plausible_confounders_reduce > 0:
            level += study.plausible_confounders_reduce
            upgrades_applied.append(f"Plausible confounders reduce effect (+1)")
    
    downgrade_total = 0
    downgrades_applied = []
    for label, delta in downgrades:
        if delta < 0:
            downgrades_applied.append(f"{label} ({delta})")
            downgrade_total += delta
    
    level += downgrade_total
    level = max(1, min(4, level))
    
    final_grade = value_levels[level]
    
    return {
        'baseline_grade': base,
        'oxford_level': oxford_level(study.design),
        'final_grade': final_grade,
        'downgrades_applied': downgrades_applied,
        'upgrades_applied': upgrades_applied,
        'net_change': level - level_values[base],
    }


# --- Examples ---

EXAMPLES = [
    Study(
        id="ex1",
        title="KEYNOTE-189 — pembrolizumab + kemoterapi vs kemoterapi tek başına NSCLC",
        design=StudyDesign.RCT.value,
        year=2018,
        n_subjects=616,
        primary_endpoint_met=True,
        blinding="double_blind",
        allocation_concealment="yes",
        risk_of_bias=0,
        inconsistency=0,
        indirectness=0,
        imprecision=0,
        publication_bias=0,
        notes="Geniş N, well-randomized, çifte kör, OS ve PFS pozitif",
    ),
    Study(
        id="ex2",
        title="CheckMate-067 — nivolumab+ipilimumab vs tek ajan melanom",
        design=StudyDesign.RCT.value,
        year=2017,
        n_subjects=945,
        primary_endpoint_met=True,
        blinding="double_blind",
        allocation_concealment="yes",
        risk_of_bias=0,
        inconsistency=-1,
        indirectness=0,
        imprecision=0,
        publication_bias=0,
        notes="OS pozitif ama subgrup inconsistency (BRAF+ vs BRAF-)",
    ),
    Study(
        id="ex3",
        title="Gerçek dünya kohort — dapagliflozin HFrEF TR 5 merkez retrospektif",
        design=StudyDesign.COHORT_RETR.value,
        year=2024,
        n_subjects=1200,
        primary_endpoint_met=True,
        blinding="open_label",
        allocation_concealment="no",
        risk_of_bias=-1,
        inconsistency=0,
        indirectness=0,
        imprecision=0,
        publication_bias=0,
        large_effect=1,       # HR 0.55 (büyük etki)
        dose_response=0,
        plausible_confounders_reduce=1,
        notes="Propensity-matched; residüel confounding olası ama birçok varyasyon kontrol edildi",
    ),
    Study(
        id="ex4",
        title="Case series — 12 hasta off-label lecanemab erken Alzheimer Türkiye",
        design=StudyDesign.CASE_SERIES.value,
        year=2025,
        n_subjects=12,
        primary_endpoint_met=None,
        notes="Kontrol yok, bildirim serileri",
    ),
    Study(
        id="ex5",
        title="Cochrane Review — CAR-T vs kemoterapi relapsed DLBCL",
        design=StudyDesign.SR_RCT.value,
        year=2024,
        n_subjects=2400,
        primary_endpoint_met=True,
        risk_of_bias=0,
        inconsistency=0,
        indirectness=0,
        imprecision=-1,   # Bazı subpopulations sparse
        publication_bias=0,
        notes="6 RCT dahil, heterojenite düşük, dolaylı karşılaştırmalar tam değil",
    ),
    Study(
        id="ex6",
        title="AZALEA-TIMI 71 — abelacimab vs rivaroksaban AF (Factor XI Faz II)",
        design=StudyDesign.RCT.value,
        year=2023,
        n_subjects=1287,
        primary_endpoint_met=True,
        risk_of_bias=0,
        inconsistency=0,
        indirectness=-1,   # Surrogate endpoint (kanama, değil stroke)
        imprecision=0,
        publication_bias=0,
        notes="Faz II — primer sonuç kanama; stroke için Faz III gerekli",
    ),
]


def print_markdown_report(studies: List[Study]):
    print()
    print("# Evidence Ranker — GRADE + Oxford CEBM Sınıflandırma")
    print()
    print(f"**Toplam çalışma**: {len(studies)}")
    print()
    
    # Özet tablo
    print("## Özet Tablosu")
    print()
    print("| # | Çalışma | Tasarım | Oxford | Baseline | Final GRADE | Net Δ |")
    print("|---|---|---|---|---|---|---|")
    for i, s in enumerate(studies, 1):
        result = compute_grade(s)
        emoji = {"HIGH": "🟢", "MODERATE": "🟡", "LOW": "🟠", "VERY LOW": "🔴"}[result['final_grade']]
        delta = result['net_change']
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        print(f"| {i} | {s.title[:60]} | `{s.design}` | Lv {result['oxford_level']} | {result['baseline_grade']} | {emoji} **{result['final_grade']}** | {delta_str} |")
    print()
    
    # Detaylı rapor
    print("## Detaylı Değerlendirme")
    print()
    for i, s in enumerate(studies, 1):
        result = compute_grade(s)
        emoji = {"HIGH": "🟢", "MODERATE": "🟡", "LOW": "🟠", "VERY LOW": "🔴"}[result['final_grade']]
        
        print(f"### {i}. {s.title}")
        print()
        print(f"- **Çalışma tasarımı**: `{s.design}`")
        print(f"- **Yıl**: {s.year}")
        if s.n_subjects:
            print(f"- **N**: {s.n_subjects}")
        print(f"- **Oxford CEBM Level**: {result['oxford_level']}")
        print(f"- **Baseline GRADE**: {result['baseline_grade']}")
        print(f"- **Final GRADE**: {emoji} **{result['final_grade']}**")
        
        if result['downgrades_applied']:
            print(f"- **Downgrades**:")
            for d in result['downgrades_applied']:
                print(f"  - {d}")
        if result['upgrades_applied']:
            print(f"- **Upgrades**:")
            for u in result['upgrades_applied']:
                print(f"  - {u}")
        
        if s.notes:
            print(f"- **Notlar**: _{s.notes}_")
        print()
    
    # GRADE dağılımı
    grade_counts = {"HIGH": 0, "MODERATE": 0, "LOW": 0, "VERY LOW": 0}
    for s in studies:
        r = compute_grade(s)
        grade_counts[r['final_grade']] += 1
    
    print("## GRADE Dağılımı")
    print()
    print("| Level | Sayı | Emoji |")
    print("|---|---|---|")
    for g in ["HIGH", "MODERATE", "LOW", "VERY LOW"]:
        emoji = {"HIGH": "🟢", "MODERATE": "🟡", "LOW": "🟠", "VERY LOW": "🔴"}[g]
        print(f"| {g} | {grade_counts[g]} | {emoji} |")
    print()


def print_json(studies: List[Study]):
    results = []
    for s in studies:
        r = compute_grade(s)
        results.append({
            "study": asdict(s),
            "grade_result": r,
        })
    print(json.dumps({"studies": results}, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Evidence Ranker v1.7.0")
    parser.add_argument('--example', action='store_true')
    parser.add_argument('--import', dest='import_path', type=str)
    parser.add_argument('--format', default='markdown', choices=['markdown', 'json'])
    
    args = parser.parse_args()
    
    studies = []
    if args.example or not args.import_path:
        studies = EXAMPLES
    else:
        with open(args.import_path) as f:
            data = json.load(f)
        studies = [Study(**s) for s in data.get('studies', [])]
    
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.7.0 — Evidence Ranker (GRADE + Oxford CEBM)      ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    if args.format == 'json':
        print_json(studies)
    else:
        print_markdown_report(studies)


if __name__ == "__main__":
    main()
