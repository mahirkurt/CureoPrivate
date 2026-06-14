#!/usr/bin/env python3
"""
kol-graph.py — KOL (Key Opinion Leader) + Araştırmacı Network Grafiği

Bir terapötik alan için KOL ağını, klinik araştırma partnershiplerini, ortak
yayınları, merkez ilişkilerini network grafiği olarak inşa eder. Çıktı: Mermaid
network + JSON + centrality metrikleri.

Network özellikleri:
    - Düğümler: KOL'ler (isim + merkez + uzmanlık)
    - Kenarlar: co-authorship (PubMed), co-PI (ClinicalTrials.gov), same-center
    - Centrality: degree, betweenness (manuel yaklaşım)
    - Kümeleme: merkez bazlı, şehir bazlı

Kullanım:
    python3 kol-graph.py --example turkish_ms      # Türkiye MS KOL
    python3 kol-graph.py --example turkish_onco    # Türkiye onkoloji KOL
    python3 kol-graph.py --example glp1_investigators  # GLP-1 klinik araştırmacıları
    python3 kol-graph.py --import kol_data.json
    python3 kol-graph.py --format mermaid          # Mermaid graph çıktı
    python3 kol-graph.py --format json             # JSON
    python3 kol-graph.py --format markdown         # centrality tablosu

Yazar: pharmapatent skill v1.7.0
Bağımlılık: standart kütüphane (networkx opsiyonel)
"""

import sys
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Set, Tuple
from collections import defaultdict


@dataclass
class KOL:
    id: str
    name: str
    title: str       # Prof. Dr. / Doç. Dr. / Dr.
    center: str
    city: str
    specialty: str
    subspecialty: str = ""
    aktif_trials: int = 0
    publications_5y: int = 0


@dataclass
class Collaboration:
    from_kol: str    # KOL.id
    to_kol: str      # KOL.id
    type: str        # co_author / co_pi / steering_committee / advisory_board / same_center
    weight: int = 1  # ortak yayın/çalışma sayısı
    note: str = ""


@dataclass
class KOLGraph:
    domain: str
    kols: List[KOL]
    collaborations: List[Collaboration]
    
    def node_count(self) -> int:
        return len(self.kols)
    
    def edge_count(self) -> int:
        return len(self.collaborations)
    
    def degree_centrality(self) -> Dict[str, int]:
        deg = defaultdict(int)
        for c in self.collaborations:
            deg[c.from_kol] += c.weight
            deg[c.to_kol] += c.weight
        return dict(deg)
    
    def weighted_centrality(self) -> Dict[str, int]:
        """Co-authorship ağırlıklı + klinik çalışma bonus."""
        centrality = defaultdict(int)
        kol_map = {k.id: k for k in self.kols}
        
        for c in self.collaborations:
            # Kenar tipi ağırlığı
            type_weights = {
                'co_author': 1,
                'co_pi': 3,            # Klinik araştırma ortaklığı daha değerli
                'steering_committee': 5,
                'advisory_board': 2,
                'same_center': 0.5,
            }
            w = type_weights.get(c.type, 1) * c.weight
            centrality[c.from_kol] += w
            centrality[c.to_kol] += w
        
        # Bonus: aktif trials ve yayın sayısı
        for k in self.kols:
            centrality[k.id] += k.aktif_trials * 2
            centrality[k.id] += k.publications_5y * 0.1
        
        return {k: round(v, 1) for k, v in centrality.items()}
    
    def center_clusters(self) -> Dict[str, List[KOL]]:
        clusters = defaultdict(list)
        for k in self.kols:
            clusters[k.center].append(k)
        return dict(clusters)
    
    def city_clusters(self) -> Dict[str, List[KOL]]:
        clusters = defaultdict(list)
        for k in self.kols:
            clusters[k.city].append(k)
        return dict(clusters)


# --- Örnek veri ---

