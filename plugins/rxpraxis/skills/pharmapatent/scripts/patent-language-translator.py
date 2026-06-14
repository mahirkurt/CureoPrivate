#!/usr/bin/env python3
"""
patent-language-translator.py — Patent İstem Dil Çevirmeni

Patent istemlerindeki "mug-and-jug" teknik-legal jargonu, operasyonel karar
vericiler (BD, stratejist, klinik, CFO) için üç farklı hedefe dönüştürür:

1. OPERATIONAL PLAIN (sade operasyonel dil) — "Bu istem şunu kapsıyor: ..."
2. INFRINGEMENT TEST (ihlal testi soruları) — "Ürün X özelliğine sahip mi?"
3. DESIGN-AROUND HINTS (etrafından dolanma ipuçları) — hangi özelliği
   değiştirmek lafzi ihlali keser

Yaklaşım: Kural tabanlı NLP (LLM/gerçek model gerekmeksizin). Patent dilinde
yaygın kalıpları (wherein, preamble/transition/body, Markush grupları,
fonksiyonel/yapısal tanımlamalar, kapsam sınırlayıcılar) regex + lemma
stratejisi ile ayrıştırır. Kapsamı özetler + açıklar + test soruları üretir.

NOT: Bu yerelleştirilmiş araç gerçek patent vekili/mahkeme kararı yerini almaz.
Hızlı tarama ve ekip eğitimi için uygundur.

Kullanım:
    python3 patent-language-translator.py --example pembrolizumab
    python3 patent-language-translator.py --example semaglutide
    python3 patent-language-translator.py --example markush
    python3 patent-language-translator.py --claim "Bir sıvı farmasötik bileşim..."
    python3 patent-language-translator.py --interactive

Yazar: pharmapatent skill v1.8.0
Bağımlılık: standart kütüphane
"""

import sys
import re
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


# --- Patent dili kalıpları ---

TRANSITION_PHRASES = {
    # Açık uçlu (open-ended)
    "comprising": "içeren",
    "containing": "içeren",
    "including": "dahil",
    "having": "sahip",
    "içeren": "içeren",
    "ihtiva eden": "içeren",
    # Kapalı uçlu (closed)
    "consisting of": "yalnızca şunlardan oluşan",
    "consisting only of": "yalnızca şunlardan oluşan",
    "consisting essentially of": "temelde şunlardan oluşan",
    "esas olarak şunlardan oluşan": "temelde şunlardan oluşan",
}

FUNCTIONAL_LANGUAGE = [
    # "means for X" / "configured to X" — fonksiyonel istem
    r"\bmeans for (\w+ing)\b",
    r"\bconfigured to (\w+)\b",
    r"\badapted to (\w+)\b",
    r"\bşekilde (\w+ için)\b",
]

SCOPE_LIMITERS = [
    # Sayısal aralıklar
    (r"\b(?:from |)(\d+(?:\.\d+)?)\s*(?:to|-|–|ila)\s*(\d+(?:\.\d+)?)\s*(mg|ml|µm|nm|%|w/w|w/v|mM|pH|°C)\b",
     lambda m: f"aralık {m.group(1)}-{m.group(2)} {m.group(3)}"),
    (r"\bat least (\d+(?:\.\d+)?)\s*(mg|ml|µm|nm|%|w/w|w/v|mM|pH|°C)\b",
     lambda m: f"en az {m.group(1)} {m.group(2)}"),
    (r"\bgreater than (\d+(?:\.\d+)?)\s*(mg|ml|%)\b",
     lambda m: f"{m.group(1)} {m.group(2)}'den fazla"),
]

MARKUSH_INDICATORS = [
    r"selected from the group consisting of",
    r"grup (?:dahilinde )?seçilen",
    r"seçenekler aşağıdakilerden oluşur",
]

WHEREIN_PATTERN = re.compile(r"(?:\bwherein\b|;\s*burada|;\s*ki burada|,\s*ki\s+burada)", re.IGNORECASE)

