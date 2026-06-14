#!/usr/bin/env python3
"""
loe-calculator.py — Loss of Exclusivity tarihi hesaplayıcı

Türkiye'de bir jenerik/biyobenzer ürünün en erken pazara giriş tarihini hesaplar.

Formül:
    LOE = MAX(
        Gümrük Birliği alanında ilk ruhsat tarihi + 6 yıl,   # veri imtiyazı
        Türkiye patent süresi (en geç biten aktif patent)     # patent duvarı
    )

Kullanım:
    python3 loe-calculator.py

Örnek:
    Ürün adı: Ozempic
    İlk AB/TR ruhsat tarihi (YYYY-MM-DD): 2018-02-08
    En geç biten aktif patent tarihi (YYYY-MM-DD): 2030-02-12
    ----
    Veri imtiyazı bitişi:   2024-02-08
    Patent bitişi:          2030-02-12
    LOE (en erken giriş):   2030-02-12 (PATENT belirleyici)

Yazar: pharmapatent skill v1.1.0
Lisans: Internal use.
"""

from datetime import date
from dateutil.relativedelta import relativedelta  # pip install python-dateutil
import sys


def parse_date(prompt: str) -> date:
    """YYYY-MM-DD formatında tarih girişi alır, doğrular."""
    while True:
        raw = input(prompt).strip()
        if not raw:
            return None
        try:
            y, m, d = map(int, raw.split('-'))
            return date(y, m, d)
        except (ValueError, IndexError):
            print(f"  ⚠ Geçersiz tarih formatı. YYYY-MM-DD olarak girin (örn. 2018-02-08).")


def calculate_loe(
    first_registration: date,
    latest_patent_expiry: date = None,
    data_exclusivity_years: int = 6
) -> dict:
    """
    LOE tarihini hesaplar.

    Args:
        first_registration: Gümrük Birliği (AB + TR) alanında ilk ruhsat tarihi
        latest_patent_expiry: En geç biten aktif patent tarihi (None ise patent engeli yok)
        data_exclusivity_years: Veri imtiyazı süresi (TR için 6)

    Returns:
        dict: {
            'data_exclusivity_end': date,
            'patent_expiry': date or None,
            'loe_date': date,
            'determining_factor': 'PATENT' | 'DATA_EXCLUSIVITY',
            'gap_days': int  (iki tarih arasındaki fark, gün)
        }
    """
    de_end = first_registration + relativedelta(years=data_exclusivity_years)

    if latest_patent_expiry is None:
        # Patent engeli yok → veri imtiyazı belirleyici
        return {
            'data_exclusivity_end': de_end,
            'patent_expiry': None,
            'loe_date': de_end,
            'determining_factor': 'DATA_EXCLUSIVITY',
            'gap_days': 0,
        }

    if latest_patent_expiry > de_end:
        loe = latest_patent_expiry
        determining = 'PATENT'
        gap = (latest_patent_expiry - de_end).days
    else:
        loe = de_end
        determining = 'DATA_EXCLUSIVITY'
        gap = (de_end - latest_patent_expiry).days

    return {
        'data_exclusivity_end': de_end,
        'patent_expiry': latest_patent_expiry,
        'loe_date': loe,
        'determining_factor': determining,
        'gap_days': gap,
    }


def practical_market_entry(loe_date: date, approval_months: int = 18, pricing_months: int = 6) -> date:
    """
    Ruhsat + fiyat + SGK müzakere süreleri dahil pratik pazara giriş tarihi.
    Jenerik için tipik: ~18 ay ruhsat + ~6 ay fiyat/SGK = 24 ay ek süre.
    Biyobenzer için: ~24-30 ay ruhsat + ~6-12 ay fiyat/SGK = 30-42 ay ek süre.
    """
    return loe_date + relativedelta(months=approval_months + pricing_months)


