#!/usr/bin/env python3
"""
fto-grid.py — FTO Özet Grid Otomasyonu

Çoklu patent × çoklu ülke × çoklu ürün kombinasyonu için FTO risk matrisi üretir.
Her hücre için: Clean / Caution / Blocker / N/A statü + gerekçe satırı.

Kullanım:
    python3 fto-grid.py                                 # interactive
    python3 fto-grid.py --example hcv                   # HCV DAA demo
    python3 fto-grid.py --example obesity               # GLP-1 demo
    python3 fto-grid.py --example biosimilar            # Humira biyobenzer demo
    python3 fto-grid.py --import data.json              # JSON'dan yükle
    python3 fto-grid.py --format markdown               # markdown çıktı (default)
    python3 fto-grid.py --format json                   # JSON çıktı

JSON input formatı:
{
  "products": ["Ürün A", "Ürün B"],
  "countries": ["TR", "US", "EP", "JP"],
  "patents": [
    {"id": "EP123456", "family": "molecule", "owner": "BigPharma", "expiry": {"TR":"2028", "US":"2027", "EP":"2028"}},
    ...
  ],
  "assessments": [
    {"product":"Ürün A", "patent":"EP123456", "country":"TR", "status":"blocker", "rationale":"Literal cover"},
    ...
  ]
}

Yazar: pharmapatent skill v1.7.0
Bağımlılık: standart kütüphane
"""

import sys
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


STATUS_MAP = {
    'clean': {'symbol': '✓', 'emoji': '🟢', 'color': '#24a148', 'label': 'Clean'},
    'caution': {'symbol': '⚠', 'emoji': '🟡', 'color': '#f1c21b', 'label': 'Caution'},
    'blocker': {'symbol': '✗', 'emoji': '🔴', 'color': '#da1e28', 'label': 'Blocker'},
    'na': {'symbol': '—', 'emoji': '⚪', 'color': '#c6c6c6', 'label': 'N/A (no patent)'},
    'expired': {'symbol': '○', 'emoji': '⚫', 'color': '#525252', 'label': 'Expired'},
}


@dataclass
class Patent:
    id: str
    family: str        # molecule / formulation / process / device / 2nd_medical_use
    owner: str
    expiry: Dict[str, str]  # {"TR": "2028-03-15", "US": "2027-06-01", ...}
    title: str = ""


@dataclass
class Assessment:
    product: str
    patent: str        # Patent.id referansı
    country: str
    status: str        # clean / caution / blocker / na / expired
    rationale: str = ""


@dataclass
class FTOGrid:
    products: List[str]
    countries: List[str]
    patents: List[Patent]
    assessments: List[Assessment]
    
    def get_assessment(self, product: str, patent_id: str, country: str) -> Optional[Assessment]:
        for a in self.assessments:
            if a.product == product and a.patent == patent_id and a.country == country:
                return a
        return None
    
    def status_counts(self) -> Dict[str, int]:
        """Tüm assessments üzerinde statü dağılımı."""
        counts = {s: 0 for s in STATUS_MAP}
        for a in self.assessments:
            if a.status in counts:
                counts[a.status] += 1
        return counts
    
    def blockers_for_product(self, product: str) -> List[Assessment]:
        return [a for a in self.assessments if a.product == product and a.status == 'blocker']
    
    def blockers_for_country(self, country: str) -> List[Assessment]:
        return [a for a in self.assessments if a.country == country and a.status == 'blocker']


# --- Örnek veri ---

