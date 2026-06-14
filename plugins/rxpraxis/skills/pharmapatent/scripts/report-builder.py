#!/usr/bin/env python3
"""
report-builder.py — Pharmapatent Rapor Otomasyon Orkestratörü

rapor-sablonlari.md'deki 10 rapor tipini + visualize-widget-kutuphanesi.md'deki
33 SVG/Mermaid şablonunu + carbon-html-report skill entegrasyonunu birleştirerek
tam rapor iskeleti üretir.

Kullanım:
    python3 report-builder.py --type fto --asset "atorvastatin 40mg" --out report.md
    python3 report-builder.py --type invalidity --asset "pembrolizumab" --out report.md
    python3 report-builder.py --list-types
    python3 report-builder.py --example

Rapor tipleri:
    fto                FTO (Faaliyet Serbestisi) Raporu
    invalidity         Invalidity Briefing
    landscape          Landscape Raporu
    lifecycle          Lifecycle Yol Haritası
    regulatory         Pazara Giriş Takvimi
    litigation         Litigation Briefing
    dd                 Due Diligence Report
    opposition         Opposition Briefing
    biosimilar         Biosimilar Pathway Briefing
    licensing          License Negotiation Memo
    expert_witness     FSHHM Bilirkişi Rapor Taslağı

Her rapor tipi için:
- İskelet bölümler (rapor-sablonlari.md'den)
- Zorunlu görsel yer tutucular (visualize-widget-kutuphanesi.md'den)
- Compliance bölümü (compliance-beyanlari.md'den)
- Hedef kitle varyantı (Technical / Executive / Legal)

Yazar: pharmapatent skill v1.6.0
Lisans: Internal use.
Bağımlılık: standart kütüphane
"""

import sys
import json
import argparse
from datetime import date
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


# --- Rapor tipi + bölüm tanımları ---

