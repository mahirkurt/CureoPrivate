#!/usr/bin/env python3
"""
realworld-evidence-harvester.py — Real-World Evidence Konsolidasyon Çerçevesi

Türkiye + global piyasa verilerini konsolide eden Real-World Evidence (RWE)
özeti üretir. Girdi: ürün + terapötik alan + periyot. Çıktı: RWE özet paketi.

Entegre edilen kaynaklar (referans — bu script harvester/orkestratör, gerçek
scraping yapmaz; ekibin manuel veya API ile topladığı veriyi konsolide eder):

    TÜRKİYE
    ----------
    - SGK Medula reçete + hasta sayısı + yıllık harcama
    - TİTCK onaylı endikasyon + OTC/Reçeteli/Kırmızı reçete durumu
    - IMS Health Türkiye pazar payı + ciro
    - Türkiye Kanser Kayıt Sistemi (onkoloji için)
    - Türkiye DSÖ surveillance (enfeksiyon için)
    
    GLOBAL
    ----------
    - FiercePharma + Endpoints News — ticari gelişmeler
    - FDA FAERS — güvenlik sinyalleri
    - EMA EudraVigilance — AB güvenlik
    - ClinicalTrials.gov ongoing RWE trials
    - Evaluate Pharma — commercial forecasts
    
    PUBLISHED RWE
    ----------
    - PubMed — RWE çalışma literatürü
    - GARDP/WHO surveillance
    - Registry çalışmaları (özellikle CAR-T, gene therapy)

NOT: Bu script konsolidasyon + şablon üretimi içindir. Gerçek veri çekme
için ayrı API client'ları (SGK Medula, FiercePharma RSS, PubMed API, FAERS
API) ekibin sorumluluğundadır.

Kullanım:
    python3 realworld-evidence-harvester.py --example pembrolizumab-tr
    python3 realworld-evidence-harvester.py --example glofitamab-tr
    python3 realworld-evidence-harvester.py --example semaglutide-global
    python3 realworld-evidence-harvester.py --list-sources
    python3 realworld-evidence-harvester.py --template --product "X" --indication "Y"

Yazar: pharmapatent skill v1.8.0
"""

import sys
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import date


# --- Source registry ---

