#!/usr/bin/env python3
"""
patent-expiry-monitor.py — TÜRKPATENT EPAAT Patent Takip Monitörü

Patent portföyünüz için otomatik izleme ve uyarı üretir:
- Yıllık harç son ödeme tarihi uyarısı (60/30/7 gün önce)
- Expiry (patent bitişi) uyarısı (365/180/90/30 gün önce)
- Status değişim takibi (granted → opposed, active → lapsed)
- Bulk patent listesi CSV/JSON import
- Uyarı raporu markdown/HTML/JSON çıktı

NOT: Bu bir araç iskelet'idir. Gerçek TÜRKPATENT EPAAT API'si public değildir;
bu script manuel girilen veya CSV import edilen patent listesi üzerinde çalışır.
Canlı EPAAT sorgulama için TÜRKPATENT ile resmi entegrasyon gereklidir.

Kullanım:
    python3 patent-expiry-monitor.py                         # interactive
    python3 patent-expiry-monitor.py --example               # örnek portföy demosu
    python3 patent-expiry-monitor.py --import portfolio.csv  # CSV import
    python3 patent-expiry-monitor.py --days 180              # uyarı penceresi 180 gün

CSV formatı:
    patent_no,baslik,basvuru_sahibi,basvuru_tarihi,yil_harci_tarihi,expiry_tarihi,status,jurisdiction
    EP1235764,Atorvastatin Form I,Pfizer,1997-07-17,2026-07-17,2024-07-17,active,TR
    ...

Yazar: pharmapatent skill v1.3.0
Lisans: Internal use.
Bağımlılık: python-dateutil (standard library csv + json)
"""

import csv
import json
import sys
from datetime import date, datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import List, Optional
from pathlib import Path

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    print("❌ python-dateutil gerekli. Yükleyin: pip install python-dateutil")
    sys.exit(1)


# --- Patent data model ---
@dataclass
class Patent:
    """Patent takip kaydı."""
    patent_no: str
    baslik: str
    basvuru_sahibi: str
    basvuru_tarihi: Optional[date] = None
    yil_harci_tarihi: Optional[date] = None  # Sıradaki yıllık harç tarihi
    expiry_tarihi: Optional[date] = None
    status: str = "active"  # active, pending, lapsed, opposed, invalidated
    jurisdiction: str = "TR"
    notes: str = ""

    def days_to_expiry(self) -> Optional[int]:
        if self.expiry_tarihi is None:
            return None
        return (self.expiry_tarihi - date.today()).days

    def days_to_annual_fee(self) -> Optional[int]:
        if self.yil_harci_tarihi is None:
            return None
        return (self.yil_harci_tarihi - date.today()).days


@dataclass
class Alert:
    """Uyarı kaydı."""
    patent_no: str
    alert_type: str   # "expiry", "annual_fee", "status_change"
    urgency: str      # "critical", "high", "medium", "low"
    days_remaining: int
    message: str
    action_required: str


# --- Threshold protokolü ---
ANNUAL_FEE_THRESHOLDS = {
    "critical": 7,      # 7 gün içinde
    "high": 30,
    "medium": 60,
    "low": 90,
}

EXPIRY_THRESHOLDS = {
    "critical": 30,     # 30 gün içinde bitiyor
    "high": 90,
    "medium": 180,
    "low": 365,
}


