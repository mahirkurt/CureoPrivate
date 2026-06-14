#!/usr/bin/env python3
"""
cpc-recommender.py — Molekül/Cihaz Özelliklerinden CPC/IPC Kodu Önerisi

Bir patent başvurusu ya da FTO araması için uygun CPC (Cooperative Patent
Classification) ve IPC kodlarını öneren script. Küçük molekül + biyolojik +
tıbbi cihaz + kombinasyon ürün kapsamında rehberlik sağlar.

Kullanım:
    python3 cpc-recommender.py                          # interactive
    python3 cpc-recommender.py --example small_molecule # küçük molekül demo
    python3 cpc-recommender.py --example biologic       # biyolojik demo
    python3 cpc-recommender.py --example device         # cihaz demo
    python3 cpc-recommender.py --json                   # JSON çıktı

Girdi (interactive):
    - Modalite (small molecule, antibody, ADC, CAR-T, device, vb.)
    - Endikasyon/terapötik alan
    - Aktif madde sınıfı
    - Dozaj formu
    - Özel özellikler (glikoprotein, nanopartikül, vb.)

Çıktı:
    - Birincil CPC kodları (öncelikli)
    - İkincil CPC kodları
    - IPC kodları
    - Boolean sorgu örnekleri (USPTO, Espacenet)

Yazar: pharmapatent skill v1.4.0
Lisans: Internal use.
"""

import sys
import json
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional


