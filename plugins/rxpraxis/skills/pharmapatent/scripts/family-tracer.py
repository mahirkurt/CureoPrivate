#!/usr/bin/env python3
"""
family-tracer.py — Patent Ailesi (INPADOC Family) Takip ve Görselleştirme

Bir patent portföyünde patent ailelerini (aynı öncelik tarihine bağlı ulusal/bölgesel
uzantılar) haritalayan ve coverage analizi yapan script. Espacenet INPADOC veri modeline
benzer mantıkla çalışır.

Kullanım:
    python3 family-tracer.py                              # interactive
    python3 family-tracer.py --example                    # hipotetik aile demosu
    python3 family-tracer.py --import portfolio.csv       # CSV import
    python3 family-tracer.py --mermaid                    # Mermaid flowchart çıktısı
    python3 family-tracer.py --json                       # JSON yapısal çıktı

CSV formatı:
    family_id,patent_no,jurisdiction,priority_date,filing_date,grant_date,status
    FAM-1,US9999999,US,2010-01-15,2011-01-10,2013-06-01,active
    FAM-1,EP2123456,EP,2010-01-15,2011-01-10,2014-03-15,active
    ...

Yazar: pharmapatent skill v1.4.0
Lisans: Internal use.
Bağımlılık: python-dateutil (opsiyonel)
"""

import csv
import json
import sys
from datetime import date, datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from collections import defaultdict


# --- Data models ---
@dataclass
class FamilyMember:
    """Bir patent ailesinin bir üyesi (ulusal/bölgesel faz)."""
    patent_no: str
    jurisdiction: str   # US, EP, TR, JP, CN, WO, ...
    priority_date: Optional[date] = None
    filing_date: Optional[date] = None
    grant_date: Optional[date] = None
    status: str = "unknown"  # granted, pending, abandoned, lapsed, revoked


@dataclass
class PatentFamily:
    """Patent ailesi — aynı priority date'e sahip tüm başvurular."""
    family_id: str
    members: List[FamilyMember] = field(default_factory=list)
    notes: str = ""

    def priority_date(self) -> Optional[date]:
        """Ailenin en eski priority date'i."""
        dates = [m.priority_date for m in self.members if m.priority_date]
        return min(dates) if dates else None

    def latest_grant(self) -> Optional[date]:
        """En son grant edilen ülke."""
        dates = [m.grant_date for m in self.members if m.grant_date]
        return max(dates) if dates else None

    def jurisdictions(self) -> List[str]:
        return sorted(set(m.jurisdiction for m in self.members))

    def active_jurisdictions(self) -> List[str]:
        return sorted(set(m.jurisdiction for m in self.members if m.status in ("granted", "active", "pending")))

    def expiry_date(self) -> Optional[date]:
        """20 yıl priority'den = expiry (SPC yoksa)."""
        p = self.priority_date()
        if not p:
            return None
        return date(p.year + 20, p.month, p.day)