RWE_SOURCES = {
    # Türkiye sources
    "SGK_Medula": {
        "country": "TR",
        "access": "gov_portal / FoIA request",
        "url": "https://medula.sgk.gov.tr/",
        "data_types": ["reçete sayısı", "hasta sayısı", "yıllık harcama", "bölge dağılımı"],
        "lag": "6-12 ay",
        "grain": "molekül × yıl × bölge",
        "cost": "free (resmi başvuru)",
    },
    "TITCK_Ruhsat": {
        "country": "TR",
        "access": "gov_portal",
        "url": "https://www.titck.gov.tr/",
        "data_types": ["ruhsat durumu", "endikasyon", "kırmızı reçete", "fiyat listesi", "SPC değişiklikleri"],
        "lag": "real-time",
        "grain": "ürün",
        "cost": "free",
    },
    "TKDS_Cancer": {
        "country": "TR",
        "access": "TKHK + epidemiology teams",
        "url": "https://hsgm.saglik.gov.tr/tr/kanser",
        "data_types": ["kanser insidansı", "5-yıl sağkalım", "evre dağılımı"],
        "lag": "24-36 ay",
        "grain": "kanser tipi × yaş × bölge",
        "cost": "free",
    },
    "IMS_Turkiye": {
        "country": "TR",
        "access": "commercial license",
        "url": "https://www.iqvia.com/",
        "data_types": ["pazar payı", "ciro", "volume", "rakiplerle karşılaştırma"],
        "lag": "1-3 ay",
        "grain": "molekül × ay × kanal",
        "cost": "subscription ($50-150K/yıl)",
    },
    
    # Global sources
    "FDA_FAERS": {
        "country": "US",
        "access": "open data + FDA API",
        "url": "https://fis.fda.gov/extensions/FPD-QDE-FAERS/",
        "data_types": ["adverse events", "serious AE", "reporter tipi", "medication error"],
        "lag": "1-3 ay",
        "grain": "molekül × quarter",
        "cost": "free",
    },
    "EMA_EudraVigilance": {
        "country": "EU",
        "access": "EMA public access + ADR reporting",
        "url": "https://www.adrreports.eu/",
        "data_types": ["suspected ADR", "signal detection", "geographic distribution"],
        "lag": "2-4 ay",
        "grain": "molekül × quarter × ülke",
        "cost": "free",
    },
    "ClinicalTrials_RWE": {
        "country": "Global",
        "access": "open API",
        "url": "https://clinicaltrials.gov/",
        "data_types": ["ongoing RWE studies", "registry trials", "PASS"],
        "lag": "real-time",
        "grain": "molekül × NCT",
        "cost": "free",
    },
    "FiercePharma": {
        "country": "Global",
        "access": "subscription",
        "url": "https://www.fiercepharma.com/",
        "data_types": ["commercial news", "deal flow", "pricing", "market access"],
        "lag": "1-7 days",
        "grain": "article",
        "cost": "$500-2000/yıl",
    },
    "Endpoints_News": {
        "country": "Global",
        "access": "subscription",
        "url": "https://endpts.com/",
        "data_types": ["pipeline news", "regulatory", "deals", "hiring moves"],
        "lag": "1-3 days",
        "grain": "article",
        "cost": "$500-1500/yıl",
    },
    "Evaluate_Pharma": {
        "country": "Global",
        "access": "commercial license",
        "url": "https://www.evaluate.com/",
        "data_types": ["forecasts", "asset NPVs", "deal values", "revenue projections"],
        "lag": "quarterly",
        "grain": "molekül × year × region",
        "cost": "subscription ($80-200K/yıl)",
    },
    "PubMed_RWE": {
        "country": "Global",
        "access": "NLM API",
        "url": "https://pubmed.ncbi.nlm.nih.gov/",
        "data_types": ["registry studies", "case series", "real-world outcomes"],
        "lag": "publication lag",
        "grain": "paper",
        "cost": "free",
    },
    "SEER_US": {
        "country": "US",
        "access": "registered access",
        "url": "https://seer.cancer.gov/",
        "data_types": ["cancer incidence", "survival", "stage distribution"],
        "lag": "24-36 ay",
        "grain": "kanser tipi × demografi",
        "cost": "free (registered)",
    },
    "GARDP_AMR": {
        "country": "Global",
        "access": "partnership",
        "url": "https://gardp.org/",
        "data_types": ["AMR surveillance", "antibiotic use", "resistance patterns"],
        "lag": "6-12 ay",
        "grain": "organizma × ülke × yıl",
        "cost": "free (partnership)",
    },
}


@dataclass
class RWEDataPoint:
    """Tek bir RWE veri noktası."""
    source: str           # Source key (RWE_SOURCES)
    metric: str           # "patient_count", "market_share", "AE_rate", "5y_survival"
    value: str            # String form for flexibility (can be numeric or categorical)
    date_range: str       # "2023-01 to 2024-12"
    note: str = ""


@dataclass
class RWEPackage:
    product: str
    indication: str
    geography: str        # "TR", "Global", "US", "EU"
    period: str           # "2023-2024"
    data_points: List[RWEDataPoint]
    summary: str = ""
    gaps: List[str] = field(default_factory=list)


# --- Örnek paketler (hipotetik konsolidasyon) ---

