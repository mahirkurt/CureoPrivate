#!/usr/bin/env python3
"""
regulatory-timeline.py — Farmasötik Regülatör + Geri Ödeme Takvim Otomasyonu

Ruhsat başvuru tarihinden piyasada satış + SGK geri ödemeye kadar tüm aşamaları
Gantt-style Mermaid + ASCII tablo + JSON çıktı olarak üretir. Türkiye (TİTCK + SGK)
odaklı; AB ve ABD karşılaştırma modu da var.

Aşamalar (Türkiye):
    1. CMC + non-clinical hazırlık
    2. Klinik çalışma (Faz I-II-III)
    3. TİTCK başvuru (Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği)
    4. TİTCK değerlendirme (180 + 60 ek gün)
    5. Ruhsat verilmesi
    6. SGK başvuru
    7. SGK değerlendirme (Ödeme Komisyonu)
    8. SUT + GLP listesi
    9. Satışa arz
    10. İhale + hastane erişim

Bolar takvimi (SMK m. 85/3):
    Patent expiry 'den geriye 2-3 yıl önce jenerik hazırlık başlar.

Kullanım:
    python3 regulatory-timeline.py --product semaglutide --tr
    python3 regulatory-timeline.py --product pembrolizumab --compare-eu
    python3 regulatory-timeline.py --biosimilar adalimumab
    python3 regulatory-timeline.py --example

Yazar: pharmapatent skill v1.7.0
Bağımlılık: python-dateutil (opsiyonel)
"""

import sys
import json
import argparse
from datetime import date, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


@dataclass
class Phase:
    name: str
    start: str       # YYYY-MM
    end: str         # YYYY-MM
    duration_months: int
    jurisdiction: str   # TR / EU / US / Global
    category: str       # clinical / regulatory / reimbursement / commercial
    notes: str = ""
    dependency: Optional[str] = None


@dataclass
class Timeline:
    product: str
    product_type: str    # innovative / biosimilar / generic
    phases: List[Phase] = field(default_factory=list)
    milestones: List[Dict] = field(default_factory=list)


# --- Template helpers ---

TR_INNOVATIVE_PHASES = [
    ("CMC + non-clinical", 36, "clinical"),
    ("Faz I (klinik giriş)", 18, "clinical"),
    ("Faz II", 24, "clinical"),
    ("Faz III", 36, "clinical"),
    ("TİTCK başvuru hazırlık", 6, "regulatory"),
    ("TİTCK değerlendirme", 10, "regulatory"),  # 180+60 gün + ek
    ("Ruhsat verilmesi", 1, "regulatory"),
    ("SGK başvuru + Ödeme Komisyonu", 8, "reimbursement"),
    ("SUT listesi yayın", 1, "reimbursement"),
    ("Satışa arz", 1, "commercial"),
    ("Hastane ihale + erişim", 6, "commercial"),
]


TR_BIOSIMILAR_PHASES = [
    ("CMC + analitik benzerlik", 18, "clinical"),
    ("Preklinik karşılaştırılabilirlik", 12, "clinical"),
    ("Faz I PK/PD karşılaştırma", 12, "clinical"),
    ("Faz III konfirmatif", 30, "clinical"),
    ("TİTCK biyobenzer başvuru", 6, "regulatory"),
    ("TİTCK değerlendirme", 12, "regulatory"),
    ("Ruhsat verilmesi", 1, "regulatory"),
    ("SGK ihale süreci", 6, "reimbursement"),
    ("Satışa arz", 1, "commercial"),
]


TR_GENERIC_PHASES = [
    ("Formülasyon geliştirme", 12, "clinical"),
    ("Biyoeşdeğerlik çalışması", 6, "clinical"),
    ("TİTCK kısaltılmış başvuru", 3, "regulatory"),
    ("TİTCK değerlendirme", 8, "regulatory"),
    ("Ruhsat verilmesi", 1, "regulatory"),
    ("SGK ihale", 3, "reimbursement"),
    ("Satışa arz", 1, "commercial"),
]


def calc_end_date(start_ym: str, months: int) -> str:
    """YYYY-MM formatında start + months."""
    y, m = map(int, start_ym.split('-'))
    total = (y * 12 + (m - 1)) + months
    ny = total // 12
    nm = (total % 12) + 1
    return f"{ny}-{nm:02d}"