# Farmasötik alan terim sözlüğü (kısaltma → açıklama)
PHARMA_TERM_DICT = {
    "API": "aktif farmasötik madde",
    "w/w": "ağırlıkça",
    "w/v": "hacme karşı ağırlık",
    "DAR": "ilaç-antikor oranı",
    "scFv": "tek zincirli değişken bölge fragmanı",
    "Fc": "kristalize edilebilir bölge (antikor sabit bölgesi)",
    "Fab": "antijen-bağlayan bölge",
    "mAb": "monoklonal antikor",
    "CDR": "tamamlayıcılığı belirleyen bölge",
    "IgG1": "immunoglobulin G alt sınıf 1",
    "IgG4": "immunoglobulin G alt sınıf 4",
    "ADC": "antikor-ilaç konjugatı",
    "CAR-T": "kimerik antijen reseptör T-hücre terapisi",
    "siRNA": "küçük girişim yapan RNA",
    "ASO": "antisense oligonükleotit",
    "GLP-1": "glukagon benzeri peptid-1",
    "PD-1": "programlanmış ölüm-1",
    "PD-L1": "programlanmış ölüm ligand-1",
    "HER2": "insan epidermal büyüme faktörü reseptörü 2",
    "VEGF": "vasküler endotelyal büyüme faktörü",
    "TNF-α": "tümör nekroz faktör alfa",
    "BCMA": "B-hücre olgunlaşma antijeni",
    "LNP": "lipid nanopartikül",
    "AAV": "adeno-ilişkili virüs",
    "CRISPR": "kümelenmiş düzenli aralıklı kısa palindromik tekrarlar",
    "PBD": "pirolobenzodiazepin (ADC yük sınıfı)",
    "MMAE": "monometil auristatin E (ADC yük)",
    "DXd": "exatecan türevi (ADC yük)",
    "SPC": "tamamlayıcı koruma belgesi",
    "EPC": "Avrupa Patent Sözleşmesi",
    "TRIPS": "Ticaretle İlgili Fikri Mülkiyet Hakları Anlaşması",
    "SMK": "Sınai Mülkiyet Kanunu (TR)",
    "TİTCK": "Türkiye İlaç ve Tıbbi Cihaz Kurumu",
    "SGK": "Sosyal Güvenlik Kurumu",
    "SUT": "Sağlık Uygulama Tebliği",
    "FTO": "faaliyet serbestisi",
    "Bolar": "Bolar istisnası (SMK m. 85/3) — ruhsat için deneme",
}


@dataclass
class Feature:
    """Ayrıştırılmış istem özelliği."""
    id: str                   # F1, F2, F3...
    raw_text: str             # Orijinal metin parçası
    category: str             # active_ingredient / excipient / physical_form / concentration / pH / process / use / device / stability
    plain_turkish: str        # Sade Türkçe çeviri
    infringement_test: str    # "Ürün bu özelliğe sahip mi?" sorusu
    design_around: str        # Bu özelliği nasıl değiştirmek lafzi ihlali keser
    is_markush: bool = False
    markush_members: List[str] = field(default_factory=list)


@dataclass
class ClaimAnalysis:
    original: str
    preamble: str             # "Bir sıvı farmasötik bileşim..."
    transition: str           # comprising / consisting of
    transition_scope: str     # open / closed / intermediate
    features: List[Feature]
    overall_plain: str        # Bütüncül sade özet
    jurisdiction_hints: List[str]


# --- Çekirdek parser ---

def expand_pharma_terms(text: str) -> str:
    """Kısaltmaları açıkla."""
    result = text
    for abbr, expansion in PHARMA_TERM_DICT.items():
        pattern = r'\b' + re.escape(abbr) + r'\b'
        result = re.sub(pattern, f"{abbr} ({expansion})", result, count=1)
    return result


def detect_transition(claim: str) -> tuple:
    """Transition cümlesini tespit et + kapsamı sınıflandır."""
    claim_lower = claim.lower()
    
    # Closed transitions first (daha spesifik)
    if "consisting essentially of" in claim_lower or "temelde şunlardan oluşan" in claim_lower:
        return ("consisting essentially of", "intermediate")
    if "consisting of" in claim_lower or "yalnızca" in claim_lower:
        return ("consisting of", "closed")
    
    # Open transitions
    for term in ["comprising", "containing", "including", "having", "içeren", "ihtiva eden"]:
        if term in claim_lower:
            return (term, "open")
    
    return ("unknown", "unknown")


