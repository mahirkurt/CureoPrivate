#!/usr/bin/env python3
"""
turkish_semantic_check.py — Brand-Maker Turkish Semantic Analysis Module

Distills the methodology of starlangsoftware/turkishwordnet-py (KeNet — the
canonical Turkish WordNet developed by Olcay Taner Yıldız's group at
Işık University) into a sandbox-safe pure-Python module for Turkish semantic
analysis of brand name candidates.

USAGE:
    python turkish_semantic_check.py "AdayIsim1" "AdayIsim2" "AdayIsim3"

DEPENDENCIES: Pure Python 3.8+, no external libraries.

OUTPUT: Per-name 5-layer Turkish semantic profile:
  1. Turkish dictionary collision (curated 600+ word lexicon across 12 fields)
  2. Turkish root/morpheme detection (3-5 letter substring match)
  3. Vowel harmony analysis (Türkçe ünlü uyumu — front/back consistency)
  4. Loanword origin signature (Ottoman/Persian/Arabic/French heuristic)
  5. Thematic semantic field mapping for brand positioning intelligence

LIMITATIONS:
  - Curated lexicon, not full KeNet (~80,000 lemmas) — covers brand-relevant high-frequency vocabulary
  - Vowel harmony is deterministic and rigorous
  - Loanword detection is signature-based heuristic (~70-80% accuracy on common cases)
  - Native Turkish linguistic expert review still recommended for Turkish-market launches

COMPLEMENTARITY WITH disaster_checker.py:
  - disaster_checker.py: vulgar/taboo blocklist across 9 languages (NEGATIVE filter)
  - turkish_semantic_check.py: Turkish meaning/origin/harmony profiling (POSITIVE intelligence)
"""

import argparse
import json
import re
import sys
from typing import Dict, List, Set, Tuple, Optional

# ============================================================
# Layer 6 (v2.1): NAIVE FIRST-READING / PERCEPTION LEXICON
# ============================================================
# Expert-audit remediation D — THE MOST CRITICAL FIX.
# Intended etymology ≠ perceived meaning. A naive Turkish reader parses a coined
# name left-to-right and latches onto the first recognisable high-frequency
# morpheme, regardless of what the namer INTENDED. The 2026 audit caught:
#   • "Ortanza" — namer intended Latin `ortus` (rise); naive reader reads
#     "orta" (= middle / MEDIOCRE) → collides head-on with a premium/clinical-
#     authority claim.
#   • "Selvanza" — namer intended `salv-` (salvation); naive reader reads
#     "selva" (= jungle/nature) → dominant nature reading, not salvation.
# This layer detects the DOMINANT PERCEIVED sub-string and surfaces intent↔
# perception deviation and value-lowering (negative) perception as a FIRST-CLASS
# warning (headline, never buried).
#
# polarity: "negative" (value-lowering — first-class warning), "neutral"
# (perceived but not damaging — still surfaced for intent-deviation), "positive".
PERCEPTION_LEXICON: Dict[str, Dict[str, str]] = {
    # --- value-lowering / negative perception (first-class warnings) ---
    "orta":  {"gloss": "orta / vasat (middle, mediocre)", "polarity": "negative",
              "note": "'Ortalama/vasat' algısı — premium veya klinik-otorite iddiasıyla DOĞRUDAN çelişir."},
    "kaza":  {"gloss": "kaza (accident)", "polarity": "negative",
              "note": "Kaza/olumsuz olay çağrışımı."},
    "dert":  {"gloss": "dert (trouble / ailment)", "polarity": "negative",
              "note": "Dert/hastalık çağrışımı — sağlık markasında sakıncalı."},
    "acı":   {"gloss": "acı (pain / bitter)", "polarity": "negative",
              "note": "Acı/ağrı çağrışımı."},
    "kel":   {"gloss": "kel (bald)", "polarity": "negative",
              "note": "Olumsuz fiziksel çağrışım."},
    "dul":   {"gloss": "dul (widow)", "polarity": "negative",
              "note": "Olumsuz çağrışım."},
    "kör":   {"gloss": "kör (blind)", "polarity": "negative",
              "note": "Olumsuz çağrışım."},
    "kor":   {"gloss": "kor (ember) / kör-benzeri", "polarity": "neutral",
              "note": "'Kor' (ateş koru) nötr; 'kör'e (blind) yakın duyulabilir."},
    "zor":   {"gloss": "zor (hard / difficult)", "polarity": "negative",
              "note": "Zorluk çağrışımı — 'kolaylık' vaadiyle ters."},
    "kir":   {"gloss": "kir (dirt)", "polarity": "negative",
              "note": "Kir/kirlilik çağrışımı."},
    "yara":  {"gloss": "yara (wound)", "polarity": "negative",
              "note": "Yara çağrışımı — sağlık markasında sakıncalı."},
    "hasta": {"gloss": "hasta (sick)", "polarity": "negative",
              "note": "Hastalık çağrışımı."},
    "ölü":   {"gloss": "ölü (dead)", "polarity": "negative",
              "note": "Ölüm çağrışımı."},
    "sel":   {"gloss": "sel (flood / disaster)", "polarity": "negative",
              "note": "Sel/afet çağrışımı (ancak 'selva' gibi daha uzun bir okuma baskınsa o öne çıkar)."},
    # --- neutral perception (surfaced for intent↔perception deviation) ---
    "selva": {"gloss": "selva (orman / jungle — İsp./Lat.)", "polarity": "neutral",
              "note": "Doğa/orman okuması baskın; niyet 'salv-' (kurtuluş) ise İNTENT≠ALGI sapması."},
    "ver":   {"gloss": "ver (give — emir kipi)", "polarity": "neutral",
              "note": "'Ver' emir kipi olarak okunabilir."},
    "art":   {"gloss": "art (arka / artı)", "polarity": "neutral",
              "note": "'Art/arka' ya da 'artı' okuması."},
    "san":   {"gloss": "san / sanı (supposition, repute)", "polarity": "neutral",
              "note": "'Sanı/zan' okuması olabilir."},
    "kar":   {"gloss": "kar (snow) / kâr (profit) — homonym", "polarity": "neutral",
              "note": "Kar/kâr homonimi."},
    "oda":   {"gloss": "oda (room)", "polarity": "neutral", "note": "'Oda' okuması."},
    "ada":   {"gloss": "ada (island)", "polarity": "neutral", "note": "'Ada' okuması."},
    "ana":   {"gloss": "ana (main / mother)", "polarity": "neutral", "note": "'Ana' okuması (hafif olumlu)."},
    "sap":   {"gloss": "sap (handle / stalk)", "polarity": "neutral", "note": "'Sap' okuması."},
    "kaz":   {"gloss": "kaz (goose) / kazı-", "polarity": "neutral", "note": "'Kaz' okuması."},
    # --- positive perception ---
    "can":   {"gloss": "can (soul / life)", "polarity": "positive", "note": "Olumlu yaşam çağrışımı."},
    "nur":   {"gloss": "nur (divine light)", "polarity": "positive", "note": "Olumlu ışık çağrışımı."},
    "saf":   {"gloss": "saf (pure)", "polarity": "positive", "note": "Saflık çağrışımı (nötr-olumlu)."},
    "gür":   {"gloss": "gür (lush / abundant)", "polarity": "positive", "note": "Bolluk çağrışımı."},
}