def build_timeline(product: str, product_type: str, start_ym: str) -> Timeline:
    """Timeline inşa et."""
    if product_type == "biosimilar":
        phases_def = TR_BIOSIMILAR_PHASES
    elif product_type == "generic":
        phases_def = TR_GENERIC_PHASES
    else:
        phases_def = TR_INNOVATIVE_PHASES
    
    phases = []
    current = start_ym
    for name, months, category in phases_def:
        end = calc_end_date(current, months)
        phase = Phase(
            name=name,
            start=current,
            end=end,
            duration_months=months,
            jurisdiction="TR",
            category=category,
        )
        phases.append(phase)
        current = end
    
    return Timeline(product=product, product_type=product_type, phases=phases)


def add_bolar_phase(timeline: Timeline, patent_expiry_ym: str) -> None:
    """Bolar dönemini patent expiry'den geriye doğru hesapla."""
    # Bolar hazırlık: patent expiry - 2 yıl
    y, m = map(int, patent_expiry_ym.split('-'))
    bolar_start = f"{y-2}-{m:02d}"
    
    bolar_phase = Phase(
        name="Bolar hazırlık (SMK m.85/3)",
        start=bolar_start,
        end=patent_expiry_ym,
        duration_months=24,
        jurisdiction="TR",
        category="clinical",
        notes="Patent expiry öncesi biyoeşdeğerlik + dossier hazırlığı yapılabilir",
    )
    timeline.phases.insert(0, bolar_phase)


def print_ascii_gantt(timeline: Timeline, width: int = 60):
    """ASCII-art Gantt chart."""
    print()
    print("═" * (width + 40))
    print(f"  REGÜLATÖR TAKVİM — {timeline.product} ({timeline.product_type})")
    print("═" * (width + 40))
    
    # Tüm tarihleri topla
    all_dates = []
    for p in timeline.phases:
        all_dates.append(p.start)
        all_dates.append(p.end)
    
    min_ym = min(all_dates)
    max_ym = max(all_dates)
    min_y, min_m = map(int, min_ym.split('-'))
    max_y, max_m = map(int, max_ym.split('-'))
    total_months = (max_y - min_y) * 12 + (max_m - min_m)
    
    print(f"  Süre: {min_ym} → {max_ym} ({total_months} ay, ~{total_months/12:.1f} yıl)")
    print()
    
    # Category icons
    cat_icons = {
        'clinical': '🧪',
        'regulatory': '📋',
        'reimbursement': '💰',
        'commercial': '🏪',
    }
    
    for p in timeline.phases:
        ps_y, ps_m = map(int, p.start.split('-'))
        pe_y, pe_m = map(int, p.end.split('-'))
        start_offset = (ps_y - min_y) * 12 + (ps_m - min_m)
        duration = (pe_y - ps_y) * 12 + (pe_m - ps_m)
        
        if total_months > 0:
            bar_start = int(start_offset / total_months * width)
            bar_end = int((start_offset + duration) / total_months * width)
            bar_len = max(1, bar_end - bar_start)
        else:
            bar_start = 0
            bar_len = width
        
        line = " " * bar_start + "█" * bar_len
        line = line.ljust(width)
        
        icon = cat_icons.get(p.category, '•')
        print(f"  {icon} {p.name[:25]:<25} {p.start}→{p.end} |{line}| {p.duration_months:>2}ay")
    
    print()
    print("═" * (width + 40))


def print_markdown_table(timeline: Timeline):
    """Markdown table çıktısı."""
    print()
    print(f"# Regülatör Takvim — {timeline.product}")
    print()
    print(f"**Ürün tipi**: {timeline.product_type}")
    print()
    
    cat_counts = {}
    total_months = 0
    for p in timeline.phases:
        cat_counts[p.category] = cat_counts.get(p.category, 0) + p.duration_months
        total_months += p.duration_months
    
    print(f"**Toplam süre**: {total_months} ay (~{total_months/12:.1f} yıl)")
    print()
    print("| Kategori | Süre (ay) | Yüzde |")
    print("|---|---|---|")
    for cat, months in cat_counts.items():
        pct = (months / total_months * 100) if total_months else 0
        print(f"| {cat} | {months} | {pct:.1f}% |")
    print()
    
    print("## Faz detayı")
    print()
    print("| Faz | Kategori | Başlangıç | Bitiş | Süre |")
    print("|---|---|---|---|---|")
    for p in timeline.phases:
        print(f"| {p.name} | {p.category} | {p.start} | {p.end} | {p.duration_months} ay |")
    print()