def split_claim_structure(claim: str) -> Dict:
    """İstem yapısını preamble / transition / body olarak ayır."""
    transition_term, scope = detect_transition(claim)
    
    parts = {
        "preamble": "",
        "transition": transition_term,
        "transition_scope": scope,
        "body": "",
    }
    
    if transition_term != "unknown":
        # Transition'ı büyük/küçük harf duyarsız bul, böl
        pattern = re.compile(re.escape(transition_term), re.IGNORECASE)
        match = pattern.search(claim)
        if match:
            parts["preamble"] = claim[:match.start()].strip().rstrip(',').strip()
            parts["body"] = claim[match.end():].strip()
    else:
        parts["body"] = claim
    
    return parts


def classify_feature(text: str) -> str:
    """Bir özellik metnini kategoriye ata."""
    t = text.lower()
    
    # Süreçler (genellikle fiil içerir)
    if any(kw in t for kw in ["wherein said", "wherein the", "prepared by", "obtained by", "synthesized"]):
        return "process"
    
    # Aktif madde - peptid/molekül sinyali
    if any(kw in t for kw in ["semaglutide", "pembrolizumab", "trastuzumab", "mab", "peptide", "antibody", "antikor", "molecule"]):
        return "active_ingredient"
    if re.search(r'\bSEQ ID NO\b', text, re.IGNORECASE):
        return "active_ingredient"
    
    # Konsantrasyon / doz
    if re.search(r'\d+\s*(mg|ml|µg|µm|mm|%|w/w|w/v)', t):
        return "concentration"
    
    # pH
    if "ph" in t and re.search(r'\d', t):
        return "pH"
    
    # Fiziksel form / formülasyon
    if any(kw in t for kw in ["tablet", "capsule", "solution", "suspension", "lyophilized", "crystalline", "amorphous", "polymorph", "nanoparticle"]):
        return "physical_form"
    
    # Eksipiyan
    if any(kw in t for kw in ["buffer", "tampon", "histidine", "sucrose", "polysorbate", "surfactant", "stabilizer", "preservative"]):
        return "excipient"
    
    # Kullanım / tıbbi endikasyon (Swiss-type veya 2. tıbbi kullanım)
    if any(kw in t for kw in ["for treatment of", "for use in treating", "for treating", "use of", "tedavisinde kullanım", "tedavisi için"]):
        return "use"
    
    # Cihaz
    if any(kw in t for kw in ["auto-injector", "pen", "device", "cihaz", "delivery system", "needle"]):
        return "device"
    
    # Stabilite
    if any(kw in t for kw in ["stable", "stability", "shelf life", "stabil", "raf ömrü"]):
        return "stability"
    
    return "other"


def extract_markush_members(text: str) -> List[str]:
    """Markush grubu üyelerini çıkart."""
    # "selected from the group consisting of A, B, C, and D"
    pattern = re.compile(
        r"(?:selected from the group consisting of|grup(?:tan| dahilinde)? seçilen)\s+([^.;]+?)(?:\.|\;|$|wherein|ki burada)",
        re.IGNORECASE
    )
    match = pattern.search(text)
    if match:
        members_raw = match.group(1)
        # A, B, C, and D → ['A', 'B', 'C', 'D']
        members = re.split(r",\s*(?:and\s+)?|\s+and\s+|\s+ve\s+", members_raw)
        return [m.strip() for m in members if m.strip()]
    return []


def generate_plain_turkish(raw_text: str, category: str) -> str:
    """Bir özellik için sade Türkçe açıklama üret."""
    text = raw_text.strip()
    
    templates = {
        "active_ingredient": f"ÜRÜNÜN AKTİF MADDESİ: {text}",
        "excipient": f"Yardımcı madde: {text}",
        "concentration": f"Miktar/oran: {text}",
        "pH": f"pH koşulu: {text}",
        "physical_form": f"Fiziksel form: {text}",
        "process": f"Üretim yöntemi: {text}",
        "use": f"Tıbbi kullanım: {text}",
        "device": f"Cihaz özelliği: {text}",
        "stability": f"Stabilite koşulu: {text}",
        "other": f"Özellik: {text}",
    }
    
    return templates.get(category, f"Özellik: {text}")