def parse_date(s: str) -> Optional[date]:
    """YYYY-MM-DD formatını date'e çevir."""
    if not s or s.lower() in ("none", "null", ""):
        return None
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def generate_alerts(patents: List[Patent], window_days: int = 365) -> List[Alert]:
    """Patent listesinden uyarıları üret."""
    alerts = []

    for p in patents:
        if p.status not in ("active", "pending"):
            continue  # Sona ermiş veya iptal edilmiş patentler uyarı üretmez

        # --- Yıllık harç uyarısı ---
        d_fee = p.days_to_annual_fee()
        if d_fee is not None and 0 < d_fee <= window_days:
            if d_fee <= ANNUAL_FEE_THRESHOLDS["critical"]:
                urgency = "critical"
                msg = f"⚠ KRİTİK: Yıllık harç {d_fee} gün içinde ({p.yil_harci_tarihi})"
                action = "DERHAL ödeme yapılmalı. Gecikirse 6 ay geç ödeme + gecikme harcı."
            elif d_fee <= ANNUAL_FEE_THRESHOLDS["high"]:
                urgency = "high"
                msg = f"Yıllık harç {d_fee} gün içinde ({p.yil_harci_tarihi})"
                action = "Ödeme planlanmalı (30 gün içinde)."
            elif d_fee <= ANNUAL_FEE_THRESHOLDS["medium"]:
                urgency = "medium"
                msg = f"Yıllık harç {d_fee} gün içinde ({p.yil_harci_tarihi})"
                action = "Yıllık bütçe takvimine eklenmeli."
            else:
                urgency = "low"
                msg = f"Yıllık harç {d_fee} gün içinde"
                action = "Planlama için not edilmeli."
            
            alerts.append(Alert(
                patent_no=p.patent_no,
                alert_type="annual_fee",
                urgency=urgency,
                days_remaining=d_fee,
                message=msg,
                action_required=action,
            ))
        
        # Geçmiş yıllık harç → LAPSED riski
        if d_fee is not None and d_fee < 0 and d_fee > -180:
            alerts.append(Alert(
                patent_no=p.patent_no,
                alert_type="annual_fee_overdue",
                urgency="critical",
                days_remaining=d_fee,
                message=f"⚠⚠ YILLIK HARÇ KAÇIRILDI ({abs(d_fee)} gün önce, {p.yil_harci_tarihi})",
                action_required=f"DERHAL gecikme harcı ile ödenmeli ({180 + d_fee} gün içinde hâlâ mümkün). Aksi halde patent sona erer.",
            ))

        # --- Expiry uyarısı ---
        d_exp = p.days_to_expiry()
        if d_exp is not None and 0 < d_exp <= window_days:
            if d_exp <= EXPIRY_THRESHOLDS["critical"]:
                urgency = "critical"
                msg = f"🔴 Patent {d_exp} gün içinde sona eriyor ({p.expiry_tarihi})"
                action = "ACİL: LOE takvimi + jenerik giriş hazırlığı + lifecycle extension kararı."
            elif d_exp <= EXPIRY_THRESHOLDS["high"]:
                urgency = "high"
                msg = f"Patent {d_exp} gün içinde sona eriyor ({p.expiry_tarihi})"
                action = "Lifecycle extension + SPC/pediatric uzatma imkanları + pazar savunma planı."
            elif d_exp <= EXPIRY_THRESHOLDS["medium"]:
                urgency = "medium"
                msg = f"Patent {d_exp} gün içinde ({p.expiry_tarihi})"
                action = "Evergreening fırsatları değerlendirilmeli."
            else:
                urgency = "low"
                msg = f"Patent {d_exp // 30} ay içinde sona eriyor"
                action = "Uzun vadeli portföy strateji notu."
            
            alerts.append(Alert(
                patent_no=p.patent_no,
                alert_type="expiry",
                urgency=urgency,
                days_remaining=d_exp,
                message=msg,
                action_required=action,
            ))

    # Öncelik sırasına göre sırala
    urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    alerts.sort(key=lambda a: (urgency_order.get(a.urgency, 99), a.days_remaining))

    return alerts


def load_portfolio_csv(path: str) -> List[Patent]:
    """CSV'den patent portföyü yükle."""
    patents = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = Patent(
                patent_no=row.get('patent_no', '').strip(),
                baslik=row.get('baslik', '').strip(),
                basvuru_sahibi=row.get('basvuru_sahibi', '').strip(),
                basvuru_tarihi=parse_date(row.get('basvuru_tarihi', '')),
                yil_harci_tarihi=parse_date(row.get('yil_harci_tarihi', '')),
                expiry_tarihi=parse_date(row.get('expiry_tarihi', '')),
                status=row.get('status', 'active').strip().lower(),
                jurisdiction=row.get('jurisdiction', 'TR').strip().upper(),
                notes=row.get('notes', '').strip(),
            )
            patents.append(p)
    return patents


