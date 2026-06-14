#!/usr/bin/env python3
"""
priority-date-matrix.py — Patent Portföyü Priority Date Kritiklik Matrisi

Bir patent portföyünde priority date'lerin invalidity riskini, prior art arama
sınırlarını ve jurisdictional koordinasyonu analiz eder. Özellikle:

- Priority date vs filing date sapmaları (12 aylık Paris Convention limit)
- PCT ulusal faz giriş zamanı (30 ay limit)
- Divisional başvurular için parent-child priority claim zinciri
- Coğrafi koordinasyon — hangi ülkede hangi priority tarihinde ayrılmış
- Prior art kesim tarihi (her jurisdictionda)

Kullanım:
    python3 priority-date-matrix.py                    # interactive
    python3 priority-date-matrix.py --example          # demo
    python3 priority-date-matrix.py --import data.csv  # CSV import
    python3 priority-date-matrix.py --check            # uyumluluk check

CSV formatı:
    family_id,patent_no,jurisdiction,priority_date,filing_date,pct_filing_date,national_phase_date
    FAM-1,US99999,US,2015-03-01,2016-02-28,2016-02-28,2017-09-01
    ...

Yazar: pharmapatent skill v1.4.0
Lisans: Internal use.
"""

import csv
import json
import sys
from datetime import date, datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from collections import defaultdict


# --- Constants ---
PARIS_CONVENTION_PRIORITY_PERIOD_DAYS = 365   # 12 ay
PCT_NATIONAL_PHASE_DEADLINE_MONTHS = 30
DIVISIONAL_DEADLINE_DEPENDS_ON_JURISDICTION = True  # US: parent pending; EP: parent pending


@dataclass
class PatentRecord:
    """Priority + filing date analiz için patent kaydı."""
    family_id: str
    patent_no: str
    jurisdiction: str
    priority_date: Optional[date] = None
    filing_date: Optional[date] = None
    pct_filing_date: Optional[date] = None
    national_phase_date: Optional[date] = None
    parent_patent_no: Optional[str] = None  # divisional'lar için


@dataclass
class CheckResult:
    """Bir patent için uyumluluk check sonucu."""
    patent_no: str
    checks: List[Dict] = field(default_factory=list)
    
    def add(self, check_type: str, status: str, message: str):
        """Ekle: status = 'pass' | 'warning' | 'fail'"""
        self.checks.append({
            "type": check_type,
            "status": status,
            "message": message,
        })


def parse_date(s: str) -> Optional[date]:
    if not s or s.lower() in ("none", "null", ""):
        return None
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def check_paris_priority(record: PatentRecord) -> CheckResult:
    """Paris Convention 12 aylık priority period check."""
    result = CheckResult(patent_no=record.patent_no)
    
    if not record.priority_date or not record.filing_date:
        result.add("paris_priority", "warning", "Priority veya filing date eksik")
        return result
    
    # PCT başvuru varsa, o tarihten, yoksa direkt filing date
    effective_filing = record.pct_filing_date or record.filing_date
    
    diff_days = (effective_filing - record.priority_date).days
    
    if diff_days > PARIS_CONVENTION_PRIORITY_PERIOD_DAYS:
        result.add("paris_priority", "fail",
                   f"Priority → filing {diff_days} gün (>{PARIS_CONVENTION_PRIORITY_PERIOD_DAYS} "
                   f"Paris Convention limit)")
    elif diff_days > 330:  # Son 35 gün uyarı
        result.add("paris_priority", "warning",
                   f"Priority → filing {diff_days} gün (Paris limit'e yakın)")
    else:
        result.add("paris_priority", "pass",
                   f"Priority → filing {diff_days} gün (limit içinde)")
    
    return result


def check_pct_national_phase(record: PatentRecord) -> CheckResult:
    """PCT ulusal faz giriş tarihi check (30 ay)."""
    result = CheckResult(patent_no=record.patent_no)
    
    if not record.pct_filing_date or not record.national_phase_date:
        result.add("pct_national_phase", "skip", "PCT veya ulusal faz tarihi yok")
        return result
    
    # 30 ay = ~913 gün (aylara göre değişir)
    deadline = date(record.pct_filing_date.year + 2, 
                     record.pct_filing_date.month, 
                     min(record.pct_filing_date.day, 28))
    deadline += timedelta(days=30*6)  # +6 ay ≈ yaklaşık ama daha iyi hesaplanır
    
    # Daha doğru: PCT filing + 30 ay
    year_shift = 2
    month_shift = 6
    new_month = record.pct_filing_date.month + month_shift
    new_year = record.pct_filing_date.year + year_shift
    if new_month > 12:
        new_month -= 12
        new_year += 1
    try:
        deadline = date(new_year, new_month, record.pct_filing_date.day)
    except ValueError:
        deadline = date(new_year, new_month, 28)
    
    if record.national_phase_date > deadline:
        result.add("pct_national_phase", "fail",
                   f"Ulusal faz girişi {record.national_phase_date} > deadline {deadline}")
    else:
        days_early = (deadline - record.national_phase_date).days
        result.add("pct_national_phase", "pass",
                   f"Ulusal faz girişi {record.national_phase_date} (deadline'dan {days_early} gün önce)")
    
    return result