EXAMPLES = {
    "hcv": FTOGrid(
        products=["Sofosbuvir jenerik 400mg", "Sofosbuvir+velpatasvir combi"],
        countries=["TR", "US", "EP", "BR", "IN"],
        patents=[
            Patent("US8334270", "molecule", "Gilead", 
                   {"TR":"2029-03-30", "US":"2029-03-30", "EP":"2029-03-30", "BR":"expired", "IN":"revoked"},
                   "Sofosbuvir composition of matter"),
            Patent("EP2752422", "formulation", "Gilead",
                   {"TR":"2033", "US":"2033", "EP":"2033", "BR":"2033", "IN":"2033"},
                   "Sofosbuvir tablet formulation"),
            Patent("WO2017083630", "combination", "Gilead",
                   {"TR":"2037", "US":"2037", "EP":"2037", "BR":"2037", "IN":"pending"},
                   "Sofosbuvir+velpatasvir combination"),
        ],
        assessments=[
            # Sofosbuvir jenerik için
            Assessment("Sofosbuvir jenerik 400mg", "US8334270", "TR", "blocker", "Literal compose match; TR'de 2029'a kadar"),
            Assessment("Sofosbuvir jenerik 400mg", "US8334270", "US", "blocker", "Temel molekül koruması"),
            Assessment("Sofosbuvir jenerik 400mg", "US8334270", "EP", "blocker", "Temel molekül koruması"),
            Assessment("Sofosbuvir jenerik 400mg", "US8334270", "BR", "expired", "Patent iptal edildi 2018"),
            Assessment("Sofosbuvir jenerik 400mg", "US8334270", "IN", "na", "Hindistan'da Section 3(d) reddi, patent yok"),
            Assessment("Sofosbuvir jenerik 400mg", "EP2752422", "TR", "caution", "Alternatif formülasyon tasarlayabilir"),
            Assessment("Sofosbuvir jenerik 400mg", "EP2752422", "US", "caution", "Formülasyon etrafından dolaş"),
            Assessment("Sofosbuvir jenerik 400mg", "EP2752422", "EP", "caution", "Formülasyon etrafından dolaş"),
            Assessment("Sofosbuvir jenerik 400mg", "EP2752422", "BR", "caution", "Formülasyon patent"),
            Assessment("Sofosbuvir jenerik 400mg", "EP2752422", "IN", "caution", "Formülasyon patent"),
            Assessment("Sofosbuvir jenerik 400mg", "WO2017083630", "TR", "na", "Tek molekül, kombinasyon ilgisiz"),
            Assessment("Sofosbuvir jenerik 400mg", "WO2017083630", "US", "na", "Tek molekül"),
            Assessment("Sofosbuvir jenerik 400mg", "WO2017083630", "EP", "na", "Tek molekül"),
            Assessment("Sofosbuvir jenerik 400mg", "WO2017083630", "BR", "na", "Tek molekül"),
            Assessment("Sofosbuvir jenerik 400mg", "WO2017083630", "IN", "na", "Tek molekül"),
            # Combi için
            Assessment("Sofosbuvir+velpatasvir combi", "US8334270", "TR", "blocker", "Molekül kapsıyor"),
            Assessment("Sofosbuvir+velpatasvir combi", "US8334270", "US", "blocker", "Molekül kapsıyor"),
            Assessment("Sofosbuvir+velpatasvir combi", "US8334270", "EP", "blocker", "Molekül kapsıyor"),
            Assessment("Sofosbuvir+velpatasvir combi", "US8334270", "BR", "expired", "Expired"),
            Assessment("Sofosbuvir+velpatasvir combi", "US8334270", "IN", "na", "No patent"),
            Assessment("Sofosbuvir+velpatasvir combi", "EP2752422", "TR", "caution", "Formülasyon"),
            Assessment("Sofosbuvir+velpatasvir combi", "EP2752422", "US", "caution", "Formülasyon"),
            Assessment("Sofosbuvir+velpatasvir combi", "EP2752422", "EP", "caution", "Formülasyon"),
            Assessment("Sofosbuvir+velpatasvir combi", "EP2752422", "BR", "caution", "Formülasyon"),
            Assessment("Sofosbuvir+velpatasvir combi", "EP2752422", "IN", "caution", "Formülasyon"),
            Assessment("Sofosbuvir+velpatasvir combi", "WO2017083630", "TR", "blocker", "Kombinasyon patenti"),
            Assessment("Sofosbuvir+velpatasvir combi", "WO2017083630", "US", "blocker", "Kombinasyon patenti"),
            Assessment("Sofosbuvir+velpatasvir combi", "WO2017083630", "EP", "blocker", "Kombinasyon patenti"),
            Assessment("Sofosbuvir+velpatasvir combi", "WO2017083630", "BR", "blocker", "Kombinasyon patenti"),
            Assessment("Sofosbuvir+velpatasvir combi", "WO2017083630", "IN", "caution", "Başvuru devam; henüz granted değil"),
        ],
    ),
    "obesity": FTOGrid(
        products=["Semaglutide jenerik 1mg/dose", "Tirzepatide jenerik 5mg/dose"],
        countries=["TR", "US", "EP", "CN", "IN"],
        patents=[
            Patent("EP2059533", "molecule", "Novo Nordisk",
                   {"TR":"2031-05-23", "US":"2032-12", "EP":"2031-05-23", "CN":"2031", "IN":"granted 2031"},
                   "Semaglutide composition"),
            Patent("US10335463", "formulation", "Novo Nordisk",
                   {"TR":"2033", "US":"2033", "EP":"2033", "CN":"2033", "IN":"pending"},
                   "Semaglutide liquid formulation"),
            Patent("US11357820", "device", "Novo Nordisk",
                   {"TR":"2038", "US":"2038", "EP":"2038", "CN":"2038", "IN":"pending"},
                   "FlexTouch auto-injector"),
            Patent("EP3283508", "molecule", "Lilly",
                   {"TR":"2036", "US":"2036", "EP":"2036", "CN":"2036", "IN":"2036"},
                   "Tirzepatide composition"),
            Patent("US11478568", "device", "Lilly",
                   {"TR":"2040", "US":"2040", "EP":"2040", "CN":"2040", "IN":"pending"},
                   "KwikPen auto-injector"),
        ],
        assessments=[
            # Semaglutide jenerik
            Assessment("Semaglutide jenerik 1mg/dose", "EP2059533", "TR", "blocker", "Temel molekül 2031"),
            Assessment("Semaglutide jenerik 1mg/dose", "EP2059533", "US", "blocker", "Temel molekül 2032"),
            Assessment("Semaglutide jenerik 1mg/dose", "EP2059533", "EP", "blocker", "Temel molekül 2031 + SPC ~2033"),
            Assessment("Semaglutide jenerik 1mg/dose", "EP2059533", "CN", "blocker", "Temel molekül 2031"),
            Assessment("Semaglutide jenerik 1mg/dose", "EP2059533", "IN", "blocker", "Granted Ocak 2024"),
            Assessment("Semaglutide jenerik 1mg/dose", "US10335463", "TR", "caution", "Alternatif formülasyon mümkün"),
            Assessment("Semaglutide jenerik 1mg/dose", "US10335463", "US", "caution", "Design-around formülasyon"),
            Assessment("Semaglutide jenerik 1mg/dose", "US10335463", "EP", "caution", "Design-around"),
            Assessment("Semaglutide jenerik 1mg/dose", "US10335463", "CN", "caution", "Design-around"),
            Assessment("Semaglutide jenerik 1mg/dose", "US10335463", "IN", "caution", "Pending; izleme"),
            Assessment("Semaglutide jenerik 1mg/dose", "US11357820", "TR", "caution", "Farklı auto-injector tasarım gerekli"),
            Assessment("Semaglutide jenerik 1mg/dose", "US11357820", "US", "caution", "Farklı cihaz"),
            Assessment("Semaglutide jenerik 1mg/dose", "US11357820", "EP", "caution", "Farklı cihaz"),
            Assessment("Semaglutide jenerik 1mg/dose", "US11357820", "CN", "caution", "Farklı cihaz"),
            Assessment("Semaglutide jenerik 1mg/dose", "US11357820", "IN", "caution", "Pending"),
            Assessment("Semaglutide jenerik 1mg/dose", "EP3283508", "TR", "na", "Tirzepatide ilgisiz"),
            Assessment("Semaglutide jenerik 1mg/dose", "EP3283508", "US", "na", "İlgisiz"),
            Assessment("Semaglutide jenerik 1mg/dose", "EP3283508", "EP", "na", "İlgisiz"),
            Assessment("Semaglutide jenerik 1mg/dose", "EP3283508", "CN", "na", "İlgisiz"),
            Assessment("Semaglutide jenerik 1mg/dose", "EP3283508", "IN", "na", "İlgisiz"),
            Assessment("Semaglutide jenerik 1mg/dose", "US11478568", "TR", "na", "İlgisiz"),
            Assessment("Semaglutide jenerik 1mg/dose", "US11478568", "US", "na", "İlgisiz"),
            Assessment("Semaglutide jenerik 1mg/dose", "US11478568", "EP", "na", "İlgisiz"),
            Assessment("Semaglutide jenerik 1mg/dose", "US11478568", "CN", "na", "İlgisiz"),
            Assessment("Semaglutide jenerik 1mg/dose", "US11478568", "IN", "na", "İlgisiz"),
            # Tirzepatide jenerik
            Assessment("Tirzepatide jenerik 5mg/dose", "EP2059533", "TR", "na", "İlgisiz"),
            Assessment("Tirzepatide jenerik 5mg/dose", "EP2059533", "US", "na", "İlgisiz"),
            Assessment("Tirzepatide jenerik 5mg/dose", "EP2059533", "EP", "na", "İlgisiz"),
            Assessment("Tirzepatide jenerik 5mg/dose", "EP2059533", "CN", "na", "İlgisiz"),
            Assessment("Tirzepatide jenerik 5mg/dose", "EP2059533", "IN", "na", "İlgisiz"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US10335463", "TR", "na", "Semaglutide formülasyon"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US10335463", "US", "na", "Semaglutide formülasyon"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US10335463", "EP", "na", "Semaglutide formülasyon"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US10335463", "CN", "na", "Semaglutide formülasyon"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US10335463", "IN", "na", "Semaglutide formülasyon"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US11357820", "TR", "na", "Novo cihazı"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US11357820", "US", "na", "Novo cihazı"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US11357820", "EP", "na", "Novo cihazı"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US11357820", "CN", "na", "Novo cihazı"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US11357820", "IN", "na", "Novo cihazı"),
            Assessment("Tirzepatide jenerik 5mg/dose", "EP3283508", "TR", "blocker", "Temel molekül 2036"),
            Assessment("Tirzepatide jenerik 5mg/dose", "EP3283508", "US", "blocker", "Temel molekül 2036"),
            Assessment("Tirzepatide jenerik 5mg/dose", "EP3283508", "EP", "blocker", "Temel molekül 2036 + SPC ~2038"),
            Assessment("Tirzepatide jenerik 5mg/dose", "EP3283508", "CN", "blocker", "Temel molekül 2036"),
            Assessment("Tirzepatide jenerik 5mg/dose", "EP3283508", "IN", "blocker", "Granted 2036"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US11478568", "TR", "caution", "Farklı auto-injector gerekli"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US11478568", "US", "caution", "Farklı cihaz"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US11478568", "EP", "caution", "Farklı cihaz"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US11478568", "CN", "caution", "Farklı cihaz"),
            Assessment("Tirzepatide jenerik 5mg/dose", "US11478568", "IN", "caution", "Pending"),
        ],
    ),
    "biosimilar": FTOGrid(
        products=["Adalimumab biyobenzer 40mg"],
        countries=["TR", "US", "EP"],
        patents=[
            Patent("US6258562", "molecule", "AbbVie", {"TR":"expired", "US":"expired", "EP":"expired"},
                   "Adalimumab molecule (Humira)"),
            Patent("US9085619", "formulation", "AbbVie", {"TR":"2031", "US":"expired 2023 US", "EP":"2030"},
                   "High-concentration citrate-free formulation"),
            Patent("US8940305", "manufacturing", "AbbVie", {"TR":"2028", "US":"2027", "EP":"2028"},
                   "Protein A purification process"),
            Patent("US10941205", "method", "AbbVie", {"TR":"2030", "US":"2029", "EP":"2030"},
                   "Interval dosing method psoriasis"),
        ],
        assessments=[
            Assessment("Adalimumab biyobenzer 40mg", "US6258562", "TR", "expired", "Expired 2018"),
            Assessment("Adalimumab biyobenzer 40mg", "US6258562", "US", "expired", "Expired 2016"),
            Assessment("Adalimumab biyobenzer 40mg", "US6258562", "EP", "expired", "Expired 2018"),
            Assessment("Adalimumab biyobenzer 40mg", "US9085619", "TR", "blocker", "Citrate-free yüksek konsantrasyon formülasyon"),
            Assessment("Adalimumab biyobenzer 40mg", "US9085619", "US", "expired", "Expired 2023"),
            Assessment("Adalimumab biyobenzer 40mg", "US9085619", "EP", "caution", "2030'a kadar — alternatif formülasyon tasarımı"),
            Assessment("Adalimumab biyobenzer 40mg", "US8940305", "TR", "caution", "Alternatif saflaştırma kullan"),
            Assessment("Adalimumab biyobenzer 40mg", "US8940305", "US", "caution", "Alternatif saflaştırma"),
            Assessment("Adalimumab biyobenzer 40mg", "US8940305", "EP", "caution", "Alternatif saflaştırma"),
            Assessment("Adalimumab biyobenzer 40mg", "US10941205", "TR", "caution", "Interval dosing labellingi dışla"),
            Assessment("Adalimumab biyobenzer 40mg", "US10941205", "US", "caution", "Interval dosing"),
            Assessment("Adalimumab biyobenzer 40mg", "US10941205", "EP", "caution", "Interval dosing"),
        ],
    ),
}