def print_mermaid_gantt(timeline: Timeline):
    """Mermaid Gantt syntax çıktısı."""
    print()
    print("```mermaid")
    print("gantt")
    print(f"    title {timeline.product} Regülatör Takvimi")
    print("    dateFormat YYYY-MM")
    print("    axisFormat %Y")
    print()
    
    sections = {}
    for p in timeline.phases:
        sections.setdefault(p.category, []).append(p)
    
    section_names = {
        'clinical': 'Klinik',
        'regulatory': 'Ruhsatlandırma',
        'reimbursement': 'Geri Ödeme',
        'commercial': 'Ticari',
    }
    
    for cat in ['clinical', 'regulatory', 'reimbursement', 'commercial']:
        if cat in sections:
            print(f"    section {section_names.get(cat, cat)}")
            for p in sections[cat]:
                task_id = p.name.replace(' ', '_').replace('+', 'plus').replace('(', '').replace(')', '').replace('.', '').replace('/', '')[:25]
                print(f"    {p.name[:30]} : {task_id}, {p.start}, {p.end}")
    
    print("```")
    print()


def example_mode():
    """Demo: üç farklı senaryo."""
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.7.0 — Regülatör Takvim Otomasyonu                ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    
    print("\n### ÖRNEK 1: Innovatif ilaç — pembrolizumab hipotetik TR yol\n")
    t1 = build_timeline("Pembrolizumab (hipotetik)", "innovative", "2024-01")
    print_ascii_gantt(t1)
    
    print("\n### ÖRNEK 2: Biyobenzer — adalimumab (Humira) TR yol\n")
    t2 = build_timeline("Adalimumab biyobenzer", "biosimilar", "2024-01")
    print_ascii_gantt(t2)
    
    print("\n### ÖRNEK 3: Jenerik + Bolar — semaglutide jenerik\n")
    t3 = build_timeline("Semaglutide jenerik 1mg", "generic", "2029-05")
    add_bolar_phase(t3, "2031-05")  # TR patent expiry 2031-05
    print_ascii_gantt(t3)
    
    print()
    print("  🇹🇷 Türkiye toplam süreleri özeti:")
    print("     Innovatif:  ~12 yıl (preklinik → ticari erişim)")
    print("     Biyobenzer: ~8 yıl (CMC → pazara arz)")
    print("     Jenerik:    ~2 yıl + Bolar 2 yıl overlap")
    print()


def main():
    parser = argparse.ArgumentParser(description="Regulatory Timeline Generator v1.7.0")
    parser.add_argument('--product', type=str, help="Ürün adı")
    parser.add_argument('--type', type=str, default='innovative', choices=['innovative', 'biosimilar', 'generic'])
    parser.add_argument('--start', type=str, default='2024-01', help="Başlangıç YYYY-MM")
    parser.add_argument('--patent-expiry', type=str, help="Patent expiry YYYY-MM (jenerik için Bolar hesabı)")
    parser.add_argument('--format', type=str, default='ascii', choices=['ascii', 'markdown', 'mermaid', 'json'])
    parser.add_argument('--example', action='store_true', help="Demo mode")
    
    args = parser.parse_args()
    
    if args.example or not args.product:
        example_mode()
        return
    
    timeline = build_timeline(args.product, args.type, args.start)
    if args.patent_expiry and args.type == 'generic':
        add_bolar_phase(timeline, args.patent_expiry)
    
    if args.format == 'ascii':
        print_ascii_gantt(timeline)
    elif args.format == 'markdown':
        print_markdown_table(timeline)
    elif args.format == 'mermaid':
        print_mermaid_gantt(timeline)
    elif args.format == 'json':
        data = asdict(timeline)
        print(json.dumps(data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