# --- CPC kodu bilgi tabanı ---
CPC_DATABASE = {
    # A61K — Medicinal preparations
    "A61K 9/00": "Medicinal preparations characterised by special physical form",
    "A61K 9/08": "Solutions",
    "A61K 9/10": "Dispersions; Emulsions",
    "A61K 9/14": "Particulate form (e.g. microcapsules)",
    "A61K 9/16": "Agglomerated particles; Granulates",
    "A61K 9/20": "Tablets",
    "A61K 9/28": "Coated tablets",
    "A61K 9/48": "Preparations in capsules",
    "A61K 9/51": "Nanocapsules, nanoparticles",
    "A61K 9/127": "Liposomes",
    "A61K 9/50": "Microcapsules",
    "A61K 31/00": "Organic active ingredients",
    "A61K 31/40": "Pirol, piridin, azol-içeren",
    "A61K 31/435": "İndol türevleri",
    "A61K 31/4412": "Piperidin türevleri (TKI yaygın)",
    "A61K 31/505": "Pirimidin türevleri",
    "A61K 31/56": "Steroidler",
    "A61K 31/66": "Fosfor-içeren",
    "A61K 31/675": "Fosfonatlar (bortezomib vb.)",
    "A61K 31/7004": "Monosakkaridler",
    "A61K 31/7088": "Oligonükleotitler",
    "A61K 38/00": "Medicinal preparations containing peptides",
    "A61K 38/17": "Peptides having more than 20 amino acids",
    "A61K 38/18": "Growth factors; Growth regulators",
    "A61K 38/22": "Hormonlar",
    "A61K 38/26": "Glukagon ve peptidler",
    "A61K 38/36": "Koagülasyon faktörleri",
    "A61K 39/00": "Medicinal preparations containing antigens or antibodies",
    "A61K 39/395": "Antikorlar (immunoglobulinler)",
    "A61K 45/00": "Medicinal preparations containing active ingredients not provided for in groups A61K 31/00 - A61K 41/00",
    "A61K 45/06": "Mixtures of active ingredients (combination therapy)",
    "A61K 47/00": "Medicinal preparations - Inactive ingredients",
    "A61K 47/68": "Antibody-drug conjugates (ADC)",
    "A61K 47/69": "Taşıyıcılar",
    "A61K 48/00": "Gene therapy preparations",
    "A61K 51/00": "Preparations containing radioactive substances",
    "A61K 51/04": "Radiopharmaceuticals",

    # A61M — Devices for administering medicaments
    "A61M 5/00": "Devices for bringing medicaments into the body (injection)",
    "A61M 5/14": "Infusion sets",
    "A61M 5/20": "Syringes (manuel)",
    "A61M 5/24": "Dual-chamber syringes",
    "A61M 5/315": "Auto-injectors (pen injectors)",
    "A61M 5/50": "Disposable syringes",
    "A61M 11/00": "Sprayers or atomisers",
    "A61M 15/00": "Inhalers",
    "A61M 15/008": "Dry powder inhalers",
    "A61M 15/009": "MDI (metered dose inhalers)",
    "A61M 25/00": "Catheters",
    "A61M 37/00": "Other apparatus (transdermal)",

    # A61B — Diagnostic devices
    "A61B 5/00": "Measuring biological data",
    "A61B 5/145": "Biochemical parameters",
    "A61B 34/00": "Robotic surgery",
    "A61B 90/00": "Auxiliary surgical apparatus",

    # A61F — Implants
    "A61F 2/00": "Filters, prostheses",
    "A61F 2/86": "Stents",
    "A61F 2/24": "Heart valves",

    # A61P — Therapeutic activity (indication)
    "A61P 1/00": "Digestive system",
    "A61P 7/00": "Blood and hematopoietic system (hematology)",
    "A61P 7/04": "Anticoagulants",
    "A61P 7/06": "Antithrombotic agents",
    "A61P 7/08": "Hemophilia treatment",
    "A61P 9/00": "Cardiovascular system",
    "A61P 25/00": "Nervous system",
    "A61P 31/00": "Antimicrobial agents",
    "A61P 31/22": "Antiviral",
    "A61P 35/00": "Antineoplastic agents (oncology)",
    "A61P 35/02": "Hematological neoplasms",
    "A61P 35/04": "Metastatic disease",
    "A61P 37/00": "Immunomodulators",
    "A61P 43/00": "Other therapeutic activity",

    # C07D — Heterocyclic compounds (ilaç kimyası)
    "C07D 207/00": "Heterocyclic compounds with five-membered rings having one nitrogen (pirrol)",
    "C07D 213/00": "Piridin türevleri",
    "C07D 231/00": "Pirazol türevleri",
    "C07D 239/00": "Pirimidin türevleri",
    "C07D 401/00": "Heterocyclic compounds bicyclic (çift halka)",
    "C07D 471/00": "Fuzyon halka sistemleri",

    # C07K — Peptides
    "C07K 1/00": "Genel peptid prosesleri",
    "C07K 14/00": "Peptidler 20+ amino asit",
    "C07K 14/47": "Dinamik-regülatör peptidler",
    "C07K 14/745": "FVIII, FIX (koagülasyon faktörleri)",
    "C07K 16/00": "Immunoglobulinler",
    "C07K 16/28": "Reseptör antikorları",
    "C07K 16/2809": "CD19 antikorları",
    "C07K 16/2812": "CD20 antikorları",
    "C07K 16/2818": "PD-1/PD-L1 antikorları",
    "C07K 16/2833": "CD38 antikorları",
    "C07K 16/30": "Tümör antikorları",
    "C07K 16/468": "Bispecific antibodies",

    # C12N — Microorganisms or enzymes
    "C12N 5/0783": "T cell therapy (CAR-T)",
    "C12N 9/00": "Enzimler",
    "C12N 15/00": "Mutation or genetic engineering",
    "C12N 15/11": "DNA/RNA fragments (sentez)",
    "C12N 15/85": "Vectors or expression systems (lentiviral, AAV)",
    "C12N 15/864": "AAV gene delivery",
    "C12N 15/869": "Lentiviral gene delivery",

    # C07H — Sugars, nucleosides
    "C07H 21/02": "RNA derivatives",
    "C07H 21/04": "DNA derivatives",

    # G16H — Healthcare informatics
    "G16H 10/00": "ICT for patient records management",
    "G16H 30/00": "ICT for medical image processing",
    "G16H 50/20": "ICT for healthcare; diagnosis by machine learning",
    "G16H 50/50": "Simulation for medical purposes",
    "G16H 70/00": "Data manipulation for medical purposes",

    # G06N — Machine learning
    "G06N 3/00": "Neural networks, deep learning",
    "G06N 20/00": "Machine learning (genel)",
}


@dataclass
class Recommendation:
    """CPC kod önerisi."""
    code: str
    description: str
    priority: str  # "primary", "secondary", "tertiary"
    rationale: str


