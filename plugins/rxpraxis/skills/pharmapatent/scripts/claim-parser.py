#!/usr/bin/env python3
"""
claim-parser.py — Patent istem metnini özelliklere ayrıştırır

Bir bağımsız istem metnini girdi olarak alıp:
1. Özellikleri (features) otomatik tespit eder
2. Numaralı özellik listesi (F1, F2, ...) üretir
3. Her özelliğin teknik kategorisini tahmin eder (active_ingredient, excipient, physical_form, range, process, use)
4. FTO/Invalidity özellik-özellik matris tablosunun kolon başlıklarını hazırlar

Kullanım:
    python3 claim-parser.py              # interactive
    python3 claim-parser.py --example    # trastuzumab örneği ile demo

Yazar: pharmapatent skill v1.1.0
Lisans: Internal use.
"""

import re
import sys
from dataclasses import dataclass, field
from typing import List


# --- Categorization patterns (Turkish + English) ---
CATEGORY_PATTERNS = {
    'active_ingredient': [
        r'\b(comprising|compris\w+|içeren|kapsayan)\b.*?(\w+mab|\w+ib|\w+statin|\w+zumab|\w+omer|antibody|antikor|peptide|peptid|compound|bileşen|bileşik)',
        r'\b(trastuzumab|atorvastatin|semaglutide|pembrolizumab|rituximab|infliximab|adalimumab|nivolumab)\b',
    ],
    'excipient': [
        r'\b(trehalose|trehaloz|mannitol|sucrose|sukroz|lactose|laktoz|histidine|histidin|polysorbate|polisorbat|tween|cellulose|selüloz|MCC|PVP|povidone|silica|silika|stearate|stearat|croscarmellose|kroskarmeloz)\b',
        r'\b(excipient|yardımcı madde|eksipiyan|buffer|tampon|carrier|taşıyıcı|stabilizer|stabilizatör)\b',
    ],
    'physical_form': [
        r'\b(tablet|capsule|kapsül|lyophilized|liyofilize|freeze[- ]dried|solution|çözelti|suspension|süspansiyon|injection|enjeksiyon|infusion|infüzyon|powder|toz|crystal\w*|kristalin|amorphous|amorf|microsphere|mikroküre|nanoparticle|nanopartikül)\b',
    ],
    'concentration_range': [
        r'(\d+(?:\.\d+)?)\s*(?:-|to|–|ila)\s*(\d+(?:\.\d+)?)\s*(%|mg/mL|mg/ml|mg|μg|ug|IU|w/w|w/v|v/v|ppm|mol|mM)',
    ],
    'ph_range': [
        r'pH\s*(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)',
    ],
    'process_step': [
        r'\b(mixing|karıştırma|heating|ısıtma|cooling|soğutma|filtration|filtrasyon|crystallization|kristalleşme|compression|kompresyon|lyophilization|liyofilizasyon|sterilization|sterilizasyon)\b',
    ],
    'use_or_treatment': [
        r'\b(for (the )?treatment of|tedavisi için|in the treatment of|use of|kullanım|kullanılan|for administering|uygulama için|for preventing|önleme için)\b',
        r'\b(for use in|için kullanım|indication|endikasyon)\b',
    ],
    'device': [
        r'\b(syringe|enjektör|auto[- ]?injector|oto[- ]?enjektör|pen|kalem|inhaler|inhalör|pump|pompa|stent|catheter|kateter|implant|prefilled|önceden dolu)\b',
    ],
    'stability_criterion': [
        r'<\s*(\d+(?:\.\d+)?)\s*%\s*(aggregation|agregasyon|degradation|bozulma|impuri\w*|safsızlık)',
        r'\bstable for\s*(\d+)\s*(months?|years?|ay|yıl)',
        r'\b(\d+)\s*(months?|years?|ay|yıl)\s*(?:at|stabilite)',
    ],
}


@dataclass
class Feature:
    """Bir patent istem özelliği."""
    id: str           # F1, F2, ...
    text: str         # Ham metin
    category: str     # active_ingredient, excipient, ...
    normalized: str   # Kısa özet


def clean_claim_text(raw: str) -> str:
    """İstem metnini normalize et."""
    # Başındaki numara/bullet'ı kaldır
    raw = re.sub(r'^(Claim\s*\d+[:.]?\s*|İstem\s*\d+[:.]?\s*|\d+[.)]\s*)', '', raw, flags=re.IGNORECASE)
    # Fazla beyaz alanı sıkıştır
    raw = re.sub(r'\s+', ' ', raw).strip()
    return raw


def split_into_clauses(claim: str) -> List[str]:
    """İstem metnini alt-maddelere ayır.
    
    Tipik istem yapısı: giriş paragrafı + noktalı virgül veya (a), (b), (c) işaretleriyle ayrılmış alt maddeler.
    """
    # Önce (a) (b) (c) benzeri paragraflar
    letter_pattern = re.compile(r'\([a-z]\)\s*')
    if letter_pattern.search(claim):
        parts = letter_pattern.split(claim)
        parts = [p.strip() for p in parts if p.strip()]
        return parts

    # Noktalı virgül ile ayrılan listeler
    if ';' in claim:
        parts = [p.strip() for p in claim.split(';') if p.strip()]
        return parts

    # "comprising A, B, and C" → virgül + and/ve
    compris_match = re.search(r'(?:comprising|compris\w+|içeren|kapsayan)\s+(.+)', claim, re.IGNORECASE)
    if compris_match:
        listing = compris_match.group(1)
        # split on , and "and"/"ve"/"veya"
        parts = re.split(r',\s*(?:and|ve)?\s*|\sand\s|\sve\s', listing)
        parts = [p.strip() for p in parts if p.strip()]
        # İlk clause'a da ana introa ekle
        intro = claim[:compris_match.start()].strip()
        if intro:
            return [intro] + parts
        return parts

    # Fallback: tek clause
    return [claim]