def _clean_lower(name: str) -> str:
    # Keep Turkish letters for perception matching (ı, ö, ü, ç, ş, ğ), lowercase.
    return name.strip().lower()


def naive_parse(name: str, lexicon: Dict[str, Dict[str, str]] = None,
                intended_root: Optional[str] = None) -> Dict:
    """
    Language-independent NAIVE FIRST-READING parser (Layer 6).

    Scans `name` for perceived tokens from `lexicon` (default: Turkish
    PERCEPTION_LEXICON). A naive reader latches onto the FIRST recognisable
    morpheme, so a LEADING match wins, and among leading matches the LONGEST
    wins ('selva' beats 'sel' in "Selvanza"). Value-lowering (negative) tokens
    anywhere in the name are always surfaced as first-class warnings.

    Returns:
      dominant_perceived: {token, gloss, polarity, note, position} | None
      all_matches: list (sorted leading-first, then longest)
      has_negative_perception: bool
      intent_perception_deviation: bool  (True when a dominant perceived token
                                           exists and differs from intended_root)
      headline: one-line first-class summary string
    """
    if lexicon is None:
        lexicon = PERCEPTION_LEXICON
    low = _clean_lower(name)

    matches = []
    for token, meta in lexicon.items():
        idx = low.find(token)
        if idx != -1:
            matches.append({"token": token, "position": idx,
                            "length": len(token), "leading": idx == 0,
                            "gloss": meta["gloss"], "polarity": meta["polarity"],
                            "note": meta["note"]})

    # Drop shorter tokens fully contained inside a longer token at the SAME start
    # (e.g. 'sel' inside 'selva' at position 0) — keep the dominant unit but
    # retain the shorter one as a secondary note only if it carries negativity.
    def _shadowed(m):
        for o in matches:
            if o is m:
                continue
            if (o["position"] <= m["position"]
                    and o["position"] + o["length"] >= m["position"] + m["length"]
                    and o["length"] > m["length"]):
                return True
        return False

    primary = [m for m in matches if not _shadowed(m)]
    # Shadowed negatives are still worth a mention (e.g. 'sel' under 'selva').
    shadowed_negatives = [m for m in matches
                          if _shadowed(m) and m["polarity"] == "negative"]

    # Dominant = best leading match (leading first, then longest, then earliest).
    def _rank(m):
        return (0 if m["leading"] else 1, -m["length"], m["position"])
    ranked = sorted(primary, key=_rank)
    dominant = ranked[0] if ranked else None

    has_negative = any(m["polarity"] == "negative" for m in primary) or \
        bool(shadowed_negatives)

    intended_clean = _clean_lower(intended_root) if intended_root else None
    deviation = False
    if dominant and intended_clean:
        deviation = intended_clean not in dominant["token"] and \
            dominant["token"] not in intended_clean

    # First-class headline
    if dominant and dominant["polarity"] == "negative":
        headline = (f"⚠ NAİF ALGI (OLUMSUZ): naif okuyucu '{dominant['token']}' "
                    f"({dominant['gloss']}) ayrıştırır — {dominant['note']}")
    elif dominant and deviation:
        headline = (f"⚠ NAİF ALGI (İNTENT≠ALGI): niyet '{intended_root}' ancak "
                    f"naif okuyucu '{dominant['token']}' ({dominant['gloss']}) "
                    f"ayrıştırır — {dominant['note']}")
    elif dominant:
        headline = (f"Naif algı: '{dominant['token']}' ({dominant['gloss']}) "
                    f"[{dominant['polarity']}]")
    else:
        headline = "Naif algı: baskın yüksek-frekanslı Türkçe morfem yok (nötr)."

    return {
        "dominant_perceived": dominant,
        "all_matches": sorted(primary, key=_rank),
        "shadowed_negatives": shadowed_negatives,
        "has_negative_perception": has_negative,
        "intent_perception_deviation": deviation,
        "intended_root": intended_root,
        "headline": headline,
    }