EXAMPLES = {
    "turkish_ms": KOLGraph(
        domain="Türkiye Multipl Skleroz KOL (hipotetik network)",
        kols=[
            KOL("k1", "A. Yılmaz", "Prof. Dr.", "İstanbul Üniversitesi Tıp", "İstanbul", "Nöroloji", "MS", 5, 85),
            KOL("k2", "M. Demir", "Prof. Dr.", "Hacettepe Üniversitesi Tıp", "Ankara", "Nöroloji", "MS", 4, 72),
            KOL("k3", "E. Kaya", "Prof. Dr.", "Ege Üniversitesi Tıp", "İzmir", "Nöroloji", "MS + NMOSD", 3, 48),
            KOL("k4", "F. Özkan", "Doç. Dr.", "Dokuz Eylül Üniversitesi", "İzmir", "Nöroloji", "MS", 2, 35),
            KOL("k5", "N. Çelik", "Prof. Dr.", "Ankara Üniversitesi Tıp", "Ankara", "Nöroloji", "MS + pediatrik MS", 3, 58),
            KOL("k6", "T. Aydın", "Doç. Dr.", "Marmara Üniversitesi", "İstanbul", "Nöroloji", "MS + BTK inhibitör trials", 4, 40),
            KOL("k7", "S. Koç", "Prof. Dr.", "Karadeniz Teknik Üniversitesi", "Trabzon", "Nöroloji", "MS", 1, 22),
            KOL("k8", "B. Yıldız", "Dr.", "VKV Amerikan Hastanesi", "İstanbul", "Nöroloji", "MS + klinik araştırma", 3, 30),
        ],
        collaborations=[
            Collaboration("k1", "k2", "co_author", 12, "MS klinik kılavuz"),
            Collaboration("k1", "k6", "same_center", 1, "İstanbul"),
            Collaboration("k1", "k8", "same_center", 1, "İstanbul"),
            Collaboration("k1", "k3", "steering_committee", 1, "Ocrevus Türkiye registry"),
            Collaboration("k1", "k5", "advisory_board", 2, "Novartis + Roche AB"),
            Collaboration("k2", "k5", "same_center", 1, "Ankara"),
            Collaboration("k2", "k3", "co_pi", 3, "BTK inhibitör Faz III"),
            Collaboration("k2", "k7", "co_author", 4, "Epidemiology paper"),
            Collaboration("k3", "k4", "same_center", 1, "İzmir"),
            Collaboration("k3", "k6", "co_pi", 2, "Multi-center tolebrutinib"),
            Collaboration("k5", "k6", "co_author", 5, "Pediatric MS"),
            Collaboration("k6", "k8", "same_center", 1, "İstanbul"),
            Collaboration("k1", "k7", "co_author", 2, ""),
            Collaboration("k2", "k6", "co_author", 3, ""),
        ],
    ),
    "turkish_onco": KOLGraph(
        domain="Türkiye Onkoloji KOL (hipotetik, solid tumor odaklı)",
        kols=[
            KOL("o1", "H. Arslan", "Prof. Dr.", "İstanbul Üniversitesi Onkoloji Enstitüsü", "İstanbul", "Tıbbi Onkoloji", "Meme kanseri + ADC", 6, 95),
            KOL("o2", "D. Şimşek", "Prof. Dr.", "Hacettepe Onkoloji Enstitüsü", "Ankara", "Tıbbi Onkoloji", "Akciğer kanseri", 5, 88),
            KOL("o3", "O. Güneş", "Prof. Dr.", "Ege Onkoloji", "İzmir", "Tıbbi Onkoloji", "GI + gastric", 4, 62),
            KOL("o4", "M. Tekin", "Prof. Dr.", "Memorial Sağlık Grubu", "İstanbul", "Tıbbi Onkoloji", "Meme + jinekolojik", 5, 55),
            KOL("o5", "A. Öztürk", "Doç. Dr.", "Dokuz Eylül Onkoloji", "İzmir", "Tıbbi Onkoloji", "Melanom + ICI", 3, 42),
            KOL("o6", "İ. Yalçın", "Prof. Dr.", "Ankara Üniversitesi Onkoloji", "Ankara", "Tıbbi Onkoloji", "Ürolojik kanserler", 3, 50),
            KOL("o7", "Ç. Polat", "Dr.", "Acıbadem Hastanesi", "İstanbul", "Tıbbi Onkoloji", "Faz I trial unit lideri", 8, 40),
            KOL("o8", "Z. Yavuz", "Prof. Dr.", "Çukurova Üniversitesi", "Adana", "Tıbbi Onkoloji", "Akciğer + baş-boyun", 2, 35),
        ],
        collaborations=[
            Collaboration("o1", "o4", "same_center", 1, "İstanbul meme kanseri"),
            Collaboration("o1", "o7", "same_center", 1, "İstanbul"),
            Collaboration("o1", "o2", "co_pi", 4, "T-DXd DESTINY programı TR koleji"),
            Collaboration("o1", "o3", "co_author", 8, "Gastrik ADC çalışmaları"),
            Collaboration("o1", "o4", "steering_committee", 2, "TR meme kanseri consensus"),
            Collaboration("o2", "o8", "co_pi", 5, "Pembrolizumab NSCLC"),
            Collaboration("o2", "o5", "co_author", 6, "ICI safety paper"),
            Collaboration("o3", "o6", "co_author", 3, ""),
            Collaboration("o4", "o7", "same_center", 1, "İstanbul private"),
            Collaboration("o4", "o2", "advisory_board", 2, "Enhertu advisory"),
            Collaboration("o5", "o8", "co_pi", 2, "Melanom Faz III"),
            Collaboration("o6", "o2", "same_center", 1, "Ankara onkoloji"),
            Collaboration("o7", "o1", "steering_committee", 1, "Faz I hub İstanbul"),
            Collaboration("o7", "o4", "co_pi", 3, "Early phase trials"),
        ],
    ),
    "glp1_investigators": KOLGraph(
        domain="Global GLP-1 Klinik Araştırmacıları (hipotetik SURMOUNT + SELECT)",
        kols=[
            KOL("g1", "R. Martinez", "Prof. MD", "Mayo Clinic", "Rochester USA", "Endocrinology", "Obesity + T2DM", 6, 120),
            KOL("g2", "S. Larsen", "Prof. MD PhD", "Copenhagen University", "Copenhagen DK", "Endocrinology", "GLP-1 mekanizma", 4, 98),
            KOL("g3", "T. Mitchell", "Prof. MD", "Novo Nordisk Foundation", "Copenhagen DK", "Endocrinology", "SELECT PI", 5, 85),
            KOL("g4", "L. Wharton", "MD", "Gateway Medical", "Ontario CA", "Obesity medicine", "SURMOUNT PI", 7, 45),
            KOL("g5", "A. Yılmaz", "Prof. Dr.", "Hacettepe Tıp", "Ankara TR", "Endocrinology", "TR site PI", 3, 30),
            KOL("g6", "K. Chen", "Prof. MD", "Peking Union Medical", "Beijing CN", "Endocrinology", "Chinese pop trials", 4, 55),
        ],
        collaborations=[
            Collaboration("g1", "g2", "co_author", 15, "GLP-1 mekanizma reviews"),
            Collaboration("g1", "g3", "steering_committee", 1, "SELECT steering"),
            Collaboration("g1", "g4", "co_pi", 3, "SURMOUNT global"),
            Collaboration("g2", "g3", "same_center", 1, "Copenhagen"),
            Collaboration("g3", "g4", "steering_committee", 1, "Global obesity consortium"),
            Collaboration("g4", "g5", "co_pi", 1, "TR site SURMOUNT"),
            Collaboration("g5", "g6", "co_author", 2, "Asian population MS obesity"),
            Collaboration("g6", "g1", "advisory_board", 2, "Novo advisory China"),
        ],
    ),
}