REPORT_TYPES = {
    "fto": {
        "name": "FTO Raporu (Faaliyet Serbestisi)",
        "template_section": "rapor-sablonlari.md §1",
        "required_visuals": [
            "fto-patent-country-heatmap",
            "fto-feature-matrix",
            "fto-design-around-tree",
            "fto-loe-gantt",
        ],
        "sections": [
            ("yonetici_ozeti", "Yönetici Özeti"),
            ("kapsam", "Kapsam ve Metodoloji"),
            ("urun_profili", "Ürün Profili"),
            ("patent_taramasi", "Patent Tarama Sonuçları"),
            ("istem_analizi", "İstem Analizi Matrisi"),
            ("risk_degerlendirme", "Risk Değerlendirmesi"),
            ("design_around", "Design-Around Seçenekleri"),
            ("rezidüel_risk", "Rezidüel Risk Beyanı"),
            ("sonuc_oneri", "Sonuç ve Öneriler"),
            ("compliance", "Compliance Beyanları"),
        ],
        "audience_default": "Legal",
        "relevant_scripts": ["loe-calculator.py", "claim-parser.py", "family-tracer.py"],
    },
    "invalidity": {
        "name": "Invalidity Briefing",
        "template_section": "rapor-sablonlari.md §2",
        "required_visuals": [
            "invalidity-mosaic",
            "invalidity-radar",
            "invalidity-citation-network",
            "invalidity-forum-tree",
        ],
        "sections": [
            ("yonetici_ozeti", "Yönetici Özeti"),
            ("hedef_patent", "Hedef Patent Profili"),
            ("hedeflenen_istemler", "Hedeflenen İstemler"),
            ("saldiri_vektorleri", "Saldırı Vektörleri (Yenilik, Buluş Basamağı, Yeterli Açıklama)"),
            ("prior_art", "Prior Art Delilleri"),
            ("mozaik_analiz", "Mozaik Tablosu (Yenilik Analizi)"),
            ("problem_cozum", "Problem-Solution Analizi (Buluş Basamağı)"),
            ("forum_secimi", "Forum Seçimi + Stratejisi"),
            ("maliyet_takvim", "Maliyet + Takvim"),
            ("compliance", "Compliance Beyanları"),
        ],
        "audience_default": "Legal",
        "relevant_scripts": ["claim-parser.py", "priority-date-matrix.py"],
    },
    "landscape": {
        "name": "Landscape Raporu",
        "template_section": "rapor-sablonlari.md §3",
        "required_visuals": [
            "landscape-filing-trend",
            "landscape-assignee-bar",
            "landscape-geo-choropleth",
            "landscape-evergreening-timeline",
        ],
        "sections": [
            ("yonetici_ozeti", "Yönetici Özeti"),
            ("teknoloji_alani", "Teknoloji Alanı Tanımı"),
            ("arama_stratejisi", "Arama Stratejisi"),
            ("yillik_trend", "Yıllık Başvuru Trendi"),
            ("assignee_analizi", "Assignee + Konsantrasyon Analizi"),
            ("cografya", "Coğrafi Dağılım"),
            ("white_space", "White Space (Boş Alan) Analizi"),
            ("rakip_porfoyu", "Rakip Portföy Derinliği"),
            ("emerging_signals", "Emerging Signals + Forecast"),
            ("oneriler", "Stratejik Öneriler"),
            ("compliance", "Compliance Beyanları"),
        ],
        "audience_default": "Executive",
        "relevant_scripts": ["cpc-recommender.py", "family-tracer.py"],
    },
    "lifecycle": {
        "name": "Lifecycle Yol Haritası",
        "template_section": "rapor-sablonlari.md §4",
        "required_visuals": [
            "lifecycle-gantt",
            "lifecycle-erosion",
            "lifecycle-quadrant",
        ],
        "sections": [
            ("yonetici_ozeti", "Yönetici Özeti"),
            ("asset_mevcut", "Asset Mevcut Durum"),
            ("patent_durumu", "Patent Portföy Durumu"),
            ("loe_projeksyonu", "LOE Projeksyonu"),
            ("lifecycle_stratejileri", "Lifecycle Stratejileri"),
            ("yeni_endikasyonlar", "Yeni Endikasyon Genişletme"),
            ("formulasyon_cihaz", "Yeni Formülasyon + Cihaz"),
            ("kombinasyon", "Kombinasyon Ürün Stratejileri"),
            ("gelir_erozyonu", "Gelir Erozyonu Projeksiyonu"),
            ("oneriler", "Stratejik Öneriler"),
            ("compliance", "Compliance Beyanları"),
        ],
        "audience_default": "Executive",
        "relevant_scripts": ["loe-calculator.py", "royalty-calculator.py"],
    },
    "regulatory": {
        "name": "Pazara Giriş Takvimi",
        "template_section": "rapor-sablonlari.md §5",
        "required_visuals": [
            "fto-loe-gantt",
            "launch-max-formula",
        ],
        "sections": [
            ("yonetici_ozeti", "Yönetici Özeti"),
            ("referans_urun", "Referans Ürün Profili"),
            ("patent_engel", "Patent Engel Analizi"),
            ("veri_imtiyazi", "Veri İmtiyazı"),
            ("max_formul", "LOE MAX Formülü Uygulaması"),
            ("bolar_takvimi", "Bolar Dönemi (SMK m.85/3)"),
            ("ruhsat_stratejisi", "Ruhsat Stratejisi (TİTCK)"),
            ("sgk_fiyat", "SGK Fiyatlandırma + Geri Ödeme"),
            ("pazara_giris", "Praktik Pazara Giriş Tarihi"),
            ("compliance", "Compliance Beyanları"),
        ],
        "audience_default": "Executive",
        "relevant_scripts": ["loe-calculator.py", "spc-calculator.py"],
    },
    "litigation": {
        "name": "Litigation Briefing",
        "template_section": "rapor-sablonlari.md §6",
        "required_visuals": [
            "litigation-decision-tree",
            "litigation-cost-curve",
            "litigation-forum-matrix",
        ],
        "sections": [
            ("yonetici_ozeti", "Yönetici Özeti"),
            ("dava_arkaplani", "Dava Arka Planı"),
            ("taraflar_talepler", "Taraflar + Talepler"),
            ("forum_secimi", "Forum Seçimi (FSHHM/Ankara/AB)"),
            ("ihtiyati_tedbir", "İhtiyati Tedbir Stratejisi"),
            ("teknik_deliller", "Teknik Delil + Bilirkişi Hazırlığı"),
            ("tazminat_hesabi", "SMK m.151 Tazminat Hesabı"),
            ("zaman_maliyet", "Zaman + Maliyet Projeksiyonu"),
            ("settlement", "Settlement Değerlendirmesi"),
            ("compliance", "Compliance Beyanları"),
        ],
        "audience_default": "Legal",
        "relevant_scripts": ["royalty-calculator.py"],
    },
    "dd": {
        "name": "Due Diligence Report (M&A)",
        "template_section": "rapor-sablonlari.md §7",
        "required_visuals": [
            "fto-patent-country-heatmap",
            "dd-radar",
            "dd-montecarlo",
            "dd-tornado",
        ],
        "sections": [
            ("yonetici_ozeti", "Yönetici Özeti"),
            ("target_profili", "Target Şirket Profili"),
            ("asset_envanteri", "Asset Envanteri"),
            ("patent_portfoyu", "Patent Portföy Kuvveti"),
            ("klinik_veri", "Klinik Veri Değerlendirmesi"),
            ("regulatory_path", "Regülatör Yol Durumu"),
            ("finansal_degerleme", "Finansal Değerleme"),
            ("monte_carlo", "Monte Carlo Risk Analizi"),
            ("duyarlilik", "Duyarlılık Analizi (Tornado)"),
            ("hukuki_riskler", "Hukuki Riskler + Litigation Exposure"),
            ("oneriler", "Deal Önerisi"),
            ("compliance", "Compliance Beyanları"),
        ],
        "audience_default": "Executive",
        "relevant_scripts": ["royalty-calculator.py", "family-tracer.py", "priority-date-matrix.py"],
    },
    "opposition": {
        "name": "Opposition Briefing (EPO)",
        "template_section": "rapor-sablonlari.md §8",
        "required_visuals": [
            "opposition-art100-map",
            "opposition-problem-solution",
            "opposition-timeline",
        ],
        "sections": [
            ("yonetici_ozeti", "Yönetici Özeti"),
            ("forum_sure", "Forum ve Süre Analizi (9 ay penceresi)"),
            ("hedef_patent", "Hedef Patent Profili"),
            ("hedeflenen_istemler", "Hedeflenen İstemler"),
            ("epc_art100", "EPC Art. 100 Bazında Gerekçe Haritası"),
            ("prior_art", "Prior Art Delilleri"),
            ("karsi_argumanlar", "Muhtemel Karşı Argümanlar"),
            ("oral_hazirlik", "Oral Proceedings Hazırlığı"),
            ("koordinasyon", "Çok-Opposition Koordinasyonu"),
            ("maliyet", "Maliyet Projeksiyonu"),
            ("compliance", "Compliance Beyanları"),
        ],
        "audience_default": "Legal",
        "relevant_scripts": ["claim-parser.py", "priority-date-matrix.py"],
    },
    "biosimilar": {
        "name": "Biosimilar Pathway Briefing",
        "template_section": "rapor-sablonlari.md §9",
        "required_visuals": [
            "biosimilar-multi-gantt",
            "biosimilar-sankey",
            "biosimilar-market-share",
            "biosimilar-launch-calendar",
        ],
        "sections": [
            ("yonetici_ozeti", "Yönetici Özeti"),
            ("referans_urun", "Referans Ürün + Patent Wall"),
            ("comparability_stratejisi", "Comparability Stratejisi (CQA)"),
            ("klinik_program", "Klinik Program (PK/PD + Faz III)"),
            ("regulatory_yolu", "Regülatör Yol (FDA + EMA + TİTCK)"),
            ("extrapolation", "Extrapolation + Interchangeability"),
            ("cihaz_stratejisi", "Cihaz Stratejisi"),
            ("pazar_projeksiyonu", "Pazar Payı Projeksiyonu"),
            ("3_jurisdiksiyon", "3-Jurisdiksiyon Launch Takvimi"),
            ("oneriler", "Stratejik Öneriler"),
            ("compliance", "Compliance Beyanları"),
        ],
        "audience_default": "Executive",
        "relevant_scripts": ["loe-calculator.py"],
    },
    "licensing": {
        "name": "License Negotiation Memo",
        "template_section": "rapor-sablonlari.md (License Negotiation)",
        "required_visuals": [
            "lifecycle-gantt",
            "dd-montecarlo",
            "dd-tornado",
        ],
        "sections": [
            ("yonetici_ozeti", "Yönetici Özeti (BLUF)"),
            ("asset_profili", "Asset Profili"),
            ("comparable_deals", "Karşılaştırılabilir Transaksiyonlar"),
            ("finansal_modelleme", "Finansal Modelleme (NPV + IRR)"),
            ("hukuki_cerceve", "Hukuki Çerçeve (lex-mercator entegrasyonu)"),
            ("muzakere_stratejisi", "Müzakere Stratejisi (BATNA + ZOPA)"),
            ("takvim_maliyet", "Takvim + Maliyet"),
            ("kirmizi_cizgiler", "Stratejik Kırmızı Çizgiler"),
            ("oneriler", "Finansal Öneri + Karar"),
            ("compliance", "Compliance Beyanları"),
        ],
        "audience_default": "Executive",
        "relevant_scripts": ["royalty-calculator.py"],
    },
    "expert_witness": {
        "name": "Expert Witness Report (FSHHM Bilirkişi)",
        "template_section": "rapor-sablonlari.md §10",
        "required_visuals": [
            "fto-feature-matrix",
            "expert-verdict-summary",
        ],
        "sections": [
            ("kimlik", "Bilirkişi Kimliği ve Uzmanlık Alanı"),
            ("gorev_tanimi", "Mahkeme Görev Tanımı"),
            ("metodoloji", "Metodoloji Beyanı"),
            ("patent_analizi", "Patent Analizi + İstem Ayrıştırması"),
            ("tecavuz_analizi", "Tecavüz Analizi (Literal + Doktrinel Eşdeğer)"),
            ("hukumsuzluk_analizi", "Hükümsüzlük Analizi"),
            ("turkiye_gecerlilik", "Türkiye'de Patentin Geçerliliği"),
            ("zarar_hesabi", "Zarar Hesabı (SMK m.151)"),
            ("sonuc_gorus", "Sonuç ve Görüş (Sorulara Tek Tek Cevap)"),
            ("savunulabilirlik", "Savunulabilirlik Notları"),
            ("bagimsizlik", "HMK m.266 Bağımsızlık Beyanı"),
            ("compliance", "Compliance Beyanları"),
        ],
        "audience_default": "Legal",
        "relevant_scripts": ["claim-parser.py"],
    },
}