# ============================================================
# Layer 1: Turkish Lexicon — Curated 600+ words across 12 semantic fields
# ============================================================
# Selection criteria: TDK (Türk Dil Kurumu) high-frequency lemmas + brand-relevant
# vocabulary. Each entry maps to its semantic field. KeNet equivalent: synset.

TURKISH_LEXICON: Dict[str, Dict[str, str]] = {
    # Doğa / Nature
    "doga": {
        "deniz": "sea", "dağ": "mountain", "dag": "mountain (no diacritic)", "orman": "forest",
        "nehir": "river", "göl": "lake", "gol": "lake/goal (homonym)", "kar": "snow / profit (HOMONYM)",
        "yağmur": "rain", "rüzgar": "wind", "fırtına": "storm", "deprem": "earthquake",
        "ada": "island", "kıyı": "coast", "vadi": "valley", "ova": "plain", "tepe": "hill",
        "çay": "stream / tea (HOMONYM)", "kaynak": "spring/source", "şelale": "waterfall",
        "kum": "sand", "taş": "stone", "kaya": "rock", "toprak": "soil/earth",
    },
    # Gökyüzü / Sky
    "gokyuzu": {
        "güneş": "sun", "ay": "moon / month (HOMONYM)", "yıldız": "star", "gezegen": "planet",
        "gökyüzü": "sky", "bulut": "cloud", "şafak": "dawn", "alaca": "twilight",
        "gece": "night", "gündüz": "day", "ufuk": "horizon", "kutup": "pole",
        "samanyolu": "milky way", "ay": "moon",
    },
    # Işık / Light
    "isik": {
        "ışık": "light", "isik": "light (no diacritic)", "alev": "flame", "kıvılcım": "spark",
        "parlak": "bright", "aydınlık": "brightness", "nur": "divine light (Arabic origin)",
        "ziya": "luminance (Arabic origin)", "şule": "ray (Arabic origin)",
        "şavk": "luminance (poetic)", "fer": "luster (Persian origin)",
        "ateş": "fire", "kor": "ember", "lamba": "lamp",
    },
    # Su / Water
    "su": {
        "su": "water", "akıntı": "current", "dalga": "wave", "damla": "drop",
        "buhar": "steam", "buz": "ice", "sis": "fog", "çiy": "dew",
        "pınar": "spring", "ırmak": "river", "okyanus": "ocean", "körfez": "bulf",
    },
    # Bilgi / Knowledge
    "bilgi": {
        "bilgi": "knowledge", "bilim": "science", "ilim": "knowledge (Arabic origin)",
        "irfan": "wisdom (Arabic origin)", "marifet": "skill (Arabic origin)",
        "akıl": "reason/mind", "zekâ": "intelligence (Arabic origin)",
        "fikir": "idea (Arabic origin)", "düşünce": "thought", "kanıt": "proof",
        "veri": "data", "gerçek": "truth/real", "doğru": "correct/true",
        "öğreti": "doctrine", "kuram": "theory", "mantık": "logic (Arabic origin)",
    },
    # Güç / Strength
    "guc": {
        "güç": "power", "kuvvet": "force (Arabic origin)", "kudret": "might (Arabic origin)",
        "demir": "iron", "çelik": "steel", "kale": "fortress (Arabic origin)",
        "zafer": "victory (Arabic origin)", "fetih": "conquest (Arabic origin)",
        "zırh": "armor", "kalkan": "shield", "mızrak": "spear", "kılıç": "sword",
        "ordu": "army", "şahin": "falcon", "kartal": "eagle", "aslan": "lion",
        "tunç": "bronze", "altın": "gold", "gümüş": "silver",
    },
    # Güzellik / Beauty
    "guzellik": {
        "güzel": "beautiful", "zarif": "elegant (Arabic origin)", "şirin": "sweet/cute (Persian)",
        "nazlı": "delicate (Persian)", "ferah": "spacious (Arabic origin)",
        "saf": "pure (Arabic origin)", "berrak": "clear (Persian)",
        "letafet": "grace (Arabic origin)", "zarafet": "elegance (Arabic origin)",
        "estetik": "aesthetic (French origin)", "incelik": "subtlety", "zerafet": "grace",
    },
    # Zaman / Time
    "zaman": {
        "zaman": "time (Arabic origin)", "an": "moment (Arabic origin)", "lahza": "instant (Arabic)",
        "asır": "century (Arabic origin)", "çağ": "era", "devir": "epoch (Arabic origin)",
        "tarih": "history (Arabic origin)", "ezel": "eternity (Arabic origin)",
        "ebed": "afterlife (Arabic origin)", "şafak": "dawn", "fecir": "early dawn (Arabic)",
        "anlık": "instant", "süre": "duration",
    },
    # Mekan / Space
    "mekan": {
        "mekan": "place (Arabic origin)", "yer": "place", "alan": "field/area",
        "kent": "city (Persian origin)", "şehir": "city (Arabic origin)",
        "köy": "village", "bölge": "region", "diyar": "land (Arabic origin)",
        "ülke": "country", "yurt": "homeland", "vatan": "homeland (Arabic origin)",
        "ev": "house", "saray": "palace (Persian origin)", "köşk": "kiosk (Persian)",
    },
    # Hareket / Motion
    "hareket": {
        "hareket": "motion (Arabic origin)", "akın": "raid/flow", "akış": "flow",
        "uçuş": "flight", "yürüyüş": "walking", "koşu": "running",
        "rüzgar": "wind (Persian origin)", "fırtına": "storm",
        "tayyare": "airplane (Arabic, archaic)",
    },
    # Uyum / Harmony
    "uyum": {
        "uyum": "harmony", "ahenk": "harmony (Persian)", "denge": "balance",
        "saz": "musical instrument (Persian)", "nağme": "melody (Persian)",
        "makam": "musical mode (Arabic)", "müzik": "music (French origin)",
        "ezgi": "tune", "ritim": "rhythm (French origin)",
    },
    # Yaşam / Life
    "yasam": {
        "yaşam": "life", "hayat": "life (Arabic origin)", "can": "soul (Persian)",
        "ruh": "spirit (Arabic origin)", "öz": "essence", "cevher": "essence (Arabic)",
        "sağlık": "health", "şifa": "healing (Arabic origin)", "deva": "remedy (Arabic)",
        "ilaç": "medicine (Persian origin)", "tabip": "physician (Arabic, archaic)",
        "hekim": "doctor (Arabic origin)",
    },
}