def print_report(result: dict, product_name: str, is_biosimilar: bool):
    """Sonuçları formatlayıp konsola yazar."""
    print()
    print("═" * 70)
    print(f"  LOE HESAPLAMA — {product_name}")
    print("═" * 70)
    print(f"  Veri imtiyazı bitişi:        {result['data_exclusivity_end']}")
    if result['patent_expiry']:
        print(f"  En geç aktif patent bitişi:  {result['patent_expiry']}")
    else:
        print(f"  Patent engeli:               YOK")
    print(f"  ────────────────────────────────────────────────────────")
    print(f"  LOE tarihi:                  {result['loe_date']}")
    print(f"  Belirleyici:                 {result['determining_factor']}")
    if result['gap_days'] > 0:
        years = result['gap_days'] / 365.25
        print(f"  Gap:                         {result['gap_days']} gün (~{years:.1f} yıl)")

    # Pratik pazara giriş
    approval = 24 if is_biosimilar else 18
    pricing = 9 if is_biosimilar else 6
    practical = practical_market_entry(result['loe_date'], approval, pricing)

    print(f"  ────────────────────────────────────────────────────────")
    print(f"  Bolar kapsamında biyoeşdeğerlik başlangıç (önerilen):")
    print(f"    Küçük molekül jenerik için:  {result['loe_date'] - relativedelta(years=3)}")
    print(f"    Biyobenzer için:             {result['loe_date'] - relativedelta(years=4)}")
    print(f"  Ruhsat başvuru (veri imtiyazı sonrası):")
    print(f"                                 {max(result['data_exclusivity_end'], result['loe_date'] - relativedelta(months=approval))}")
    print(f"  Pratik pazara arz (ruhsat + fiyat + SGK):")
    print(f"    {'Biyobenzer' if is_biosimilar else 'Jenerik'}:                   {practical}")
    print("═" * 70)
    print()

    # Uyarılar
    if result['determining_factor'] == 'PATENT' and result['gap_days'] > 365:
        print(f"  ⚠ UYARI: Patent {result['gap_days'] // 365} yıl daha uzun koruma sağlıyor.")
        print(f"    → Hükümsüzlük davası feasibility incelenmeli.")
        print(f"    → `pharmapatent invalidity` modunu çalıştırın.")
        print()

    if result['determining_factor'] == 'DATA_EXCLUSIVITY':
        print(f"  ℹ NOT: Patent koruma süresi veri imtiyazından kısa.")
        print(f"    → Veri imtiyazı belirleyici engel.")
        print(f"    → Bolar istisnası kapsamında biyoeşdeğerlik çalışmaları")
        print(f"      {result['loe_date'] - relativedelta(years=3)} tarihinden başlayabilir.")
        print()


def main():
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.1.0 — Loss of Exclusivity (LOE) Hesaplayıcı        ║")
    print("║  Türkiye pazarı için patent + veri imtiyazı MAX formülü             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()

    try:
        # Girdi
        product_name = input("Ürün adı (INN veya ticari): ").strip() or "Ürün"
        is_biosimilar = input("Biyobenzer mi? (e/h) [varsayılan: h]: ").strip().lower() == 'e'
        first_reg = parse_date("Gümrük Birliği'nde ilk ruhsat tarihi (YYYY-MM-DD): ")
        if not first_reg:
            print("❌ İlk ruhsat tarihi zorunludur.")
            sys.exit(1)

        patent_raw = input("En geç biten aktif patent tarihi (YYYY-MM-DD veya boş): ").strip()
        if patent_raw:
            try:
                y, m, d = map(int, patent_raw.split('-'))
                patent_expiry = date(y, m, d)
            except (ValueError, IndexError):
                print(f"  ⚠ Geçersiz tarih, patent engeli olmadan devam ediliyor.")
                patent_expiry = None
        else:
            patent_expiry = None

        # Hesaplama
        result = calculate_loe(first_reg, patent_expiry)

        # Rapor
        print_report(result, product_name, is_biosimilar)

    except KeyboardInterrupt:
        print("\n\n⏹ İşlem iptal edildi.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Beklenmedik hata: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