def print_markdown_grid(grid: FTOGrid):
    """Markdown grid tablosu."""
    print()
    print(f"# FTO Risk Matrisi")
    print()
    print(f"**Ürün sayısı**: {len(grid.products)} · **Ülke sayısı**: {len(grid.countries)} · **Patent sayısı**: {len(grid.patents)}")
    print()
    
    counts = grid.status_counts()
    total = sum(counts.values())
    print(f"**Özet statü dağılımı** (toplam {total} değerlendirme):")
    print()
    print("| Statü | Sayı | Yüzde |")
    print("|---|---|---|")
    for status, count in counts.items():
        if count > 0:
            meta = STATUS_MAP[status]
            pct = (count / total * 100) if total else 0
            print(f"| {meta['emoji']} {meta['label']} | {count} | {pct:.1f}% |")
    print()
    
    for product in grid.products:
        print(f"## {product}")
        print()
        
        header = "| Patent | Kategori | Sahip |"
        for country in grid.countries:
            header += f" {country} |"
        print(header)
        
        sep = "|---|---|---|"
        for _ in grid.countries:
            sep += "---|"
        print(sep)
        
        for patent in grid.patents:
            row = f"| `{patent.id}` | {patent.family} | {patent.owner} |"
            for country in grid.countries:
                a = grid.get_assessment(product, patent.id, country)
                if a:
                    meta = STATUS_MAP.get(a.status, STATUS_MAP['na'])
                    row += f" {meta['emoji']} {meta['symbol']} |"
                else:
                    row += " — |"
            print(row)
        print()
        
        # Product-specific blockers
        blockers = grid.blockers_for_product(product)
        if blockers:
            print(f"**🔴 Blocker'lar ({product})** — {len(blockers)} adet:")
            for b in blockers:
                print(f"- {b.patent} @ {b.country}: {b.rationale}")
            print()
    
    print(f"\n---\n\n**Ülke bazlı blocker yoğunluğu**:")
    print()
    print("| Ülke | Blocker sayısı |")
    print("|---|---|")
    for country in grid.countries:
        blockers = grid.blockers_for_country(country)
        print(f"| {country} | {len(blockers)} |")
    print()


