#!/usr/bin/env python3
"""
spc-calculator.py — AB Supplementary Protection Certificate (SPC) Süre Hesaplayıcı

AB'de farmasötik ve tarım kimyasalları için patent süresini uzatan SPC (Tamamlayıcı
Koruma Sertifikası) süresini ve uzatma tiplerini hesaplayan script.

**ÖNEMLİ**: SPC, AB ve bazı Avrupa ülkeleri (İsviçre, Norveç, Birleşik Krallık) için
geçerlidir. Türkiye'de SPC karşılığı YOKTUR — SMK 6769 sadece 20 yıl patent süresi
tanır ve SPC eşdeğeri mekanizma içermez. Bu script, Türkiye operasyon için Türkiye
LOE'si hesaplarken AB portföyü karşılaştırması için kullanılır.

Formül (Regulation (EC) No 469/2009 Article 13):

    SPC süresi = (İlk AB ruhsat tarihi - Patent başvuru tarihi) - 5 yıl
    Max SPC süresi = 5 yıl (ek 6 ay pediatric uzatma mümkün)
    
    Toplam patent + SPC koruma = Patent expiry + SPC süresi
    Market exclusivity max: başvurudan 15 yıl sonra

Kullanım:
    python3 spc-calculator.py                    # interactive
    python3 spc-calculator.py --example keytruda # Keytruda hipotetik örneği
    python3 spc-calculator.py --example sovaldi  # Sovaldi hipotetik
    python3 spc-calculator.py --compare-tr       # TR vs AB karşılaştırma

Yazar: pharmapatent skill v1.5.0
Lisans: Internal use.
Bağımlılık: python-dateutil
"""

import sys
from datetime import date
from dataclasses import dataclass, asdict
from typing import Optional

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    print("❌ python-dateutil gerekli. Yükleyin: pip install python-dateutil")
    sys.exit(1)


@dataclass
class SPCCalculation:
    """SPC hesaplama sonucu."""
    product_name: str
    patent_filing_date: date
    patent_expiry_date: date  # 20 yıl sonrası (normal patent expiry)
    first_eu_authorization_date: date
    pediatric_extension: bool
    eligible_for_spc: bool
    spc_duration_months: int   # 0-60 ay + 6 ay pediatric
    spc_effective_from: Optional[date]
    spc_expiry_date: Optional[date]
    total_protection_years: float
    max_market_exclusivity_date: date   # başvurudan 15 yıl sonra cap


def calculate_spc(
    patent_filing_date: date,
    first_eu_authorization_date: date,
    patent_duration_years: int = 20,
    pediatric_extension: bool = False,
) -> SPCCalculation:
    """
    SPC süresini Regulation (EC) No 469/2009 Art. 13 formülüne göre hesapla.
    
    Art. 13:
    - SPC süresi = (ilk ruhsat - patent başvuru) - 5 yıl
    - Max: 5 yıl (60 ay)
    - SPC, patent expiry'den itibaren başlar
    - Pediatric extension +6 ay (Regulation EC No 1901/2006)
    - Toplam koruma ≤ ilk ruhsat + 15 yıl (+ 6 ay pediatric)
    
    Args:
        patent_filing_date: Patent başvuru tarihi (PCT veya ulusal)
        first_eu_authorization_date: İlk AB ruhsat tarihi (EMA merkezi veya ulusal)
        patent_duration_years: Patent süresi (standart 20 yıl)
        pediatric_extension: Pediatric araştırma kapsamında 6 ay ek mümkün mü?
    
    Returns:
        SPCCalculation: Hesaplama sonucu
    """
    # Patent expiry = filing + 20 yıl
    patent_expiry = date(
        patent_filing_date.year + patent_duration_years,
        patent_filing_date.month,
        patent_filing_date.day
    )
    
    # SPC süresi formülü (Art. 13): (ruhsat - başvuru) - 5 yıl
    days_to_authorization = (first_eu_authorization_date - patent_filing_date).days
    years_to_authorization = days_to_authorization / 365.25
    
    spc_months = int((years_to_authorization - 5) * 12)
    
    # SPC eligibility + clamping
    eligible = spc_months > 0
    
    if not eligible:
        spc_months = 0
        spc_effective_from = None
        spc_expiry = None
    else:
        # Max 5 yıl (60 ay)
        if spc_months > 60:
            spc_months = 60
        
        # Pediatric extension: +6 ay
        if pediatric_extension:
            spc_months += 6
        
        spc_effective_from = patent_expiry
        spc_expiry = patent_expiry + relativedelta(months=spc_months)
    
    # Max market exclusivity tavan (Art. 13(2)):
    # Toplam koruma ruhsat tarihinden 15 yıl sonra sona erer
    max_exclusivity = first_eu_authorization_date + relativedelta(years=15)
    
    # Pediatric extension (Reg 1901/2006) — bu 15 yıl sınırını +6 ay uzatabilir
    if pediatric_extension:
        max_exclusivity_effective = max_exclusivity + relativedelta(months=6)
    else:
        max_exclusivity_effective = max_exclusivity
    
    # SPC expiry max_exclusivity'yi aşarsa clamp
    if spc_expiry and spc_expiry > max_exclusivity_effective:
        spc_expiry = max_exclusivity_effective
        # Recompute spc_months from effective spc_expiry
        if spc_effective_from:
            delta_days = (spc_expiry - spc_effective_from).days
            spc_months = max(0, int(delta_days / 30.4375))
    
    # Toplam koruma süresi
    if spc_expiry:
        total_years = (spc_expiry - patent_filing_date).days / 365.25
    else:
        total_years = (patent_expiry - patent_filing_date).days / 365.25
    
    return SPCCalculation(
        product_name="",
        patent_filing_date=patent_filing_date,
        patent_expiry_date=patent_expiry,
        first_eu_authorization_date=first_eu_authorization_date,
        pediatric_extension=pediatric_extension,
        eligible_for_spc=eligible,
        spc_duration_months=spc_months,
        spc_effective_from=spc_effective_from,
        spc_expiry_date=spc_expiry,
        total_protection_years=round(total_years, 2),
        max_market_exclusivity_date=max_exclusivity,
    )