def generate_example_portfolio() -> List[Patent]:
    """Demo portföyü — hipotetik firma."""
    today = date.today()
    return [
        Patent(
            patent_no="EP1235764",
            baslik="Atorvastatin Form I crystal polymorph",
            basvuru_sahibi="Pfizer",
            basvuru_tarihi=date(1997, 7, 17),
            yil_harci_tarihi=today + timedelta(days=5),   # KRİTİK: 5 gün
            expiry_tarihi=date(2024, 7, 17),
            status="active",
            jurisdiction="TR",
        ),
        Patent(
            patent_no="EP2876108",
            baslik="Stabilized microencapsulated atorvastatin formulation",
            basvuru_sahibi="Teva",
            basvuru_tarihi=date(2009, 3, 12),
            yil_harci_tarihi=today + timedelta(days=25),  # HIGH: 25 gün
            expiry_tarihi=date(2029, 3, 12),
            status="active",
            jurisdiction="TR",
        ),
        Patent(
            patent_no="EP3012345",
            baslik="Amorphous atorvastatin calcium composition",
            basvuru_sahibi="Watson",
            basvuru_tarihi=date(2012, 8, 3),
            yil_harci_tarihi=today + timedelta(days=55),  # MEDIUM: 55 gün
            expiry_tarihi=date(2032, 8, 3),
            status="active",
            jurisdiction="TR",
        ),
        Patent(
            patent_no="TR2015/12345",
            baslik="Direct compression atorvastatin process",
            basvuru_sahibi="Abdi İbrahim",
            basvuru_tarihi=date(2015, 6, 20),
            yil_harci_tarihi=today + timedelta(days=200),  # LOW: 200 gün
            expiry_tarihi=date(2035, 6, 20),
            status="active",
            jurisdiction="TR",
        ),
        Patent(
            patent_no="EP1996220",
            baslik="Semaglutide base compound",
            basvuru_sahibi="Novo Nordisk",
            basvuru_tarihi=date(2005, 5, 23),
            yil_harci_tarihi=today + timedelta(days=15),
            expiry_tarihi=today + timedelta(days=45),  # CRITICAL expiry: 45 gün
            status="active",
            jurisdiction="TR",
        ),
        Patent(
            patent_no="EP3456789",
            baslik="FlexTouch injection device",
            basvuru_sahibi="Novo Nordisk",
            basvuru_tarihi=date(2014, 11, 3),
            yil_harci_tarihi=today - timedelta(days=10),  # KAÇIRILDI: 10 gün önce
            expiry_tarihi=date(2034, 11, 3),
            status="active",
            jurisdiction="TR",
        ),
    ]


def print_alert_report(alerts: List[Alert], patents: List[Patent]):
    """Uyarı raporunu konsolda yazdır."""
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  PATENT UYARI RAPORU — " + date.today().strftime("%Y-%m-%d") + "                                   ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    total = len(patents)
    active = sum(1 for p in patents if p.status == "active")
    
    print(f"\n  📊 Portföy özeti: {total} patent ({active} aktif)")
    print(f"  🔔 Toplam uyarı: {len(alerts)}")

    # Öncelik bazlı özet
    counts = {}
    for a in alerts:
        counts[a.urgency] = counts.get(a.urgency, 0) + 1
    
    print(f"\n  Öncelik dağılımı:")
    for u in ["critical", "high", "medium", "low"]:
        c = counts.get(u, 0)
        if c > 0:
            icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[u]
            print(f"    {icon} {u.upper():<10} {c}")

    # Detaylı uyarılar
    print(f"\n  ═══ DETAYLI UYARILAR ═══\n")
    
    current_urgency = None
    for a in alerts:
        if a.urgency != current_urgency:
            current_urgency = a.urgency
            icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[a.urgency]
            print(f"\n  {icon} {a.urgency.upper()}\n")
        
        patent = next((p for p in patents if p.patent_no == a.patent_no), None)
        print(f"  [{a.patent_no}] {patent.baslik if patent else '?'}")
        print(f"    Sahip: {patent.basvuru_sahibi if patent else '?'}")
        print(f"    {a.message}")
        print(f"    → {a.action_required}")
        print()

    if not alerts:
        print("  ✓ Herhangi bir uyarı yok.\n")