def categorize_clause(clause: str) -> str:
    """Bir clause'un kategorisini tahmin et."""
    for cat, patterns in CATEGORY_PATTERNS.items():
        for p in patterns:
            if re.search(p, clause, re.IGNORECASE):
                return cat
    return 'other'


def normalize_clause(clause: str, max_chars: int = 60) -> str:
    """Clause için kısa, özetleyici bir ad üret."""
    # İlk content-bearing 8-10 kelimeyi al
    words = clause.split()
    # Stop words'leri temizle
    stop = {'a', 'an', 'the', 'of', 'in', 'by', 'as', 'and', 've', 'bir', 'ile', 've'}
    keywords = [w for w in words if w.lower().strip(',.();:') not in stop][:10]
    normalized = ' '.join(keywords)
    if len(normalized) > max_chars:
        normalized = normalized[:max_chars - 3] + '...'
    return normalized


def parse_claim(claim_text: str) -> List[Feature]:
    """Bir bağımsız istem metnini özelliklere ayrıştır."""
    claim = clean_claim_text(claim_text)
    clauses = split_into_clauses(claim)

    features = []
    for i, clause in enumerate(clauses, 1):
        feature = Feature(
            id=f'F{i}',
            text=clause,
            category=categorize_clause(clause),
            normalized=normalize_clause(clause),
        )
        features.append(feature)

    return features


def print_feature_table(features: List[Feature]):
    """Özellik listesini tablo olarak yazdır."""
    print()
    print("═" * 100)
    print(f"  ÖZELLİK-ÖZELLİK AYRIŞTIRMASI ({len(features)} özellik)")
    print("═" * 100)
    print(f"  {'ID':<5} {'Kategori':<22} {'Özet':<48} ")
    print(f"  {'-' * 5} {'-' * 22} {'-' * 48}")
    for f in features:
        print(f"  {f.id:<5} {f.category:<22} {f.normalized:<48}")
    print("═" * 100)
    print()


def print_fto_matrix_template(features: List[Feature]):
    """FTO özellik-özellik matrisi şablonunu yazdır (markdown formatı)."""
    print("### Özellik-özellik eşleştirme (FTO/Invalidity Matrisi Şablonu)")
    print()
    print("| Özellik | İstem | Hedef ürün | Eşleşme | Not |")
    print("|---|---|---|---|---|")
    for f in features:
        print(f"| **{f.id}** {f.normalized[:35]} | {f.text[:50]}... | [HEDEF] | [EVET/HAYIR] | [açıklama] |")
    print()


def print_detailed_features(features: List[Feature]):
    """Her özelliğin tam metnini yazdır."""
    print("### Özellik Detayları")
    for f in features:
        print(f"\n**{f.id}** ({f.category})")
        print(f"  Tam metin: {f.text}")


# --- Example demo ---
EXAMPLE_TRASTUZUMAB = """
A stabilized lyophilized pharmaceutical formulation comprising:
(a) trastuzumab in an amount of 10-200 mg/mL upon reconstitution,
(b) trehalose dihydrate in an amount of 50-300 mg/mL,
(c) L-histidine buffer at pH 5.5-6.5,
(d) polysorbate 80 in an amount of 0.01-0.1% (w/v),
wherein the formulation exhibits <5% aggregation after 24 months at 2-8°C.
""".strip()


def main():
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.1.0 — Patent İstem Ayrıştırıcı (Claim Parser)      ║")
    print("║  Bağımsız istem metnini özelliklere (F1, F2, ...) ayrıştırır        ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()

    if '--example' in sys.argv:
        print("📄 Örnek: Hipotetik trastuzumab formülasyon istemi\n")
        print("GİRDİ:")
        print(EXAMPLE_TRASTUZUMAB)
        features = parse_claim(EXAMPLE_TRASTUZUMAB)
        print_feature_table(features)
        print_fto_matrix_template(features)
        print_detailed_features(features)
        return

    # Interactive
    print("İstem metnini girin (birden fazla satır için boş satırla bitirin):")
    print("Örnek için Ctrl+D veya boş giriş + --example argümanıyla çalıştırın.\n")
    lines = []
    try:
        while True:
            line = input()
            if not line and lines:
                break
            if not line:
                continue
            lines.append(line)
    except EOFError:
        pass
    except KeyboardInterrupt:
        print("\n⏹ İptal.")
        sys.exit(0)

    claim_text = ' '.join(lines)
    if not claim_text.strip():
        print("❌ Boş istem metni.")
        sys.exit(1)

    features = parse_claim(claim_text)
    print_feature_table(features)
    print_fto_matrix_template(features)
    print_detailed_features(features)


if __name__ == '__main__':
    main()