def print_report(result: SPCCalculation):
    """SPC hesaplama sonucunu yazdır."""
    print()
    print("═" * 74)
    print(f"  SPC HESAPLAMA — {result.product_name or 'Ürün'}")
    print("═" * 74)
    print(f"  Patent başvuru tarihi:       {result.patent_filing_date}")
    print(f"  Patent normal expiry (20 yıl): {result.patent_expiry_date}")
    print(f"  İlk AB ruhsat tarihi:        {result.first_eu_authorization_date}")
    print(f"  Pediatric extension talep:    {'EVET' if result.pediatric_extension else 'HAYIR'}")
    print(f"  Max market exclusivity (15y): {result.max_market_exclusivity_date}")
    
    print(f"\n  ─────────────────────────────────────────────────────────────────")
    print(f"  SPC UYGUN MU?                {'✓ EVET' if result.eligible_for_spc else '✗ HAYIR'}")
    
    if result.eligible_for_spc:
        print(f"  SPC süresi:                  {result.spc_duration_months} ay ({result.spc_duration_months / 12:.1f} yıl)")
        print(f"  SPC yürürlüğe giriş:         {result.spc_effective_from}")
        print(f"  SPC expiry:                  {result.spc_expiry_date}")
        print(f"  Toplam koruma süresi:        {result.total_protection_years} yıl (patent+SPC)")
    else:
        print(f"  → Patent başvurudan ruhsata kadar ≤5 yıl geçti, SPC yok")
        print(f"  → Sadece standart 20 yıl patent koruması")
    
    print("═" * 74)
    
    # Interpretasyon
    if result.eligible_for_spc:
        print(f"\n  📊 İNTERPRETASYON")
        if result.spc_duration_months == 66:  # 60 + 6 pediatric
            print(f"  ✓ Maksimum SPC (5 yıl + 6 ay pediatric) kazandınız")
        elif result.spc_duration_months == 60:
            print(f"  ✓ Maksimum SPC (5 yıl) kazandınız — pediatric research için +6 ay değerlendirin")
        elif result.spc_duration_months > 30:
            print(f"  ⚠ İyi SPC süresi. Pediatric extension için +6 ay mümkün")
        else:
            print(f"  ⚠ Kısa SPC süresi. Aslında klinik geliştirme hızlı gitti.")
    
    # TR karşılaştırma
    print(f"\n  🇹🇷 TÜRKİYE KARŞILAŞTIRMA")
    print(f"     Türkiye'de SPC eşdeğeri YOK. Sadece 20 yıl patent koruma.")
    print(f"     Türkiye patent expiry:       {result.patent_expiry_date}")
    if result.eligible_for_spc and result.spc_expiry_date:
        diff = (result.spc_expiry_date - result.patent_expiry_date).days
        print(f"     Koruma farkı (AB - TR):      {diff} gün ({diff/365.25:.1f} yıl)")
        print(f"     → TR jenerik {result.spc_expiry_date.year - result.patent_expiry_date.year} yıl önce girebilir")
    print()


def print_comparison_table(results: list):
    """Birden fazla ürün karşılaştırma tablosu."""
    print()
    print("═" * 94)
    print("  SPC KARŞILAŞTIRMA TABLOSU")
    print("═" * 94)
    print(f"  {'Ürün':<20} {'Başvuru':<12} {'Ruhsat':<12} {'Pat.expiry':<12} {'SPC ay':<8} {'SPC expiry':<12}")
    print(f"  {'-'*20} {'-'*12} {'-'*12} {'-'*12} {'-'*8} {'-'*12}")
    for r in results:
        spc_exp = str(r.spc_expiry_date) if r.spc_expiry_date else "—"
        print(f"  {r.product_name[:20]:<20} {str(r.patent_filing_date):<12} {str(r.first_eu_authorization_date):<12} "
              f"{str(r.patent_expiry_date):<12} {r.spc_duration_months:<8} {spc_exp:<12}")
    print("═" * 94)