def generate_infringement_test(feature: Feature) -> str:
    """Özellik için ihlal testi sorusu üret."""
    cat = feature.category
    
    templates = {
        "active_ingredient": f"Test: Ürün, bu aktif maddeyi (veya immatériel eşdeğerini) içeriyor mu? ({feature.raw_text[:80]}...)",
        "excipient": f"Test: Ürün bu yardımcı maddeye sahip mi? Alternatif yardımcı madde ile değişim mümkün mü?",
        "concentration": f"Test: Ürün bu konsantrasyon/doz aralığında mı? Aralık dışı bir formülasyon lafzi ihlali keser.",
        "pH": f"Test: Ürünün pH'ı bu aralıkta mı? Dışına çıkmak lafzi ihlali keser.",
        "physical_form": f"Test: Ürün bu fiziksel formda mı? (tablet/solüsyon/lyofilize vb.)",
        "process": f"Test: Ürün bu üretim sürecini kullanıyor mu? Alternatif süreç ile üretim ihlali keser.",
        "use": f"Test: Ürün bu endikasyonda mı kullanılıyor? Off-label kullanım Swiss-type tartışması açar.",
        "device": f"Test: Cihaz bu özelliklere sahip mi? Farklı cihaz tasarımı ile design-around yapılabilir.",
        "stability": f"Test: Ürün bu stabilite koşulunu karşılıyor mu?",
        "other": f"Test: Ürün bu özelliği taşıyor mu?",
    }
    
    base = templates.get(cat, f"Test: Ürün bu özelliği taşıyor mu? ({feature.raw_text[:80]})")
    
    if feature.is_markush and feature.markush_members:
        members_preview = ", ".join(feature.markush_members[:3])
        base += f"\n  (Markush üyeleri: {members_preview}... Ürün listedeki HANGİ üyeyi içeriyor?)"
    
    return base


def generate_design_around(feature: Feature) -> str:
    """Etrafından dolanma önerisi üret."""
    cat = feature.category
    
    templates = {
        "active_ingredient": "Farklı aktif madde veya bambaşka sınıf ile değiştirin (genelde sert kısıt — temel molekül patent).",
        "excipient": "Alternatif yardımcı madde kullanın (citrate → histidine gibi). Orta zorluk.",
        "concentration": "Aralık dışı konsantrasyon formüle edin. En kolay design-around yollarından biri.",
        "pH": "İstem aralığı dışında pH tasarlayın. Çoğu durumda mümkün.",
        "physical_form": "Farklı form (tablet → kapsül, solüsyon → lyofilize) tercih edin.",
        "process": "Alternatif üretim sürecine geçin. Süreç patenti sadece süreci korur — ürün aynı olsa bile farklı süreç ihlali önler.",
        "use": "Farklı endikasyon veya off-label kullanım (ikinci tıbbi kullanım patenti için özellikle dikkatli olun).",
        "device": "Farklı cihaz (auto-injector → viyal + şırınga, özel pen tasarımı).",
        "stability": "Farklı stabilite profili/ raf ömrü özelliği — genellikle ürün değişikliği gerekir.",
        "other": "Bu özellik etrafından dolanma fizibilitesini patent vekili ile değerlendirin.",
    }
    
    return templates.get(cat, "Özellik etrafından dolanma fizibilitesini patent vekili ile değerlendirin.")


def split_body_into_features(body: str) -> List[str]:
    """Body metnini özellik parçalarına böl."""
    # Wherein bölücüleri kullan
    wherein_splits = WHEREIN_PATTERN.split(body)
    
    all_parts = []
    for chunk in wherein_splits:
        # Chunk içindeki virgül/ ";"/ ")" bazlı alt bölümleri de ayır
        # Sadece üst düzey ayırıcılar (parantez derinliği 0)
        parts = []
        current = []
        paren_depth = 0
        for ch in chunk:
            if ch == "(":
                paren_depth += 1
            elif ch == ")":
                paren_depth -= 1
            if (ch == ";" or (ch == "," and paren_depth == 0 and len(current) > 40)) and paren_depth == 0:
                parts.append("".join(current).strip())
                current = []
            else:
                current.append(ch)
        if current:
            parts.append("".join(current).strip())
        
        all_parts.extend([p for p in parts if len(p) > 5])
    
    return all_parts


