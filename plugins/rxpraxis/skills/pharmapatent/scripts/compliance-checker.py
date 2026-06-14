#!/usr/bin/env python3
"""
compliance-checker.py — Farmasötik Compliance Otomatik Uyum Kontrolü

Pharma operasyonları + HCP etkileşimleri + pazarlama + tedarik zinciri + veri
işleme senaryolarını 7 majör compliance çerçevesine karşı değerlendirir:

    1. FCPA (US Foreign Corrupt Practices Act)
    2. UK Bribery Act 2010
    3. TR MASAK (Mali Suçları Araştırma Kurulu) + 5607 s.Kaçakçılıkla Mücadele
    4. KVKK (TR Kişisel Verileri Koruma Kanunu) / GDPR
    5. EFPIA Code of Practice (AB pharma etik)
    6. IFPMA Code (global pharma etik)
    7. Roche Group Audit compliance (internal — Mahir'in audit bağlamı)

Senaryo tipleri:
    - HCP honorarium (toplantı/konferans konuşmacı ödemesi)
    - Congress sponsorship
    - Advisory board
    - Hasta organizasyonu bağışı
    - Sample + tıbbi literatür dağıtımı
    - Medical education grant
    - Consulting agreement
    - Clinical trial investigator ödemeleri
    - KOL engagement
    - Promosyon malzemeleri
    - Dijital pazarlama + sosyal medya
    - Veri işleme (hasta + HCP)

Output: risk puanı (0-100) + kırmızı bayrak listesi + ilgili SOP referansları
+ öneriler.

Kullanım:
    python3 compliance-checker.py --example hcp-honorarium
    python3 compliance-checker.py --example advisory-board
    python3 compliance-checker.py --example clinical-investigator
    python3 compliance-checker.py --list-scenarios
    python3 compliance-checker.py --framework-table

Yazar: pharmapatent skill v1.8.0
"""

import sys
import json
import argparse
from dataclasses import dataclass, field, asdict
from typing import List, Dict


# --- Framework metadata ---