EXAMPLES = {
    "pembrolizumab-tr": RWEPackage(
        product="Pembrolizumab (Keytruda) — Merck/MSD",
        indication="NSCLC, Melanom, HNSCC, Hodgkin lenfoma, Mesane (çoklu onay)",
        geography="Türkiye",
        period="2023-01 to 2024-12",
        data_points=[
            RWEDataPoint("SGK_Medula", "reçete sayısı 2024", "~32,500", "2024", "Onkoloji tümör kategorilerinde"),
            RWEDataPoint("SGK_Medula", "hasta sayısı 2024", "~8,200", "2024", "Aktif tedavi gören"),
            RWEDataPoint("SGK_Medula", "yıllık harcama 2024", "₺1.8B (~$55M USD)", "2024", "SGK perspektifi"),
            RWEDataPoint("SGK_Medula", "ortalama tedavi süresi", "11.4 ay", "2024", "Metastatik NSCLC"),
            RWEDataPoint("IMS_Turkiye", "ICI pazar payı", "%48 (volume)", "2024-Q4", "TR ICI sınıfı içinde"),
            RWEDataPoint("IMS_Turkiye", "YoY büyüme", "+%22", "2023→2024", "TR satış büyüme"),
            RWEDataPoint("TKDS_Cancer", "NSCLC insidansı TR", "28,500 yeni vaka/yıl", "2022", "TR Kanser Kayıt"),
            RWEDataPoint("TITCK_Ruhsat", "onaylı endikasyon sayısı", "14", "2024-12", "Multi-indikasyon"),
            RWEDataPoint("FDA_FAERS", "Ciddi AE bildirimleri 2024", "~11,500", "2024", "Global FAERS"),
            RWEDataPoint("FDA_FAERS", "Pnömonit oranı", "%3.8", "2024", "En sık Grade 3+ irAE"),
            RWEDataPoint("EMA_EudraVigilance", "AB içi ADR sayısı", "~8,200", "2024", "Tüm endikasyonlar"),
            RWEDataPoint("ClinicalTrials_RWE", "aktif RWE çalışmaları", "147", "2024-12", "Global, registry + PASS"),
            RWEDataPoint("FiercePharma", "2024 global satış", "$29.5B", "2024", "Merck yıllık rapor"),
            RWEDataPoint("Evaluate_Pharma", "2030 peak forecast", "$35B", "forecast", "Biosimilar öncesi"),
            RWEDataPoint("PubMed_RWE", "son 12 ay yayın (registry/RWE)", "~185", "2023-2024", "NSCLC + melanom ağırlıklı"),
        ],
        summary="Pembrolizumab 2024 Türkiye'de onkoloji ICI pazar lideri (volume %48). SGK harcaması ₺1.8B. Pazar büyümesi güçlü; 2028-2030 biosimilar penceresi öncesi hazırlık dönemi.",
        gaps=[
            "SGK regional breakdown (il bazında) eksik",
            "OS + PFS RWE (TR kohort) yeterli değil — REGISTURK-LUNG gibi yeni registry'ler gerekli",
            "Biyobenzer hazırlık verisi Türkiye'de kısıtlı (Samsung Bioepis + Kashiv + diğer adaylar)",
        ],
    ),
    "glofitamab-tr": RWEPackage(
        product="Glofitamab (Columvi) — Roche",
        indication="Relapsed/refractory DLBCL, 3L+",
        geography="Türkiye",
        period="2024-01 to 2024-12",
        data_points=[
            RWEDataPoint("TITCK_Ruhsat", "TR onay tarihi", "2024-Q2", "2024", "STARGLO Faz III sonrası"),
            RWEDataPoint("SGK_Medula", "hasta sayısı 2024", "~45 (tahmini)", "2024", "Dar endikasyon — 3L+ DLBCL"),
            RWEDataPoint("SGK_Medula", "yıllık harcama 2024", "₺75M (tahmini)", "2024", "Sınırlı pazar; bireysel başvuru ağırlıklı"),
            RWEDataPoint("TITCK_Ruhsat", "kırmızı reçete", "Evet", "2024", "Hematolog reçetesi gerekli"),
            RWEDataPoint("FDA_FAERS", "CRS oranı global", "%47 (any grade) / %4 (Grade 3+)", "2024", "Bispecific sınıf özelliği"),
            RWEDataPoint("ClinicalTrials_RWE", "aktif RWE çalışmaları", "22", "2024-12", "Global STARGLO genişleme"),
            RWEDataPoint("FiercePharma", "2024 global satış", "$385M", "2024", "Roche Q4 raporu"),
            RWEDataPoint("Evaluate_Pharma", "2028 peak forecast", "$1.5B", "forecast", "1L+ expansion potansiyeli"),
            RWEDataPoint("PubMed_RWE", "STARGLO follow-up yayınları", "8", "2024", "Roche sponsored"),
        ],
        summary="Glofitamab 2024'te TR'de dar endikasyon onayı aldı (3L+ DLBCL). SGK bireysel başvuru süreci, hasta sayısı sınırlı (~45). Roche Türkiye malignant hematology portföyünün parçası — Mahir'in doğrudan sorumluluğu altında. 1L+ expansion klinik program STARGLO-2/3 ile devam.",
        gaps=[
            "TR'de CRS yönetim protokolü standardizasyonu gerekli",
            "SGK 1L+ endikasyon genişlemesi için hazırlık (2026-2027)",
            "Roche Türkiye glofitamab registry başlatılmadı — REGISTURK-HEM fırsat",
        ],
    ),
    "semaglutide-global": RWEPackage(
        product="Semaglutide (Ozempic / Wegovy / Rybelsus) — Novo Nordisk",
        indication="T2DM + obezite + CV risk reduction (SELECT)",
        geography="Global",
        period="2023-01 to 2024-12",
        data_points=[
            RWEDataPoint("FiercePharma", "2024 global satış (Ozempic)", "$20.4B", "2024", "Novo Q4 2024"),
            RWEDataPoint("FiercePharma", "2024 global satış (Wegovy)", "$10.6B", "2024", "Obezite"),
            RWEDataPoint("FiercePharma", "2024 global satış (Rybelsus)", "$2.1B", "2024", "Oral T2DM"),
            RWEDataPoint("Evaluate_Pharma", "2030 peak forecast (combined)", "$85B", "forecast", "Novo + paralel generic"),
            RWEDataPoint("FDA_FAERS", "GI AE oranı", "%30-45", "2024", "Bulantı + kusma + ishal"),
            RWEDataPoint("FDA_FAERS", "Pankreatit bildirim", "~1,200", "2024", "Causal link belirsiz"),
            RWEDataPoint("FDA_FAERS", "Tiroid C-cell tümör sinyali", "izleniyor", "2024", "Ratmodelli sinyalin klinik karşılığı tartışmalı"),
            RWEDataPoint("EMA_EudraVigilance", "AB içi ADR", "~45,000", "2024", "Yüksek volume, yüksek exposure"),
            RWEDataPoint("ClinicalTrials_RWE", "aktif RWE + post-marketing", "280+", "2024", "Global (SELECT, SUSTAIN, STEP uzantıları)"),
            RWEDataPoint("SGK_Medula", "TR reçete sayısı 2024", "~195,000 (diyabet)", "2024", "T2DM; obezite off-label ilave"),
            RWEDataPoint("SGK_Medula", "TR yıllık harcama", "₺2.1B (T2DM)", "2024", "SGK perspektifi"),
            RWEDataPoint("PubMed_RWE", "RWE yayın 2024", "~420", "2024", "Kardiyovasküler + obezite + MASH"),
            RWEDataPoint("TITCK_Ruhsat", "TR Wegovy onay", "2024", "2024", "Obezite; SGK kapsam dışı"),
            RWEDataPoint("Endpoints_News", "Compounded versions kontroversi", "aktif 2024", "2024", "FDA DEA tartışmalar"),
        ],
        summary="Semaglutide 2024'te Novo Nordisk'in tek başına tek başına globalde en büyük ilacı ($33B+ kombine). Türkiye'de T2DM hegemonyası güçlü, obezite off-label kullanımı yaygın. Patent expiry 2031-2032 — pre-LOE hazırlık kritik. Oral GLP-1 (orforglipron) + tirzepatide rekabeti artıyor.",
        gaps=[
            "Long-term CV outcome data TR kohort eksik (SELECT TR alt-grup)",
            "Obezite off-label TR kullanımının gerçek hacmi belirsiz (cepten alım)",
            "MASH + CKD endikasyon genişleme RWE çalışmaları devam",
        ],
    ),
}


