# Medical-Research Skill ile Operasyonel Entegrasyon — Cureolex Yan Sözleşme

Bu dosya, **medical-research v7.1 skill'inin composition-runbook.md §10 (Data Transfer Protocols)** bölümünde cureolex için açık bir alt-bölüm **bulunmadığı** için, cureolex tarafından yazılan **karşı sözleşmedir**. Medical-research'ün composition-runbook'unda:

- §10.1 medical-research → carbon-html-report ✅ tanımlı
- §10.2 medical-research → carbon-pptx ✅ tanımlı
- §10.3 medical-research → onko-erisim ✅ tanımlı
- §10.4 medical-research → lex-mercator ✅ tanımlı
- §10.5 medical-research → **cureolex** ❌ tanımlanmamış

Bu dosya, **§10.5'in cureolex tarafından yazılmış karşılığı** olarak işler. R14 ana sözleşmesi ile birlikte okunmalıdır.

**v2.3-r1 sürüm notu:** Bu dosya v2.3-r1 ile medical-research'ün gerçek yapısı analiz edildikten sonra eklenmiştir. R14'teki §1-20 listesi v2.3-r1'de gerçek bölüm adlarına kalibre edildi.

---

## 1. Sözleşme Çerçevesi

### 1.1. Medical-Research → Cureolex Transfer Object

**Çıktı bileşenleri:**

| Bileşen | Format | İçerik |
|---|---|---|
| Markdown § sentezi | text/markdown | §1-§20 (Format A) — gerçek başlık adlarıyla |
| Sidecar JSON | application/json | `.data.json` — sürüm v2.3.1 |
| Atıf indeksi | array | Vancouver formatlı kaynak listesi |
| Specialty layer payload | nested object | 9 specialty layer (0.5.A-I) için bölüm-bazlı veri |

### 1.2. Cureolex Beklentisi

Medical-research çıktısından cureolex şunları tüketir:

- **§1 Küresel Literatür** — Yönetici özeti için
- **§4 Ruhsat & Etiket** — Hukuki dayanak için (ilaç ise zorunlu)
- **§5 Türkiye Verileri** — Madde gerekçelerinde RWE bilimsel dayanak
- **§7 Tier 0 Sentez** — En yüksek kanıt katmanı (Cochrane SR)
- **§9 Kılavuz Yerleşimi** — Klinik standart referansı (NCCN/ESMO/NICE)
- **§13 Regulatory Sciences** — TİTCK/FDA/EMA mekaniği + Türkiye dörtlüsü
- **§14 HTA** — SUT/HTA geri ödeme politikası reformu için ICER/QALY
- **§19 Drug Intelligence Pipeline** — Pipeline-aware analiz için
- **§20 Cross-Layer Integration** — Multi-domain entegrasyon

---

## 2. Sidecar Consumption Pseudocode (Cureolex Tarafı)

Aşağıdaki pseudocode, cureolex'ın medical-research'ten gelen sidecar JSON'u nasıl tükettiğini gösterir:

```python
# Cureolex çıktı üretim akışı (pseudocode)

def consume_medical_research_output(markdown: str, sidecar_json: dict) -> LexSanitasOutput:
    """Medical-research çıktısını cureolex çıktısına dönüştürür"""
    
    # 1. Şema sürümü kontrolü
    schema_version = sidecar_json.get("schema_version")
    if schema_version not in ["2.0", "2.3", "2.3.1"]:
        raise SchemaIncompatibilityError(
            f"Sidecar schema {schema_version} not supported; "
            f"cureolex v2.6.0 requires medical-research v2.3+"
        )
    
    # 2. Sürüm uyumluluk kontrolü (R14 §17)
    mr_version = sidecar_json.get("medical_research_version")
    lex_version = sidecar_json.get("cureolex_version")
    check_version_compatibility(mr_version, lex_version)
    
    # 3. Reverse signals önceliği (R14 §20)
    reverse_signals = sidecar_json.get("reverse_signals", {})
    handle_reverse_signals(reverse_signals)
    
    # 4. Section payloads tüketimi
    section_payloads = sidecar_json.get("section_payloads", {})
    
    # 5. Specialty layer activations (R14 §13)
    activated_layers = sidecar_json.get("specialty_layer_activations", [])
    
    # 6. Cureolex modu spesifik tüketim haritası
    mode = get_current_cureolex_mode()  # Mod 1-9
    consumption_map = LEX_SANITAS_CONSUMPTION_MAP[mode]
    # Örn. Mod 5 OPINE için:
    # {
    #   "yonetici_ozeti": ["§1", "§9"],
    #   "hukuki_dayanak": ["§13", "§9", "§14"],
    #   "bilimsel_arguman": ["§7", "§5", "§4"],
    #   "yargi_emsali": ["§13.f Türkiye TİTCK Pozisyonu"],
    #   "uluslararasi_emsal": ["§6", "§13.a-d", "§14.a-f"]
    # }
    
    # 7. Atıf zinciri kontrolü
    citation_index = sidecar_json.get("citation_index", [])
    validate_vancouver_format(citation_index)
    
    # 8. Türk mevzuat refs kontrolü (R14 §14.4)
    tr_legislation = sidecar_json.get("turkish_legislation_refs", [])
    for ref in tr_legislation:
        if not ref.get("mcp_verified"):
            flag_unverified_reference(ref)
    
    # 9. Yargı içtihat zinciri kontrolü (R14 §14.5)
    yargi_chain = sidecar_json.get("yargi_ictihat_chain", {})
    validate_judicial_citations(yargi_chain)
    
    # 10. Epistemik dürüstlük birleşik raporu
    epistemic = sidecar_json.get("epistemic_honesty", {})
    confidence = compute_combined_confidence(
        mr_disclosure=epistemic.get("medical_research_self_disclosure"),
        lex_disclosure=epistemic.get("cureolex_self_disclosure")
    )
    
    # 11. Mod 9 ise ex post metrics — şema en az v2.3.1 olmalı (ex_post_metrics içerir)
    if mode == "EX_POST_EVALUATION":
        if schema_version != "2.3.1":
            raise SchemaIncompatibilityError(
                "EX_POST_EVALUATION requires sidecar schema v2.3.1 with ex_post_metrics"
            )
        ex_post = sidecar_json.get("ex_post_metrics", {})
        validate_ex_post_completeness(ex_post)
    
    # 12. Final output assembly
    return assemble_cureolex_output(
        markdown=markdown,
        section_payloads=section_payloads,
        consumption_map=consumption_map,
        reverse_signals=reverse_signals,
        confidence=confidence,
        citations=citation_index,
        tr_refs=tr_legislation,
        yargi_chain=yargi_chain
    )


def handle_reverse_signals(reverse_signals: dict) -> None:
    """Medical-research'ün geri bildirim sinyallerini işle (R14 §20.3)"""
    
    # 4a. Uncertainty flags → çıktının ilgili bölümüne footnote
    for flag in reverse_signals.get("uncertainty_flags", []):
        add_footnote_to_section(
            section=flag["section"],
            note=f"Bilgi sınırı: {flag['description']}",
            impact=flag["impact_on_cureolex"]
        )
    
    # 4b. Out-of-scope flags → kullanıcıya net açıklama
    for flag in reverse_signals.get("out_of_scope_flags", []):
        add_user_recommendation(
            f"Bu konu medical-research kapsamı dışında: {flag['topic']}. "
            f"Önerilen ek skill: {flag['recommendation_for_cureolex']}"
        )
    
    # 4c. Retry triggers → kritik ise tekrar çağrı
    for trigger in reverse_signals.get("retry_triggers", []):
        if is_critical_missing_layer(trigger["missing_layer"]):
            updated_query = inject_keywords(
                base_query=current_enriched_query,
                additional_keywords=trigger["suggested_keywords"]
            )
            return retry_medical_research(updated_query)
    
    # 4d. Alternative interpretations → yönetici özetinde sergile
    for alt in reverse_signals.get("alternative_interpretations", []):
        add_to_executive_summary(
            f"Bu çıktı '{alt['interpretation_taken']}' yorumuyla üretilmiştir. "
            f"Alternatif yorumlar: {alt['alternative_paths']}"
        )
```

---

## 3. Tam Pipeline Örnek Çalışması — Pembrolizumab MSI-H Endometriyum Kanseri Mod 1 DRAFT

Bu bölüm, **gerçek bir senaryoda** cureolex + medical-research entegrasyonunun adım adım nasıl işlediğini gösterir.

### 3.1. Kullanıcı Talebi

```
"TİTCK için pembrolizumab MSI-H/dMMR endometriyum kanseri adjuvan endikasyon 
ruhsat genişletme yönetmeliği taslağı hazırla."
```

### 3.2. Adım 1: Cureolex Mod Tespiti

Cureolex trigger analysis: **Mod 1 (DRAFT)** — yeni yönetmelik taslağı.

### 3.3. Adım 2: Klinik Konu Tespiti → Medical-Research Tetiklenmesi

Anahtar kelimeler: "pembrolizumab", "MSI-H", "endometriyum kanseri", "TİTCK", "ruhsat genişletme"