def check_priority_consistency(records: List[PatentRecord]) -> List[CheckResult]:
    """Aynı family_id içindeki priority date'lerin tutarlılığını kontrol et."""
    by_family = defaultdict(list)
    for r in records:
        by_family[r.family_id].append(r)
    
    results = []
    for fam_id, fam_records in by_family.items():
        priority_dates = [r.priority_date for r in fam_records if r.priority_date]
        if not priority_dates:
            continue
        
        earliest = min(priority_dates)
        latest = max(priority_dates)
        
        for r in fam_records:
            cr = CheckResult(patent_no=r.patent_no)
            if r.priority_date and r.priority_date != earliest:
                cr.add("family_priority_consistency", "warning",
                       f"Priority date {r.priority_date}, ailenin en eski {earliest}'dan farklı")
            else:
                cr.add("family_priority_consistency", "pass",
                       f"Priority date aileyle tutarlı")
            results.append(cr)
    
    return results


def generate_prior_art_cutoff_matrix(records: List[PatentRecord]) -> Dict:
    """Her aile için prior art kesim tarihini tespit et."""
    by_family = defaultdict(list)
    for r in records:
        by_family[r.family_id].append(r)
    
    cutoffs = {}
    for fam_id, fam_records in by_family.items():
        priority_dates = [r.priority_date for r in fam_records if r.priority_date]
        if priority_dates:
            cutoffs[fam_id] = {
                "earliest_priority": min(priority_dates),
                "prior_art_cutoff": min(priority_dates),  # Invalidity için tarama tarihi
                "members_count": len(fam_records),
                "jurisdictions": sorted(set(r.jurisdiction for r in fam_records)),
            }
    
    return cutoffs


def print_matrix(records: List[PatentRecord]):
    """Priority date matrisi tablo olarak yazdır."""
    print()
    print("═" * 98)
    print("  PRIORITY DATE MATRİSİ")
    print("═" * 98)
    print(f"  {'Family':<15} {'Patent':<18} {'Juris':<6} {'Priority':<12} {'Filing':<12} {'PCT':<12} {'Nat.Phase':<12}")
    print(f"  {'-'*15} {'-'*18} {'-'*6} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")
    
    by_family = defaultdict(list)
    for r in records:
        by_family[r.family_id].append(r)
    
    for fam_id in sorted(by_family.keys()):
        for r in by_family[fam_id]:
            p = str(r.priority_date) if r.priority_date else "—"
            f = str(r.filing_date) if r.filing_date else "—"
            pct = str(r.pct_filing_date) if r.pct_filing_date else "—"
            np = str(r.national_phase_date) if r.national_phase_date else "—"
            print(f"  {r.family_id:<15} {r.patent_no:<18} {r.jurisdiction:<6} {p:<12} {f:<12} {pct:<12} {np:<12}")
    
    print("═" * 98)


def run_all_checks(records: List[PatentRecord]) -> List[CheckResult]:
    """Tüm uyumluluk check'lerini uygula."""
    all_results = []
    for r in records:
        all_results.append(check_paris_priority(r))
        all_results.append(check_pct_national_phase(r))
    
    # Family consistency (paralel)
    all_results.extend(check_priority_consistency(records))
    
    return all_results


def print_check_results(results: List[CheckResult]):
    """Uyumluluk check sonuçlarını yazdır."""
    print()
    print("═" * 80)
    print("  UYUMLULUK CHECK SONUÇLARI")
    print("═" * 80)
    
    # Patent bazlı grupla
    by_patent = defaultdict(list)
    for r in results:
        by_patent[r.patent_no].extend(r.checks)
    
    counts = {"pass": 0, "warning": 0, "fail": 0, "skip": 0}
    
    for patent_no in sorted(by_patent.keys()):
        checks = by_patent[patent_no]
        print(f"\n  📄 {patent_no}")
        for c in checks:
            status = c['status']
            counts[status] = counts.get(status, 0) + 1
            icon = {"pass": "✓", "warning": "⚠", "fail": "✗", "skip": "○"}.get(status, "?")
            print(f"     {icon} [{c['type']}] {c['message']}")
    
    # Özet
    print()
    print(f"  ═══ ÖZET ═══")
    print(f"  ✓ PASS:    {counts['pass']}")
    print(f"  ⚠ WARNING: {counts['warning']}")
    print(f"  ✗ FAIL:    {counts['fail']}")
    print(f"  ○ SKIP:    {counts['skip']}")
    print()