@dataclass
class ReportConfig:
    """Rapor yapılandırma parametreleri."""
    report_type: str
    asset_name: str
    audience: str = "Executive"  # Technical / Executive / Legal
    preparer: str = "[Hazırlayan Adı]"
    reviewer: str = "[İnceleyen Adı]"
    date: str = None
    custom_sections: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if self.date is None:
            self.date = date.today().isoformat()


def build_frontmatter(config: ReportConfig, rt_info: Dict) -> str:
    """Rapor frontmatter + başlık."""
    return f"""# {rt_info['name']} — {config.asset_name}

**Versiyon**: v1.0 — {config.date}
**Hedef kitle**: {config.audience}
**Hazırlayan**: {config.preparer}
**İnceleyen**: {config.reviewer}
**Şablon kaynağı**: `{rt_info['template_section']}`
**Dağıtım kısıtı**: GİZLİ — AVUKAT-MÜVEKKİL AYRICALIĞI + ÇALIŞMA ÜRÜNÜ

---
"""


def build_section_skeleton(section_id: str, section_name: str, rt_info: Dict) -> str:
    """Her bölüm için iskelet üret."""
    visuals = rt_info.get('required_visuals', [])
    
    placeholders = {
        "yonetici_ozeti": """## 1. Yönetici Özeti (BLUF)

**Asset özeti**: [Ürün adı + endikasyon + aşama]

**Ana bulgular**:
- Bulgu 1 — [açıklama]
- Bulgu 2 — [açıklama]
- Bulgu 3 — [açıklama]

**Kritik risk/ fırsat**:
- [Ana risk]
- [Ana fırsat]

**Öneri**: [DEVAM / DUR / DEĞİŞTİR — kısa gerekçe]

**Finansal özet** (varsa):
- NPV: $[X]M
- IRR: [Y]%
- Payback: [Z] yıl

---
""",
        "kapsam": """## 2. Kapsam ve Metodoloji

**Analiz kapsamı**:
- Coğrafya: [TR / AB / ABD / Worldwide]
- Zaman çerçevesi: [Geçmiş N yıl + Gelecek M yıl]
- Patent tipleri: [Molekül / Formülasyon / Cihaz / Kombinasyon / İkinci tıbbi kullanım]

**Kullanılan veri tabanları**:
- EPAAT (TR geçerlilik)
- USPTO Patent Public Search
- Espacenet + INPADOC
- WIPO PATENTSCOPE
- Orange Book (referans ilaç)
- Purple Book (biyolojikler)

**Boolean sorgu stratejisi**:
```
[Buraya CPC kodları + Boolean ifade]
```

**Sınırlılıklar**:
- [Veri erişim limiti]
- [Dil / geographic gap]
- [Zaman gap]

---
""",
        "compliance": """## N. Compliance Beyanları

### Avukat-Müvekkil Ayrıcalığı
Bu rapor 1136 sayılı Avukatlık Kanunu m. 36 + HMK m. 219/3 kapsamında **avukat-müvekkil ayrıcalığı + work product** statüsündedir.

### Çıkar Çatışması
Rapor hazırlayıcıları [Müvekkil]'nin çalışanları veya sözleşmeli dış müşavirleridir. [İlgili üçüncü taraflar] ile geçmiş profesyonel ilişki yok/açıklanmıştır.

### KVKK + GDPR
Raporda kullanılan kişisel veriler GDPR Art. 6(1)(f) meşru menfaat kapsamında işlenmiştir; pseudonymization uygulanmıştır.

### Anti-Bribery
Bu rapor hazırlık sürecinde FCPA + UK Bribery Act + TR 5607 sayılı Kanun uyumuna riayet edilmiştir.

### Compliance detay
Detaylar için: `references/compliance-beyanlari.md`

---
""",
    }
    
    # Default skeleton for non-mapped sections
    default_skeleton = f"""## {section_name}

**[Bu bölüm için içerik]**:

- Alt başlık 1: [açıklama]
- Alt başlık 2: [açıklama]

**Görsel gereksinimi**:
{chr(10).join([f'- `visualize:show_widget` — {v} şablonu (`visualize-widget-kutuphanesi.md`)' for v in visuals[:2]]) if visuals else '- Gerekmez veya serbest format'}

**Kaynaklar**:
- [Kaynak 1]
- [Kaynak 2]

---
"""
    
    return placeholders.get(section_id, default_skeleton)