def parse_date(s: str) -> Optional[date]:
    if not s or s.lower() in ("none", "null", ""):
        return None
    try:
        return datetime.strptime(s.strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def load_families_csv(path: str) -> Dict[str, PatentFamily]:
    """CSV'den aile verisini yükle."""
    families = {}
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            fam_id = row.get('family_id', '').strip()
            if not fam_id:
                continue
            if fam_id not in families:
                families[fam_id] = PatentFamily(family_id=fam_id)
            member = FamilyMember(
                patent_no=row.get('patent_no', '').strip(),
                jurisdiction=row.get('jurisdiction', '').strip().upper(),
                priority_date=parse_date(row.get('priority_date', '')),
                filing_date=parse_date(row.get('filing_date', '')),
                grant_date=parse_date(row.get('grant_date', '')),
                status=row.get('status', 'unknown').strip().lower(),
            )
            families[fam_id].members.append(member)
    return families


def coverage_gap_analysis(family: PatentFamily, target_jurisdictions: List[str]) -> Dict:
    """Ailenin hedef ülkelerdeki coverage boşluklarını tespit et."""
    active = set(family.active_jurisdictions())
    target = set(j.upper() for j in target_jurisdictions)
    covered = active & target
    gaps = target - active
    extra = active - target  # Hedef dışı ama aktif (belki gerekmiyor)
    
    return {
        "target": sorted(target),
        "covered": sorted(covered),
        "gaps": sorted(gaps),
        "extra": sorted(extra),
        "coverage_pct": round(len(covered) / len(target) * 100, 1) if target else 0,
    }


def print_family_summary(families: Dict[str, PatentFamily], target_juris: List[str] = None):
    """Tüm aile envanterini tablo olarak yazdır."""
    print()
    print("═" * 80)
    print(f"  PATENT AİLESİ ÖZET ({len(families)} aile)")
    print("═" * 80)
    
    for fid, fam in sorted(families.items()):
        print(f"\n  📁 {fid}  ({len(fam.members)} üye)")
        p = fam.priority_date()
        e = fam.expiry_date()
        if p:
            print(f"     Priority: {p} → Expiry (teorik): {e}")
        print(f"     Jurisdictions: {', '.join(fam.jurisdictions())}")
        print(f"     Active: {', '.join(fam.active_jurisdictions())}")
        
        if target_juris:
            gap = coverage_gap_analysis(fam, target_juris)
            print(f"     Coverage: {gap['coverage_pct']}% ({', '.join(gap['covered'])})")
            if gap['gaps']:
                print(f"     ⚠ Boşluklar: {', '.join(gap['gaps'])}")
        
        print(f"     Üyeler:")
        for m in fam.members:
            status_icon = {
                "granted": "✓", "active": "✓", "pending": "○",
                "abandoned": "✗", "lapsed": "✗", "revoked": "✗"
            }.get(m.status, "?")
            grant_str = str(m.grant_date) if m.grant_date else "pending"
            print(f"       {status_icon} [{m.jurisdiction:<3}] {m.patent_no:<18} grant:{grant_str:<12} status:{m.status}")
    
    print()
    print("═" * 80)


def generate_mermaid_flowchart(families: Dict[str, PatentFamily]) -> str:
    """Mermaid flowchart formatında aile diyagramı üret."""
    lines = ["flowchart TD"]
    
    for fid, fam in families.items():
        p = fam.priority_date()
        # Priority node
        p_id = f"PRI_{fid}"
        lines.append(f'    {p_id}["<b>{fid}</b><br/>Priority: {p or "?"}"]')
        
        for m in fam.members:
            m_id = f"M_{m.patent_no.replace('/', '_').replace(' ', '_')}"
            style = {
                "granted": ":::granted",
                "active": ":::granted",
                "pending": ":::pending",
                "abandoned": ":::abandoned",
                "lapsed": ":::lapsed",
                "revoked": ":::revoked",
            }.get(m.status, "")
            label = f'{m_id}["{m.jurisdiction}: {m.patent_no}<br/>{m.status}"]{style}'
            lines.append(f'    {p_id} --> {label}')
    
    # Styles
    lines.extend([
        "",
        "    classDef granted fill:#d4f4dd,stroke:#24a148,stroke-width:2px",
        "    classDef pending fill:#fff4d4,stroke:#f1c21b,stroke-width:2px",
        "    classDef abandoned fill:#f5d4d4,stroke:#da1e28,stroke-width:1px,stroke-dasharray: 5 5",
        "    classDef lapsed fill:#e0e0e0,stroke:#525252,stroke-width:1px",
        "    classDef revoked fill:#f5d4d4,stroke:#da1e28,stroke-width:2px",
    ])
    
    return "\n".join(lines)


def generate_coverage_matrix(families: Dict[str, PatentFamily], all_jurisdictions: List[str] = None) -> str:
    """Aile × ülke coverage matrisi (markdown tablo)."""
    if all_jurisdictions is None:
        all_juris = set()
        for f in families.values():
            all_juris |= set(f.jurisdictions())
        all_jurisdictions = sorted(all_juris)
    
    lines = []
    lines.append("| Family | " + " | ".join(all_jurisdictions) + " |")
    lines.append("|" + "---|" * (len(all_jurisdictions) + 1))
    
    for fid, fam in sorted(families.items()):
        row = [fid]
        active = set(fam.active_jurisdictions())
        pending = set(m.jurisdiction for m in fam.members if m.status == "pending")
        abandoned = set(m.jurisdiction for m in fam.members if m.status in ("abandoned", "lapsed", "revoked"))
        for j in all_jurisdictions:
            if j in active and j not in pending:
                row.append("✓")
            elif j in pending:
                row.append("○")
            elif j in abandoned:
                row.append("✗")
            else:
                row.append("—")
        lines.append("| " + " | ".join(row) + " |")
    
    return "\n".join(lines)


def export_json(families: Dict[str, PatentFamily]) -> str:
    """JSON'a serialize et."""
    data = {}
    for fid, fam in families.items():
        data[fid] = {
            "family_id": fid,
            "priority_date": str(fam.priority_date()) if fam.priority_date() else None,
            "expiry_date": str(fam.expiry_date()) if fam.expiry_date() else None,
            "jurisdictions": fam.jurisdictions(),
            "active_jurisdictions": fam.active_jurisdictions(),
            "member_count": len(fam.members),
            "members": [
                {
                    "patent_no": m.patent_no,
                    "jurisdiction": m.jurisdiction,
                    "priority_date": str(m.priority_date) if m.priority_date else None,
                    "filing_date": str(m.filing_date) if m.filing_date else None,
                    "grant_date": str(m.grant_date) if m.grant_date else None,
                    "status": m.status,
                }
                for m in fam.members
            ],
        }
    return json.dumps(data, indent=2, ensure_ascii=False)


def example_families() -> Dict[str, PatentFamily]:
    """Hipotetik örnek: bir onkoloji ilacının 3 patent ailesi."""
    return {
        "FAM-MOL-001": PatentFamily(
            family_id="FAM-MOL-001",
            members=[
                FamilyMember("US9999999", "US", date(2010, 1, 15), date(2011, 1, 10), date(2013, 6, 1), "granted"),
                FamilyMember("EP2123456", "EP", date(2010, 1, 15), date(2011, 1, 10), date(2014, 3, 15), "granted"),
                FamilyMember("TR/EP2123456", "TR", date(2010, 1, 15), date(2011, 1, 10), date(2014, 6, 20), "granted"),
                FamilyMember("JP5555555", "JP", date(2010, 1, 15), date(2011, 1, 10), date(2014, 9, 10), "granted"),
                FamilyMember("CN103123456", "CN", date(2010, 1, 15), date(2011, 1, 10), date(2015, 2, 1), "granted"),
                FamilyMember("BR112012123456", "BR", date(2010, 1, 15), date(2012, 7, 10), None, "abandoned"),
                FamilyMember("IN2012/12345", "IN", date(2010, 1, 15), date(2012, 7, 10), date(2016, 4, 5), "revoked"),
            ],
            notes="Birincil molekül patenti — uluslararası geniş portföy",
        ),
        "FAM-POLYMORPH-002": PatentFamily(
            family_id="FAM-POLYMORPH-002",
            members=[
                FamilyMember("US10123456", "US", date(2012, 5, 20), date(2013, 5, 15), date(2015, 8, 1), "granted"),
                FamilyMember("EP2765432", "EP", date(2012, 5, 20), date(2013, 5, 15), date(2016, 1, 10), "granted"),
                FamilyMember("TR/EP2765432", "TR", date(2012, 5, 20), date(2013, 5, 15), date(2016, 4, 15), "granted"),
                FamilyMember("WO2013/155555", "WO", date(2012, 5, 20), date(2013, 5, 15), None, "pending"),
            ],
            notes="Form II kristal polimorf patenti",
        ),
        "FAM-DEVICE-003": PatentFamily(
            family_id="FAM-DEVICE-003",
            members=[
                FamilyMember("US10987654", "US", date(2015, 3, 10), date(2016, 3, 5), date(2018, 11, 1), "granted"),
                FamilyMember("EP3222222", "EP", date(2015, 3, 10), date(2016, 3, 5), date(2019, 5, 20), "granted"),
                FamilyMember("TR/EP3222222", "TR", date(2015, 3, 10), date(2016, 3, 5), date(2019, 8, 10), "granted"),
            ],
            notes="Prefilled syringe cihaz patenti",
        ),
    }


def main():
    print()
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.4.0 — Patent Family Tracer                           ║")
    print("║  INPADOC-style patent ailesi haritalama + coverage analizi            ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")

    # Load families
    families = None
    if '--example' in sys.argv:
        print("\n📄 Örnek: Hipotetik onkoloji ilacının 3 patent ailesi\n")
        families = example_families()
    elif '--import' in sys.argv:
        try:
            idx = sys.argv.index('--import')
            path = sys.argv[idx + 1]
            print(f"\n📂 CSV import: {path}\n")
            families = load_families_csv(path)
        except (IndexError, FileNotFoundError) as e:
            print(f"❌ Import hatası: {e}")
            sys.exit(1)
    else:
        print("\nKullanım:")
        print("  --example         Örnek portföy ile demo")
        print("  --import <file>   CSV'den yükle")
        print("  --mermaid         Mermaid flowchart çıktısı")
        print("  --json            JSON çıktı")
        print()
        print("CSV format:")
        print("  family_id,patent_no,jurisdiction,priority_date,filing_date,grant_date,status")
        sys.exit(0)

    # Output format
    if '--mermaid' in sys.argv:
        print(generate_mermaid_flowchart(families))
        return
    
    if '--json' in sys.argv:
        print(export_json(families))
        return

    # Default: human-readable özet
    target = ["US", "EP", "TR", "JP", "CN", "BR", "IN"]
    print_family_summary(families, target_juris=target)
    
    # Coverage matrix
    print("\n  COVERAGE MATRİSİ (markdown):\n")
    print(generate_coverage_matrix(families))
    print()


if __name__ == "__main__":
    main()