def analyze_claim(claim: str) -> ClaimAnalysis:
    """Bir istemi tam ayrıştır + Türkçeleştir."""
    structure = split_claim_structure(claim)
    feature_texts = split_body_into_features(structure["body"])
    
    features = []
    for i, ft in enumerate(feature_texts, 1):
        cat = classify_feature(ft)
        markush_members = extract_markush_members(ft)
        is_markush = len(markush_members) > 0
        
        feature = Feature(
            id=f"F{i}",
            raw_text=ft[:300],  # Truncate for safety
            category=cat,
            plain_turkish=generate_plain_turkish(ft, cat),
            infringement_test="",
            design_around="",
            is_markush=is_markush,
            markush_members=markush_members,
        )
        feature.infringement_test = generate_infringement_test(feature)
        feature.design_around = generate_design_around(feature)
        features.append(feature)
    
    # Jurisdiction hints
    hints = []
    if "consisting of" in structure["transition"]:
        hints.append("Kapalı uçlu transition → istem içeriğinin listedekilerle sınırlı yorumlanması beklenir")
    elif structure["transition_scope"] == "open":
        hints.append("Açık uçlu transition (comprising) → listelenen özellikler asgari; ek özellikler de kapsam içinde kalabilir")
    
    if any(f.is_markush for f in features):
        hints.append("Markush grubu tespit edildi → her üye ayrı ayrı değerlendirilmeli; hedef ürünün hangi üyeyi içerdiği lafzi ihlal için kritik")
    
    if any(f.category == "process" for f in features):
        hints.append("Süreç özelliği tespit edildi → sadece süreci korur (SMK m. 85/2: ürün piyasa geniş ama süreç patent süreç ile bağlı)")
    
    if any(f.category == "use" for f in features):
        hints.append("Kullanım / 2. tıbbi kullanım ögeleri → Swiss-type yorumunun TR'de kabulü değişken; off-label kullanım ihlal tartışması")
    
    # Overall plain summary
    overall = f"Bu istem, '{structure['preamble'][:80]}...' için bir koruma talep ediyor ve aşağıdaki {len(features)} özelliği belirtiyor:\n"
    overall += "\n".join([f"  - {f.id}: {f.plain_turkish[:100]}" for f in features[:6]])
    if len(features) > 6:
        overall += f"\n  ... ve {len(features)-6} daha."
    
    return ClaimAnalysis(
        original=claim,
        preamble=structure["preamble"],
        transition=structure["transition"],
        transition_scope=structure["transition_scope"],
        features=features,
        overall_plain=overall,
        jurisdiction_hints=hints,
    )


# --- Örnek veri ---

EXAMPLES = {
    "pembrolizumab": """A pharmaceutical composition comprising pembrolizumab at a concentration of from 15 mg/mL to 35 mg/mL, histidine buffer at a concentration of 10 mM, polysorbate 80 at 0.02% w/v, and sucrose at 7% w/v, wherein the pH is in the range of 5.5 to 6.0, and wherein the composition is stable for at least 24 months at 2-8°C, and wherein said composition is administered intravenously for the treatment of non-small cell lung cancer.""",
    
    "semaglutide": """A peptide composition comprising:
(a) N-terminal(ε)-[(S)-(2-[2-(2-amino-ethoxy)-ethoxy]-acetyl)-(γGlu)-(17-carboxyheptadecanoyl)]Lys26 modified GLP-1(7-37) analogue;
(b) wherein Aib at position 8;
(c) wherein the peptide is presented in a liquid formulation at a concentration of 1 mg/0.74 mL;
(d) wherein said composition is packaged in a pre-filled single-use auto-injector device;
and wherein the composition is used for the treatment of type 2 diabetes mellitus.""",
    
    "markush": """A compound of Formula (I) selected from the group consisting of atorvastatin, rosuvastatin, simvastatin, pravastatin, and fluvastatin, wherein said compound is present in a tablet formulation at a concentration of 5 mg to 80 mg, together with a pharmaceutically acceptable excipient selected from microcrystalline cellulose, lactose, and magnesium stearate, wherein the tablet is coated with a film coating comprising hypromellose.""",
    
    "adc": """An antibody-drug conjugate comprising:
(a) a humanized anti-HER2 antibody comprising a heavy chain of SEQ ID NO: 1 and a light chain of SEQ ID NO: 2;
(b) a cleavable linker connecting said antibody to a cytotoxic payload;
(c) wherein said cytotoxic payload is a topoisomerase I inhibitor selected from the group consisting of exatecan, SN-38, and DXd derivatives;
(d) wherein the drug-to-antibody ratio (DAR) is from 6 to 8;
wherein said conjugate is used for treating HER2-positive breast cancer.""",
}