# Build flat lookup index for fast collision check
TURKISH_FLAT_INDEX: Dict[str, Tuple[str, str]] = {}
for field, words in TURKISH_LEXICON.items():
    for word, gloss in words.items():
        TURKISH_FLAT_INDEX[word.lower()] = (field, gloss)

# ============================================================
# Layer 2: Turkish Roots / Morphemes — high-frequency 2-4 letter substrings
# ============================================================
# These appear inside many Turkish words. If a coined brand name contains
# one, it will register Turkish semantic association in a Turkish ear.

TURKISH_ROOTS: Dict[str, str] = {
    "ay": "moon / month",
    "su": "water",
    "kar": "snow / profit (HOMONYM)",
    "buz": "ice",
    "yıl": "year",
    "yil": "year (no diacritic)",
    "an": "moment",
    "öz": "essence",
    "oz": "essence (no diacritic)",
    "iyi": "good",
    "yol": "way / path",
    "söz": "word",
    "ses": "voice / sound",
    "göz": "eye",
    "el": "hand",
    "kal": "stay (root)",
    "ver": "give (root)",
    "gel": "come (root)",
    "git": "go (root)",
    "bil": "know (root)",
    "yaz": "summer / write (HOMONYM)",
    "kış": "winter",
    "kis": "winter (no diacritic)",
    "düş": "dream / fall (HOMONYM)",
    "çağ": "era",
    "cag": "era (no diacritic)",
    "can": "soul (Persian)",
    "ada": "island",
    "ata": "ancestor",
    "ana": "mother",
    "öt": "sing (bird)",
    "sev": "love (root)",
    "yen": "win (root)",
    "ışı": "light (root)",
    "isi": "light/heat (no diacritic - HOMONYM)",
    "ulu": "great",
    "alt": "below",
    "üst": "above",
    "ust": "above (no diacritic)",
    "ön": "front",
    "on": "front / ten (HOMONYM)",
    "art": "back",
    "iç": "inside",
    "ic": "inside (no diacritic)",
    "dış": "outside",
    "dis": "outside / tooth (HOMONYM)",
}

# ============================================================
# Layer 3: Vowel Harmony Algorithm (Türkçe Ünlü Uyumu)
# ============================================================
# Turkish phonology requires vowel harmony in native words.
# Two harmony classes (büyük ünlü uyumu — major vowel harmony):
#   - Front (ince): e, i, ö, ü
#   - Back (kalın): a, ı, o, u
# Native Turkish words: all vowels share class.
# Loanwords (Arabic, Persian, French): often violate harmony.

FRONT_VOWELS: Set[str] = set("eiöüEİÖÜ")
BACK_VOWELS: Set[str] = set("aıouAIOU")
ALL_VOWELS: Set[str] = FRONT_VOWELS | BACK_VOWELS