def print_prior_art_cutoffs(records: List[PatentRecord]):
    """Her aile için prior art kesim tarihlerini yazdır."""
    cutoffs = generate_prior_art_cutoff_matrix(records)
    
    print()
    print("═" * 80)
    print("  PRIOR ART KESİM TARİHLERİ (Invalidity Araştırma Sınırları)")
    print("═" * 80)
    
    for fam_id in sorted(cutoffs.keys()):
        info = cutoffs[fam_id]
        print(f"\n  📁 {fam_id}")
        print(f"     Prior art kesim tarihi: {info['prior_art_cutoff']}")
        print(f"     → Invalidity araştırmasında bu tarihten ÖNCEKİ belgeler adaydır")
        print(f"     → {info['members_count']} üye ({', '.join(info['jurisdictions'])})")
    
    print()


def load_records_csv(path: str) -> List[PatentRecord]:
    """CSV import."""
    records = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            r = PatentRecord(
                family_id=row.get('family_id', '').strip(),
                patent_no=row.get('patent_no', '').strip(),
                jurisdiction=row.get('jurisdiction', '').strip().upper(),
                priority_date=parse_date(row.get('priority_date', '')),
                filing_date=parse_date(row.get('filing_date', '')),
                pct_filing_date=parse_date(row.get('pct_filing_date', '')),
                national_phase_date=parse_date(row.get('national_phase_date', '')),
                parent_patent_no=row.get('parent_patent_no', '').strip() or None,
            )
            records.append(r)
    return records


def example_records() -> List[PatentRecord]:
    """Örnek: bir portföyün priority date matrisi."""
    return [
        # Aile 1: normal PCT rotası
        PatentRecord("FAM-1", "US9999999", "US",
                     priority_date=date(2015, 3, 1),
                     filing_date=date(2016, 2, 28),
                     pct_filing_date=date(2016, 2, 28),
                     national_phase_date=date(2017, 8, 25)),
        PatentRecord("FAM-1", "EP2123456", "EP",
                     priority_date=date(2015, 3, 1),
                     filing_date=date(2016, 2, 28),
                     pct_filing_date=date(2016, 2, 28),
                     national_phase_date=date(2017, 8, 25)),
        PatentRecord("FAM-1", "TR/EP2123456", "TR",
                     priority_date=date(2015, 3, 1),
                     filing_date=date(2016, 2, 28),
                     pct_filing_date=date(2016, 2, 28),
                     national_phase_date=date(2017, 8, 25)),
        # Aile 2: Paris priority limit'e yakın
        PatentRecord("FAM-2", "US10123456", "US",
                     priority_date=date(2018, 1, 10),
                     filing_date=date(2019, 1, 5),
                     pct_filing_date=date(2019, 1, 5),
                     national_phase_date=date(2020, 7, 10)),
        # Aile 3: Paris priority aşıldı (fail case)
        PatentRecord("FAM-3", "US11123456", "US",
                     priority_date=date(2020, 5, 1),
                     filing_date=date(2021, 6, 15),  # 410 gün! Paris limit aşıldı
                     pct_filing_date=date(2021, 6, 15),
                     national_phase_date=date(2022, 11, 1)),
        # Aile 4: Ulusal faz gecikmiş (fail case)
        PatentRecord("FAM-4", "EP2444444", "EP",
                     priority_date=date(2017, 9, 20),
                     filing_date=date(2018, 9, 15),
                     pct_filing_date=date(2018, 9, 15),
                     national_phase_date=date(2021, 5, 1)),  # 32 ay sonra — aşıldı
    ]


def main():
    print()
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.4.0 — Priority Date Matrix Analyzer                 ║")
    print("║  Patent portföyü priority date kritiklik analizi                     ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")

    records = None
    if '--example' in sys.argv:
        print("\n📄 Örnek: 4 aile + 6 patent (bir fail case dahil)\n")
        records = example_records()
    elif '--import' in sys.argv:
        try:
            idx = sys.argv.index('--import')
            path = sys.argv[idx + 1]
            records = load_records_csv(path)
        except (IndexError, FileNotFoundError) as e:
            print(f"❌ Import hatası: {e}")
            sys.exit(1)
    else:
        print("\nKullanım:")
        print("  --example         Örnek portföy ile demo")
        print("  --import <file>   CSV'den yükle")
        print("  --check           Uyumluluk check'lerini çalıştır")
        print()
        print("CSV format:")
        print("  family_id,patent_no,jurisdiction,priority_date,filing_date,pct_filing_date,national_phase_date")
        sys.exit(0)

    # Matrix
    print_matrix(records)
    
    # Prior art cutoffs
    print_prior_art_cutoffs(records)
    
    # Checks (default çalışır example veya --check ile)
    if '--example' in sys.argv or '--check' in sys.argv:
        results = run_all_checks(records)
        print_check_results(results)


if __name__ == "__main__":
    main()