@dataclass
class MoleculeProfile:
    """Molekül/cihaz profili."""
    modality: str  # "small_molecule", "antibody", "adc", "car_t", "mrna", "device", "gene_therapy", "radioligand"
    indication: str  # "oncology", "hematology", "cardiovascular", "neurology", "infectious", ...
    specific_target: Optional[str] = None  # "HER2", "CD20", "PD-1", "BCMA", "FVIII", ...
    dosage_form: Optional[str] = None  # "tablet", "injection", "lyophilized", "inhaler", "implant"
    molecule_class: Optional[str] = None  # "pyrimidine", "pyrrole", "peptide", "antibody", ...
    device_component: Optional[str] = None  # "syringe", "pen", "inhaler", "pump"
    special_features: List[str] = field(default_factory=list)  # "nanoparticle", "liposome", "bispecific", vb.


def recommend_cpc(profile: MoleculeProfile) -> List[Recommendation]:
    """Molekül profilinden CPC kod önerileri üret."""
    recs = []

    # --- Indication bazlı CPC (A61P) ---
    indication_map = {
        "oncology": ("A61P 35/00", "Antineoplastic agents"),
        "hematology_malignancy": ("A61P 35/02", "Hematological neoplasms"),
        "hemophilia": ("A61P 7/08", "Hemophilia treatment"),
        "anticoagulation": ("A61P 7/04", "Anticoagulants"),
        "antithrombotic": ("A61P 7/06", "Antithrombotic agents"),
        "cardiovascular": ("A61P 9/00", "Cardiovascular system"),
        "neurology": ("A61P 25/00", "Nervous system"),
        "infectious_disease": ("A61P 31/00", "Antimicrobial agents"),
        "antiviral": ("A61P 31/22", "Antiviral"),
        "immunology": ("A61P 37/00", "Immunomodulators"),
        "hematology_general": ("A61P 7/00", "Blood and hematopoietic system"),
    }
    ind_key = profile.indication.lower().replace(" ", "_").replace("-", "_")
    if ind_key in indication_map:
        code, desc = indication_map[ind_key]
        recs.append(Recommendation(
            code=code, description=desc, priority="primary",
            rationale=f"Endikasyon '{profile.indication}' için birincil terapötik sınıf CPC",
        ))

    # --- Modalite bazlı birincil CPC ---
    if profile.modality == "small_molecule":
        recs.append(Recommendation(
            code="A61K 31/00", description=CPC_DATABASE["A61K 31/00"],
            priority="primary",
            rationale="Küçük molekül aktif madde için genel CPC",
        ))
        # Kimya sınıfı bazlı C07D
        class_map = {
            "pyrrole": "C07D 207/00",
            "pyridine": "C07D 213/00",
            "pyrimidine": "C07D 239/00",
            "piperidine": "A61K 31/4412",
            "indole": "A61K 31/435",
            "bicyclic": "C07D 401/00",
            "fused_ring": "C07D 471/00",
        }
        if profile.molecule_class and profile.molecule_class.lower() in class_map:
            code = class_map[profile.molecule_class.lower()]
            recs.append(Recommendation(
                code=code, description=CPC_DATABASE.get(code, ""),
                priority="primary",
                rationale=f"Küçük molekül sınıfı '{profile.molecule_class}' için spesifik CPC",
            ))

    elif profile.modality == "antibody":
        recs.append(Recommendation(
            code="A61K 39/395", description=CPC_DATABASE["A61K 39/395"],
            priority="primary",
            rationale="Monoklonal antikor aktif madde için genel CPC",
        ))
        recs.append(Recommendation(
            code="C07K 16/00", description=CPC_DATABASE["C07K 16/00"],
            priority="primary",
            rationale="İmmunoglobulin yapı için kimyasal sınıflandırma",
        ))
        # Hedef bazlı
        target_map = {
            "cd19": "C07K 16/2809",
            "cd20": "C07K 16/2812",
            "cd38": "C07K 16/2833",
            "pd-1": "C07K 16/2818",
            "pd-l1": "C07K 16/2818",
            "pdl1": "C07K 16/2818",
            "her2": "C07K 16/30",
            "bcma": "C07K 16/30",
            "egfr": "C07K 16/28",
            "vegf": "C07K 16/28",
        }
        if profile.specific_target:
            t = profile.specific_target.lower()
            if t in target_map:
                code = target_map[t]
                recs.append(Recommendation(
                    code=code, description=CPC_DATABASE.get(code, ""),
                    priority="primary",
                    rationale=f"Spesifik hedef '{profile.specific_target}' antikoru için alt sınıf",
                ))

    elif profile.modality == "adc":
        recs.extend([
            Recommendation("A61K 47/68", CPC_DATABASE["A61K 47/68"], "primary",
                          "ADC (antibody-drug conjugate) için spesifik CPC"),
            Recommendation("C07K 16/00", CPC_DATABASE["C07K 16/00"], "primary",
                          "Antikor kısmı için kimyasal sınıflandırma"),
        ])

    elif profile.modality == "car_t":
        recs.extend([
            Recommendation("C12N 5/0783", CPC_DATABASE["C12N 5/0783"], "primary",
                          "CAR-T hücre terapisi için spesifik CPC"),
            Recommendation("A61K 35/17", "Hematopoetic cells (CAR-T)", "primary",
                          "Allogeneic/autologous hücre preparatı"),
        ])

    elif profile.modality == "mrna":
        recs.extend([
            Recommendation("C07H 21/02", CPC_DATABASE["C07H 21/02"], "primary",
                          "mRNA (RNA türevi) kimyasal sınıflandırması"),
            Recommendation("A61K 48/00", CPC_DATABASE["A61K 48/00"], "primary",
                          "Gene therapy preparatı (mRNA delivery)"),
            Recommendation("A61K 9/51", CPC_DATABASE["A61K 9/51"], "primary",
                          "Nanopartikül formülasyon (LNP)"),
        ])

    elif profile.modality == "gene_therapy":
        recs.append(Recommendation(
            code="A61K 48/00", description=CPC_DATABASE["A61K 48/00"],
            priority="primary",
            rationale="Gene therapy preparatları için genel CPC",
        ))
        if "aav" in [f.lower() for f in profile.special_features]:
            recs.append(Recommendation(
                code="C12N 15/864", description=CPC_DATABASE["C12N 15/864"],
                priority="primary",
                rationale="AAV-tabanlı gen terapisi için spesifik CPC",
            ))
        if "lentiviral" in [f.lower() for f in profile.special_features]:
            recs.append(Recommendation(
                code="C12N 15/869", description=CPC_DATABASE["C12N 15/869"],
                priority="primary",
                rationale="Lentiviral gen terapisi için spesifik CPC",
            ))

    elif profile.modality == "radioligand":
        recs.append(Recommendation(
            code="A61K 51/04", description=CPC_DATABASE["A61K 51/04"],
            priority="primary",
            rationale="Radyofarmasötik için spesifik CPC",
        ))

    elif profile.modality == "device":
        recs.append(Recommendation(
            code="A61M 5/00", description=CPC_DATABASE["A61M 5/00"],
            priority="primary",
            rationale="Medikal cihaz (uygulama cihazı) için genel CPC",
        ))

    # --- Dozaj formu bazlı ikincil CPC (A61K 9/*) ---
    dosage_map = {
        "tablet": "A61K 9/20",
        "coated_tablet": "A61K 9/28",
        "capsule": "A61K 9/48",
        "solution": "A61K 9/08",
        "injection": "A61K 9/08",
        "lyophilized": "A61K 9/19",
        "nanoparticle": "A61K 9/51",
        "liposome": "A61K 9/127",
        "microcapsule": "A61K 9/50",
        "granulate": "A61K 9/16",
    }
    if profile.dosage_form and profile.dosage_form.lower() in dosage_map:
        code = dosage_map[profile.dosage_form.lower()]
        recs.append(Recommendation(
            code=code, description=CPC_DATABASE.get(code, ""),
            priority="secondary",
            rationale=f"Dozaj formu '{profile.dosage_form}' için formülasyon CPC",
        ))

    # --- Cihaz komponenti bazlı CPC (A61M 5/*) ---
    device_map = {
        "syringe": "A61M 5/20",
        "auto_injector": "A61M 5/315",
        "pen": "A61M 5/315",
        "inhaler": "A61M 15/00",
        "dpi": "A61M 15/008",
        "mdi": "A61M 15/009",
        "pump": "A61M 5/14",
        "stent": "A61F 2/86",
        "catheter": "A61M 25/00",
    }
    if profile.device_component and profile.device_component.lower() in device_map:
        code = device_map[profile.device_component.lower()]
        recs.append(Recommendation(
            code=code, description=CPC_DATABASE.get(code, ""),
            priority="secondary",
            rationale=f"Cihaz bileşeni '{profile.device_component}' için spesifik CPC",
        ))

    # --- Özel özellikler ---
    feature_map = {
        "bispecific": ("C07K 16/468", "Bispecific antibody"),
        "combination_therapy": ("A61K 45/06", "Kombinasyon terapisi"),
        "peptide": ("C07K 14/00", "Peptid 20+ amino asit"),
        "growth_factor": ("A61K 38/18", "Büyüme faktörü"),
        "hormone": ("A61K 38/22", "Hormon"),
        "coagulation_factor": ("A61K 38/36", "Koagülasyon faktörü"),
        "ai_diagnostic": ("G16H 50/20", "ML tabanlı teşhis"),
        "ai_imaging": ("G16H 30/00", "Medikal görüntü işleme"),
    }
    for feat in profile.special_features:
        fkey = feat.lower().replace(" ", "_").replace("-", "_")
        if fkey in feature_map:
            code, desc = feature_map[fkey]
            recs.append(Recommendation(
                code=code, description=desc, priority="secondary",
                rationale=f"Özel özellik '{feat}' için ek CPC",
            ))

    return recs