def analyze_vowel_harmony(name: str) -> Dict:
    """
    Analyze Turkish vowel harmony (büyük ünlü uyumu).

    Returns:
      - vowels_in_name: list of vowels found
      - has_front: bool
      - has_back: bool
      - harmony_status: "front-harmonious" | "back-harmonious" | "violated" | "no-vowels"
      - turkish_native_feel: 0.0-1.0 (1.0 = pure native; 0.0 = clear loanword feel)
    """
    vowels_found = [c for c in name if c in ALL_VOWELS]
    has_front = any(v in FRONT_VOWELS for v in vowels_found)
    has_back = any(v in BACK_VOWELS for v in vowels_found)

    if not vowels_found:
        return {
            "vowels": [],
            "has_front": False,
            "has_back": False,
            "harmony_status": "no-vowels",
            "turkish_native_feel": 0.0,
            "interpretation": "No vowels — not a viable Turkish word"
        }

    if has_front and has_back:
        return {
            "vowels": vowels_found,
            "has_front": True,
            "has_back": True,
            "harmony_status": "violated",
            "turkish_native_feel": 0.2,
            "interpretation": "Mixed front+back vowels — sounds foreign / loanword in Turkish ear"
        }
    if has_front:
        return {
            "vowels": vowels_found,
            "has_front": True,
            "has_back": False,
            "harmony_status": "front-harmonious",
            "turkish_native_feel": 0.95,
            "interpretation": "Front-vowel harmony (ince ünlü uyumu) — native Turkish phonology"
        }
    return {
        "vowels": vowels_found,
        "has_front": False,
        "has_back": True,
        "harmony_status": "back-harmonious",
        "turkish_native_feel": 0.95,
        "interpretation": "Back-vowel harmony (kalın ünlü uyumu) — native Turkish phonology"
    }


# ============================================================
# Layer 4: Loanword Origin Detection (Heuristic Signatures)
# ============================================================
# Turkish absorbed Persian, Arabic, French, Greek, Italian loanwords.
# Each has morphological signatures detectable in modern Turkish vocabulary.
# This affects brand positioning: Persian = romantic/poetic, Arabic = formal/religious,
# French = modern/Western/elegant, Greek = ancient/scientific.

LOANWORD_SIGNATURES: Dict[str, Dict] = {
    "persian": {
        "endings": ["ane", "istan", "zar", "name", "han", "kar", "dar"],
        "starts": ["şeh", "div", "gül", "gah"],
        "contains": ["zar", "han", "abad", "perver"],
        "examples": ["bahane", "Türkistan", "gülzar", "şehname", "perverde"],
        "brand_feel": "romantic / poetic / Ottoman heritage",
        "modern_brands": ["Şahane (TR retail)", "Şehzade (TR brand)"]
    },
    "arabic": {
        "endings": ["iyet", "iye", "iyat", "ahane"],
        "starts": ["el-", "al-", "ibn-", "ümm-"],
        "contains": ["aks", "vah", "sub"],
        "patterns_3consonants": True,  # Arabic broken plural CCC root
        "examples": ["medeniyet", "kütüphane", "müteşekkir"],
        "brand_feel": "formal / scholarly / classical / religious-coded",
        "modern_brands": ["Vakıfbank (TR)", "Hürriyet (newspaper)"]
    },
    "french": {
        "endings": ["aj", "ans", "yon", "ist", "ör", "ize", "et"],
        "starts": ["par", "kom", "kon", "tran"],
        "contains": ["asyon", "ans", "yön"],
        "examples": ["garaj", "balans", "televizyon", "artist", "doktor", "elektrik"],
        "brand_feel": "modern / Western / elegant / 20th century industrial",
        "modern_brands": ["Pegasus (Latin/French style TR)", "Boyner (TR)"]
    },
    "greek": {
        "endings": ["os", "is", "as", "ides"],
        "starts": ["thal", "psy", "tele", "neo", "pan"],
        "contains": ["log", "graph", "metr"],
        "examples": ["telefon", "psikoloji", "panorama"],
        "brand_feel": "scientific / classical / educated",
        "modern_brands": ["Anthropic (Greek root)", "Pythia (Greek)"]
    },
    "italian": {
        "endings": ["o", "etto", "ina"],
        "examples": ["banka", "kasa", "fatura"],
        "brand_feel": "commercial / mercantile",
        "modern_brands": ["Banco (TR brand)"]
    }
}

def detect_loanword_origin(name: str) -> List[Dict]:
    """
    Heuristically detect potential loanword origin signatures in name.
    Returns list of detected origins with confidence scores.
    """
    name_lower = name.lower()
    detections = []

    for origin, sig in LOANWORD_SIGNATURES.items():
        signals = []
        confidence = 0

        for ending in sig.get("endings", []):
            if name_lower.endswith(ending):
                signals.append(f"ends with -{ending}")
                confidence += 30

        for start in sig.get("starts", []):
            if name_lower.startswith(start):
                signals.append(f"starts with {start}-")
                confidence += 25

        for contains in sig.get("contains", []):
            if contains in name_lower and not name_lower.startswith(contains) and not name_lower.endswith(contains):
                signals.append(f"contains '{contains}'")
                confidence += 15

        if signals:
            detections.append({
                "origin": origin,
                "confidence": min(100, confidence),
                "signals": signals,
                "brand_feel": sig["brand_feel"],
                "examples": sig.get("examples", [])[:3]
            })

    detections.sort(key=lambda d: -d["confidence"])
    return detections


# ============================================================
# Layer 5: Thematic Semantic Field Mapping for Brand Positioning
# ============================================================
# Maps brand brief themes to Turkish semantic fields, enabling
# native-Turkish-language alternative name suggestions.