FRAMEWORKS = {
    "FCPA": {
        "name": "US Foreign Corrupt Practices Act",
        "jurisdiction": "US + US-listed firms globally",
        "key_rules": [
            "Anything of value to foreign official → bribery risk",
            "HCP'ler devlet sağlık sisteminde görevli → çoğunlukla 'foreign official'",
            "Books & records accuracy — her ödeme doğru kayıt",
            "Facilitation payments çok kısıtlı (US'te izinli — çoğu diğer yerde değil)",
        ],
        "penalties": "per-violation $2M firm / $250K + 5yr hapis individual",
    },
    "UKBA": {
        "name": "UK Bribery Act 2010",
        "jurisdiction": "UK + UK connection globally",
        "key_rules": [
            "FCPA'den daha sert: commercial bribery + facilitation payment YASAK",
            "Section 7: 'failure to prevent bribery' strict liability",
            "'Adequate procedures' defense — iyi tasarlanmış compliance program",
            "HCP etkileşimi özel dikkat — UK pharmaceutical code enforcement",
        ],
        "penalties": "unlimited fine + 10yr hapis",
    },
    "MASAK": {
        "name": "TR MASAK + 5549 + 6362 s. Kanunlar",
        "jurisdiction": "TR",
        "key_rules": [
            "Şüpheli işlem bildirimi (Suspicious Transaction Report)",
            "Müşteri tanıma (Know Your Customer) — distribütör, müşaviri",
            "Nakit işlem limitleri ve bildirim",
            "Rüşvet + kara para aklama koordinasyonu",
        ],
        "penalties": "TCK + idari para cezaları + 10yr'a kadar hapis",
    },
    "KVKK_GDPR": {
        "name": "TR KVKK 6698 + AB GDPR 2016/679",
        "jurisdiction": "TR + EU",
        "key_rules": [
            "Açık rıza VEYA meşru menfaat (Art. 6)",
            "Sağlık verisi özel nitelikli veri (Art. 9 GDPR / KVKK 6)",
            "Veri güvenliği teknik + idari önlemler",
            "Hak ihlalinde 72-saat bildirim (GDPR Art. 33) / makul süre KVKK",
            "Veri İşleyen sözleşmesi (DPA) zorunlu",
            "VERBIS (TR) / GDPR Art. 30 Record of Processing Activities",
        ],
        "penalties": "GDPR: €20M veya %4 global ciro; KVKK: ₺50M'a kadar",
    },
    "EFPIA": {
        "name": "EFPIA Code of Practice",
        "jurisdiction": "AB üyesi pharma firmalar (Türkiye AİFD gözleminde)",
        "key_rules": [
            "HCP/HCO transfer of value (ToV) yıllık şeffaf açıklama",
            "Hospitality sınırlı — meeting-related + makul",
            "Hediye yasak (düşük değerli tıbbi ürün hariç)",
            "Örnekler sınırlı — reçete onayı için",
            "Medical education grant — impartial + educational",
        ],
        "penalties": "Endüstri özdenetim — üyelik kaybı, reputational",
    },
    "IFPMA": {
        "name": "IFPMA Code of Practice",
        "jurisdiction": "Global (IFPMA üye firmalar)",
        "key_rules": [
            "EFPIA'ye benzer + global standardizasyon",
            "Yerel regülasyonlar IFPMA üstünde",
            "HCP etkileşimi şeffaflık",
            "Clinical trial registration + sonuç raporlama",
        ],
        "penalties": "Endüstri özdenetim",
    },
    "Roche_Group_Audit": {
        "name": "Roche Group Audit (internal)",
        "jurisdiction": "Roche Group worldwide (internal)",
        "key_rules": [
            "Congress + event management — pre-approval zorunlu",
            "HCP honorarium tariff — market-rate FMV bazlı",
            "Distributor due diligence — periyodik yenileme",
            "Sample traceability + storage + expiry",
            "Digital promotional content pre-approval",
            "Patient support program (PSP) governance",
        ],
        "penalties": "Internal corrective action + whistleblower investigation",
    },
}


@dataclass
class Scenario:
    """Değerlendirilecek compliance senaryosu."""
    name: str
    scenario_type: str     # hcp_honorarium / congress_sponsorship / advisory_board / ...
    description: str
    parameters: Dict       # Senaryo-spesifik parametreler
    
    
@dataclass
class ComplianceFlag:
    framework: str
    severity: str          # critical / high / medium / low / info
    finding: str
    recommendation: str


@dataclass
class ComplianceResult:
    scenario: Scenario
    flags: List[ComplianceFlag]
    overall_risk: str      # low / medium / high / critical
    risk_score: int        # 0-100
    required_approvals: List[str]
    applicable_sops: List[str]


# --- Severity mapping ---

SEVERITY_WEIGHTS = {
    "critical": 40,
    "high": 20,
    "medium": 10,
    "low": 5,
    "info": 0,
}


def aggregate_risk(flags: List[ComplianceFlag]) -> (str, int):
    score = sum(SEVERITY_WEIGHTS.get(f.severity, 0) for f in flags)
    score = min(100, score)
    
    critical_count = sum(1 for f in flags if f.severity == "critical")
    high_count = sum(1 for f in flags if f.severity == "high")
    
    if critical_count > 0:
        return ("critical", score)
    if high_count >= 2 or score >= 50:
        return ("high", score)
    if score >= 25:
        return ("medium", score)
    return ("low", score)


# --- Scenario evaluators ---