def generate_boolean_queries(recs: List[Recommendation], profile: MoleculeProfile) -> Dict[str, str]:
    """Önerilen CPC'lerden Boolean sorgu örnekleri üret."""
    primary_codes = [r.code for r in recs if r.priority == "primary"]
    
    # USPTO format (.CPC. suffix)
    uspto_cpc = " AND ".join([f"CPC/{c.replace(' ', '')}.CPC." for c in primary_codes[:3]])
    
    # Espacenet format (cpc=)
    espacenet_cpc = " AND ".join([f'cpc="{c}"' for c in primary_codes[:3]])
    
    # Keyword bileşeni
    keywords = []
    if profile.specific_target:
        keywords.append(profile.specific_target)
    if profile.molecule_class:
        keywords.append(profile.molecule_class)
    keywords.extend(profile.special_features)
    
    kw_str = " OR ".join(f'"{k}"' for k in keywords if k)
    
    return {
        "uspto": f"({uspto_cpc}) AND ({kw_str})" if kw_str else f"({uspto_cpc})",
        "espacenet": f"({espacenet_cpc}) AND ({kw_str})" if kw_str else f"({espacenet_cpc})",
    }


def print_recommendations(profile: MoleculeProfile, recs: List[Recommendation], queries: Dict[str, str]):
    """Önerileri formatla ve yazdır."""
    print()
    print("═" * 74)
    print(f"  CPC/IPC KOD ÖNERİSİ")
    print("═" * 74)
    print(f"  Modalite:       {profile.modality}")
    print(f"  Endikasyon:     {profile.indication}")
    if profile.specific_target:
        print(f"  Hedef:          {profile.specific_target}")
    if profile.molecule_class:
        print(f"  Molekül sınıfı: {profile.molecule_class}")
    if profile.dosage_form:
        print(f"  Dozaj formu:    {profile.dosage_form}")
    if profile.device_component:
        print(f"  Cihaz:          {profile.device_component}")
    if profile.special_features:
        print(f"  Özel özellikler: {', '.join(profile.special_features)}")
    
    print(f"\n  Toplam öneri: {len(recs)}")
    
    # Öncelik bazlı gruplama
    for priority in ["primary", "secondary", "tertiary"]:
        priority_recs = [r for r in recs if r.priority == priority]
        if not priority_recs:
            continue
        icon = {"primary": "🎯", "secondary": "🔸", "tertiary": "🔹"}[priority]
        print(f"\n  {icon} {priority.upper()} KODLAR ({len(priority_recs)})")
        print()
        for r in priority_recs:
            print(f"     {r.code:<20} — {r.description}")
            print(f"     {'':>20}   → {r.rationale}")

    print("\n" + "═" * 74)
    print("  BOOLEAN SORGU ÖRNEKLERİ")
    print("═" * 74)
    print(f"\n  USPTO Patent Public Search:")
    print(f"    {queries['uspto']}")
    print(f"\n  Espacenet:")
    print(f"    {queries['espacenet']}")
    print()