# --- Örnekler (hipotetik simplifiye senaryolar — gerçek EPAAT kontrolü zorunlu) ---

EXAMPLES = {
    "keytruda": {
        "name": "Keytruda (pembrolizumab) — hipotetik",
        "patent_filing": date(2007, 10, 4),
        "eu_auth": date(2015, 7, 17),
        "pediatric": True,
    },
    "sovaldi": {
        "name": "Sovaldi (sofosbuvir) — hipotetik",
        "patent_filing": date(2003, 5, 30),
        "eu_auth": date(2014, 1, 16),
        "pediatric": False,
    },
    "ozempic": {
        "name": "Ozempic (semaglutide) — hipotetik",
        "patent_filing": date(2005, 5, 23),
        "eu_auth": date(2018, 2, 8),
        "pediatric": False,
    },
    "enhertu": {
        "name": "Enhertu (T-DXd) — hipotetik",
        "patent_filing": date(2013, 3, 13),
        "eu_auth": date(2021, 1, 18),
        "pediatric": False,
    },
    "xtandi": {
        "name": "Xtandi (enzalutamide) — hipotetik",
        "patent_filing": date(2006, 3, 27),
        "eu_auth": date(2013, 6, 21),
        "pediatric": False,
    },
    "fast_approval": {
        "name": "Hızlı onay örneği (4 yıl)",
        "patent_filing": date(2020, 1, 1),
        "eu_auth": date(2024, 1, 1),
        "pediatric": False,
    },
}


def main():
    print()
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.5.0 — SPC (AB Supplementary Protection) Calculator   ║")
    print("║  AB patent süre uzatma (max 5 yıl + 6 ay pediatric)                   ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")
    print()
    print("  ⚠ NOT: SPC Türkiye'de geçerli değildir. Bu araç AB portföy karşılaştırması")
    print("    için kullanılır; Türkiye LOE hesabı için loe-calculator.py'ı kullanın.")

    # Example mode
    if '--example' in sys.argv:
        try:
            idx = sys.argv.index('--example')
            example_name = sys.argv[idx + 1]
        except (IndexError, ValueError):
            example_name = "keytruda"
        
        if example_name not in EXAMPLES:
            print(f"\n❌ Bilinmeyen örnek: {example_name}")
            print(f"   Mevcut: {list(EXAMPLES.keys())}")
            sys.exit(1)
        
        ex = EXAMPLES[example_name]
        result = calculate_spc(
            patent_filing_date=ex["patent_filing"],
            first_eu_authorization_date=ex["eu_auth"],
            pediatric_extension=ex["pediatric"],
        )
        result.product_name = ex["name"]
        print_report(result)
        return
    
    # Compare TR mode — tüm örnekleri tablo
    if '--compare-tr' in sys.argv:
        results = []
        for key, ex in EXAMPLES.items():
            r = calculate_spc(
                patent_filing_date=ex["patent_filing"],
                first_eu_authorization_date=ex["eu_auth"],
                pediatric_extension=ex["pediatric"],
            )
            r.product_name = ex["name"]
            results.append(r)
        print_comparison_table(results)
        print()
        print("  🇹🇷 ANA GÖZLEM: Türkiye'de SPC olmadığı için tüm bu ürünler için")
        print("     'Pat.expiry' sütunundaki tarih Türkiye LOE tarihidir.")
        print("     AB'de ise 'SPC expiry' tarihine kadar korumalıdır.")
        print("     Fark: tipik 2-5 yıl avantaj AB pazarında vs TR pazarında.")
        print()
        return
    
    # Interactive
    print("\n🎯 Interactive Mode\n")
    try:
        name = input("Ürün adı: ").strip() or "Ürün"
        
        filing_raw = input("Patent başvuru tarihi (YYYY-MM-DD): ").strip()
        y, m, d = map(int, filing_raw.split('-'))
        filing = date(y, m, d)
        
        auth_raw = input("İlk AB ruhsat tarihi (YYYY-MM-DD): ").strip()
        y, m, d = map(int, auth_raw.split('-'))
        auth = date(y, m, d)
        
        pediatric = input("Pediatric research extension (e/h) [h]: ").strip().lower() == 'e'
        
        result = calculate_spc(
            patent_filing_date=filing,
            first_eu_authorization_date=auth,
            pediatric_extension=pediatric,
        )
        result.product_name = name
        print_report(result)
        
    except (ValueError, KeyboardInterrupt) as e:
        print(f"\n⏹ İşlem sonlandı: {e}")
        sys.exit(0)


if __name__ == "__main__":
    main()