def evaluate_hcp_honorarium(params: Dict) -> List[ComplianceFlag]:
    """HCP honorarium değerlendirme."""
    flags = []
    fee = params.get("fee_per_hour_usd", 0)
    hours = params.get("hours", 1)
    total = fee * hours
    hcp_is_public_official = params.get("hcp_is_public_official", True)
    fmv_documented = params.get("fmv_documented", False)
    contract_signed = params.get("contract_signed", False)
    deliverables_defined = params.get("deliverables_defined", False)
    disclosure_consent = params.get("disclosure_consent", False)
    
    # FCPA: HCP public official ise özellikle dikkat
    if hcp_is_public_official:
        if not fmv_documented:
            flags.append(ComplianceFlag(
                framework="FCPA",
                severity="critical",
                finding="HCP devlet görevlisi (Türkiye'de üniversite hastanesi çalışanları dahil) + FMV dokümantasyonu yok. FCPA 'anything of value' kapsamında bribery riski.",
                recommendation="Harici FMV benchmarkı (pazar fiyatı anketi) ile honorarium'u doğrula; yazılı FMV rapor dosyasına ekle.",
            ))
        if total > 5000:
            flags.append(ComplianceFlag(
                framework="FCPA",
                severity="high",
                finding=f"Yüksek honorarium (${total} toplam). FCPA 'books & records' ve 'anti-bribery' hükümleri için risk seviyesi yükseliyor.",
                recommendation="Alternate: daha düşük saatlik oran + az saat; veya birden fazla KOL arasında paylaştırma.",
            ))
    
    # UK Bribery Act
    if not contract_signed:
        flags.append(ComplianceFlag(
            framework="UKBA",
            severity="high",
            finding="Yazılı sözleşme yok — UKBA Section 7 'failure to prevent bribery' strict liability için 'adequate procedures' savunmasını zayıflatır.",
            recommendation="Standart HCP consulting agreement imzalat (deliverables + FMV + conflict of interest).",
        ))
    
    # EFPIA / IFPMA
    if not deliverables_defined:
        flags.append(ComplianceFlag(
            framework="EFPIA",
            severity="high",
            finding="Deliverables tanımsız — EFPIA Code + IFPMA'ya göre her HCP ödemesi 'legitimate services' karşılığı olmalı.",
            recommendation="Saat başına bir output tanımla (slide deck, literatür incelemesi, advisory sunumu). Output'ı dosyada tut.",
        ))
    if not disclosure_consent:
        flags.append(ComplianceFlag(
            framework="EFPIA",
            severity="medium",
            finding="Transfer of Value (ToV) disclosure rızası alınmamış — EFPIA yıllık açıklama için HCP onayı gerekli.",
            recommendation="Sözleşmede disclosure rıza maddesi + yıllık EFPIA ToV raporuna dahil etme.",
        ))
    
    # MASAK
    if total >= 7500:    # TR'de nakit işlem bildirim eşiği yaklaşık
        flags.append(ComplianceFlag(
            framework="MASAK",
            severity="medium",
            finding=f"Ödeme tutarı ($ {total}) TR MASAK yüksek değerli işlem bildirim eşiğine yakın. Banka transferi ile ödeme + kayıt zorunlu.",
            recommendation="Nakit ödeme KESİNLİKLE hayır; banka havalesi + fatura + stopaj kesintisi.",
        ))
    
    # Roche-specific
    if not params.get("pre_approved", False):
        flags.append(ComplianceFlag(
            framework="Roche_Group_Audit",
            severity="high",
            finding="Pre-approval prosedürü tamamlanmamış. Roche HCP honorarium SOP v6/v7 ön-onay zorunlu.",
            recommendation="VEEVA Contract Management veya eşdeğer sistemden pre-approval aç; medical affairs + compliance imzası.",
        ))
    
    return flags