def export_alerts_json(alerts: List[Alert], patents: List[Patent], path: str):
    """JSON formatında dışa aktar."""
    data = {
        "generated_at": datetime.now().isoformat(),
        "portfolio_size": len(patents),
        "active_patents": sum(1 for p in patents if p.status == "active"),
        "total_alerts": len(alerts),
        "alerts": [asdict(a) for a in alerts],
    }
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str, ensure_ascii=False)
    print(f"\n  💾 JSON dışa aktarıldı: {path}")


def export_alerts_markdown(alerts: List[Alert], patents: List[Patent], path: str):
    """Markdown rapor olarak dışa aktar."""
    lines = [
        f"# Patent Uyarı Raporu",
        f"",
        f"**Tarih**: {date.today().strftime('%Y-%m-%d')}",
        f"**Portföy**: {len(patents)} patent ({sum(1 for p in patents if p.status == 'active')} aktif)",
        f"**Toplam uyarı**: {len(alerts)}",
        f"",
        f"## Öncelik Özeti",
        f"",
    ]
    counts = {}
    for a in alerts:
        counts[a.urgency] = counts.get(a.urgency, 0) + 1
    lines.append("| Öncelik | Adet |")
    lines.append("|---|---|")
    for u in ["critical", "high", "medium", "low"]:
        lines.append(f"| {u.upper()} | {counts.get(u, 0)} |")

    lines.append("")
    lines.append("## Detaylı Uyarılar")
    lines.append("")

    for a in alerts:
        patent = next((p for p in patents if p.patent_no == a.patent_no), None)
        lines.append(f"### [{a.urgency.upper()}] {a.patent_no}")
        lines.append("")
        if patent:
            lines.append(f"- **Başlık**: {patent.baslik}")
            lines.append(f"- **Başvuru sahibi**: {patent.basvuru_sahibi}")
            lines.append(f"- **Jurisdiction**: {patent.jurisdiction}")
        lines.append(f"- **Uyarı tipi**: {a.alert_type}")
        lines.append(f"- **Mesaj**: {a.message}")
        lines.append(f"- **Gün**: {a.days_remaining}")
        lines.append(f"- **Aksiyon**: {a.action_required}")
        lines.append("")

    with open(path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"  💾 Markdown dışa aktarıldı: {path}")


def main():
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.3.0 — Patent Expiry + Annual Fee Monitor           ║")
    print("║  Otomatik portföy izleme ve uyarı üretme                            ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    # Argüman parsing (basit)
    window_days = 365
    import_path = None
    
    if '--days' in sys.argv:
        try:
            idx = sys.argv.index('--days')
            window_days = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("❌ --days için geçerli tam sayı gerekli")
            sys.exit(1)

    if '--import' in sys.argv:
        try:
            idx = sys.argv.index('--import')
            import_path = sys.argv[idx + 1]
        except IndexError:
            print("❌ --import için CSV yolu gerekli")
            sys.exit(1)
        if not Path(import_path).exists():
            print(f"❌ Dosya bulunamadı: {import_path}")
            sys.exit(1)

    # Portföyü yükle
    if '--example' in sys.argv:
        print("\n📄 Örnek portföy ile çalışıyor\n")
        patents = generate_example_portfolio()
    elif import_path:
        print(f"\n📂 CSV'den import ediliyor: {import_path}\n")
        patents = load_portfolio_csv(import_path)
    else:
        print("\nKullanım:")
        print("  --example              Örnek portföy ile demo")
        print("  --import <file.csv>    CSV'den yükle")
        print("  --days N               Uyarı penceresi (default 365)")
        print()
        print("CSV formatı:")
        print("  patent_no,baslik,basvuru_sahibi,basvuru_tarihi,yil_harci_tarihi,expiry_tarihi,status,jurisdiction")
        sys.exit(0)

    # Uyarıları üret
    alerts = generate_alerts(patents, window_days=window_days)

    # Rapor
    print_alert_report(alerts, patents)

    # Otomatik dışa aktarım
    if '--example' in sys.argv or import_path:
        ts = date.today().strftime("%Y%m%d")
        out_md = f"/tmp/patent-alerts-{ts}.md"
        out_json = f"/tmp/patent-alerts-{ts}.json"
        export_alerts_markdown(alerts, patents, out_md)
        export_alerts_json(alerts, patents, out_json)


if __name__ == "__main__":
    main()