# --- Çıktı fonksiyonları ---

def print_package_report(pkg: RWEPackage):
    print()
    print("═" * 90)
    print(f"  REAL-WORLD EVIDENCE PAKETİ")
    print("═" * 90)
    print(f"  Ürün: {pkg.product}")
    print(f"  Endikasyon: {pkg.indication}")
    print(f"  Coğrafya: {pkg.geography}")
    print(f"  Periyot: {pkg.period}")
    print(f"  Veri noktası: {len(pkg.data_points)}")
    print()
    
    # Source dağılımı
    source_counts = {}
    for dp in pkg.data_points:
        source_counts[dp.source] = source_counts.get(dp.source, 0) + 1
    
    print(f"  ┌─ KAYNAK DAĞILIMI ───────────────────────────────────────────┐")
    for src, count in sorted(source_counts.items(), key=lambda x: -x[1]):
        src_info = RWE_SOURCES.get(src, {})
        country = src_info.get('country', '?')
        print(f"  │  [{country}] {src:<30} {count} veri noktası")
    print(f"  └──────────────────────────────────────────────────────────────┘")
    print()
    
    print(f"  ┌─ VERİ NOKTALARI ────────────────────────────────────────────┐")
    for i, dp in enumerate(pkg.data_points, 1):
        src_info = RWE_SOURCES.get(dp.source, {})
        country = src_info.get('country', '?')
        print(f"  │  {i:2}. [{country}] {dp.source}")
        print(f"  │      Metrik: {dp.metric}")
        print(f"  │      Değer:  {dp.value}")
        print(f"  │      Tarih:  {dp.date_range}")
        if dp.note:
            print(f"  │      Not:    {dp.note}")
        print(f"  │")
    print(f"  └──────────────────────────────────────────────────────────────┘")
    print()
    
    if pkg.summary:
        print(f"  ┌─ ÖZET ──────────────────────────────────────────────────────┐")
        for line in wrap_text(pkg.summary, 68):
            print(f"  │  {line}")
        print(f"  └──────────────────────────────────────────────────────────────┘")
        print()
    
    if pkg.gaps:
        print(f"  ┌─ VERİ BOŞLUKLARI (Identified Gaps) ─────────────────────────┐")
        for g in pkg.gaps:
            print(f"  │  ⚠ {g}")
        print(f"  └──────────────────────────────────────────────────────────────┘")
        print()