def evaluate_advisory_board(params: Dict) -> List[ComplianceFlag]:
    flags = []
    participants = params.get("participant_count", 0)
    location = params.get("location", "domestic")
    duration_days = params.get("duration_days", 1)
    per_participant_fee = params.get("per_participant_fee_usd", 0)
    meals_per_day_usd = params.get("meals_per_day_usd", 0)
    hotel_per_night_usd = params.get("hotel_per_night_usd", 0)
    family_accompany = params.get("family_accompany", False)
    
    # EFPIA hospitality
    if meals_per_day_usd > 150:
        flags.append(ComplianceFlag(
            framework="EFPIA",
            severity="high",
            finding=f"Günlük yemek maliyeti (${meals_per_day_usd}) EFPIA'nın 'modest hospitality' beklentisinin üstünde (~$100-150).",
            recommendation="Yemek menüsünü yeniden değerlendirip limit içine çek; lüks restoranlar yerine konferans/otel menüsü.",
        ))
    if hotel_per_night_usd > 300:
        flags.append(ComplianceFlag(
            framework="EFPIA",
            severity="medium",
            finding=f"Otel maliyeti (${hotel_per_night_usd}/gece) yüksek. EFPIA 4-yıldız seviyesini aşmamalı.",
            recommendation="Standart 4-yıldız otel seçeneği veya konferans merkezi.",
        ))
    
    # Family accompanying
    if family_accompany:
        flags.append(ComplianceFlag(
            framework="EFPIA",
            severity="critical",
            finding="Aile üyelerinin programa eşlik etmesi EFPIA + IFPMA Code + UKBA ağır ihlal — hediye/rüşvet olarak değerlendirilir.",
            recommendation="Aile üyesi masraflarını KESİNLİKLE karşılama; eğer HCP kendi isterse kendi cebinden ödemeli.",
        ))
    
    # Luxurious location
    if location.lower() in ["antalya resort", "bodrum", "costa smeralda", "maldives", "cancun"]:
        flags.append(ComplianceFlag(
            framework="EFPIA",
            severity="high",
            finding=f"Konum ({location}) turistik/lüks algısı yüksek. EFPIA: 'main purpose should be scientific, not leisure'.",
            recommendation="İş merkezli, turistik olmayan konum (major şehir konferans merkezi). Veya konumu gerekçelendirecek bilimsel altyapı gösterilmeli.",
        ))
    
    # Duration vs content
    total_fee = per_participant_fee * participants * duration_days
    if total_fee > 50000 and duration_days >= 2:
        flags.append(ComplianceFlag(
            framework="Roche_Group_Audit",
            severity="medium",
            finding=f"Yüksek toplam tutar (${total_fee}) ve uzun süre. Roche Group Audit congress/event yönetim findings'larına benzer pattern.",
            recommendation="Süreyi 1 güne indir + agenda'yı scientific content'e odakla + katılımcı sayısını optimize et.",
        ))
    
    # Agenda
    if not params.get("written_agenda", False):
        flags.append(ComplianceFlag(
            framework="IFPMA",
            severity="high",
            finding="Yazılı detaylı agenda eksik — danışma kurulunun 'scientific advice' olduğunu ispatlayacak doküman olmalı.",
            recommendation="Saat bazlı agenda + soru listesi + beklenen outputs önceden hazırla; toplantı sonrası dakikalar.",
        ))
    
    return flags