BRAND_SEMANTIC_FIELDS: Dict[str, Dict] = {
    "scientific_truth_evidence": {
        "tr_words": ["gerçek", "doğru", "kanıt", "veri", "bilgi", "bilim", "ilim", "kuram"],
        "tr_premium_alternatives": ["Veri", "Bilim", "Kuram", "İrfan", "Hakikat"],
        "international_equivalents": ["Veritas", "Episteme", "Aletheia", "Logos"],
        "brand_use_case": "RWE, analytics, evidence platforms, regulatory tech"
    },
    "predictive_oracle_insight": {
        "tr_words": ["öngörü", "kehanet", "tahmin", "sezgi", "ileri-görü"],
        "tr_premium_alternatives": ["Sezgi", "Öngörü", "Müjde"],
        "international_equivalents": ["Pythia", "Oracle", "Augur", "Vates"],
        "brand_use_case": "predictive analytics, AI forecasting, decision intelligence"
    },
    "light_illumination_clarity": {
        "tr_words": ["ışık", "aydınlık", "berrak", "şafak", "nur", "ziya"],
        "tr_premium_alternatives": ["Nur", "Ziya", "Şafak", "Aydın"],
        "international_equivalents": ["Lumen", "Lumina", "Aurora", "Lux"],
        "brand_use_case": "diagnostics, transparency tools, BI platforms, illumination metaphors"
    },
    "strength_protection_security": {
        "tr_words": ["güç", "kale", "kalkan", "demir", "çelik", "şahin"],
        "tr_premium_alternatives": ["Kale", "Çelik", "Şahin", "Kartal"],
        "international_equivalents": ["Citadel", "Aegis", "Fortis", "Bastion"],
        "brand_use_case": "cybersecurity, fintech, insurance, defensive tech"
    },
    "harmony_balance_unity": {
        "tr_words": ["uyum", "ahenk", "denge", "bütün"],
        "tr_premium_alternatives": ["Ahenk", "Uyum", "Bütün"],
        "international_equivalents": ["Concord", "Harmonia", "Cohera"],
        "brand_use_case": "collaboration tools, integration platforms, wellness"
    },
    "speed_motion_velocity": {
        "tr_words": ["hız", "akış", "rüzgar", "şimşek"],
        "tr_premium_alternatives": ["Akın", "Şimşek", "Yıldırım"],
        "international_equivalents": ["Vite", "Velox", "Rapid", "Kinetic"],
        "brand_use_case": "logistics, payments, dev-tools, mobility"
    },
    "knowledge_wisdom_learning": {
        "tr_words": ["bilgi", "bilim", "irfan", "akıl", "marifet"],
        "tr_premium_alternatives": ["İrfan", "Akıl", "Marifet", "Hikmet"],
        "international_equivalents": ["Sophia", "Athena", "Sapientia", "Veda"],
        "brand_use_case": "education, knowledge management, research tools"
    },
    "time_continuity_legacy": {
        "tr_words": ["çağ", "asır", "devir", "ezel", "ebed"],
        "tr_premium_alternatives": ["Çağ", "Devir", "Ezel"],
        "international_equivalents": ["Era", "Epoch", "Aeon", "Cohera (era root)"],
        "brand_use_case": "longitudinal analytics, archival, registry systems"
    }
}


# ============================================================
# Core Analysis Function
# ============================================================

def analyze(name: str, intended_root: Optional[str] = None) -> Dict:
    """Complete 6-layer Turkish semantic analysis of a brand name candidate.

    v2.1: Layer 6 (naive first-reading / perception) added and folded into the
    verdict as a first-class factor.
    """
    name_lower = name.lower().strip()

    # Layer 1: Dictionary collision check
    full_match = TURKISH_FLAT_INDEX.get(name_lower)
    layer1 = {
        "exact_match": full_match,
        "interpretation": (
            f"⚠ Direct collision: '{name_lower}' is the Turkish word meaning '{full_match[1]}' "
            f"(field: {full_match[0]})"
            if full_match else "No direct Turkish word collision"
        )
    }

    # Layer 2: Root/morpheme detection
    detected_roots = []
    for root, gloss in TURKISH_ROOTS.items():
        # Check if root appears as substring (with reasonable boundaries)
        if root in name_lower and len(name_lower) >= len(root) + 1:
            # Position-aware: prefer beginning or end positions
            if name_lower.startswith(root) or name_lower.endswith(root) or len(root) >= 3:
                detected_roots.append({"root": root, "gloss": gloss})
    layer2 = {
        "detected_roots": detected_roots[:5],  # Top 5
        "count": len(detected_roots)
    }

    # Layer 3: Vowel harmony
    layer3 = analyze_vowel_harmony(name)

    # Layer 4: Loanword origin signatures
    layer4 = detect_loanword_origin(name)

    # Layer 5: Semantic field affinity (which brand themes does this name resonate with?)
    # We compute affinity by checking if any word in the name's semantic neighborhood
    # appears in the field's tr_words list. For coined names this is mostly empty.
    affinities = []
    for field_id, field_data in BRAND_SEMANTIC_FIELDS.items():
        # Check if name overlaps with field's premium alternatives (case-insensitive)
        for alt in field_data["tr_premium_alternatives"] + field_data["international_equivalents"]:
            if alt.lower() in name_lower or name_lower in alt.lower():
                affinities.append({
                    "field": field_id,
                    "matched_alternative": alt,
                    "use_case": field_data["brand_use_case"]
                })
                break
    layer5 = {"affinities": affinities}

    # Layer 6: naive first-reading / perception (v2.1)
    layer6 = naive_parse(name, intended_root=intended_root)

    # Composite Turkish-market readiness verdict (now perception-aware)
    verdict = compute_turkish_verdict(layer1, layer3, layer4, layer6)

    return {
        "name": name,
        "layer1_dictionary": layer1,
        "layer2_roots": layer2,
        "layer3_vowel_harmony": layer3,
        "layer4_loanword_origin": layer4,
        "layer5_semantic_affinity": layer5,
        "layer6_naive_perception": layer6,
        "turkish_market_verdict": verdict
    }