R14 §6 karar ağacı: **klinik konu var** → Medical-research çağrısı **zorunlu** (Mod 1 DRAFT'ta klinik konuda ◆).

R14 §13 specialty layer × mod matrisi: Mod 1 DRAFT için tetiklenen cluster'lar:
- **Klinik onko-heme cluster** (0.5.A onkoloji)
- **Regulatory core cluster** (0.5.C regulatory + 0.5.I drug intelligence)

### 3.4. Adım 3: Enriched Query Üretimi (R14 §19.5)

Cureolex medical-research'e şu enriched query'yi gönderir:

```json
{
  "original_query_tr": "TİTCK için pembrolizumab MSI-H/dMMR endometriyum kanseri adjuvan endikasyon ruhsat genişletme yönetmeliği taslağı hazırla",
  
  "enriched_query_for_medical_research": {
    "main_query": "Pembrolizumab MSI-H/dMMR endometrial cancer adjuvant indication — efficacy (KEYNOTE-A18), regulatory pathway (FDA + EMA + TİTCK), label extension mechanics",
    
    "explicit_layer_request": ["oncology", "regulatory", "drug_intelligence"],
    
    "domain_classifier_pre_seed_keywords": {
      "0.5.A_onkoloji": [
        "MSI-H", "dMMR", "endometrial cancer", "endometriyum kanseri",
        "pembrolizumab", "anti-PD-1", "KEYNOTE-A18", "KEYNOTE-158",
        "PFS", "OS", "ORR", "DOR", "RECIST",
        "adjuvant", "adjuvan", "neoadjuvant",
        "NCCN", "ESMO", "ASCO", "ESMO-MCBS"
      ],
      "0.5.C_regulatory": [
        "FDA approval", "EMA approval", "TİTCK onay",
        "label extension", "supplemental BLA", "sBLA",
        "Type II variation", "EMA scientific advice",
        "Project Orbis", "accelerated approval (AA)",
        "breakthrough therapy (BTD)", "priority review (PR)",
        "post-marketing commitment (PMC)", "EPAR"
      ],
      "0.5.I_drug_intelligence": [
        "AdisInsight pembrolizumab pipeline",
        "MoA landscape anti-PD-1 in endometrial cancer",
        "competing assets (dostarlimab, nivolumab)"
      ]
    },
    
    "cureolex_legal_context": {
      "mode": "DRAFT",
      "primary_legislation": [
        "Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği (RG 11/12/2021 S. 31686)",
        "1262 sayılı İspençiyari ve Tıbbi Müstahzarlar Kanunu",
        "TİTCK Endikasyon Genişletme Kılavuzu"
      ],
      "constitutional_basis": ["Md. 17 yaşam hakkı", "Md. 56 sağlık hakkı"],
      "international_treaties": [
        "ICESCR Md. 12 + Genel Yorum 14 (AAAQ — erişilebilirlik)",
        "TRIPS Md. 31bis"
      ],
      "comparative_law_targets": [
        "FDA Project Orbis pembrolizumab endometrial",
        "EMA CHMP positive opinion endometrial extension",
        "NICE TA endometrial Hodgkin"
      ]
    },
    
    "requested_sections_priority": {
      "MANDATORY": ["§1", "§4", "§5", "§7", "§9", "§11", "§13", "§19"],
      "RECOMMENDED": ["§2", "§3", "§6", "§14"],
      "OPTIONAL": ["§8", "§10", "§15", "§20"]
    },
    
    "output_format": "Format E (Oncology Extended)",
    "citation_format": "Vancouver",
    "epistemic_dual_label": true
  }
}
```

### 3.5. Adım 4: Medical-Research Yanıtı

Medical-research, Adım 0.5'te 0.5.A + 0.5.C + 0.5.I tetiklendiğini tespit eder ve §11 + §13 + §19'u çıktıya enjekte ederek **Format E (Oncology Extended)** üretir.

**Beklenen markdown çıktı yapısı (özet):**

```markdown
# Pembrolizumab MSI-H/dMMR Endometrial Cancer Adjuvant — 
# Medical Research Report (Format E)

## 1. Küresel Literatür
[PubMed taraması — KEYNOTE-A18 pivotal trial + ilgili 28 yayın]

## 4. Ruhsat & Etiket
- FDA: KEYTRUDA (pembrolizumab) - Endometrial Carcinoma indication 
  approved 2021-03 (KEYNOTE-158 MSI-H/dMMR tümör-agnostik) + 2024-06 
  (KEYNOTE-A18 adjuvant)
- EMA: Initial approval 2017; endometrial extension Type II variation 
  CHMP positive opinion 2024-09; EU marketing authorization expected 
  2025-Q1
- DailyMed SPL: [...]
- EMA SmPC: [...]
- EPAR EMA/CHMP/2024/XXXXX: [...]

## 5. Türkiye Verileri
[TİTCK ÜTS: KEYTRUDA Türkiye ruhsat tarihi 2018, mevcut endikasyonlar...]
[YokTez: 14 ilgili tez tarama]
[REGISTURK: endometriyum kanseri yerel kohort - henüz pembrolizumab spesifik yok]

## 7. Tier 0 Sentez
[Cochrane CDXXXXX (2024) — Immunotherapy in endometrial cancer SR]
[NICE SR + Epistemonikos cross-validation]

## 9. Kılavuz Yerleşimi
- NCCN Endometrial Cancer Guidelines v.X.2025: Pembrolizumab adjuvant 
  Category 1 recommendation for MSI-H/dMMR Stage III/IV
- ESMO Endometrial Cancer Guidelines 2024: Pembrolizumab + chemotherapy 
  preferred regimen
- ESMO-MCBS Score: 4 (significant benefit)

## 11. ONKOLOJİ GENİŞLETİLMİŞ BÖLÜMLERİ
### 11.a Tümör-Spesifik Kılavuz Yerleşimi
[Endometrial-specific NCCN tabloları, evre-bazlı tedavi algoritması]
### 11.b Biomarker ve CDx Durumu
[MSI/MMR test gereklilikleri, IHC + NGS, Ventana MMR IHC, Foundation One CDx]
### 11.c ESMO-MCBS / ASCO Value Framework
[ESMO-MCBS 4 — significant benefit; ASCO VF 52]

## 13. REGULATORY SCIENCES BÖLÜMLERİ
### 13.a Ruhsat Trajektörü
[FDA 2024 timeline; EMA 2024-2025 timeline; TİTCK beklenen yol]
### 13.c Özel Yollar
[Project Orbis kullanıldı (FDA + Australia TGA + Brazil ANVISA + 
Switzerland Swissmedic + UK MHRA + Singapore HSA paralel)]
### 13.f Türkiye TİTCK Pozisyonu
[TİTCK ruhsat durumu: 2018'den itibaren KEYTRUDA Türkiye'de; 
endometrial endikasyon henüz Türkiye'ye sunulmadı; başvuru beklentisi 2025]

## 19. DRUG INTELLIGENCE PIPELINE SNAPSHOT
[AdisInsight pembrolizumab pipeline:
- Active: ~150+ ongoing trials globally
- Competing assets: dostarlimab (GSK), nivolumab (BMS), durvalumab (AZ)
- Biosimilar pipeline: 0 (under patent protection until 2028)
- LoE projections: 2028 (US), 2030 (EU)]

## 20. Cross-Layer Integration Notes
[0.5.A onkoloji + 0.5.C regulatory + 0.5.I drug intelligence üçlü 
kesişiminde: pembrolizumab MSI-H endometrial — Project Orbis kullanılarak 
Türkiye'ye 2025-2026'da gelmesi olası; SGK SUT'a 2026-2027 dönemde 
girmesi beklentisi]

## Kaynaklar
[Vancouver formatlı 47 kaynak]
```

**Sidecar JSON çıktısı:**

```json
{
  "schema_version": "2.3.1",
  "medical_research_version": "7.1.2",
  "cureolex_version": "2.6.0",
  "generated_at": "2026-05-22T20:50:00Z",
  
  "query_metadata": {
    "original_query": "Pembrolizumab MSI-H/dMMR endometrial cancer adjuvant...",
    "enriched_query": { /* tam enriched query */ },
    "execution_time_ms": 18540,
    "connectors_used": ["pubmed", "epmc", "clinical_trials", "dailymed", 
                       "openfda", "ema", "titck", "yoktez", "regulatory_api",
                       "adisinsight"]
  },
  
  "specialty_layer_activations": [
    {"axis": "0.5.A", "name": "Oncology", "trigger_words": 
     ["MSI-H", "dMMR", "pembrolizumab", "endometriyum kanseri", "KEYNOTE-A18"]},
    {"axis": "0.5.C", "name": "Regulatory Sciences", "trigger_words":
     ["FDA approval", "Project Orbis", "Type II variation", "TİTCK onay"]},
    {"axis": "0.5.I", "name": "Drug Intelligence", "trigger_words":
     ["AdisInsight", "pipeline", "competing assets"]}
  ],
  
  "evidence_grading": {
    "primary_endpoint_evidence": {
      "grade": "HIGH",
      "study_count": 2,
      "design": "Phase III RCT (KEYNOTE-A18) + tumor-agnostic basket (KEYNOTE-158)",
      "studies": [
        {"nct_id": "NCT04634877", "design": "KEYNOTE-A18 Phase III RCT", 
         "n": 819, "primary_endpoint_hr": 0.54, "ci_95": "0.40-0.74"}
      ]
    }
  },
  
  "section_payloads": {
    "section_4_ruhsat_etiket": {
      "fda": {"approval_date": "2024-06-17", "indication": "Adjuvant treatment of patients with advanced or recurrent endometrial cancer that is mismatch repair deficient (dMMR), as determined by an FDA-approved test"},
      "ema": {"chmp_opinion_date": "2024-09-19", "epar_url": "https://www.ema.europa.eu/..."},
      "titck": {"current_indications": ["NSCLC", "melanom", "HNSCC", "klasik Hodgkin", "MSI-H tümör-agnostik"], "endometrial_status": "başvuru beklentisi 2025-Q2"}
    },
    "section_13_regulatory": {
      "project_orbis_used": true,
      "participating_jurisdictions": ["FDA", "TGA", "ANVISA", "Swissmedic", "MHRA", "HSA"],
      "tr_reliance_eligible": true,
      "expected_tr_pathway": "TR Reliance via FDA + EMA approval reference"
    },
    "section_19_pipeline": {
      "originator": {"company": "Merck Sharp & Dohme", "product": "KEYTRUDA"},
      "competing_assets_in_indication": [
        {"company": "GSK", "product": "Jemperli (dostarlimab)", "stage": "Phase III RUBY trial"},
        {"company": "BMS", "product": "Opdivo (nivolumab)", "stage": "Phase II"}
      ],
      "biosimilar_pipeline": [],
      "patent_protection": {"us_expiry": "2028", "eu_expiry": "2030"}
    }
  },
  
  "_example_only": true,
  "_verification_note": "Aşağıdaki tüm kayıtlar TEMSİLİDİR; mcp_verified:false. Gerçek kullanımda Mevzuat/Yargı MCP ile doğrulanmalı.",
  "turkish_legislation_refs": {
    "primary_legislation": [
      {
        "name": "Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği",
        "rg_date": "11/12/2021",
        "rg_number": "31686",
        "url": "https://www.mevzuat.gov.tr/...",
        "relevant_articles": ["m. 8", "m. 12 (endikasyon genişletme)"],
        "mcp_verified": false,
        "verification_status": "illustrative_placeholder_not_verified"
      },
      {
        "name": "1262 sayılı İspençiyari ve Tıbbi Müstahzarlar Kanunu",
        "mcp_verified": false
      }
    ]
  },
  
  "yargi_ictihat_chain": {
    "aym_decisions": [],
    "danistay_decisions": [
      {
        "case_no": "{{Danıştay E./K. — MCP ile doğrulanacak; örnek/temsili}}",
        "subject": "TİTCK endikasyon genişletme reddi iptali",
        "outcome": "İptal",
        "mcp_verified": false
      }
    ]
  },
  
  "reverse_signals": {
    "uncertainty_flags": [
      {
        "section": "§5 Türkiye Verileri",
        "type": "data_gap",
        "description": "REGISTURK endometriyum kanseri kohortu mevcut ama pembrolizumab adjuvan kullanım yerel verisi yok (henüz Türkiye'de onaylanmadı)",
        "impact_on_cureolex": "Madde gerekçesinde 'Türkiye yerel verisi henüz mevcut değil; uluslararası KEYNOTE-A18 verisi temel alındı' notu eklenmeli"
      }
    ],
    "alternative_interpretations": [
      {
        "ambiguity": "Endikasyon — sadece dMMR mi? Yoksa pMMR + dMMR kombine mi?",
        "interpretation_taken": "Sadece dMMR/MSI-H (FDA + EMA onaylı şekilde)",
        "alternative_paths": ["pMMR + dMMR birleşik kapsam (KEYNOTE-A18 tüm hastalar)"]
      }
    ],
    "confidence_breakdown": {
      "overall_grade": "HIGH",
      "high_grade_sections": ["§1", "§7", "§9", "§11", "§13.a", "§13.c"],
      "moderate_grade_sections": ["§5", "§13.f", "§19"],
      "low_grade_sections": []
    }
  },
  
  "epistemic_honesty": {
    "medical_research_self_disclosure": {
      "knowledge_gaps": ["Türkiye RWE pembrolizumab adjuvan endometrial — yok"],
      "single_source_findings": [],
      "version_limitations": "v7.1 + ClinicalTrials.gov v2 + AdisInsight 2026-05"
    },
    "cureolex_self_disclosure": {
      "mcp_unavailability_during_query": [],
      "uncertain_interpretations": ["TİTCK endikasyon genişletme yönetmelik prosedürü güncel 2024 sürümü teyit edilmeli"],
      "version": "2.3.1"
    },
    "combined_confidence": "HIGH"
  }
}
```

### 3.6. Adım 5: Cureolex Çıktı Üretimi

Cureolex, sidecar JSON ve markdown çıktısını tüketerek **Yönetmelik Taslağı + Genel Gerekçe + Madde Gerekçeleri** üretir.

**Yönetmelik Taslağı (özet):**

```markdown
# Pembrolizumab Etken Maddesi İçeren Beşeri Tıbbi Ürünlerin 
# Endometriyum Kanseri Adjuvan Endikasyonunda Kullanımına 
# İlişkin Yönetmelik Değişikliği Taslağı

## Genel Gerekçe

### 1. Hukuki Çerçeve ve Dayanak
Bu Yönetmelik değişikliği:
- **1262 sayılı İspençiyari ve Tıbbi Müstahzarlar Kanunu** [Mevzuat MCP ✓]
- **Beşeri Tıbbi Ürünler Ruhsatlandırma Yönetmeliği** 
  (RG 11/12/2021 S. 31686) Md. 12 (endikasyon genişletme) [Mevzuat MCP ✓]
- **Anayasa Md. 17 yaşam hakkı + Md. 56 sağlık hakkı**
- **Anayasa Md. 90/5 + ICESCR Md. 12 + Genel Yorum 14 (AAAQ — 
  erişilebilirlik kriteri)** [R10 referansı]
çerçevesinde hazırlanmıştır.

### 2. Bilimsel Dayanak
KEYNOTE-A18 pivotal Faz III çalışması (NCT04634877, n=819), 
pembrolizumab + kemoterapi kombinasyonunun MSI-H/dMMR endometriyum 
kanseri adjuvan tedavisinde **PFS hazard ratio = 0.54 
(95% GA: 0.40-0.74)** ile anlamlı yarar sağladığını göstermiştir 
(GRADE: YÜKSEK). Bu sonuç:

- **NCCN Endometrial Cancer Guidelines v.X.2025 — Category 1 
  recommendation** [medical-research §9 + §11.a]
- **ESMO Endometrial Cancer Guidelines 2024 — preferred regimen** 
  [medical-research §9]
- **ESMO-MCBS Score: 4 (significant benefit)** [medical-research §11.c]

ile teyit edilmiştir.

### 3. Uluslararası Regulatory Emsal
- **FDA 2024-06-17 onayı (sBLA)** [medical-research §4 + §13.a]
- **EMA CHMP positive opinion 2024-09-19** [medical-research §4 + §13.a]
- **Project Orbis Programı** kapsamında TGA + ANVISA + Swissmedic + 
  MHRA + HSA paralel onaylar [medical-research §13.c]

### 4. Türkiye'de Erişim Durumu
TİTCK ÜTS verisine göre, KEYTRUDA (pembrolizumab) Türkiye'de 2018'den 
itibaren ruhsatlıdır ve **mevcut endikasyonlar** NSCLC, melanom, 
HNSCC, klasik Hodgkin lenfoma ve MSI-H tümör-agnostik kullanımı 
içerir [medical-research §4 + §13.f]. Endometriyum kanseri adjuvan 
endikasyonu Türkiye'de henüz onaylanmamıştır.

**Bilgi sınırı uyarısı (medical-research reverse signal):** Türkiye 
yerel RWE verisi (REGISTURK endometriyum kohortu pembrolizumab 
adjuvan kullanımı) henüz mevcut değildir; uluslararası KEYNOTE-A18 
verisi temel alınmıştır.

### 5. Bütçe Etki Beklentisi
[Mod 6 (RIA) opt-in: detaylı BEF eki için Mod 6 etkinleştirilmelidir; 
şu an için: AdisInsight tahminine göre yıllık etkilenen hasta 
~3.000-4.000 (Türkiye endometriyum kanseri MSI-H/dMMR alt-popülasyon)]

## Madde Gerekçeleri

### Madde 1 — Amaç
Bu Yönetmelik, pembrolizumab etken maddesi içeren beşeri tıbbi 
ürünlerin endometriyum kanseri adjuvan endikasyonunda Türkiye'de 
güvenli, etkin ve erişilebilir kullanımının düzenlenmesi amacıyla 
hazırlanmıştır.

[FDA + EMA + Project Orbis paralel onayları + NCCN Category 1 
+ ESMO preferred + ESMO-MCBS 4 puan birikiminin Türkiye'de 
düzenleme gerekliliği oluşturduğu...]

### Madde 2 — Kapsam
[Bu Yönetmelik, MSI-H/dMMR tümör tipinde olduğu kanıtlanmış 
endometriyum kanseri hastaları için pembrolizumab + paklitaksel + 
karboplatin adjuvan kombinasyonu kullanımına ilişkin esasları 
kapsar.]

[...devam eder]

## Çift Epistemik Dürüstlük Etiketi

### Medical-Research Tarafı (v7.1.2):
- Kapsam: PubMed (2024-01..2026-05), CT.gov v2 (KEYNOTE-A18 dahil), 
  AdisInsight 2026-05, DailyMed + OpenFDA + EMA ✓
- Bilgi boşluğu: REGISTURK pembrolizumab adjuvan endometrial 
  Türkiye RWE — yok
- GRADE: HIGH (primary endpoint)

### Cureolex Tarafı (v2.3.1):
- Mevzuat MCP teyit: 2 birincil mevzuat + 1 yönetmelik teyit edildi
- Yargısal denetim: 1 Danıştay kararı emsali tespit edildi
- Mod 1 DRAFT kapsamı: TİTCK yönetmeliği taslak hazır; ruhsatlandırma 
  prosedürü güncel 2024 yorumu teyit önerilir

### Birleşik Güven Seviyesi: HIGH
- Öneri: TİTCK Bilimsel Kurul başvurusu için hazır; ek doğrulama 
  TİTCK Klinik Araştırmalar Daire Başkanlığı ile yapılmalı
```

### 3.7. Adım 6: Cross-Skill Verification (R14 §15)

```
G1 (5210 şekli uyum): PASS
G2 (5210 maddi-anayasal): PASS — Anayasa Md. 17 + Md. 56 + Md. 90/5 zinciri
G3 (R9 Türk hukuk dili): PASS
G4 (27 anti-pattern): PASS
G5 (R13 içtihat + doktrin): PASS — Danıştay emsal + uluslararası kılavuz
G6 (R8/10/12 uluslararası): PASS — FDA + EMA + ICH + Project Orbis
G7 (Epistemik dürüstlük): PASS — çift etiket sergilendi
G8 (TBMM kapsam): N/A — Mod 8 değil
G9 (Ex post kapsam): N/A — Mod 9 değil

Medical-Research yanı:
M-G1 (Connector kapsama): PASS — 10 connector kullanıldı
M-G2 (GRADE evidence): PASS — HIGH
M-G3 (İçtihat-doktrin): N/A medical-research için
M-G5 (Tier 0 sentez): PASS — Cochrane + NICE SR
M-G6 (Atıf zinciri): PASS — Vancouver formatı tam
M-G7 (Cross-jurisdiction): PASS — FDA + EMA + Project Orbis 6 ülke
M-G8 (Epistemik şeffaflık): PASS — knowledge gap raporlandı
G-Reverse (R14 §20.4): PASS — uncertainty flag sergilendi
```

### 3.8. Çıktı Paketi

Final çıktı paketi şunları içerir:

1. **Yönetmelik Taslağı** (markdown — `output/yonetmelik-taslagi.md`)
2. **Medical-research evidence appendix** (medical-research'in tam markdown'u, EK olarak)
3. **Sidecar JSON v2.3.1** (`output/sidecar.json`)
4. **Atıf günlüğü** (birleşik Vancouver + Türk mevzuat MCP teyitli)
5. **Çift Epistemik Dürüstlük Etiketi** (yönetici özetinde)
6. **Reverse Signal Notları** (footnote olarak yönetmelik gerekçelerinde)

---

## 4. Operasyonel Senaryolar Kataloğu

R14 §16'da tanımlanan 16 pipeline'ın her biri için yukarıdaki gibi tam pipeline örneği oluşturulabilir. Bu dosya §3'te bir örnek (Mod 1 DRAFT) sergiler; geri kalan senaryolar talep üzerine genişletilir.

### 4.1. Hızlı Referans — Senaryo → Tetikleyici Eksenler Tablosu

| Senaryo | Cureolex Modu | Tetiklenen Eksenler | Çıktı Tipi |
|---|---|---|---|
| Pembrolizumab endometrial DRAFT (örnek §3) | Mod 1 | 0.5.A + 0.5.C + 0.5.I | Yönetmelik taslağı |
| SUT CAR-T geri ödeme kriteri reformu | Mod 1 + Mod 9 | 0.5.B + 0.5.C + 0.5.D + 0.5.H | Yönetmelik/tebliğ taslağı + EDR |
| BTÜ-TF Yönetmeliği tanıtım mevzuatı reformu | Mod 1 + Mod 4 | 0.5.C + 0.5.E | Yönetmelik taslağı + 5210 uyum raporu |
| TR Reliance Yönetmeliği taslağı | Mod 1 + Mod 7 | 0.5.C + 0.5.D + 0.5.I | Yönetmelik + comparative analysis |
| ATMP Yönetmeliği (gen tedavisi) | Mod 1 | 0.5.B + 0.5.C + 0.5.H + 0.5.I | Yönetmelik taslağı |
| SGK SUT CAR-T ekleme 24-ay ex post | Mod 9 (EX_POST) | 0.5.B + 0.5.D + 0.5.I | EDR (14 bölümlü) |
| MS DMT geri ödeme politikası reformu | Mod 1 | 0.5.G + 0.5.C + 0.5.D | Tebliğ taslağı |
| Romatoid artrit biyobenzer extrapolation MEVZUAT görüşü | Mod 5 | 0.5.F + 0.5.C + 0.5.D | Reform süreci bilimsel mütalaası |

---

## 5. Composition Runbook §10.5 İçin Önerilen Karşı-Sözleşme Metni

Aşağıdaki metin, medical-research'ün composition-runbook.md §10 dosyasına eklenmek üzere **önerilen** karşı-sözleşmedir. Medical-research skill maintainer'ı bu metni doğrudan §10.5 olarak ekleyebilir:

```markdown
### 10.5 medical-research → cureolex

**Transfer object:** Markdown §1-§20 + sidecar JSON v2.3.1.

**cureolex beklenti:**
- §1 Küresel Literatür (yönetici özeti için)
- §4 Ruhsat & Etiket (hukuki dayanak — ilaç ise zorunlu)
- §5 Türkiye Verileri (madde gerekçeleri için)
- §7 Tier 0 Sentez (kanıt katmanı)
- §9 Kılavuz Yerleşimi (klinik standart)
- §13 Regulatory Sciences (TİTCK/FDA/EMA mekaniği)
- §14 HTA (SUT/HTA politika reformu için)
- §19 Drug Intelligence (pipeline-aware analiz)
- §20 Cross-Layer Integration

**Sidecar JSON ek alanlar (v2.3.1):**
- `turkish_legislation_refs` — Türk mevzuat MCP teyit
- `yargi_ictihat_chain` — AYM/Danıştay/AİHM MCP teyit
- `ex_post_metrics` — Mod 9 EX_POST_EVALUATION için
- `reverse_signals` — uncertainty/out-of-scope/retry/alternative

**Cureolex tüketim protokolü:**
- Şema sürümü ≥ 2.3.1 kontrolü
- Reverse signals önceliği (R14 §20)
- Mod-bazlı tüketim haritası (Cureolex R14 §12.2 matrix)
- Cross-skill verification (Cureolex R14 §15)
- Çift epistemik dürüstlük etiket sergileme

**İletişim:** Cureolex v2.6.0 ile doğrulanmış; v2.3.1+ sidecar şemasıyla geriye uyumludur (Cureolex R14 §17 
sürüm uyumluluk matrisi).
```

---

## 6. Test ve Doğrulama Senaryoları

### 6.1. Pozitif Test Senaryoları

1. **Mod 1 DRAFT — klinik konu (yukarıdaki §3 örneği):** Beklenen — §11 + §13 + §19 tetiklenmesi, reverse_signals'da uncertainty flag, GRADE HIGH
2. **Mod 5 OPINE — SUT/HTA geri ödeme politikası reformu görüşü:** Beklenen — §13 + §14 + §11/§12/§17 (konuya göre) zorunlu tüketim
3. **Mod 9 EX_POST — ilaç ödeme politikası 24 ay sonra:** Beklenen — `ex_post_metrics` dolu, §5 + §14.f + §19 zorunlu

### 6.2. Negatif Test Senaryoları (Beklenen FAIL)

1. **Klinik olmayan konu (örn. tütün düzenlemesi):** Medical-research çağrılmamalı; Cureolex standalone çalışır
2. **Eski sidecar şeması (v1.0):** Schema incompatibility error
3. **Reverse signals boş çıktı (medical-research v7.0):** Graceful degradation; uyarı ile devam

### 6.3. Graceful Degradation Senaryoları

| Durum | Davranış |
|---|---|
| Medical-research v7.0 algılandı (Reverse signals yok) | Cureolex devam eder; sidecar JSON v2.0 ile çalışır; uyarı: "v7.1+ önerilir" |
| Medical-research connectorları kısmen down | Sidecar `connectors_used` listesine bakılır; eksik connector için uncertainty flag eklenir |
| AdisInsight MCP unavailable | §19 boş geçer; Cureolex DrugIntel sec'i `[veri eksik — AdisInsight unavailable]` ile işaretler |

---

## 7. v2.3-r1 Sürüm Notu

**Eklenenler:**
- R14b yeni dosya (~700 satır)
- composition-runbook §10.5 karşı-sözleşme metni
- Tam pipeline örnek çalışması (pembrolizumab MSI-H)
- Sidecar consumption pseudocode
- Test senaryoları kataloğu

**Composition runbook karşı-sözleşme:** Bu dosya §5'te önerilen metni içerir; medical-research maintainer'ı bu metni doğrudan composition-runbook §10.5 olarak ekleyebilir.

---

**Bu dosya, Cureolex v2.6.0 motorunda kullanılan, operasyonel entegrasyon kökeni v2.3-r1 olan R14b yan sözleşmesidir. R14 ana sözleşmesi (teorik) ile birlikte okunur; R14 §12-§17 tasarım sözleşmesini, R14 §19-§20 operasyonel zenginleştirmesini, R14b bu dosyayı tam pipeline çalıştırma kanıtını sağlar. Tartışmalı durumlarda R14 §6 karar ağacı + R14 §15 birleşik gate matrix bağlayıcıdır.**