def evaluate_clinical_investigator(params: Dict) -> List[ComplianceFlag]:
    flags = []
    per_patient_fee = params.get("per_patient_fee_usd", 0)
    fmv_benchmarked = params.get("fmv_benchmarked", False)
    ctms_recorded = params.get("ctms_recorded", False)
    ct_registered = params.get("ct_registered", False)
    data_retention = params.get("data_retention_years", 0)
    hcp_also_consulting = params.get("hcp_also_in_consulting", False)
    
    # FCPA — per-patient payment yüksekse
    if per_patient_fee > 15000 and not fmv_benchmarked:
        flags.append(ComplianceFlag(
            framework="FCPA",
            severity="high",
            finding=f"Per-patient ödeme (${per_patient_fee}) piyasanın üstünde görünüyor + FMV benchmark yok. Bribery / kickback olarak yorumlanabilir.",
            recommendation="Harici benchmark (CRO fiyat listesi, Grant Thornton vb.) ile FMV doğrula.",
        ))
    
    # Clinical trial registration
    if not ct_registered:
        flags.append(ComplianceFlag(
            framework="IFPMA",
            severity="critical",
            finding="Klinik çalışma henüz ClinicalTrials.gov/EUCTR/CTIS'e kayıtlı değil. IFPMA + Helsinki Deklarasyonu + FDA FDAAA requirement.",
            recommendation="İlk hasta enroll'undan ÖNCE registration yapılmalı (NCT numarası veya EUCTR numarası).",
        ))
    
    # Double-role: investigator + consultant
    if hcp_also_consulting:
        flags.append(ComplianceFlag(
            framework="EFPIA",
            severity="high",
            finding="Investigator aynı zamanda consulting agreement altında — çifte ödeme hattı, conflict of interest algısı.",
            recommendation="İki rolü ayrı değerlendirme + her birinin legitimate services farklılığını dokümante et.",
        ))
    
    # Data retention
    if data_retention < 15:
        flags.append(ComplianceFlag(
            framework="KVKK_GDPR",
            severity="medium",
            finding=f"Veri saklama süresi ({data_retention} yıl) klinik araştırma regülasyon gereksinimlerinin altında (ICH-GCP: minimum 15-25 yıl).",
            recommendation="Veri saklama politikasını ICH-GCP + TİTCK + GDPR Art. 5 uyumuna göre revize et (minimum 15 yıl + pediatric 25 yıl).",
        ))
    
    if not ctms_recorded:
        flags.append(ComplianceFlag(
            framework="Roche_Group_Audit",
            severity="medium",
            finding="CTMS (Clinical Trial Management System) kaydı eksik — Roche clinical operations standardı.",
            recommendation="Tüm aktif investigator ilişkileri CTMS + financial disclosure sistemine girilmeli.",
        ))
    
    return flags


def evaluate_patient_data_processing(params: Dict) -> List[ComplianceFlag]:
    flags = []
    consent_obtained = params.get("consent_obtained", False)
    explicit_consent = params.get("explicit_consent", False)
    pseudonymization = params.get("pseudonymization", False)
    dpa_signed = params.get("dpa_with_vendor", False)
    data_export_eu_to_tr = params.get("data_export_eu_to_tr", False)
    data_subject_rights_sop = params.get("dsr_sop_in_place", False)
    verbis_registered = params.get("verbis_registered", False)
    breach_procedure = params.get("breach_procedure", False)
    
    # KVKK/GDPR — sensitive data
    if not consent_obtained:
        flags.append(ComplianceFlag(
            framework="KVKK_GDPR",
            severity="critical",
            finding="Sağlık verisi özel nitelikli — açık rıza veya Art. 9 istisnası zorunlu. Mevcut durumda hiçbir hukuki temel yok.",
            recommendation="Hasta onam formunu revize et: specific, informed, explicit consent; alternatif olarak Art. 9(2)(h) healthcare exception geçerliyse dokümante et.",
        ))
    elif not explicit_consent:
        flags.append(ComplianceFlag(
            framework="KVKK_GDPR",
            severity="high",
            finding="Onam alınmış ama 'açık rıza' (GDPR Art. 9 / KVKK 6) değil — sağlık verisi için yetersiz.",
            recommendation="Onam formunu 'açık rıza' seviyesine getir (unambiguous + informed + specific).",
        ))
    
    if not pseudonymization:
        flags.append(ComplianceFlag(
            framework="KVKK_GDPR",
            severity="high",
            finding="Pseudonymization uygulanmıyor — GDPR Art. 32 + KVKK teknik önlem eksik.",
            recommendation="Hasta ID → pseudonym mapping; ana liste ayrı key-managed database'de.",
        ))
    
    if not dpa_signed:
        flags.append(ComplianceFlag(
            framework="KVKK_GDPR",
            severity="critical",
            finding="Data Processing Agreement (DPA) yok — her third-party processor (CRO, cloud, lab) ile zorunlu.",
            recommendation="Tüm vendor'larla GDPR Art. 28 + KVKK uyumlu DPA imzala; standart AB Commission SCC kullan.",
        ))
    
    if data_export_eu_to_tr:
        flags.append(ComplianceFlag(
            framework="KVKK_GDPR",
            severity="high",
            finding="AB → TR veri transferi — Türkiye 'adequate country' değil. GDPR Art. 46 SCC + supplementary measures zorunlu.",
            recommendation="AB Commission Standard Contractual Clauses (2021/914) + transfer impact assessment + supplementary measures (encryption).",
        ))
    
    if not verbis_registered:
        flags.append(ComplianceFlag(
            framework="KVKK_GDPR",
            severity="medium",
            finding="VERBIS kaydı tamamlanmamış — KVKK veri sorumluları için zorunlu.",
            recommendation="VERBIS'e tescil + yıllık güncellemeleri sürdür.",
        ))
    
    if not breach_procedure:
        flags.append(ComplianceFlag(
            framework="KVKK_GDPR",
            severity="high",
            finding="Veri ihlali prosedürü yok — GDPR Art. 33-34 + KVKK m. 12 72-saat bildirim zorunluluğu yerine getirilemez.",
            recommendation="Breach response plan: detection → internal escalation → authority notification (72 saat) → data subject notification (gerekirse).",
        ))
    
    return flags