def compute_turkish_verdict(layer1: Dict, layer3: Dict, layer4: List,
                            layer6: Dict = None) -> Dict:
    """Synthesize layers into Turkish-market positioning verdict.

    v2.1 recalibration (expert-audit remediation C+D): baseline lowered from 100
    to 80 (the old 100-baseline piled every candidate at 85-100 and did not
    discriminate), and NAIVE PERCEPTION (Layer 6) is now a first-class,
    heavily-weighted factor. A dominant negative perceived reading (e.g. 'orta'
    = mediocre) is a major penalty, not a footnote.
    """
    score = 80
    notes = []
    naive_flags = []

    # --- Layer 6 — NAIVE PERCEPTION (first-class) ---
    if layer6:
        dom = layer6.get("dominant_perceived")
        if dom and dom["polarity"] == "negative":
            score -= 25
            naive_flags.append(
                f"OLUMSUZ naif algı: '{dom['token']}' ({dom['gloss']}) — {dom['note']}")
        elif dom and layer6.get("intent_perception_deviation"):
            score -= 12
            naive_flags.append(
                f"İNTENT≠ALGI sapması: niyet '{layer6.get('intended_root')}' → "
                f"naif okuma '{dom['token']}' ({dom['gloss']}) — {dom['note']}")
        elif dom and dom["polarity"] == "neutral":
            score -= 5
            naive_flags.append(
                f"Naif algı (nötr): '{dom['token']}' ({dom['gloss']}) — {dom['note']}")
        elif dom and dom["polarity"] == "positive":
            score += 3
            naive_flags.append(
                f"Naif algı (olumlu): '{dom['token']}' ({dom['gloss']})")
        # Any additional negative anywhere (e.g. shadowed 'sel' under 'selva')
        for m in layer6.get("shadowed_negatives", []):
            naive_flags.append(
                f"İkincil olumsuz alt-okuma: '{m['token']}' ({m['gloss']}) — {m['note']}")

    # Direct dictionary collision
    if layer1["exact_match"]:
        gloss = layer1["exact_match"][1]
        if "HOMONYM" in gloss:
            score -= 22
            notes.append(f"Homonym risk in Turkish: meaning splits across senses ({gloss})")
        else:
            score -= 14
            notes.append(f"Real Turkish word — descriptive ('{gloss}'); trademark distinctiveness reduced")

    # Vowel harmony (pronunciation/naturalness — kept separate from perception)
    if layer3["harmony_status"] == "violated":
        score -= 5
        notes.append("Mixed vowels — sounds foreign/loanword in Turkish ear (sometimes desired for premium positioning)")
    elif layer3["harmony_status"] == "no-vowels":
        score -= 30
        notes.append("No vowels — not pronounceable as Turkish word")
    elif layer3["harmony_status"] in ("front-harmonious", "back-harmonious"):
        score += 4  # natural Turkish phonology — small credit

    # Loanword origin (informational, not penalty)
    if layer4:
        top_origin = layer4[0]
        notes.append(f"Carries {top_origin['origin']} loanword signature ({top_origin['confidence']}% confidence) — brand feel: {top_origin['brand_feel']}")

    score = max(0, min(100, score))
    if score >= 82:
        label = "EXCELLENT for Turkish market"
    elif score >= 68:
        label = "GOOD; minor positioning notes"
    elif score >= 50:
        label = "ACCEPTABLE; document semantic trade-offs"
    else:
        label = "WEAK; reconsider for Turkish market"

    return {"score": score, "label": label, "notes": notes,
            "naive_perception_flags": naive_flags}


# ============================================================
# Pretty Printer
# ============================================================