def wrap_text(text: str, width: int) -> List[str]:
    words = text.split()
    lines = []
    current = []
    current_len = 0
    for w in words:
        if current_len + len(w) + 1 > width:
            lines.append(" ".join(current))
            current = [w]
            current_len = len(w)
        else:
            current.append(w)
            current_len += len(w) + 1
    if current:
        lines.append(" ".join(current))
    return lines


def print_markdown_report(pkg: RWEPackage):
    print()
    print(f"# RWE Paketi — {pkg.product}")
    print()
    print(f"**Endikasyon**: {pkg.indication}")
    print(f"**Coğrafya**: {pkg.geography}")
    print(f"**Periyot**: {pkg.period}")
    print(f"**Veri noktası**: {len(pkg.data_points)}")
    print()
    
    # Data points by source
    by_source = {}
    for dp in pkg.data_points:
        by_source.setdefault(dp.source, []).append(dp)
    
    print("## Veri Noktaları (kaynak bazlı)")
    print()
    for src, dps in by_source.items():
        src_info = RWE_SOURCES.get(src, {})
        country = src_info.get('country', '?')
        print(f"### {src} [{country}]")
        print()
        print("| Metrik | Değer | Tarih | Not |")
        print("|---|---|---|---|")
        for dp in dps:
            note = dp.note.replace("|", "/") if dp.note else ""
            print(f"| {dp.metric} | {dp.value} | {dp.date_range} | {note} |")
        print()
    
    if pkg.summary:
        print("## Özet")
        print()
        print(pkg.summary)
        print()
    
    if pkg.gaps:
        print("## Tespit Edilen Veri Boşlukları")
        print()
        for g in pkg.gaps:
            print(f"- {g}")
        print()