# --- Scenario registry ---

SCENARIOS = {
    "hcp-honorarium-risky": Scenario(
        name="HCP Honorarium — Yüksek Risk Senaryosu",
        scenario_type="hcp_honorarium",
        description="Türkiye üniversite hastanesi profesörüne advisory sunum için saatlik $2000 × 4 saat ödeme",
        parameters={
            "fee_per_hour_usd": 2000,
            "hours": 4,
            "hcp_is_public_official": True,
            "fmv_documented": False,
            "contract_signed": False,
            "deliverables_defined": False,
            "disclosure_consent": False,
            "pre_approved": False,
        },
    ),
    "hcp-honorarium-clean": Scenario(
        name="HCP Honorarium — Temiz Senaryo",
        scenario_type="hcp_honorarium",
        description="Üniversite hastanesi profesörüne peer-reviewed scientific presentation için $500/saat × 2 saat",
        parameters={
            "fee_per_hour_usd": 500,
            "hours": 2,
            "hcp_is_public_official": True,
            "fmv_documented": True,
            "contract_signed": True,
            "deliverables_defined": True,
            "disclosure_consent": True,
            "pre_approved": True,
        },
    ),
    "advisory-board-risky": Scenario(
        name="Advisory Board — Kırmızı Bayraklarla Dolu",
        scenario_type="advisory_board",
        description="Bodrum resort'ta 3 günlük advisory board, 20 katılımcı, aile üyeleri eşlik, lüks yemek",
        parameters={
            "participant_count": 20,
            "location": "Bodrum",
            "duration_days": 3,
            "per_participant_fee_usd": 5000,
            "meals_per_day_usd": 250,
            "hotel_per_night_usd": 450,
            "family_accompany": True,
            "written_agenda": False,
        },
    ),
    "advisory-board-clean": Scenario(
        name="Advisory Board — EFPIA Compliant",
        scenario_type="advisory_board",
        description="İstanbul konferans merkezi 1 gün, 8 uzman, scientific agenda, uygun hospitality",
        parameters={
            "participant_count": 8,
            "location": "İstanbul conference center",
            "duration_days": 1,
            "per_participant_fee_usd": 2000,
            "meals_per_day_usd": 120,
            "hotel_per_night_usd": 250,
            "family_accompany": False,
            "written_agenda": True,
        },
    ),
    "clinical-investigator": Scenario(
        name="Klinik Çalışma Investigator Sözleşmesi",
        scenario_type="clinical_investigator",
        description="Oncology Faz III investigator sözleşmesi, per-patient $25K, pre-enrollment",
        parameters={
            "per_patient_fee_usd": 25000,
            "fmv_benchmarked": False,
            "ctms_recorded": True,
            "ct_registered": False,
            "data_retention_years": 10,
            "hcp_also_in_consulting": True,
        },
    ),
    "patient-data-eu-to-tr": Scenario(
        name="AB → TR Hasta Veri Transferi",
        scenario_type="patient_data_processing",
        description="Alman merkez bir CRO'dan Türk araştırma merkezine EHR veri transferi — hasta kohort",
        parameters={
            "consent_obtained": True,
            "explicit_consent": False,
            "pseudonymization": False,
            "dpa_with_vendor": False,
            "data_export_eu_to_tr": True,
            "dsr_sop_in_place": False,
            "verbis_registered": False,
            "breach_procedure": False,
        },
    ),
}