def print_recommendations_json(profile: MoleculeProfile, recs: List[Recommendation], queries: Dict[str, str]):
    """JSON formatında çıktı."""
    data = {
        "profile": asdict(profile),
        "recommendations": [asdict(r) for r in recs],
        "boolean_queries": queries,
    }
    print(json.dumps(data, indent=2, ensure_ascii=False))


# --- Örnekler ---
EXAMPLES = {
    "small_molecule": MoleculeProfile(
        modality="small_molecule",
        indication="hematology_malignancy",
        molecule_class="pyrimidine",
        dosage_form="tablet",
        specific_target="BTK",
        special_features=["combination_therapy"],
    ),
    "biologic": MoleculeProfile(
        modality="antibody",
        indication="oncology",
        specific_target="PD-1",
        dosage_form="injection",
        special_features=["combination_therapy"],
    ),
    "adc": MoleculeProfile(
        modality="adc",
        indication="oncology",
        specific_target="HER2",
        dosage_form="lyophilized",
    ),
    "car_t": MoleculeProfile(
        modality="car_t",
        indication="hematology_malignancy",
        specific_target="BCMA",
    ),
    "mrna": MoleculeProfile(
        modality="mrna",
        indication="oncology",
        special_features=["nanoparticle", "LNP"],
    ),
    "device": MoleculeProfile(
        modality="device",
        indication="hematology_general",
        device_component="auto_injector",
        special_features=["coagulation_factor"],
    ),
    "gene_therapy": MoleculeProfile(
        modality="gene_therapy",
        indication="hemophilia",
        special_features=["AAV", "FIX"],
    ),
}