def print_source_directory():
    print()
    print("═" * 100)
    print("  RWE KAYNAK DİZİNİ — pharmapatent v1.8.0")
    print("═" * 100)
    
    # Group by country
    by_country = {}
    for name, info in RWE_SOURCES.items():
        by_country.setdefault(info['country'], []).append((name, info))
    
    for country in sorted(by_country.keys()):
        print(f"\n  {country}:")
        for name, info in by_country[country]:
            print(f"    {name}")
            print(f"      URL: {info['url']}")
            print(f"      Erişim: {info['access']}")
            print(f"      Veri tipleri: {', '.join(info['data_types'])}")
            print(f"      Gecikme: {info['lag']}  ·  Granularite: {info['grain']}  ·  Maliyet: {info['cost']}")


def print_empty_template(product: str, indication: str):
    """Boş şablon üret."""
    print()
    print(f"# RWE Paketi (ŞABLON) — {product}")
    print()
    print(f"**Endikasyon**: {indication}")
    print(f"**Coğrafya**: [TR / Global / US / EU]")
    print(f"**Periyot**: [YYYY-YYYY]")
    print()
    print("## Toplanacak Veri Noktaları")
    print()
    print("### Türkiye")
    print("- [ ] SGK Medula — reçete sayısı, hasta sayısı, yıllık harcama")
    print("- [ ] TİTCK — ruhsat durumu, endikasyon listesi, fiyat")
    print("- [ ] IMS Turkey — pazar payı, ciro trendi")
    print("- [ ] TR Kanser Kayıt (onkoloji ise) — insidans, sağkalım")
    print()
    print("### Global")
    print("- [ ] FiercePharma — ticari gelişmeler, global ciro")
    print("- [ ] Endpoints News — pipeline, regülatör, dealler")
    print("- [ ] FDA FAERS — AE sinyalleri")
    print("- [ ] EMA EudraVigilance — AB ADR")
    print("- [ ] ClinicalTrials.gov — aktif RWE çalışmaları")
    print("- [ ] Evaluate Pharma — forecast")
    print("- [ ] PubMed — registry + RWE yayınları")
    print()
    print("## Bilinen Boşluklar (a priori)")
    print("- [ ] TR regional breakdown")
    print("- [ ] Uzun dönem outcome data")
    print("- [ ] Combination therapy RWE")
    print()


def main():
    parser = argparse.ArgumentParser(description="RWE Harvester v1.8.0")
    parser.add_argument('--example', type=str)
    parser.add_argument('--format', default='ascii', choices=['ascii', 'markdown', 'json'])
    parser.add_argument('--list-examples', action='store_true')
    parser.add_argument('--list-sources', action='store_true')
    parser.add_argument('--template', action='store_true')
    parser.add_argument('--product', type=str, default="[Ürün]")
    parser.add_argument('--indication', type=str, default="[Endikasyon]")
    
    args = parser.parse_args()
    
    if args.list_sources:
        print_source_directory()
        return
    
    if args.list_examples:
        print("\nMevcut örnek RWE paketleri:")
        for name, pkg in EXAMPLES.items():
            print(f"  {name:<25} {pkg.product[:60]}")
        return
    
    if args.template:
        print_empty_template(args.product, args.indication)
        return
    
    if not args.example:
        print()
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║  pharmapatent v1.8.0 — RWE Harvester (SGK+IMS+FiercePharma)       ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print()
        print("Kullanım:")
        print("  --example pembrolizumab-tr   Pembrolizumab TR RWE")
        print("  --example glofitamab-tr      Glofitamab Roche TR RWE")
        print("  --example semaglutide-global Semaglutide global RWE")
        print("  --list-sources               Tüm RWE kaynakları")
        print("  --template --product X --indication Y  Boş şablon üret")
        print("  --format ascii|markdown|json")
        return
    
    if args.example not in EXAMPLES:
        print(f"❌ Bilinmeyen örnek: {args.example}")
        sys.exit(1)
    
    pkg = EXAMPLES[args.example]
    
    if args.format == 'json':
        data = {"package": asdict(pkg), "sources_used": list(set(dp.source for dp in pkg.data_points))}
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif args.format == 'markdown':
        print_markdown_report(pkg)
    else:
        print_package_report(pkg)


if __name__ == "__main__":
    main()