def build_visual_requirements(rt_info: Dict) -> str:
    """Zorunlu görsel listesini çıktıla."""
    visuals = rt_info.get('required_visuals', [])
    if not visuals:
        return "Bu rapor tipi için zorunlu görsel tanımlanmamış."
    
    lines = ["## Görsel Gereksinimleri", ""]
    lines.append(f"Bu rapor için `visualize-widget-kutuphanesi.md`'den kullanılacak zorunlu görsel şablonları:")
    lines.append("")
    for v in visuals:
        lines.append(f"- `{v}` — ilgili bölümde `visualize:show_widget` ile inline render")
    lines.append("")
    lines.append("**Akış**:")
    lines.append("1. `visualize:read_me(modules=['chart' veya 'diagram'])` çağrısı (sessiz)")
    lines.append("2. Kütüphaneden şablonu al + placeholder'ları vakaya özgü doldur")
    lines.append("3. `visualize:show_widget(title=..., widget_code=..., loading_messages=...)`")
    lines.append("")
    return "\n".join(lines)


def build_scripts_hint(rt_info: Dict) -> str:
    """Rapor tipi için ilgili scriptleri listele."""
    scripts = rt_info.get('relevant_scripts', [])
    if not scripts:
        return ""
    
    lines = ["## İlgili Scriptler", ""]
    lines.append("Bu raporun hesaplama + analiz bölümleri için aşağıdaki scriptler kullanılabilir:")
    lines.append("")
    for s in scripts:
        lines.append(f"- `scripts/{s}` — [`--example` ile demo / `--import <file>` ile veri]")
    lines.append("")
    return "\n".join(lines)