# --- Çıktı formatları ---

def print_markdown_analysis(analysis: ClaimAnalysis):
    print()
    print("# Patent İstem Dil Çevirmeni — Analiz Sonucu")
    print()
    print("## Orijinal İstem")
    print()
    print(f"> {analysis.original[:500]}{'...' if len(analysis.original) > 500 else ''}")
    print()
    
    print("## Yapısal Ayrıştırma")
    print()
    print(f"- **Preamble**: {analysis.preamble}")
    print(f"- **Transition**: `{analysis.transition}` ({analysis.transition_scope})")
    print(f"- **Özellik sayısı**: {len(analysis.features)}")
    print()
    
    print("## Bütüncül Sade Özet")
    print()
    print(analysis.overall_plain)
    print()
    
    if analysis.jurisdiction_hints:
        print("## Hukuki Notlar")
        print()
        for h in analysis.jurisdiction_hints:
            print(f"- {h}")
        print()
    
    print("## Özellik-Özellik Tablosu")
    print()
    print("| ID | Kategori | Sade Türkçe | İhlal Testi | Design-Around |")
    print("|---|---|---|---|---|")
    for f in analysis.features:
        plain_short = f.plain_turkish[:60].replace("|", "/").replace("\n", " ")
        test_short = f.infringement_test[:60].replace("|", "/").replace("\n", " ")
        da_short = f.design_around[:50].replace("|", "/").replace("\n", " ")
        markush_tag = " ⚡ Markush" if f.is_markush else ""
        print(f"| {f.id}{markush_tag} | {f.category} | {plain_short}... | {test_short}... | {da_short}... |")
    print()
    
    # Markush detayları
    markush_features = [f for f in analysis.features if f.is_markush]
    if markush_features:
        print("## Markush Grupları Detayı")
        print()
        for f in markush_features:
            print(f"- **{f.id}**: {len(f.markush_members)} üye — {', '.join(f.markush_members)}")
        print()


def print_json(analysis: ClaimAnalysis):
    data = asdict(analysis)
    print(json.dumps(data, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Patent Language Translator v1.8.0")
    parser.add_argument('--example', type=str, help="Örnek: pembrolizumab, semaglutide, markush, adc")
    parser.add_argument('--claim', type=str, help="İstem metni (quote'lu)")
    parser.add_argument('--format', default='markdown', choices=['markdown', 'json'])
    parser.add_argument('--list-examples', action='store_true')
    
    args = parser.parse_args()
    
    if args.list_examples:
        print("\nMevcut örnekler:")
        for name, claim in EXAMPLES.items():
            print(f"  {name:<15} ({len(claim)} char)")
        return
    
    if not (args.example or args.claim):
        print()
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║  pharmapatent v1.8.0 — Patent İstem Dil Çevirmeni                 ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print()
        print("Kullanım:")
        print("  --example pembrolizumab      Antikor formülasyon")
        print("  --example semaglutide        Peptid + cihaz")
        print("  --example markush            Statin Markush grup")
        print("  --example adc                ADC + DAR + Markush payload")
        print("  --claim \"A composition...\"   Özel istem metni")
        print("  --format markdown | json")
        return
    
    if args.example:
        if args.example not in EXAMPLES:
            print(f"❌ Bilinmeyen örnek: {args.example}")
            sys.exit(1)
        claim_text = EXAMPLES[args.example]
    else:
        claim_text = args.claim
    
    analysis = analyze_claim(claim_text)
    
    if args.format == 'json':
        print_json(analysis)
    else:
        print_markdown_analysis(analysis)


if __name__ == "__main__":
    main()