def print_json_grid(grid: FTOGrid):
    """JSON çıktı."""
    data = {
        "products": grid.products,
        "countries": grid.countries,
        "patents": [asdict(p) for p in grid.patents],
        "assessments": [asdict(a) for a in grid.assessments],
        "status_counts": grid.status_counts(),
    }
    print(json.dumps(data, indent=2, ensure_ascii=False))


def load_grid_from_json(path: str) -> FTOGrid:
    """JSON dosyadan yükle."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    patents = [Patent(**p) for p in data.get('patents', [])]
    assessments = [Assessment(**a) for a in data.get('assessments', [])]
    return FTOGrid(
        products=data.get('products', []),
        countries=data.get('countries', []),
        patents=patents,
        assessments=assessments,
    )


def main():
    parser = argparse.ArgumentParser(description="FTO Grid Otomasyonu v1.7.0")
    parser.add_argument('--example', type=str, help="Örnek: hcv, obesity, biosimilar")
    parser.add_argument('--import', dest='import_path', type=str, help="JSON import")
    parser.add_argument('--format', type=str, default='markdown', choices=['markdown', 'json'])
    parser.add_argument('--list-examples', action='store_true')
    
    args = parser.parse_args()
    
    if not any([args.example, args.import_path, args.list_examples]):
        print()
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║  pharmapatent v1.7.0 — FTO Grid Otomasyonu                        ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print()
        print("Kullanım:")
        print("  --example hcv         HCV DAA jenerik demo")
        print("  --example obesity     GLP-1 jenerik demo")
        print("  --example biosimilar  Adalimumab biyobenzer demo")
        print("  --import data.json    Özel veri yükle")
        print("  --format json         JSON çıktı")
        print("  --list-examples       Mevcut örnekleri listele")
        sys.exit(0)
    
    if args.list_examples:
        print()
        print("Mevcut örnekler:")
        for name, grid in EXAMPLES.items():
            print(f"  {name:<15} {len(grid.products)} ürün × {len(grid.countries)} ülke × {len(grid.patents)} patent = {len(grid.assessments)} değerlendirme")
        return
    
    grid = None
    if args.example:
        if args.example not in EXAMPLES:
            print(f"❌ Bilinmeyen örnek: {args.example}. Mevcut: {list(EXAMPLES.keys())}")
            sys.exit(1)
        grid = EXAMPLES[args.example]
    elif args.import_path:
        grid = load_grid_from_json(args.import_path)
    
    if args.format == 'json':
        print_json_grid(grid)
    else:
        print_markdown_grid(grid)


if __name__ == "__main__":
    main()