SCENARIO_EVALUATORS = {
    "hcp_honorarium": evaluate_hcp_honorarium,
    "advisory_board": evaluate_advisory_board,
    "clinical_investigator": evaluate_clinical_investigator,
    "patient_data_processing": evaluate_patient_data_processing,
}


def evaluate_scenario(scenario: Scenario) -> ComplianceResult:
    evaluator = SCENARIO_EVALUATORS.get(scenario.scenario_type)
    if not evaluator:
        return ComplianceResult(scenario=scenario, flags=[], overall_risk="unknown", risk_score=0, required_approvals=[], applicable_sops=[])
    
    flags = evaluator(scenario.parameters)
    overall, score = aggregate_risk(flags)
    
    # SOP refs
    sop_map = {
        "hcp_honorarium": ["Roche HCP Honorarium SOP v7", "EFPIA Code 2023", "FCPA Guidance 2020"],
        "advisory_board": ["Roche Advisory Board Management SOP", "EFPIA Code Section 5 Hospitality", "IFPMA Code"],
        "clinical_investigator": ["Roche CTMS + Financial Disclosure SOP", "ICH-GCP E6(R2)", "TITCK İyi Klinik Uygulamalar"],
        "patient_data_processing": ["KVKK 6698 + GDPR 2016/679", "Roche Global Data Privacy Policy", "Standard Contractual Clauses 2021/914"],
    }
    sops = sop_map.get(scenario.scenario_type, [])
    
    # Required approvals
    approval_map = {
        "hcp_honorarium": ["Medical Affairs Head", "Compliance Officer", "Finance"],
        "advisory_board": ["Medical Affairs Head", "Compliance", "General Manager"],
        "clinical_investigator": ["Medical Director", "CRO Partner", "Compliance", "Finance"],
        "patient_data_processing": ["DPO (Data Protection Officer)", "Legal", "IT Security"],
    }
    approvals = approval_map.get(scenario.scenario_type, [])
    
    return ComplianceResult(
        scenario=scenario,
        flags=flags,
        overall_risk=overall,
        risk_score=score,
        required_approvals=approvals,
        applicable_sops=sops,
    )


def print_result(result: ComplianceResult):
    print()
    print("═" * 90)
    print(f"  COMPLIANCE DEĞERLENDİRME")
    print("═" * 90)
    print(f"  Senaryo: {result.scenario.name}")
    print(f"  Tip: {result.scenario.scenario_type}")
    print(f"  Açıklama: {result.scenario.description}")
    print()
    
    risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴", "unknown": "⚪"}[result.overall_risk]
    print(f"  ╔═ OVERALL RİSK ══════════════════════════════════════╗")
    print(f"  ║  {risk_emoji} {result.overall_risk.upper():<10}  Skor: {result.risk_score}/100")
    print(f"  ╚═════════════════════════════════════════════════════╝")
    print()
    
    if result.flags:
        print(f"  ┌─ COMPLIANCE FLAGS ({len(result.flags)}) ─────────────────────────────────────┐")
        for i, flag in enumerate(result.flags, 1):
            sev_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🔵", "info": "ℹ"}[flag.severity]
            print(f"  │  {i}. {sev_icon} [{flag.framework}] {flag.severity.upper()}")
            for line in wrap_text(f"   Bulgu: {flag.finding}", 78):
                print(f"  │     {line}")
            for line in wrap_text(f"   Öneri: {flag.recommendation}", 78):
                print(f"  │     {line}")
            print(f"  │")
        print(f"  └──────────────────────────────────────────────────────────────┘")
        print()
    else:
        print(f"  ✓ Hiç kırmızı bayrak tespit edilmedi.")
        print()
    
    if result.required_approvals:
        print(f"  ┌─ GEREKLİ ONAYLAR ───────────────────────────────────────────┐")
        for a in result.required_approvals:
            print(f"  │  ☐ {a}")
        print(f"  └──────────────────────────────────────────────────────────────┘")
        print()
    
    if result.applicable_sops:
        print(f"  ┌─ İLGİLİ SOP'LAR ────────────────────────────────────────────┐")
        for s in result.applicable_sops:
            print(f"  │  • {s}")
        print(f"  └──────────────────────────────────────────────────────────────┘")
        print()