def print_mermaid(graph: KOLGraph):
    """Mermaid flowchart LR syntax."""
    print()
    print(f"## KOL Graph — {graph.domain}")
    print()
    print("```mermaid")
    print("flowchart LR")
    print()
    
    # City-based subgraphs
    cities = graph.city_clusters()
    for city, city_kols in cities.items():
        safe_city = city.replace(' ', '_').replace('İ', 'I').replace('Ç', 'C')
        print(f"    subgraph {safe_city}[{city}]")
        for k in city_kols:
            label = f"{k.name}<br/>{k.center[:30]}<br/><i>{k.subspecialty}</i>"
            print(f"        {k.id}[\"{label}\"]")
        print(f"    end")
        print()
    
    # Edges
    type_styles = {
        'co_author': '-.->|co-author|',
        'co_pi': '==>|co-PI|',
        'steering_committee': '==>|steering|',
        'advisory_board': '-->|AB|',
        'same_center': '---',
    }
    
    for c in graph.collaborations:
        style = type_styles.get(c.type, '-->')
        if c.type == 'same_center':
            continue  # Aynı subgraph zaten cluster
        weight_label = f"{c.weight}" if c.weight > 1 else ""
        print(f"    {c.from_kol} {style} {c.to_kol}")
    
    # Centrality-based styling
    centrality = graph.weighted_centrality()
    if centrality:
        top_kol = max(centrality, key=centrality.get)
        print(f"    classDef top fill:#0f62fe,stroke:#0043ce,color:#fff,stroke-width:2px")
        print(f"    class {top_kol} top")
    
    print("```")
    print()