def build_report(config: ReportConfig) -> str:
    """Tam rapor iskeletini inşa et."""
    if config.report_type not in REPORT_TYPES:
        raise ValueError(f"Bilinmeyen rapor tipi: {config.report_type}. Mevcut: {list(REPORT_TYPES.keys())}")
    
    rt_info = REPORT_TYPES[config.report_type]
    
    out = []
    out.append(build_frontmatter(config, rt_info))
    out.append(build_visual_requirements(rt_info))
    out.append(build_scripts_hint(rt_info))
    out.append("---\n")
    
    # Sections (numbered)
    for idx, (section_id, section_name) in enumerate(rt_info['sections'], 1):
        if section_id == "compliance":
            # Compliance her zaman son
            continue
        skeleton = build_section_skeleton(section_id, f"{idx}. {section_name}", rt_info)
        # Kontent içindeki numaralandırmayı düzelt
        skeleton = skeleton.replace("## 1. ", f"## {idx}. ").replace("## 2. ", f"## {idx}. ").replace("## N. ", f"## {idx}. ")
        out.append(skeleton)
    
    # Compliance en sonda
    compliance_idx = len(rt_info['sections'])
    compliance_skeleton = build_section_skeleton("compliance", f"{compliance_idx}. Compliance Beyanları", rt_info)
    compliance_skeleton = compliance_skeleton.replace("## N. ", f"## {compliance_idx}. ")
    out.append(compliance_skeleton)
    
    # Footer
    out.append("---\n")
    out.append(f"*Hazırlayan: {config.preparer} · Tarih: {config.date} · Pharmapatent skill v1.6.0*")
    
    return "\n".join(out)