def wrap_text(text: str, width: int) -> List[str]:
    words = text.split()
    lines = []
    current = []
    current_len = 0
    for w in words:
        if current_len + len(w) + 1 > width:
            lines.append(" ".join(current))
            current = [w]
            current_len = len(w)
        else:
            current.append(w)
            current_len += len(w) + 1
    if current:
        lines.append(" ".join(current))
    return lines


def print_framework_table():
    print()
    print("═" * 100)
    print("  COMPLIANCE FRAMEWORK TABLOSU — pharmapatent v1.8.0")
    print("═" * 100)
    for key, fw in FRAMEWORKS.items():
        print(f"\n  ▸ {key}: {fw['name']}")
        print(f"    Kapsam: {fw['jurisdiction']}")
        print(f"    Cezalar: {fw['penalties']}")
        print(f"    Kilit kurallar:")
        for rule in fw['key_rules']:
            for line in wrap_text(f"- {rule}", 90):
                print(f"      {line}")


def main():
    parser = argparse.ArgumentParser(description="Compliance Checker v1.8.0")
    parser.add_argument('--example', type=str)
    parser.add_argument('--format', default='ascii', choices=['ascii', 'markdown', 'json'])
    parser.add_argument('--list-scenarios', action='store_true')
    parser.add_argument('--framework-table', action='store_true')
    
    args = parser.parse_args()
    
    if args.framework_table:
        print_framework_table()
        return
    
    if args.list_scenarios:
        print("\nMevcut senaryolar:")
        for name, s in SCENARIOS.items():
            print(f"  {name:<30} {s.name}")
        return
    
    if not args.example:
        print()
        print("╔════════════════════════════════════════════════════════════════════╗")
        print("║  pharmapatent v1.8.0 — Compliance Checker                          ║")
        print("║  FCPA + UKBA + MASAK + KVKK/GDPR + EFPIA + IFPMA + Roche Group    ║")
        print("╚════════════════════════════════════════════════════════════════════╝")
        print()
        print("Kullanım:")
        print("  --example hcp-honorarium-risky     Yüksek risk HCP ödeme")
        print("  --example hcp-honorarium-clean     Temiz HCP ödeme")
        print("  --example advisory-board-risky     Kırmızı bayraklı AB")
        print("  --example advisory-board-clean     EFPIA uyumlu AB")
        print("  --example clinical-investigator    Klinik çalışma investigator")
        print("  --example patient-data-eu-to-tr    AB → TR hasta verisi")
        print("  --list-scenarios                   Tüm senaryolar")
        print("  --framework-table                  7 compliance framework detayı")
        return
    
    if args.example not in SCENARIOS:
        print(f"❌ Bilinmeyen senaryo: {args.example}")
        sys.exit(1)
    
    scenario = SCENARIOS[args.example]
    result = evaluate_scenario(scenario)
    
    if args.format == 'json':
        print(json.dumps(asdict(result), indent=2, ensure_ascii=False))
    else:
        print_result(result)


if __name__ == "__main__":
    main()