def print_markdown_report(graph: KOLGraph):
    """Markdown centrality raporu."""
    print()
    print(f"# KOL Network — {graph.domain}")
    print()
    print(f"**Düğüm**: {graph.node_count()} KOL · **Kenar**: {graph.edge_count()} işbirliği")
    print()
    
    # Centrality ranking
    centrality = graph.weighted_centrality()
    kol_map = {k.id: k for k in graph.kols}
    
    print("## Weighted Centrality Rankings")
    print()
    print("| Rank | KOL | Merkez | Şehir | Aktif Trial | 5y Publ. | Centrality |")
    print("|---|---|---|---|---|---|---|")
    sorted_kols = sorted(centrality.items(), key=lambda x: -x[1])
    for rank, (kol_id, score) in enumerate(sorted_kols, 1):
        k = kol_map[kol_id]
        print(f"| {rank} | {k.title} {k.name} | {k.center} | {k.city} | {k.aktif_trials} | {k.publications_5y} | **{score:.1f}** |")
    print()
    
    # Merkez dağılımı
    centers = graph.center_clusters()
    print("## Merkez Dağılımı")
    print()
    print("| Merkez | KOL sayısı |")
    print("|---|---|")
    for center, ks in sorted(centers.items(), key=lambda x: -len(x[1])):
        print(f"| {center} | {len(ks)} |")
    print()
    
    # Şehir dağılımı
    cities = graph.city_clusters()
    print("## Şehir Dağılımı")
    print()
    print("| Şehir | KOL sayısı |")
    print("|---|---|")
    for city, ks in sorted(cities.items(), key=lambda x: -len(x[1])):
        print(f"| {city} | {len(ks)} |")
    print()
    
    # İşbirliği tipi dağılımı
    type_counts = defaultdict(int)
    for c in graph.collaborations:
        type_counts[c.type] += 1
    
    print("## İşbirliği Tipi Dağılımı")
    print()
    print("| Tip | Adet |")
    print("|---|---|")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"| {t} | {c} |")
    print()


def print_json(graph: KOLGraph):
    data = {
        "domain": graph.domain,
        "kols": [asdict(k) for k in graph.kols],
        "collaborations": [asdict(c) for c in graph.collaborations],
        "centrality": graph.weighted_centrality(),
        "metrics": {
            "node_count": graph.node_count(),
            "edge_count": graph.edge_count(),
            "cities": list(graph.city_clusters().keys()),
        },
    }
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="KOL Graph Builder v1.7.0")
    parser.add_argument('--example', type=str, help="Örnek: turkish_ms, turkish_onco, glp1_investigators")
    parser.add_argument('--import', dest='import_path', type=str)
    parser.add_argument('--format', default='mermaid', choices=['mermaid', 'markdown', 'json'])
    parser.add_argument('--list-examples', action='store_true')
    
    args = parser.parse_args()
    
    if args.list_examples:
        print("\nMevcut örnekler:")
        for name, g in EXAMPLES.items():
            print(f"  {name:<25} {g.node_count()} KOL, {g.edge_count()} işbirliği")
        return
    
    if not args.example and not args.import_path:
        print()
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║  pharmapatent v1.7.0 — KOL Graph Builder                          ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print()
        print("Kullanım:")
        print("  --example turkish_ms              Türkiye MS KOL")
        print("  --example turkish_onco            Türkiye Onkoloji KOL")
        print("  --example glp1_investigators      Global GLP-1 araştırmacıları")
        print("  --format mermaid | markdown | json")
        sys.exit(0)
    
    graph = None
    if args.example:
        if args.example not in EXAMPLES:
            print(f"❌ Bilinmeyen örnek: {args.example}")
            sys.exit(1)
        graph = EXAMPLES[args.example]
    elif args.import_path:
        with open(args.import_path) as f:
            data = json.load(f)
        kols = [KOL(**k) for k in data['kols']]
        collaborations = [Collaboration(**c) for c in data['collaborations']]
        graph = KOLGraph(domain=data.get('domain', ''), kols=kols, collaborations=collaborations)
    
    if args.format == 'json':
        print_json(graph)
    elif args.format == 'markdown':
        print_markdown_report(graph)
    else:
        print_mermaid(graph)


if __name__ == "__main__":
    main()