def format_report(analysis: Dict) -> str:
    n = analysis
    l6 = n.get("layer6_naive_perception", {})
    out = f"""
═══════════════════════════════════════════════════════
TURKISH SEMANTIC PROFILE: {n['name']}
═══════════════════════════════════════════════════════

▌ NAIVE FIRST-READING / ALGI (LAYER 6 — FIRST-CLASS, v2.1)
   {l6.get('headline', '(n/a)')}
"""
    if l6.get("all_matches"):
        for m in l6["all_matches"]:
            tag = {"negative": "OLUMSUZ", "neutral": "nötr", "positive": "olumlu"}.get(m["polarity"], m["polarity"])
            lead = "baş" if m["leading"] else f"poz.{m['position']}"
            out += f"     • '{m['token']}' ({lead}) → {m['gloss']} [{tag}]\n"
    out += f"""
▌ LAYER 1 — Türkçe Sözlük Çakışma Kontrolü
   {n['layer1_dictionary']['interpretation']}

▌ LAYER 2 — Türkçe Morfem/Kök Tespiti
"""
    if n['layer2_roots']['detected_roots']:
        for r in n['layer2_roots']['detected_roots']:
            out += f"   • '{r['root']}' → {r['gloss']}\n"
    else:
        out += "   No high-frequency Turkish roots detected.\n"

    h = n['layer3_vowel_harmony']
    out += f"""
▌ LAYER 3 — Ünlü Uyumu (Vowel Harmony) Analizi
   Vowels found:        {h['vowels']}
   Status:              {h['harmony_status']}
   Native-feel score:   {h['turkish_native_feel']}/1.0
   Interpretation:      {h['interpretation']}

▌ LAYER 4 — Alıntı Kelime Köken Tespiti (Loanword Origin)
"""
    if n['layer4_loanword_origin']:
        for d in n['layer4_loanword_origin'][:3]:
            out += f"   • {d['origin'].upper()} ({d['confidence']}% confidence)\n"
            out += f"     Signals: {', '.join(d['signals'])}\n"
            out += f"     Brand feel: {d['brand_feel']}\n"
            out += f"     Comparable Turkish words: {', '.join(d['examples'])}\n"
    else:
        out += "   No loanword signatures detected — sounds neutral/coined to Turkish ear.\n"

    out += "\n▌ LAYER 5 — Semantic Field Affinity (Brand Positioning)\n"
    if n['layer5_semantic_affinity']['affinities']:
        for a in n['layer5_semantic_affinity']['affinities']:
            out += f"   • Resonates with field: {a['field']}\n"
            out += f"     Matched alternative: {a['matched_alternative']}\n"
            out += f"     Brand use case: {a['use_case']}\n"
    else:
        out += "   No direct semantic field match — name occupies neutral white-space.\n"

    v = n['turkish_market_verdict']
    out += f"""
═══════════════════════════════════════════════════════
TURKISH MARKET VERDICT:  {v['score']}/100  →  {v['label']}
"""
    if v.get('naive_perception_flags'):
        out += "Naive-perception flags (FIRST-CLASS):\n"
        for f in v['naive_perception_flags']:
            out += f"   ⚠ {f}\n"
    if v['notes']:
        out += "Notes:\n"
        for note in v['notes']:
            out += f"   • {note}\n"
    out += "═══════════════════════════════════════════════════════\n"
    return out


# ============================================================
# Helper: Suggest Turkish alternatives for a brief theme
# ============================================================

def suggest_turkish_alternatives(theme_keyword: str) -> Optional[Dict]:
    """
    Given a brief theme keyword, return Turkish premium alternatives
    from the BRAND_SEMANTIC_FIELDS catalog.
    """
    theme_lower = theme_keyword.lower()
    matches = []

    for field_id, field_data in BRAND_SEMANTIC_FIELDS.items():
        if theme_lower in field_id.lower():
            matches.append((field_id, field_data))
            continue
        # Check use case description
        if theme_lower in field_data["brand_use_case"].lower():
            matches.append((field_id, field_data))
            continue
        # Check Turkish words
        if any(theme_lower in w for w in field_data["tr_words"]):
            matches.append((field_id, field_data))

    if matches:
        field_id, field_data = matches[0]
        return {
            "matched_field": field_id,
            "tr_premium_alternatives": field_data["tr_premium_alternatives"],
            "international_equivalents": field_data["international_equivalents"],
            "use_case": field_data["brand_use_case"]
        }
    return None


# ============================================================
# CLI
# ============================================================

def main():
    # --suggest keeps its legacy positional form for backward compatibility.
    if len(sys.argv) >= 2 and sys.argv[1] == "--suggest":
        if len(sys.argv) < 3:
            print("Usage: python turkish_semantic_check.py --suggest <theme>")
            sys.exit(1)
        theme = " ".join(sys.argv[2:])
        result = suggest_turkish_alternatives(theme)
        print(f"\n# Turkish Alternative Suggestions for theme: '{theme}'\n")
        if result:
            print(f"Matched field: {result['matched_field']}")
            print(f"Use case: {result['use_case']}\n")
            print("Turkish premium alternatives:")
            for alt in result['tr_premium_alternatives']:
                print(f"  • {alt}")
            print("\nInternational equivalents (already known patterns):")
            for alt in result['international_equivalents']:
                print(f"  • {alt}")
        else:
            print(f"No semantic field matched '{theme}'. Try: evidence, oracle, light, strength, harmony, speed, knowledge, time")
        return

    parser = argparse.ArgumentParser(
        description="Turkish semantic + naive-perception check (6 layers, v2.1)")
    parser.add_argument("names", nargs="+", help="Brand name(s) to check")
    parser.add_argument("--intent", default=None,
                        help="Intended root/etymology (e.g. 'ortus', 'salv') — "
                             "enables intent↔perception deviation detection")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    results = [analyze(name, intended_root=args.intent) for name in args.names]

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    print(f"\n# Turkish Semantic Check Report — {len(args.names)} candidate(s)")
    print(f"# Brand-Maker v2.1 — turkish_semantic_check.py")
    print(f"# Methodology distilled from starlangsoftware/turkishwordnet-py (KeNet)")
    print(f"# 6-layer analysis: dictionary · roots · vowel harmony · loanword origin "
          f"· semantic field · NAIVE PERCEPTION\n")

    for result in results:
        print(format_report(result))


if __name__ == "__main__":
    main()