def main():
    print()
    print("╔════════════════════════════════════════════════════════════════════════╗")
    print("║  pharmapatent v1.4.0 — CPC/IPC Code Recommender                       ║")
    print("║  Molekül/cihaz özelliklerinden CPC kodu önerisi                       ║")
    print("╚════════════════════════════════════════════════════════════════════════╝")

    json_output = '--json' in sys.argv

    # Example mode
    if '--example' in sys.argv:
        try:
            idx = sys.argv.index('--example')
            example_name = sys.argv[idx + 1]
        except (IndexError, ValueError):
            example_name = "small_molecule"
        
        if example_name not in EXAMPLES:
            print(f"❌ Bilinmeyen örnek: {example_name}")
            print(f"Mevcut: {list(EXAMPLES.keys())}")
            sys.exit(1)
        
        profile = EXAMPLES[example_name]
        if not json_output:
            print(f"\n📄 Örnek: {example_name}\n")
    
    else:
        # Interactive
        print("\n🎯 Interactive — molekül/cihaz profili girin:\n")
        try:
            modality = input("Modalite (small_molecule/antibody/adc/car_t/mrna/gene_therapy/radioligand/device): ").strip() or "small_molecule"
            indication = input("Endikasyon (oncology/hematology_malignancy/hemophilia/cardiovascular/neurology/...): ").strip() or "oncology"
            target = input("Hedef (HER2/CD20/PD-1/BCMA/FVIII, boş=atla): ").strip() or None
            mol_class = input("Molekül sınıfı (pyrimidine/pyrrole/indole, boş=atla): ").strip() or None
            dosage = input("Dozaj formu (tablet/capsule/injection/lyophilized/inhaler, boş=atla): ").strip() or None
            device = input("Cihaz bileşeni (syringe/pen/inhaler/pump, boş=atla): ").strip() or None
            features_raw = input("Özel özellikler (virgülle ayır, örn: bispecific,nanoparticle): ").strip()
            features = [f.strip() for f in features_raw.split(",") if f.strip()] if features_raw else []
            
            profile = MoleculeProfile(
                modality=modality,
                indication=indication,
                specific_target=target,
                molecule_class=mol_class,
                dosage_form=dosage,
                device_component=device,
                special_features=features,
            )
        except (KeyboardInterrupt, EOFError):
            print("\n⏹ İptal edildi.")
            sys.exit(0)

    recs = recommend_cpc(profile)
    queries = generate_boolean_queries(recs, profile)
    
    if json_output:
        print_recommendations_json(profile, recs, queries)
    else:
        print_recommendations(profile, recs, queries)


if __name__ == "__main__":
    main()