def list_report_types():
    """Tüm rapor tiplerini tablo olarak listele."""
    print()
    print("═" * 100)
    print("  MEVCUT RAPOR TİPLERİ")
    print("═" * 100)
    print(f"  {'ID':<18} {'İsim':<40} {'Varsayılan kitle':<15} {'Bölüm':<6}")
    print(f"  {'-'*18} {'-'*40} {'-'*15} {'-'*6}")
    for rt_id, rt_info in REPORT_TYPES.items():
        audience = rt_info['audience_default']
        sections = len(rt_info['sections'])
        name = rt_info['name']
        print(f"  {rt_id:<18} {name[:40]:<40} {audience:<15} {sections:<6}")
    print("═" * 100)
    print()
    print("  Kullanım:")
    print("    python3 report-builder.py --type <ID> --asset \"<ürün adı>\" --out <dosya.md>")
    print()


def run_example():
    """Örnek rapor üret — FTO raporu atorvastatin için."""
    print()
    print("═" * 80)
    print("  ÖRNEK RAPOR ÜRETİMİ — FTO Raporu (atorvastatin)")
    print("═" * 80)
    
    config = ReportConfig(
        report_type="fto",
        asset_name="Atorvastatin 40mg film-coated tablet",
        audience="Legal",
        preparer="Patent İstihbarat Ekibi",
        reviewer="Başhukuk Müşaviri",
    )
    
    report = build_report(config)
    
    # Örnek olarak özeti yazdır
    lines = report.split('\n')
    preview_lines = lines[:60]
    print()
    for line in preview_lines:
        print(line)
    print()
    print(f"... ({len(lines) - 60} satır daha)")
    print()
    print(f"Toplam rapor uzunluğu: {len(report)} karakter, {len(lines)} satır")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Pharmapatent Rapor Otomasyon Orkestratörü (v1.6.0)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--type', type=str, help="Rapor tipi (örn. fto, invalidity, licensing)")
    parser.add_argument('--asset', type=str, default="[Asset Name]", help="Asset adı")
    parser.add_argument('--audience', type=str, default=None, help="Technical / Executive / Legal")
    parser.add_argument('--preparer', type=str, default="[Hazırlayan]", help="Hazırlayan adı")
    parser.add_argument('--reviewer', type=str, default="[İnceleyen]", help="İnceleyen adı")
    parser.add_argument('--out', type=str, help="Çıktı dosyası (yoksa stdout)")
    parser.add_argument('--list-types', action='store_true', help="Rapor tiplerini listele")
    parser.add_argument('--example', action='store_true', help="FTO örnek raporu üret")
    
    args = parser.parse_args()
    
    print()
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.6.0 — Report Builder Orkestratörü                    ║")
    print("║  rapor-sablonlari + visualize-widget + carbon-html entegrasyonu       ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")
    
    if args.list_types:
        list_report_types()
        return
    
    if args.example:
        run_example()
        return
    
    if not args.type:
        print("\n❌ --type parametresi zorunlu. --list-types ile rapor tiplerini görün.")
        sys.exit(1)
    
    if args.type not in REPORT_TYPES:
        print(f"\n❌ Bilinmeyen rapor tipi: {args.type}")
        print(f"   Mevcut: {list(REPORT_TYPES.keys())}")
        sys.exit(1)
    
    rt_info = REPORT_TYPES[args.type]
    audience = args.audience or rt_info['audience_default']
    
    config = ReportConfig(
        report_type=args.type,
        asset_name=args.asset,
        audience=audience,
        preparer=args.preparer,
        reviewer=args.reviewer,
    )
    
    report = build_report(config)
    
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n✓ Rapor iskeleti oluşturuldu: {args.out}")
        print(f"  Rapor tipi: {rt_info['name']}")
        print(f"  Asset: {args.asset}")
        print(f"  Hedef kitle: {audience}")
        print(f"  Bölüm sayısı: {len(rt_info['sections'])}")
        print(f"  Zorunlu görsel: {len(rt_info.get('required_visuals', []))}")
        print(f"  İlgili scripts: {', '.join(rt_info.get('relevant_scripts', []))}")
    else:
        print()
        print(report)


if __name__ == "__main__":
    main()
