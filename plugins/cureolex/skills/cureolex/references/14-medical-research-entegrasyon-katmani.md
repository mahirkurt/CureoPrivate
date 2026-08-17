# Medical-Research Skill ile Bidirectional Entegrasyon Katmanı

Bu dosya, **Cureolex'ın medical-research orkestrasyon skill'i ile yapısal entegrasyon protokolünü** tanımlar. İki skill arasındaki çift yönlü veri akışı, paralel pipeline tasarımları, kanıt katmanı senkronizasyonu ve composability sözleşmeleri burada operasyonel düzeyde belgelenmiştir.

> **Versiyonlar:** Bu protokol, **medical-research v7.1** + **Cureolex v2.6.0** birleşim noktasında doğrulanmıştır. medical-research'ün v7.2'ye yükselmesi durumunda Bölüm 9'daki composability sözleşmesi yeniden teyit edilmelidir.

> **Çekirdek prensip:** Cureolex, **hukuki epistemik otorite**; medical-research, **bilimsel-tıbbi epistemik otoritedir**. İki skill çakışmaz — birbirini tamamlar. Cureolex çıktısının "bilimsel dayanak", "kanıt katmanı", "ICER analizi", "uluslararası karşılaştırma" boyutları **medical-research tarafından beslenir**. Tersine, medical-research'ün regulatory, HTA ve medical-affairs katmanlarının **Türkiye-spesifik yargı ve mevzuat boyutu Cureolex tarafından zenginleştirilir**.

---

## 1. Medical-Research Skill'inin Tanınması ve Tetikleme Sözleşmesi

### 1.1. Medical-Research'ün Cureolex Açısından İşlevi

Medical-research, **Anthropic kullanıcı skill ekosisteminin en kapsamlı tıbbi bilgi orkestrasyon protokolüdür** (v7.1, ~13.500 satır). Aşağıdaki kanıt katmanlarını üretir:

| Çıktı bölümü | İçerik | Cureolex için kullanım alanı |
|---|---|---|
| **§ 1** Küresel literatür | PubMed + Europe PMC | DRAFT madde gerekçesinde primer kanıt |
| **§ 2** Klinik pipeline | ClinicalTrials.gov v2 | TBMM teklifi genel gerekçede güncel pipeline |
| **§ 3** Mekanizma & farmakoloji | ChEMBL + PubChem | KÜB-paralel terim tanımı |
| **§ 4** Ruhsat & etiket | DailyMed + OpenFDA + EMA | DRAFT yönetmelik bilimsel dayanağı |
| **§ 5** Türkiye verileri | TİTCK + SGK + YokTez + AFF:Turkey | ANALYZE mevzuat eleştirisi Türk verisi |
| **§ 6** Çok dilli kapsama | 6 ülke AFF matriksi | COMPARATIVE_LAW karşılaştırmalı temel |
| **§ 7** Tier 0 sentez | Cochrane + Epistemonikos + NICE SR | GRADE-temelli madde gerekçesi |
| **§ 8** KOL haritası | OpenAlex + S2 + EPMC | OPINE/RIA paydaş analizi |
| **§ 9** Kılavuz yerleşimi | NICE + ESMO + NCCN | Yönetmelik/tebliğ "uluslararası kabul gören kılavuz" atfı |
| **§ 10** Açık erişim | Unpaywall + DOAJ | Kanıt erişilebilirliği |
| **§ 11-12** Onko/heme genişletme | Hastalık-spesifik | Sağlık özel mevzuatta klinik temellendirme |
| **§ 13** Regulatory sciences | FDA/EMA/TİTCK/AdComm/CHMP | COMPARATIVE_LAW + ANALYZE asgari katman |
| **§ 14** HTA | NICE/CADTH/PBAC/IQWiG/HAS/ICER + SGK SUT | RIA (BEF/DEA) + OPINE (SUT/HTA geri ödeme politikası reformu görüşü) |
| **§ 15** Medical affairs ops | EFPIA/IFPMA/FCPA/İEİS + GPP3 | COMPLY 21-noktalı denetim çapraz doğrulama |
| **§ 16-17** İmmunoloji/nöroloji | Hastalık peyzajı | Sağlık özel mevzuatta klinik dayanak |
| **§ 18** Rare disease | Orphanet + OMIM + GARD + ODD | TBMM nadir hastalık kanun teklifi gerekçesi |
| **§ 19** Drug intelligence pipeline | AdisInsight + pipeline_payload | Yatay rekabet manzarası → kanun teklifi gerekçesi |
| **§ 20** Cross-layer integration | Katman çapraz referanslar | TBMM_KANUN_TEKLIFI tam entegre temel |

### 1.2. Medical-Research'ün Otomatik Tetiklenme Koşulları

Cureolex çıktısının kalite eşiğini geçmesi için **aşağıdaki durumlarda medical-research otomatik olarak çağrılır:**

| Cureolex Modu | medical-research zorunluluk seviyesi | Tetikleyici sinyaller |
|---|---|---|
| **DRAFT** | Zorunlu (yeni yönetmelik/tebliğ taslağında bilimsel dayanak hattı için) | Klinik konu (onkoloji, hematoloji, nadir hast.), ilaç adı, hastalık adı, terapi sınıfı |
| **AMEND** | Şartlı zorunlu (mevcut mevzuatın bilimsel zemini değişiyorsa) | Yeni kanıt çıkışı, etiket değişikliği, AdComm güncellemesi referansı |
| **ANALYZE** | Zorunlu (Türkiye TİTCK pozisyonu için § 13.f) | TİTCK iptal/değişiklik analizi, ruhsat süreci eleştirisi |
| **COMPLY** | Şartlı (yeni tanıtım/klinik mevzuat reform metninin 5210 + bilimsel gerekçe denetimi için § 15.e) | Tanıtım mevzuatı reform uyumu, etik çerçeve mevzuatı |
| **OPINE** | Zorunlu (SUT/HTA geri ödeme politikası reformunda § 14.f) | SUT atfı, geri ödeme kriteri reformu, ICER karşılaştırması |
| **RIA** | Zorunlu (BEF için § 14.d, DEA için § 14.c) | Bütçe etki analizi, ICER/QALY hesabı, ödeme modeli |
| **COMPARATIVE_LAW** | Zorunlu (regulatory mechanics karşılaştırması için § 13.a-c) | FDA-EMA-TİTCK karşılaştırma, AB müktesebatı |
| **TBMM_KANUN_TEKLIFI** | Çift zorunlu (genel gerekçenin 4-6. alt başlıkları için tam medical-research raporu) | Her TBMM teklifi |
| **EX_POST_EVALUATION** | Zorunlu (klinik/HTA/ilaç/tıbbi cihaz/geri ödeme ex post analizinde § 5 + § 14.f + § 19) | Uygulama sonrası veri, RWE, SGK/MEDULA/SUT etkisi, openFDA/PBS/WHO GHO trendi, HTA outcome, geri ödeme sonuçları |

### 1.3. Tetikleme Sözleşmesinin Operasyonel Uygulaması

Cureolex, modunu seçtikten sonra **aşağıdaki kararla** medical-research'ü çağırır:

```
EĞER mod ∈ {DRAFT, ANALYZE, OPINE, RIA, COMPARATIVE_LAW,
            TBMM_KANUN_TEKLIFI, EX_POST_EVALUATION}:
    medical-research'ü tam yapılandırılmış sorguyla çağır
    .data.json sidecar çıktısını talep et
    en az 4-6 bölümü (§ 5, 7, 9, 13, 14, ilgili specialty) tüket
    (Mod 9 ise § 5 + § 14.f + § 19 zorunlu; sidecar `ex_post_metrics` dolu olmalı)
ELİF mod ∈ {AMEND, COMPLY}:
    Bağlam medical-research gerektiriyor mu? Eğer evet, çağır.
    Aksi takdirde Mevzuat MCP + Hukuki Veritabanları MCP yeterli.
```

---

## 2. Çift Yönlü Veri Akışı

### 2.1. medical-research → cureolex (Downstream Tüketim)

Medical-research, **kanıt katmanını yapılandırılmış formda** Cureolex'a iletir. İki transfer mekanizması vardır:

**(a) Markdown bölüm transferi:** Medical-research çıktısının § 5, 7, 9, 13, 14, 18, 19 bölümleri Cureolex tarafından **doğrudan citation-aware** olarak alıntılanır. Atıf formatı:

```
[medical-research v7.1, § 13.f, TİTCK ruhsat durumu, sorgu tarihi: gg/aa/yyyy]
[medical-research v7.1, § 14.a, NICE TA 712 ICER £42.300/QALY, 2024]
```

**(b) `.data.json` sidecar transferi:** Medical-research çıktısı eş zamanlı bir `.data.json` sidecar üretir. Bu yapısal veri Cureolex tarafından **doğrudan tüketilir**. Sidecar şeması:

```json
{
  "metadata": {
    "version": "medical-research v7.1",
    "query": "...",
    "timestamp": "...",
    "active_layers": ["regulatory", "hta", "rare_disease"]
  },
  "evidence_table": [...],
  "trial_table": [...],
  "guideline_table": [...],
  "regulatory_timeline": [...],
  "hta_summary": [...],
  "specialty_payload": {...},
  "pipeline_payload": {
    "drug_profile": {...},
    "competitor_landscape": [...],
    "regulatory_milestones": [...],
    "deals": [...],
    "conference_coverage": [...],
    "data_gaps": [...]
  }
}
```

Cureolex, sidecar tüketim sırasında **her bölümü ilgili moduna eşler:**

| Sidecar bölümü | Cureolex modu/bölümü | Kullanım |
|---|---|---|
| `evidence_table` | DRAFT madde gerekçesi | Primer kanıt + GRADE |
| `trial_table` | DRAFT + AMEND + TBMM teklifi | Güncel pipeline durumu |
| `guideline_table` | DRAFT + COMPARATIVE_LAW | Uluslararası kılavuz atfı |
| `regulatory_timeline` | COMPARATIVE_LAW + ANALYZE | FDA-EMA-TİTCK senkronizasyon |
| `hta_summary` | RIA (BEF/DEA) + OPINE | ICER/QALY/budget impact |
| `specialty_payload` | Sağlık özel mevzuat | Hastalık-spesifik derinlik |
| `pipeline_payload` | TBMM teklifi + COMPARATIVE_LAW | Yatay rekabet manzarası |

### 2.2. cureolex → medical-research (Upstream Sinyal)

Cureolex, medical-research'e **Türkiye-spesifik mevzuat ve içtihat sinyallerini** iletir. Bu sinyaller medical-research'ün **Türkiye Dörtlüsünü** (TİTCK + SGK + YokTez + AFF:Turkey) zenginleştirir.

**Transfer mekanizması:** Cureolex, medical-research'ü çağırırken **enriched query** üretir:

```
ORIJINAL KULLANICI SORGUSU:
"1219 sayılı Kanun reformatlama"

LEX-SANITAS ZENGİNLEŞTİRMESİ:
{
  "original_query": "1219 sayılı Kanun reformatlama",
  "mode": "TBMM_KANUN_TEKLIFI",
  "cureolex_context": {
    "primary_legislation": ["1219 SK", "1262 SK", "6197 SK"],
    "constitutional_basis": ["Md. 17", "Md. 56", "Md. 90/5"],
    "international_treaties": ["ICESCR Md. 12", "AİHS Md. 2", "Oviedo Sözleşmesi"],
    "yargi_ictihat_focus": ["AYM sağlık hakkı + belirlilik içtihadı (reform gerekçesi)", "Danıştay düzenleme iptal içtihadı"],
    "comparative_law_targets": ["Almanya BÄO", "İngiltere Medical Act 1983", "Fransa CSP"]
  },
  "requested_layers": ["regulatory", "medaffairs", "rare_disease"]
}
```

Medical-research, bu zenginleştirilmiş sorguyu işlerken:
- § 13.f (TİTCK pozisyonu) **derinleştirilir** — Cureolex Mevzuat MCP'den gelen primer kaynak metnine atıfla
- § 9 (Kılavuz yerleşimi) **Türk yorumla** zenginleştirilir
- § 5 (Türkiye verileri) **mevzuat MCP atıfları** ile çapraz doğrulanır
- § 15.e (Compliance stack) **Türk düzenleyici çerçeve** ile uyumlu hâle gelir

### 2.3. Çift Yönlü Veri Akışı — Görselleştirilmiş Akış

```
┌─────────────────────────────────────────────────────────────────┐
│  KULLANICI SORGUSU                                               │
│  "1219 SK reformatlama — telesağlık dahil"                      │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │   LEX-SANITAS v2.2      │
        │   Mod tespiti:          │
        │   TBMM_KANUN_TEKLIFI    │
        └────────┬────────────────┘
                 │
                 │  (1) Mevzuat MCP → primer kaynak
                 │  (2) Yargı içtihat hattı tespiti
                 │  (3) Anayasa Md. 90/5 atıf zinciri
                 │
                 ▼
        ┌─────────────────────────┐
        │   Enriched Query        │
        │   (cureolex_context) │
        └────────┬────────────────┘
                 │
                 │ İletim →
                 ▼
        ┌─────────────────────────┐
        │   MEDICAL-RESEARCH v7.1 │
        │   Adım 0.5 sinyal:      │
        │   C + E + G + I aktif   │
        └────────┬────────────────┘
                 │
                 │  Çıktı:
                 │  - 20 bölüm rapor
                 │  - .data.json sidecar
                 │
                 ▼
        ┌─────────────────────────┐
        │   LEX-SANITAS v2.2      │
        │   (Tüketim aşaması)     │
        │                         │
        │   § 5 → ANALYZE         │
        │   § 7 → DRAFT gerekçe   │
        │   § 9 → DRAFT kılavuz   │
        │   § 13 → COMPARATIVE_LAW│
        │   § 14 → RIA + OPINE    │
        │   § 18 → TBMM teklifi   │
        │   § 19 → TBMM teklifi   │
        └────────┬────────────────┘
                 │
                 ▼
        ┌─────────────────────────────────────┐
        │  ÇIKTI: TBMM Kanun Teklifi          │
        │  (templates/tbmm-kanun-teklifi.md)  │
        │  + Tam medical-research kanıt zinciri│
        │  + Türk mevzuat + içtihat zemini     │
        │  + Anayasa Md. 90/5 uluslararası kat │
        └─────────────────────────────────────┘
```

---

## 3. Pipeline Senaryoları — Sekiz Co-Execution Mimarisi

Aşağıda Cureolex + medical-research birleşik pipeline'ları detaylanmaktadır. Her pipeline, gerçek bir Türk sağlık politika ihtiyacına denk gelir.

### 3.1. Pipeline P-1: TBMM Sağlık Reform Kanun Teklifi

**Senaryo:** Mahir Bey'in 1219 sayılı Tababet ve Şuabatı San'atlarının Tarzı İcrasına Dair Kanun (1928) reformatlama projesi gibi büyük sağlık reform kanun teklifleri.

**Pipeline:**

1. **cureolex** (Mod 8 — TBMM_KANUN_TEKLIFI başlatma)
   - Mevzuat MCP → 1219 SK + uyumlu mevzuat metni
   - Yargı içtihat MCP → AYM sağlık hakkı/belirlilik içtihadı (reform gerekçesi) + Danıştay düzenleme içtihadı
   - Enriched query üret
2. **medical-research** (paralel çağrı)
   - Adım 0.5.C (regulatory) + 0.5.E (medical affairs) + ilgili specialty
   - § 9 (Kılavuz: NICE/ESMO/NCCN), § 13 (FDA/EMA/TİTCK), § 14 (HTA), § 18 (rare disease — varsa)
   - `.data.json` sidecar üret
3. **cureolex** (tüketim + Mod 8 protokolü)
   - Medical-research sidecar → Genel Gerekçe Bölüm 4-6 (uluslararası hukukî çerçeve + AB müktesebatı + karşılaştırmalı mevzuat)
   - R9 dil katmanı + R13 içtihat-doktrin katmanı eklensin
   - TMK 4721 gerekçesi tabloları (R9 Bölüm 6.bis-6.sexies) terim modernizasyonu
4. **pharmapatent** (paralel)
   - SMK uyumu (varsa)
5. **carbon-html-report** veya **roche-design**
   - Final TBMM Kanun Teklifi paketi

**Çıktılar:**
- Tam TBMM Kanun Teklifi (`templates/tbmm-kanun-teklifi.md` formatında)
- Medical-research evidence appendix
- Sidecar `.data.json`
- Carbon HTML report (gerekiyorsa)

### 3.2. Pipeline P-2: TİTCK Düzenleyici İşlem İptal Riski / Reform Savunulabilirliği Analizi

**Senaryo:** TİTCK düzenlemesinin Danıştay iptal riski ve reform gerekçesi açısından değerlendirilmesi (mevzuat tutarlılığı + 5210 uyum + bilimsel dayanak analizi).

> ⚠️ **Kapsam dışı:** Dava savunma dilekçesi, Bakanlık avukatlığı defans paketi, bilirkişi sunum deck'i ve somut dava stratejisi cureolex kapsamı DIŞINDADIR (→ saglik-sigorta/ilgili hukuk birimi). Burada yalnızca düzenlemenin **reform/iptal-riski analizi** yapılır.

**Pipeline:**

1. **cureolex** (Mod 3 — ANALYZE)
   - Hedef yönetmelik metni okuma
   - 21-noktalı 5210 uyum denetimi (Mod 4'e geçiş)
   - Anayasa Mahkemesi belirlilik içtihatı taraması (R13)
2. **medical-research** (paralel)
   - Adım 0.5.C tetiklenir (regulatory)
   - § 13.a-c → FDA + EMA paralel başvuru/onay senkron
   - § 13.f → TİTCK pozisyonu — yönetmeliğin bilimsel dayanağı
   - § 15.e → Compliance stack (EFPIA + IFPMA + FCPA + İEİS) çapraz doğrulama
3. **cureolex** (Mod 3/6 — ANALYZE/RIA, iptal riski + reform gerekçe notu)
   - Medical-research § 13 + § 9 → bilimsel dayanak gerekçesi
   - Danıştay 13. D içtihat hattı (R13 Bölüm 1.4)
   - Anayasa Md. 90/5 uluslararası uyum
4. **carbon-html-report**
   - İptal riski / reform gerekçe analiz raporu

**Çıktılar:**
- İptal riski / reform savunulabilirliği analiz notu
- 5210 + anayasal belirlilik uyum değerlendirmesi
- Çapraz doğrulanmış uluslararası emsal tablosu (reform gerekçesi)

### 3.3. ~~Pipeline P-3: SGK Ödeme Reddi Bireysel Başvuru~~ — DEPRECATED / KAPSAM DIŞI (v2.5.2)

> ⛔ **KAPSAM DIŞI — v2.5.2'de DEPRECATED.** Bu pipeline bireysel SGK ödeme reddi → AYM bireysel başvuru üretimini tanımlıyordu; bu, v2.4 saflaştırma kararı uyarınca cureolex kapsamı DIŞINDADIR ve `saglik-sigorta` / `onko-erisim` skill'lerine aittir. Aşağıdaki adımlar yalnızca **tarihsel kayıt** olarak bırakılmıştır; cureolex tarafından **çalıştırılmaz**. cureolex yalnızca SUT/HTA **geri ödeme politikası reformu** (Mod 1/6/9) bağlamında devreye girer; bireysel başvuru formu veya savunma ÜRETMEZ.
>
> **In-scope reform karşılığı (P-3'ün yerini alan):** "SUT geri ödeme kriterini kanıt temelli reforme eden tebliğ taslağı + Bütçe Etki Formu" → Mod 1 (DRAFT) + Mod 6 (RIA) + medical-research §7/§9/§14 (HTA delili reform gerekçesi olarak).

*Tarihsel pipeline gövdesi (DEPRECATED — bireysel AYM başvuru akışı) `CHANGELOG-v2.5.4.md` "Arşivlenen Deprecated Pipeline Gövdeleri" bölümüne taşınmıştır; bu referans dosyasında çalıştırılabilir adım bırakılmamıştır.*

### 3.4. Pipeline P-4: Sağlık Yönetmeliği DRAFT — TİTCK için

**Senaryo:** TİTCK'nın yeni bir yönetmelik (örn. ileri tedavi tıbbi ürünleri ATMP, gen tedavisi, telesağlık) hazırlaması.

**Pipeline:**

1. **cureolex** (Mod 1 — DRAFT)
   - 5210 sayılı Yönetmelik prensiplerine uygun iskelet
   - R9 dil katmanı + 15-noktalı kontrol listesi
2. **medical-research** (zorunlu)
   - Adım 0.5.C + ilgili specialty (örn. nadir hastalık ise 0.5.H)
   - § 4 (Ruhsat & etiket) → DailyMed + OpenFDA + EMA paralel
   - § 9 (Kılavuz) → ICH + IMDRF + PIC/S
   - § 13.a-c (FDA/EMA özel onay yolları) → Project Orbis, PRIME, ODD
   - § 13.f (TİTCK pozisyonu)
3. **cureolex** (madde gerekçesi yazımı)
   - Her madde için medical-research'ten bilimsel temellendirme
   - 5210 Md. 23 paralel — gerekçe madde metninin tekrarı değil
4. **carbon-html-report**
   - Yönetmelik tam metin + gerekçe

**Çıktılar:**
- Yönetmelik taslak metni
- Madde gerekçeleri (medical-research kanıt zinciri ile temellendirilmiş)
- 21-noktalı 5210 uyum denetim raporu

### 3.5. Pipeline P-5: Bütçe Etki Formu (BEF) + Düzenleyici Etki Analizi (DEA)

**Senaryo:** Cumhurbaşkanı kararı veya CBK ile sağlık alanında yeni mali yük doğuran düzenleme — SBB koordinasyonunda DEA + BEF zorunluluğu.

**Pipeline:**

1. **cureolex** (Mod 6 — RIA başlatma)
   - 5210 Md. 26 + 27 çerçevesi
   - `templates/dea-template.md` + `templates/bef-template.md`
2. **medical-research** (zorunlu)
   - Adım 0.5.D (HTA) tetiklenir
   - § 14.c → ICER + NMB + CEAC (PSA sonuçları)
   - § 14.d → Budget Impact Analizi (hasta havuzu, uptake eğrisi)
   - § 14.e → Managed Entry / Outcome-Based Agreement örnekleri
   - § 14.f → SGK SUT entegrasyonu
3. **cureolex** (DEA + BEF tamamlama)
   - Karşılaştırmalı uluslararası ICER tablosu medical-research § 14.a'dan
   - SGK bütçe etkisi medical-research § 14.f'den
4. **roche-design** veya **carbon-pptx**
   - SBB koordinasyon toplantısı sunumu

**Çıktılar:**
- DEA tam dokümanı
- BEF tam dokümanı
- Uluslararası ICER karşılaştırma tablosu
- SBB sunum deck'i

### 3.6. Pipeline P-6: Comparative Health Law Analysis

**Senaryo:** Sağlık Bakanlığı politika dairesi için karşılaştırmalı uluslararası mevzuat analizi (örn. "Almanya'da telesağlık nasıl düzenleniyor?").

**Pipeline:**

1. **cureolex** (Mod 7 — COMPARATIVE_LAW)
   - R8 + R12 katmanları (gelişmiş ülke rejimleri)
2. **medical-research** (zorunlu)
   - Adım 0.5.C (regulatory) tetiklenir
   - § 13.a-c → FDA + EMA + üye devlet karşılaştırması
   - § 6 → Çok dilli AFF matriksi (Almanya AFF özelinde)
3. **cureolex** (sentez)
   - Eşdüzey vs. tarihsel paralel ayrımı
   - Türk hukuk dilinde sunum (R9 Bölüm 8 — Latin terim minimumu)
4. **carbon-html-report**

**Çıktılar:**
- Karşılaştırmalı tablo (5+ ülke)
- Medical-research uluslararası kanıt eki

### 3.7. ~~Pipeline P-7: TİTCK ADACLIN-Tipi Çoklu Red Savunma Paketi~~ — DEPRECATED / KAPSAM DIŞI (v2.5.3)

> ⛔ **KAPSAM DIŞI — v2.5.3'te DEPRECATED.** Bu pipeline ürün-spesifik/bireysel TİTCK red savunma paketi (Bilimsel Kurul sözlü savunması) üretimine yönelikti; bu cureolex kapsamı DIŞINDADIR (→ onko-erisim/ilgili başvuru sahibi). Aşağıdaki adımlar yalnızca **tarihsel kayıt**; cureolex tarafından **çalıştırılmaz**.
>
> **In-scope reform karşılığı:** TİTCK başvuru/red süreçlerinin **usul standardı veya mevzuat reformu** analizi → Mod 1 (DRAFT) / Mod 3 (ANALYZE) / Mod 6 (RIA).

*Tarihsel pipeline gövdesi (DEPRECATED — ürün-spesifik ADACLIN-tipi savunma paketi) `CHANGELOG-v2.5.4.md` "Arşivlenen Deprecated Pipeline Gövdeleri" bölümüne taşınmıştır; bu referans dosyasında çalıştırılabilir adım bırakılmamıştır.*

### 3.8. Pipeline P-8: Türkiye Sağlık Mevzuat Reform Yol Haritası

**Senaryo:** 48 aylık Türkiye Sağlık Mevzuatı Reformu Yol Haritası (mevcut projeniz) gibi büyük-ölçekli reform planlaması.

**Pipeline:**

1. **cureolex** (Mod 3 — ANALYZE, mevcut 16 temel kanun + CBK + ikincil mevzuat envanteri)
2. **medical-research** (paralel)
   - Tüm 9 specialty layer eş zamanlı tetiklenir
   - § 1-20 tam rapor
3. **cureolex** (Mod 8 — TBMM_KANUN_TEKLIFI, 48 ay timeline)
   - Reform önceliklendirme
   - Her teklif için R9 + R13 katmanı
4. **roche-design** veya **carbon-pptx**
   - Üst düzey strateji dokümanı + executive briefing
5. **carbon-html-report**
   - 145+ sayfalık akademik politika dokümanı

**Çıktılar:**
- 48 aylık reform yol haritası
- Her reform paketi için TBMM kanun teklifi taslağı
- Karşılaştırmalı uluslararası temel doküman
- Carbon HTML executive policy paper

---

## 4. Cureolex Modlarında Medical-Research Handoff Protokolleri

### 4.1. Mod 1 (DRAFT) — Medical-Research Handoff

**Çağrı koşulu:** Yeni yönetmelik/tebliğ taslağı klinik konuda ise.

**Beklenen medical-research bölümleri:**
- § 7 (Tier 0 sentez) — Cochrane SR + NICE SR
- § 9 (Kılavuz yerleşimi) — NICE + ESMO + NCCN + ilgili specialty
- § 4 (Ruhsat & etiket) — TİTCK uyumlu KÜB temeli
- İlgili specialty (§ 11-18)

**Cureolex tüketim noktaları:**
- **Madde gerekçesi yazımı:** "Bilimsel dayanak" alt başlığı medical-research § 7 + § 9'a atıfla
- **Tanımlar maddesi:** medical-research § 3 (mekanizma & farmakoloji) terim temelinden
- **Anti-pattern kontrolü:** Medical-research § 4'tan KÜB-paralel terim kontrolü

**Çıktıya entegre format:**

```markdown
MADDE 5- (1) [...]

MADDE GEREKÇESİ — MADDE 5

Düzenlemenin bilimsel dayanağı:

Cochrane Sistematik Derlemesi [CD012345, 2024, son güncelleme: 03/2024] ve 
NICE TA 712 (2023) sonuçlarına göre... [medical-research § 7]

NCCN Onkoloji Kılavuzu v.4.2024, ESMO Klinik Pratik Kılavuzu 2024 ve 
ASCO Guideline 2024.05 ortak biçimde... [medical-research § 9]

FDA tarafından 04/2024'te ve EMA tarafından 07/2024'te onaylanan etiket 
bilgileri... [medical-research § 4]
```

### 4.2. Mod 2 (AMEND) — Medical-Research Handoff

**Çağrı koşulu:** Mevzuatın bilimsel zemini değişiyorsa (yeni RCT sonucu, etiket güncellemesi, AdComm güncel).

**Beklenen medical-research bölümleri:**
- § 13.e (Historical parallel) — withdrawal + AA failure
- § 4 (Ruhsat & etiket) — güncel KÜB durumu
- § 19 (Drug intelligence pipeline) — son 24 ay pipeline değişimi

**Cureolex tüketim noktaları:**
- **Değişiklik gerekçesi:** "Mevzuatın bilimsel dayanağı niçin güncellenmelidir" sorusu medical-research kanıt zinciriyle yanıtlanır

### 4.3. Mod 3 (ANALYZE) — Medical-Research Handoff

**Çağrı koşulu:** Mevcut Türk mevzuatın bilimsel yeterliliği eleştirisi yapılıyorsa.

**Beklenen medical-research bölümleri:**
- § 5 (Türkiye verileri) — TİTCK + SGK + YokTez + AFF:Turkey
- § 13.f (TİTCK pozisyonu)
- § 6 (Çok dilli kapsama — AB üye devletleri ile karşılaştırma)

**Cureolex tüketim noktaları:**
- **5210 Md. 4/e (kapsam netliği) eleştirisi:** medical-research § 5'ten Türkiye-spesifik veri boşluğu
- **Üst hukuk normuna aykırılık değerlendirmesi:** medical-research § 13.f'ten uluslararası emsal

### 4.4. Mod 4 (COMPLY) — Medical-Research Handoff

**Çağrı koşulu:** Denetlenen metin bir promosyonel materyal DEĞİL, sağlık/tanıtım/klinik araştırma/geri ödeme mevzuatı reform taslağı ise ve taslak klinik veya compliance gerekçesi içeriyorsa.

**Kapsam dışı:** Detail aid, leave-behind, e-detailing, MLR onayı, speaker bureau, CME governance ve materyal PASS/FAIL denetimi → `promo-censor`.

**Beklenen medical-research bölümleri:**
- § 15.e (Compliance stack — EFPIA + IFPMA + FCPA + İEİS)
- § 15.a (MSL engagement framework)
- § 15.f (Speaker Bureau + CME governance)

**Cureolex tüketim noktaları:**
- **21-noktalı 5210 uyum denetimine çapraz katman:** Medical-research § 15 ile 5210 denetimi çapraz doğrulanır
- **Önemli ek:** `promo-censor` skill ile birleşim noktası — medical-research → promo-censor → cureolex

### 4.5. Mod 5 (OPINE) — Medical-Research Handoff

**Çağrı koşulu:** Reform sürecinde klinik/HTA içerikli kurum/paydaş görüşü, TBMM komisyonu bilimsel mütalaası, yönetmelik değişikliği görüşü veya SUT/HTA politika reformu değerlendirmesi gerekiyorsa.

**Kapsam dışı:** Bireysel SGK ödeme reddi, bireysel tedavi reddi, AYM bireysel başvuru formu, kompasyonel kullanım talebi → saglik-sigorta/onko-erisim.

**Beklenen medical-research bölümleri:**
- § 14.a (HTA ajans-ajans matriksi) — NICE/CADTH/PBAC/IQWiG/HAS/ICER
- § 14.f (SGK SUT)
- § 7 (Tier 0 sentez)
- İlgili specialty

**Cureolex tüketim noktaları:**
- **Mütalaa "bilimsel ve uluslararası emsal" bölümü:** medical-research § 14.a tam aktarımı
- **SUT/HTA geri ödeme politikası reformu görüşü:** medical-research § 7 + § 14.f → reform gerekçesi + uluslararası HTA emsali (R12/R13)

### 4.6. Mod 6 (RIA) — Medical-Research Handoff

**Çağrı koşulu:** Cumhurbaşkanı kararı / CBK ile düzenleme yapılıyor.

**Beklenen medical-research bölümleri:**
- § 14.c (ICER + NMB + CEAC)
- § 14.d (Budget Impact Analysis)
- § 14.e (Managed Entry / Outcome-Based Agreement)
- § 14.f (SGK SUT)

**Cureolex tüketim noktaları:**
- **DEA "uluslararası karşılaştırmalı maliyet etkinliği" bölümü:** medical-research § 14.a + § 14.c
- **BEF "hasta havuzu + uptake eğrisi"**: medical-research § 14.d

### 4.7. Mod 7 (COMPARATIVE_LAW) — Medical-Research Handoff

**Çağrı koşulu:** Tüm comparative law modunda **zorunlu**.

**Beklenen medical-research bölümleri:**
- § 13.a-c (FDA + EMA + özel onay yolları)
- § 13.f (TİTCK pozisyonu)
- § 6 (6 ülke AFF matriksi)
- § 14.a (HTA ajans-ajans)
- İlgili specialty

**Cureolex tüketim noktaları:**
- **R12 katmanına ek karşılaştırmalı veri:** medical-research'ten Asya-Pasifik, Latin Amerika tabakaları
- **Eşdüzey vs. tarihsel paralel ayrımı:** medical-research § 13.e (historical parallel)

### 4.8. Mod 8 (TBMM_KANUN_TEKLIFI) — Medical-Research Handoff

**Çağrı koşulu:** Tüm TBMM kanun teklifi modunda **çift zorunlu**.

**Beklenen medical-research bölümleri:** **TÜM § 1-20 tam rapor**.

**Cureolex tüketim noktaları:**
- **Genel Gerekçe Bölüm 3 (uluslararası hukukî çerçeve):** medical-research § 9 + § 13.a-c + § 14.a
- **Genel Gerekçe Bölüm 4 (AB müktesebatı uyumu):** medical-research § 13.b (EMA mechanics)
- **Genel Gerekçe Bölüm 5 (karşılaştırmalı mevzuat):** medical-research § 6 + § 13 + § 14
- **Genel Gerekçe Bölüm 7 (Türk akademik doktrin):** medical-research § 5 (YokTez)
- **Genel Gerekçe Bölüm 8 (beklenen etkiler):** medical-research § 14.d (BIA) + § 18.b (epidemiyoloji)
- **Genel Gerekçe Bölüm 9 (mali etki):** medical-research § 14.d (BIA) + § 14.f (SGK)
- **Madde Gerekçeleri:** Her madde için ilgili medical-research bölümünden atıf

### 4.9. Mod 9 (EX_POST_EVALUATION) — Medical-Research Handoff

**Çağrı koşulu:** Yürürlükteki sağlık/farmasötik mevzuatın klinik, HTA, geri ödeme, güvenlilik, gerçek dünya verisi veya uygulama sonrası etki değerlendirmesi yapılıyorsa **zorunlu**.

**Beklenen medical-research bölümleri:**
- **§ 5** Türkiye verileri / RWE (uygulama sonrası yerel kohort, tez, dergi)
- **§ 14.f** SGK SUT / ödeme politikası entegrasyonu (uygulama dönemi bütçe-etki ve geri ödeme sonuçları)
- **§ 19** Drug intelligence / label update / withdrawal / pipeline trend (rakip terapiler, LoE, güvenlilik sinyali)
- **§ 20** Cross-layer integration (çoklu eksen kesişim notları)
- İlgili specialty layer (onko/heme/immuno/neuro/rare — konuya göre)

**Cureolex tüketim noktaları (Etki Değerlendirme Raporu — EDR):**
- **Hedeflere ulaşma / etkililik:** medical-research § 5 (Türkiye RWE) + ilgili specialty outcome
- **Maliyet-etkililik gerçekleşmesi:** medical-research § 14.f (SGK SUT uygulama verisi) + § 14.d (BIA realize)
- **Beklenmeyen etkiler / güvenlilik:** medical-research § 19 (withdrawal/label/FAERS) + § 13.d (post-marketing)
- **Revizyon önerisi:** Mod 6 (RIA — ex ante) çıktısıyla çift-zamanlı karşılaştırma

**Sidecar zorunluluğu:** `ex_post_metrics` alanı dolu olmalıdır; eksikse cross-skill gate **G9 CONDITIONAL/FAIL** döner (bkz. §15.1 G9 satırı + §6.3 Mod 9 notu).

**Kapsam dışı:** Bireysel SGK ödeme reddi sonrası tazminat/dava değerlendirmesi, hasta özelinde erişim dosyası → `saglik-sigorta`/`onko-erisim`. Mod 9 yalnızca **politika/mevzuat düzeyinde** ex post değerlendirme üretir.

---

## 5. Veri Kalite Sözleşmesi — Cureolex + Medical-Research

### 5.1. Kanıt Hiyerarşisi Senkronizasyonu

Cureolex, medical-research'ün **GRADE / Tier 0-6 hiyerarşisini** kabul eder ve hukukî üretiminde aynı çerçeveyi referans alır.

**Operasyonel kural:** Cureolex DRAFT/OPINE çıktısında **GRADE kanıt seviyesi** belirtilir:

```
"Tıbbi müdahalenin etkililiği konusunda Tier 0 (Cochrane SR + NICE SR) 
düzeyinde HIGH GRADE kanıt bulunmaktadır. Bu kanıt, düzenlemenin 
'üst hukuk normuna aykırılığı' eleştirisinde de mahkemece dikkate 
alınması gerekli niteliktedir."
```

### 5.2. Atıf Standardı Senkronizasyonu

**Medical-research atıf formatı (Vancouver paralel):**
```
[Smith J, et al. Lancet 2024;403(10421):145-152. doi:10.1016/...]
```

**Cureolex atıf formatı (Türk mevzuat):**
```
1219 sayılı Kanunun 5 inci maddesinin birinci fıkrası
```

**Birleşik çıktıda kullanım:** Medical-research kaynakları Vancouver formatında; Türk mevzuat kaynakları R9 Bölüm 7 + R13 hiyerarşisi uyarınca Cureolex formatında. **İki format karıştırılmaz; kompleks atıflar Cureolex öncülü, medical-research zenginleştirici olur.**

### 5.3. Epistemik Dürüstlük Sözleşmesi

İki skill de **epistemik dürüstlük ilkesini** paylaşır:

- **Medical-research:** "Bu klinik öneri RCT-temellidir ancak Türk popülasyonunda doğrulanmamıştır."
- **Cureolex:** "Bu medical-research kanıt zincirine atıfla mevzuat yorumu yapılmıştır; hukuki bağlayıcılık için TBMM Başkanlığı + Bakanlık Hukuk Müşavirliği teyidi gerekir."

Birleşik çıktıda **çift epistemik etiket** kullanılır.

### 5.4. Bilgi Sınırı Sözleşmesi

| Bilgi türü | Yetkili skill | Diğer skill notu |
|---|---|---|
| Klinik etkililik (RCT, SR) | medical-research | "cureolex, klinik kararı vermez" |
| Türk mevzuat metni | Cureolex (Mevzuat MCP) | "medical-research, Türk mevzuat metnini referans alır ama yorumlamaz" |
| Türk yargı içtihatı | Cureolex (Hukuki Veritabanları MCP + R13) | "medical-research yargı içtihatı için cureolex'a yönlendirir" |
| FDA/EMA/TİTCK kararları | medical-research § 13 + Cureolex (Mevzuat MCP) | Ortak yetki — çapraz doğrulama |
| HTA kararları (NICE/ICER) | medical-research § 14 | "cureolex, RIA mod'unda medical-research § 14'e başvurur" |
| Akademik doktrin | medical-research § 5 (YokTez) + Cureolex R13 | Ortak yetki — Türk doktrin Cureolex, uluslararası doktrin medical-research |

---

## 6. Operasyonel Uygulama — Adım Adım Cureolex İş Akışı

### 6.1. Otomatik Tetikleme Karar Ağacı

Cureolex çağrıldığında, **aşağıdaki karar ağacı** medical-research entegrasyonunu otomatik yönetir:

```
1. Mod belirleme (Bölüm 6 — SKILL.md)
2. Konu klinik mi? (anahtar kelime: ilaç, hastalık, terapi, klinik araştırma, vd.)
   ├── EVET → 3'e geç
   └── HAYIR → 4'e geç (medical-research çağrılmaz)
3. Aktif mod ne?
   ├── {DRAFT, ANALYZE, OPINE, RIA, COMPARATIVE_LAW,
   │    TBMM_KANUN_TEKLIFI, EX_POST_EVALUATION}
   │   └── medical-research zorunlu çağrılır
   │   └── Cureolex_context enriched query üretilir
   │   └── Beklenen § bölümleri belirtilir
   │   └── EX_POST_EVALUATION ise §5 + §14.f + §19 + `ex_post_metrics` zorunlu
   ├── AMEND
   │   └── Şartlı çağrılır — bilimsel zemin değişiyor mu?
   └── COMPLY
       └── Şartlı çağrılır — compliance stack gerekli mi?
4. Enriched query medical-research'e iletilir (bash_tool ile veya 
   açık olarak prompt aktarımı yoluyla)
5. Medical-research çıktısı + sidecar tüketilir
6. Cureolex çıktısı, medical-research kanıt zinciri ile zenginleştirilmiş 
   şekilde üretilir
7. Birleşik epistemik dürüstlük etiketleri yerleştirilir
```

### 6.2. Enriched Query Yapısı

Cureolex'ın medical-research'e ilettiği zenginleştirilmiş sorgu yapısı:

```yaml
medical_research_call:
  original_user_query: "{{kullanıcı sorgusu}}"
  invoking_skill: "cureolex"
  invoking_skill_version: "v2.6.0"
  invoking_mode: "{{DRAFT|AMEND|ANALYZE|COMPLY|OPINE|RIA|COMPARATIVE_LAW|TBMM_KANUN_TEKLIFI|EX_POST_EVALUATION}}"
  
  cureolex_context:
    primary_legislation:
      - "{{kanun adı + numarası}}"
    secondary_legislation:
      - "{{yönetmelik adı + RG tarihi}}"
    constitutional_basis:
      - "Anayasa Md. {{X}}"
    international_treaties:
      - "{{ICESCR Md. 12 | AİHS Md. 2 | Oviedo Md. {{Y}}}}"
    yargi_ictihat_focus:
      - "{{AYM BB referansı | Danıştay 13 D referansı | Yargıtay 13 HD referansı}}"
    comparative_law_targets:
      - "{{Almanya | Fransa | İngiltere | İspanya | ABD | Japonya}}"
  
  requested_layers:
    - "{{regulatory | hta | medaffairs | onco | heme | immuno | neuro | rare | drug_intel}}"
  
  output_format_preferences:
    sidecar_required: true
    sections_priority: ["§5", "§7", "§9", "§13", "§14", "§18"]
    citation_format: "vancouver"
    language: "tr"
```

### 6.3. Tüketim Karar Tablosu

| Cureolex Mod | Zorunlu medical-research § | Opsiyonel § | Sidecar zorunlu mu? |
|---|---|---|---|
| DRAFT | §4, §5, §7, §9 | §13, §14 | Evet |
| AMEND | §4, §13.e | §19 | Şartlı |
| ANALYZE | §5, §13.f | §6, §9 | Evet |
| COMPLY | §15.e | §15.a-f | Şartlı |
| OPINE | §7, §9, §14.a, §14.f | İlgili specialty | Evet |
| RIA | §14.c, §14.d, §14.e, §14.f | §14.a | Evet |
| COMPARATIVE_LAW | §6, §13.a-c, §13.f | §14.a | Evet |
| TBMM_KANUN_TEKLIFI | §1-20 (TAM RAPOR) | — | Evet |
| EX_POST_EVALUATION | §5, §14.f, §19, §20 | §6, §7, §9, §13 | Evet — `ex_post_metrics` zorunlu |

> **Mod 9 notu:** EX_POST_EVALUATION klinik/HTA içeriyorsa sidecar `ex_post_metrics` alanı zorunludur; eksikse cross-skill gate G9 CONDITIONAL/FAIL döner (bkz. §15.1 G9 satırı).

---

## 7. Anti-Pattern'ler — Medical-Research Entegrasyonu Bağlamında

Cureolex'a Anti-Pattern listesine **yeni eklenen v2.2 anti-pattern'leri:**

### 7.1. Bilimsel Kanıt Olmadan DRAFT/OPINE Üretmek

**Yasak:** Klinik konuda (ilaç, hastalık, tıbbi cihaz, terapi) DRAFT yönetmelik veya OPINE mütalaa üretirken medical-research'ün § 7 (Tier 0 sentez) ve § 9 (Kılavuz) bölümlerini **dahil etmemek**.

**Hata örneği:** "Onkoloji ilaçları için aydınlatılmış onam yönetmeliği" taslağı medical-research bölümleri olmadan üretiliyor → bilimsel temellendirme eksik → 5210 Md. 4/e (kapsam netliği) ihlali + Md. 23 (gerekçe yetersizliği) riski.

**Doğru yaklaşım:** Mod 1 (DRAFT) tetiklendiğinde otomatik medical-research çağrısı yapılır; § 7 + § 9 madde gerekçesinde gösterilir.

### 7.2. Medical-Research Çıktısının Doğrulanmadan Aktarılması

**Yasak:** Medical-research çıktısındaki bir kanun maddesi referansını veya AYM bireysel başvuru numarasını **Cureolex Mevzuat MCP veya Hukuki Veritabanları MCP doğrulaması olmadan** Cureolex çıktısında kullanmak.

**Doğru yaklaşım:** Medical-research § 13.f (TİTCK pozisyonu) veya § 5 (Türkiye verileri) kullanıldığında, **Cureolex Mevzuat MCP üzerinden çapraz doğrulama** yapılır.

### 7.3. Skill Yetki Çatışması

**Yasak:** Medical-research'ün yetkili olduğu bir konuda (klinik etkililik, GRADE değerlendirmesi, ICER hesabı) **Cureolex'ın bağımsız yorum üretmesi**.

**Doğru yaklaşım:** Klinik karar veya HTA değerlendirmesi gerektiren konularda Cureolex, medical-research'e **delege eder** ve onun çıktısını aktarır; bağımsız klinik yorum üretmez.

### 7.4. Epistemik Etiketsiz Birleşim

**Yasak:** Medical-research çıktısını Cureolex çıktısına **kaynağı belirtilmeden** entegre etmek.

**Doğru yaklaşım:** Birleşik çıktıda her medical-research alıntısı **[medical-research v7.1, § X.Y, tarih]** formatında etiketlenir.

### 7.5. Tek Yönlü Veri Akışı

**Yasak:** Medical-research'ten Cureolex'a veri akışı sağlanıp **upstream sinyalin gönderilmemesi**.

**Doğru yaklaşım:** Cureolex, medical-research'ü çağırırken **enriched query** üretir; sadece original_query iletmez. Bu, medical-research'ün Türkiye Dörtlüsü ve § 13.f (TİTCK pozisyonu) bölümlerinin derinleşmesini sağlar.

---

## 8. Çıktı Format Standartları — Birleşik Sunum

### 8.1. Hibrit Çıktı Yapısı

Cureolex + medical-research birleşik çıktıları **iki başlık katmanı** kullanır:

**Üst katman (Cureolex):** Mevzuat metni, madde gerekçesi, mütalaa, RIA, kanun teklifi
**Alt katman (medical-research):** Bilimsel kanıt eki, kılavuz tablosu, regulatory timeline

**Örnek (DRAFT modu):**

```markdown
# {{Yönetmelik Adı}} Taslağı

## 1. Yönetici Özeti
[Cureolex üretir]

## 2. Hukuki Çerçeve ve Dayanak
[Cureolex üretir — Mevzuat MCP + R13]

## 3. Taslak Metni
[Cureolex üretir — R9 dil katmanı]

## 4. Madde Gerekçeleri
[Cureolex üretir]
  → Madde 5 gerekçesi:
     "...bilimsel dayanak: [medical-research v7.1, § 7, Tier 0 sentez]..."
     "...uluslararası kılavuz: [medical-research v7.1, § 9, NCCN/ESMO/ASCO]..."
     "...FDA/EMA pozisyonu: [medical-research v7.1, § 13.a, 13.b]..."

## 5. Risk ve Uyum Değerlendirmesi
[Cureolex üretir — Mod 4 21-noktalı denetim]

## 6. Karşılaştırmalı Tablo
[medical-research § 6 + § 13'ten alıntı + cureolex yorumu]

## 7. Tavsiyeler / Sonraki Adımlar
[Cureolex üretir]

## 8. Kaynakça
8.1. Mevzuat (Türk + uluslararası)
   [Cureolex üretir]
8.2. Bilimsel Kaynaklar (medical-research'ten)
   [medical-research § 1 + § 7 + § 9 + ilgili specialty kaynakları]
8.3. Türk Yargı İçtihatı
   [Cureolex R13'ten]

## EK A — Medical-Research Tam Rapor (referans olarak)
[medical-research orijinal çıktısı eklenebilir]

## EK B — Pipeline Sidecar Veri
[.data.json sidecar — gerekirse Cureolex üretir]
```

### 8.2. Atıf İstatistik Sözleşmesi

Birleşik çıktıda atıf istatistikleri raporlanır:

```
ATIF İSTATİSTİĞİ
- Türk mevzuat atfı: 23
- Türk yargı içtihatı atfı: 11 (AYM:4, Danıştay:5, Yargıtay:2)
- Uluslararası sözleşme atfı: 6 (ICESCR Md. 12, AİHS Md. 2/8, Oviedo, vd.)
- AB regülasyonu atfı: 4 (CELEX numarası ile)
- Medical-research § atfı: 17
  ├── § 7 (Tier 0): 5
  ├── § 9 (Kılavuz): 4
  ├── § 13 (Regulatory): 3
  ├── § 14 (HTA): 3
  └── İlgili specialty: 2
- Cochrane SR atfı: 3
- NICE TA atfı: 2
- Akademik doktrin atfı: 14 (Türk: 9, Uluslararası: 5)
```

---

## 9. Composability Sözleşmesi — SMP Manifest

Aşağıdaki YAML, **cureolex v2.2'nin SMP manifest dosyasına eklenecek** composability bloğudur. Bu, smp-orchestrator skill'inin Cureolex + medical-research pipeline'larını otomatik öneri yapmasını sağlar.

```yaml
# <plugin-root>/skill-manifest.yaml — composes_with bölümü (illüstratif)
composes_with:
  # Upstream — medical-research'ten beslenen
  - skill: medical-research
    protocol: bidirectional-evidence-exchange
    version_compatibility: ">= v7.1"
    invocation:
      auto_trigger_modes: [DRAFT, ANALYZE, OPINE, RIA, COMPARATIVE_LAW, TBMM_KANUN_TEKLIFI, EX_POST_EVALUATION]
      conditional_trigger_modes: [AMEND, COMPLY]
    data_flow:
      cureolex_to_medical_research:
        - primary_legislation_refs
        - yargi_ictihat_focus
        - constitutional_basis
        - international_treaty_refs
        - comparative_law_targets
      medical_research_to_cureolex:
        - section_5_turkey_data
        - section_7_tier0_synthesis
        - section_9_guideline_placement
        - section_13_regulatory_sciences
        - section_14_hta_pharmacoeconomics
        - section_15_medical_affairs_ops
        - section_18_rare_disease
        - section_19_drug_intelligence_pipeline
        - data_json_sidecar
    quality_contract:
      grade_synchronization: true
      epistemic_honesty_dual_tag: true
      citation_format_separation: 
        - turkish_legislation: cureolex_format
        - international_evidence: vancouver_format
    pipelines:
      - name: "P-1 TBMM Health Reform Bill"
        modes: [TBMM_KANUN_TEKLIFI]
        peer_skills: [pharmapatent, carbon-html-report]
      - name: "P-2 TİTCK Regulation Annulment Risk / Reform Defensibility Analysis"
        modes: [ANALYZE, COMPLY, RIA]
        peer_skills: [carbon-html-report]
      - name: "P-3R SUT/HTA Reimbursement Policy Reform"
        replaces_deprecated: "P-3 SGK Ödeme Reddi Bireysel Başvuru (bkz §3.3 — KAPSAM DIŞI)"
        modes: [DRAFT, RIA, EX_POST_EVALUATION]
        scope: "policy_reform_only"
        peer_skills: [onko-erisim, carbon-html-report]
      - name: "P-4 Health Regulation DRAFT — TİTCK"
        modes: [DRAFT]
        peer_skills: [carbon-html-report]
      - name: "P-5 BEF + DEA Bundle"
        modes: [RIA]
        peer_skills: [carbon-pptx, roche-design]
      - name: "P-6 Comparative Health Law Analysis"
        modes: [COMPARATIVE_LAW]
        peer_skills: [carbon-html-report]
      - name: "P-7R TİTCK Application/Rejection Procedure Reform"
        replaces_deprecated: "P-7 ADACLIN-tipi ürün-spesifik savunma (bkz §3.7 — KAPSAM DIŞI)"
        modes: [DRAFT, ANALYZE, RIA]
        scope: "procedure_reform_only"
        peer_skills: [pharmapatent, carbon-html-report]
      - name: "P-8 Turkey Health Legislation 48-Month Roadmap"
        modes: [ANALYZE, TBMM_KANUN_TEKLIFI]
        peer_skills: [roche-design, carbon-html-report, carbon-pptx]
```

### 9.1. Medical-Research Tarafına Önerilen Karşı-Manifest Güncellemesi

Aşağıdaki ekleme **medical-research SKILL.md'sinin manifest bloğuna** önerilir (kullanıcı tarafından manuel uygulanmalıdır — medical-research read-only durumdadır):

```yaml
# medical-research SKILL.md — composes_with bölümüne ekleme
composes_with:
  # ... mevcut girişler korunur ...
  
  # YENİ — Cureolex v2.2 bidirectional integration
  - skill: cureolex
    protocol: bidirectional-evidence-exchange + turkish-legislation-context
    version_compatibility: ">= v2.5.6"
    trigger:
      auto_invoke_from:
        - 0.5.C signal (regulatory) + Turkey context
        - 0.5.D signal (HTA) + SGK / SUT context
        - 0.5.E signal (medical affairs) + İEİS context
    enrichment_received:
      - turkish_legislation_primary_refs (1219 SK, 1262 SK, 6197 SK, 7223 SK, 5210)
      - constitutional_anchors (Md. 17, Md. 56, Md. 90/5)
      - turkish_jurisprudence_focus (AYM, Danıştay 13, Yargıtay 11/13 HD)
      - international_treaty_explicit_chain (ICESCR Md. 12, AİHS Md. 2/8, Oviedo)
    enrichment_produced:
      - section_13f_titck_position_deepening
      - section_9_turkish_guideline_interpretation
      - section_5_legislation_cross_validation
      - section_15e_iEIS_compliance_overlay
    pipelines_enabled:
      - "Turkish health regulation bill drafting"
      - "Health-rights jurisprudence signals for legislation reform"
      - "TİTCK regulation annulment risk / reform defensibility analysis"
      - "Health legislation comparative reform analysis"
      - "SUT/HTA reimbursement policy reform"
    pipelines_disabled:
      # Cross-skill Scope Guard — cureolex bu hatlar için ASLA çağrılmaz
      - "Constitutional Court individual application drafting"
      - "individual SGK reimbursement denial defense"
      - "TİTCK litigation defense brief"
      - "ADACLIN-type product-specific rejection defense"
      - "promotional material PASS/FAIL review"
```

---

## 10. Test ve Doğrulama

### 10.1. Entegrasyon Kalite Kontrol Listesi

Birleşik bir Cureolex + medical-research çıktısının kalite kabul kriterleri:

```
☐ 1. Medical-research zorunlu mod tetikleyicisi doğru tespit edildi mi?
☐ 2. Enriched query medical-research'e iletildi mi?
☐ 3. Medical-research çıktısı (rapor + sidecar) alındı mı?
☐ 4. İlgili § bölümleri (Bölüm 4'teki tabloya göre) Cureolex'a tüketildi mi?
☐ 5. Atıflar [medical-research v7.1, § X.Y] formatında işaretlendi mi?
☐ 6. Türk mevzuat atıfları (Mevzuat MCP doğrulamalı) ayrı işaretlendi mi?
☐ 7. Çift epistemik dürüstlük etiketi yerleştirildi mi?
☐ 8. Birleşik kaynakça (8.1, 8.2, 8.3) düzgün ayrıştırıldı mı?
☐ 9. Atıf istatistiği raporlandı mı?
☐ 10. R9 (Türk hukuk dili) ve medical-research Vancouver formatı 
       karıştırılmadan kullanıldı mı?
```

### 10.2. Tipik Test Senaryoları

**Test 1: TBMM Sağlık Reform Teklifi**
- Sorgu: "1219 sayılı Kanunun reformatlama TBMM teklifi"
- Beklenen: P-1 pipeline tetiklenir; medical-research § 1-20 tam çağrılır; cureolex Mod 8 protokolü çalışır
- Çıktı doğrulaması: 80+ atıf, 20+ medical-research § referansı, 60+ Türk mevzuat referansı

**Test 2 (NEGATİF — Scope Guard): Bireysel SGK Ödeme Reddi / AYM**
- Sorgu: "Trastuzumab deruksetkan T-DXd SGK ödeme reddi bireysel başvuru"
- Beklenen: cureolex **AKTİVE OLMAZ**; istem kapsam dışı tespit edilir ve `saglik-sigorta`/`onko-erisim` skill'ine yönlendirilir (SKILL.md §2 Scope Guard). Eski P-3 pipeline **DEPRECATED**'tir.
- Doğrulama: Hiçbir OPINE/AYM çıktısı üretilmez; yalnızca yönlendirme mesajı döner. In-scope karşılığı: "SUT geri ödeme kriteri reformu tebliğ taslağı" (Mod 1+6).

**Test 3: TİTCK Yönetmelik İptal Riski / Reform Savunulabilirliği Analizi**
- Sorgu: "Klinik araştırmalar yönetmeliğinin Danıştay iptal riski ve reform savunulabilirliği analizi"
- Beklenen: P-2 pipeline tetiklenir; cureolex Mod 3 (ANALYZE) + Mod 6 (RIA); medical-research 0.5.C + 0.5.E
- Çıktı doğrulaması: İptal riski / reform gerekçe analiz notu + medical-research § 13 + § 15.e aktarımı (dava savunma dilekçesi DEĞİL)

---

## 11. Sürüm Notları

**Cureolex v2.2 medical-research entegrasyonu — 22 Mayıs 2026**

- İlk yapılandırılmış bidirectional integration sözleşmesi
- 8 co-execution pipeline tanımı
- Karar ağacı tabanlı otomatik tetikleme
- Çift epistemik dürüstlük protokolü
- SMP manifest composability sözleşmesi (her iki skill için)
- Medical-research v7.1 ile doğrulanmış uyumluluk

---

## 12. Section-by-Section Integration Matrix (v2.3 YENİ — Derin Entegrasyon Katmanı)

Bu bölüm, medical-research'ün § 1-20 arasındaki tüm çıktı bölümlerini cureolex'ın 9 işletim modunda tam haritalayarak, **hangi medical-research bölümünün hangi cureolex modunda ne tür çıktıya beslendiğini** bire-bir gösterir. v2.2'nin handoff yaklaşımı bölüm bazında genel önerilerle sınırlıydı; v2.3 ile **§ × mod × çıktı kesiti = 180 hücre** matriksi devreye girer.

### 12.1. Medical-Research §1-20 Bölüm Listesi (v7.1 Format A — GERÇEK YAPI v2.3-r1'de Kalibre Edildi)

Medical-research v7.1 Output Format A standart yapısı 20 ana bölümden oluşur. Aşağıdaki tablo medical-research SKILL.md'sinin **gerçek** Adım 3 ("Çıktı Zorunluluğu") satır 887-980 üzerinden doğrulanmıştır:

| § | Bölüm Adı (medical-research GERÇEK adı) | İçerik / Connector | Tetiklenme |
|---|---|---|---|
| § 1 | **Küresel Literatür** (PubMed + Europe PMC) | Ana literatür taraması — primer akademik kaynak | DAİMA |
| § 2 | **Klinik Pipeline** (CT.gov v2) | Trial registries — Phase 1/2/3/4 + status | DAİMA |
| § 3 | **Mekanizma & Farmakoloji** (ChEMBL + PubChem) | Hedef, MoA, farmakokinetik, kimyasal yapı | ⚠ İLAÇ İSE |
| § 4 | **Ruhsat & Etiket** (DailyMed + OpenFDA + EMA) | FDA SPL + EU SmPC + EPAR — etiket karşılaştırma | ⚠ İLAÇ İSE |
| § 5 | **Türkiye Verileri** (TİTCK + SGK + YokTez + AFF:"Turkey") | Türkiye RWE + yerel kohort + tez + dergi | DAİMA |
| § 6 | **Çok Dilli Kapsama** (6 ülke AFF matriksi) | Almanya/Fransa/UK/İtalya/İspanya/Japonya yerel literatür | DAİMA |
| § 7 | **Tier 0 Sentez** (SR + Cochrane + Epistemonikos) | Sistematik incelemeler — en yüksek kanıt katmanı | DAİMA |
| § 8 | **KOL Haritası** (OpenAlex → S2 → EPMC meta fallback) | Anahtar kanaat önderleri — co-author network, h-index | DAİMA |
| § 9 | **Kılavuz Yerleşimi** (NICE + ESMO + NCCN) | Tedavi rehberleri — recommendation grade + tedavi algoritması | DAİMA |
| § 10 | **Açık Erişim Alternatifleri** (Unpaywall + DOAJ) | Paywalled yayınlara açık erişim alternatif PDF | DAİMA |
| § 11 | **ONKOLOJİ GENİŞLETİLMİŞ BÖLÜMLERİ** (katman aktifse) | 11.a Tümör-spesifik kılavuz + 11.b biomarker/CDx + 11.c ESMO-MCBS/ASCO VF | Adım 0.5.A tetiklerse |
| § 12 | **HEMATOLOJİ GENİŞLETİLMİŞ BÖLÜMLERİ** (katman aktifse) | WHO-HAEM5 + ELN-2022 + IPSS-M + R-ISS + iwCLL/IMWG | Adım 0.5.B tetiklerse |
| § 13 | **REGULATORY SCIENCES BÖLÜMLERİ** (v7.0, katman aktifse) | 13.a Ruhsat trajektörü • 13.b AdComm/CHMP • 13.c Özel yollar (BTD/AA/CMA/Orbis/PRIME/ODD) • 13.d Post-marketing (REMS/RMP) • 13.e Historical parallel (withdrawal) • 13.f Türkiye TİTCK pozisyonu | Adım 0.5.C tetiklerse |
| § 14 | **HTA / PHARMACOECONOMICS BÖLÜMLERİ** (v7.0, katman aktifse) | 14.a Ajans-ajans matriksi (NICE/CADTH/PBAC/IQWiG/HAS/ICER) • 14.b Ekonomik model (Markov/PSM/DES) • 14.c ICER+NMB+CEAC • 14.d Budget Impact • 14.e Managed Entry/OBA • 14.f Türkiye SGK SUT | Adım 0.5.D tetiklerse |
| § 15 | **MEDICAL AFFAIRS OPERATIONS BÖLÜMLERİ** (v7.0, katman aktifse) | 15.a MSL Engagement • 15.b Advisory Board • 15.c Publication Planning (GPP3) • 15.d IIS/ISR rubrik • 15.e Compliance Stack (EFPIA/IFPMA/FCPA/İEİS) • 15.f Speaker Bureau/CME | Adım 0.5.E tetiklerse |
| § 16 | **IMMUNOLOGY BÖLÜMLERİ** (v7.0, katman aktifse) | RA/PsA/AS/SLE/Crohn/UC/atopik dermatit + JAK/IL-17/IL-23/TNF + biyobenzer | Adım 0.5.F tetiklerse |
| § 17 | **NEUROLOGY BÖLÜMLERİ** (v7.0, katman aktifse) | MS/ALS/Alzheimer/Parkinson/SMA/migren + DMT seçimi + ECTRIMS/AAN | Adım 0.5.G tetiklerse |
| § 18 | **RARE DISEASE BÖLÜMLERİ** (v7.0, katman aktifse) | Orphanet + OMIM + GARD + ODD + EAP + ultra-rare prevalence | Adım 0.5.H tetiklerse |
| § 19 | **DRUG INTELLIGENCE PIPELINE SNAPSHOT** (v7.1, katman aktifse) | AdisInsight + Synapse — pipeline + MoA landscape + biosimilar + M&A + LoE | Adım 0.5.I tetiklerse |
| § 20 | **CROSS-LAYER INTEGRATION NOTES** (v7.1) | Çoklu eksen tetiklendiğinde kesişim analizi — örn. onkoloji + regulatory + HTA üçlü pivot | Multi-domain durumlarda |

**v2.3 öncesi R14'teki tahminden farklılıklar (v2.3-r1 düzeltmesi):**
- § 3 önceki tahmin: "Connector Bazlı Bulgu Detayları" → **gerçek:** "Mekanizma & Farmakoloji (ChEMBL + PubChem) — İLAÇ İSE şartlı"
- § 4 önceki tahmin: "Exa + Tavily OSINT Bulguları" → **gerçek:** "Ruhsat & Etiket (DailyMed + OpenFDA + EMA) — İLAÇ İSE şartlı"
- § 8 önceki tahmin: "Pivotal Trial Sentezi" → **gerçek:** "KOL Haritası (OpenAlex → S2)"
- § 10 önceki tahmin: "Biomarker ve Companion Diagnostic" → **gerçek:** "Açık Erişim Alternatifleri (Unpaywall + DOAJ)" — biomarker §11.b'de
- § 11 ile §18 arası **tek bir specialty katmanı** değil, **bağımsız 8 layer** (her biri Adım 0.5.A-H ekseninde tetiklenir)
- § 19 "Drug Intelligence" (v7.1 — Adım 0.5.I tetikler)
- § 20 önceki tahmin: "Bilgi Boşlukları + Kaynaklar" → **gerçek:** "Cross-Layer Integration Notes" (Vancouver kaynakları ise format-spesifik kapanış bölümünde, ayrı §)

**Tetiklenme mekanigi:** Medical-research'te Adım 0.5 Domain Classifier sözlük tabanlı sinyal tespiti yapar; tetiklenen eksen (A-I) ilgili specialty bölümünü (§ 11-19) çıktıya enjekte eder. Cureolex'tan enriched query üretirken **bu sözlük kelimelerinin doğru tetiklenmesi** kritiktir — bu §19'da operasyonel olarak detaylandırılır.

### 12.2. § × Mod Tam Matrisi (Gerçek § Adlarıyla — v2.3-r1 Kalibre)

Aşağıdaki tablo, **her medical-research § için hangi cureolex modunda zorunlu/önerilen/opsiyonel tüketim** yapılacağını belirtir. Tablo medical-research v7.1'in **gerçek bölüm adlandırması** ile uyumludur:

| § | Mod 1 DRAFT | Mod 2 AMEND | Mod 3 ANALYZE | Mod 4 COMPLY | Mod 5 OPINE | Mod 6 RIA | Mod 7 COMPARE | Mod 8 TBMM | Mod 9 EX_POST |
|---|---|---|---|---|---|---|---|---|---|
| § 1 Küresel Literatür | ▣ | ▣ | ◆ | ○ | ◆ | ▣ | ▣ | ◆ | ◆ |
| § 2 Klinik Pipeline | ▣ | ▣ | ◆ | ○ | ▣ | ◆ | ▣ | ◆ | ▣ |
| § 3 Mekanizma & Farmakoloji (ilaç ise) | ▣ | ▣ | ▣ | ○ | ▣ | ▣ | ▣ | ▣ | ○ |
| § 4 Ruhsat & Etiket (ilaç ise) | ◆ | ◆ | ◆ | ▣ | ◆ | ◆ | ◆ | ◆ | ◆ |
| § 5 Türkiye Verileri | ◆ | ◆ | ◆ | ▣ | ◆ | ◆ | ▣ | ◆ | ◆ |
| § 6 Çok Dilli Kapsama | ▣ | ▣ | ▣ | ○ | ▣ | ▣ | ◆ | ◆ | ▣ |
| § 7 Tier 0 Sentez | ◆ | ◆ | ◆ | ▣ | ◆ | ◆ | ◆ | ◆ | ◆ |
| § 8 KOL Haritası | ○ | ○ | ▣ | ○ | ▣ | ○ | ○ | ▣ | ○ |
| § 9 Kılavuz Yerleşimi | ◆ | ◆ | ◆ | ▣ | ◆ | ◆ | ◆ | ◆ | ◆ |
| § 10 Açık Erişim Alternatifleri | ○ | ○ | ○ | ○ | ○ | ○ | ○ | ▣ | ○ |
| § 11 Onkoloji Ext | (clinical mode) ▣ | ▣ | ▣ | ○ | ▣ | ▣ | ▣ | ▣ | ▣ |
| § 12 Hematology Ext | (clinical mode) ▣ | ▣ | ▣ | ○ | ▣ | ▣ | ▣ | ▣ | ▣ |
| § 13 Regulatory Sciences | ◆ | ◆ | ◆ | ◆ | ◆ | ◆ | ◆ | ◆ | ◆ |
| § 14 HTA / Pharmacoeconomics | ▣ | ▣ | ▣ | ○ | ◆ | ◆ | ◆ | ◆ | ◆ |
| § 15 Medical Affairs Ops | ○ | ○ | ▣ | ◆ | ▣ | ▣ | ○ | ▣ | ▣ |
| § 16 Immunology | (clinical mode) ▣ | ▣ | ▣ | ○ | ▣ | ▣ | ▣ | ▣ | ▣ |
| § 17 Neurology | (clinical mode) ▣ | ▣ | ▣ | ○ | ▣ | ▣ | ▣ | ▣ | ▣ |
| § 18 Rare Disease | ▣ | ▣ | ▣ | ○ | ◆ | ▣ | ▣ | ◆ | ▣ |
| § 19 Drug Intelligence Pipeline | ▣ | ▣ | ◆ | ○ | ◆ | ◆ | ▣ | ▣ | ◆ |
| § 20 Cross-Layer Integration | ▣ | ▣ | ◆ | ○ | ◆ | ▣ | ◆ | ▣ | ◆ |

**Lejant:** ◆ = ZORUNLU tüketim (mod ↔ konu klinik bağlamda) — § eksikse Cureolex çıktısı tamamlanmaz; ▣ = ÖNERİLİR (önemli destek bölümü); ○ = OPSİYONEL (içerik gerektiriyorsa kullanılır); "(clinical mode)" = specialty katman aktif olduğunda zorunlu.

**Kritik değişiklikler v2.3 → v2.3-r1:**
- § 1 (Küresel Literatür) artık ANALYZE/OPINE/TBMM/EX_POST modlarında ◆ ZORUNLU (önceki: ▣)
- § 4 (Ruhsat & Etiket — ilaç ise) artık DRAFT/AMEND/ANALYZE/OPINE/RIA/COMPARE/TBMM/EX_POST'ta ◆ ZORUNLU (önceki: ○/▣)
- § 7 (Tier 0 Sentez) DRAFT/AMEND/ANALYZE/OPINE/RIA/COMPARE/TBMM/EX_POST'ta ◆ ZORUNLU (önceki kısmen ▣)
- § 9 (Kılavuz Yerleşimi) DRAFT/AMEND/ANALYZE/OPINE/RIA/COMPARE/TBMM/EX_POST'ta ◆ ZORUNLU (önceki kısmen ◆)
- § 14 (HTA) Mod 5 OPINE'da ◆ ZORUNLU oldu (SUT/HTA geri ödeme politikası reformunda HTA delili kritik)
- § 15 (MedAffairs Ops) Mod 4 COMPLY'de ◆ ZORUNLU (tanıtım mevzuatı reform uyumunda EFPIA/IFPMA/AİFD compliance stack referansı zorunlu)
- § 18 (Rare Disease) Mod 5 OPINE + Mod 8 TBMM'de ◆ ZORUNLU (nadir hastalık erişim kararlarında kritik)
- § 19 (DrugIntel) Mod 3/5/6/9'da ◆ ZORUNLU (pipeline-aware analiz + RIA + ex post)
- § 20 (Cross-Layer) Mod 3/5/7/9'da ◆ ZORUNLU (multi-domain durumda kesişim analizi)

### 12.3. Cureolex Çıktı Bölümü ↔ Medical-Research § Eşleme

Her cureolex çıktı standardı (`SKILL.md Bölüm 8`) bölümü için tipik medical-research § beslemesi:

| Cureolex Çıktı Bölümü | Tipik Medical-Research § Beslemesi |
|---|---|
| 1. Yönetici Özeti | § 1 (özet) + § 9 (kılavuz konsensüs) |
| 2. Hukuki Çerçeve ve Dayanak | § 13 (regulatory mechanics) + § 9 (kılavuz) + § 14 (HTA) |
| 3. Ana Bulgular / Taslak Metni | § 7 (Tier 0 sentez) + § 8 (pivotal trials) + § 5 (Türkiye verileri) |
| 4. Madde Gerekçeleri | § 5 (Türkiye verileri) + § 9 (kılavuz) + ilgili § (modaliteye göre) |
| 5. Risk ve Uyum Değerlendirmesi | § 13.c (TİTCK) + § 14.f (SGK) + § 15 (compliance) |
| 6. Karşılaştırmalı Tablo | § 6 (karşılaştırmalı ülke verisi) + § 13 + § 14 |
| 7. Tavsiyeler / Sonraki Adımlar | § 19 (pipeline — gelecek katalizörler) + § 20 (bilgi boşlukları) |
| 8. Kaynakça | § 20 (Vancouver formatlı kaynaklar) — birleştirme |

### 12.4. Operasyonel İşletim — Otomatik Bölüm Talep Üretimi

Cureolex, medical-research'e enriched query gönderirken **§-bazlı request** ekler. Örnek enriched query:

```json
{
  "original_query": "Pembrolizumab MSI-H endometriyum kanseri tedavisinde adjuvan kullanım",
  "mode": "DRAFT",
  "cureolex_context": {
    "drafting_target": "SGK SUT EK-4/A güncellemesi",
    "primary_legislation": ["SGK Sağlık Uygulama Tebliği"],
    "constitutional_basis": ["Md. 17 yaşam hakkı", "Md. 56 sağlık hakkı"],
    "international_treaties": ["ICESCR Md. 12 + GC 14 AAAQ"],
    "comparative_law_targets": ["NICE TA 779", "G-BA Nutzenbewertung", "PBAC submission"]
  },
  "requested_layers": ["regulatory", "hta", "medaffairs"],
  "requested_sections_by_priority": {
    "MANDATORY": ["§13", "§14", "§15"],
    "RECOMMENDED": ["§5", "§7", "§8", "§9", "§11"],
    "OPTIONAL": ["§16", "§19"]
  },
  "specialty_layer_focus": "oncology",
  "output_format": "Format E (Oncology Extended)",
  "citation_format": "Vancouver",
  "epistemic_dual_label": true,
  "version_compat": {
    "medical_research_min": "7.1",
    "cureolex": "2.6.0",
    "sidecar_schema": "2.3.1"
  }
}
```

Bu format, medical-research'ün **gereksiz bölümler üretmesini engeller** ve token verimliliğini artırır.

---

## 13. Specialty Layer × Mod Matrisi (v2.3 YENİ)

Medical-research v7.1, dokuz specialty layer içerir: Onco, Heme, Regulatory, HTA, MedAffairs, Immunology, Neurology, RareDisease, DrugIntelligence. v2.3, bu layer'ların cureolex'ın 9 modundaki tetikleyici-tabanlı kullanımını matrislemiştir.

### 13.1. Specialty Layer × Mod Tam Matrisi (81 Hücre)

| Layer ↓ / Mod → | M1 DRAFT | M2 AMEND | M3 ANALYZE | M4 COMPLY | M5 OPINE | M6 RIA | M7 COMPARE | M8 TBMM | M9 EX_POST |
|---|---|---|---|---|---|---|---|---|---|
| **Oncology** | A: solid tumor mevzuat | A: hedefli tedavi access | A: AYM onko ictihad | A: 1262 SK yetki | A: SUT geri ödeme kriteri reformu | A: onko BEF projeksiyon | A: NCCN/ESMO karşılaştırma | A: kanser kontrol kanunu | A: onko mevzuat ex-post |
| **Hematology** | A: heme mevzuat | A: CAR-T access | A: heme yargı | A: TİTCK yetki | A: CAR-T ödeme politikası reformu | A: heme BEF | A: ASH/EHA karşılaştırma | A: HEMATOPATIA reform | A: heme RWE ex-post |
| **Regulatory** | **B: temel ruhsat reform** | **B: ürün dosyası amend** | **B: TİTCK düzenleme iptal riski analizi** | **B: 5210 + 1262 SK yetki** | **B: TİTCK görüşü** | **B: RIA EMA + FDA paralel** | **B: ICH/PIC/S karşılaştırma** | **B: 1262 SK reform** | **B: ruhsat mevzuat ex-post** |
| **HTA** | A: HTA mevzuat | A: HTA prosedür değişikliği | A: HTA itiraz | A: HTA yetki kanunu | A: HTA karar usulü/itiraz mekanizması reformu | **B: BEF/DEA core layer** | A: NICE/G-BA karşılaştırma | A: HTA kurumu kanunu | A: HTA ex-post |
| **MedAffairs** | A: tanıtım mevzuat | A: tanıtım amend | A: tanıtım denetim | A: BTÜ-TF Yön. yetki | **B: tanıtım mevzuatı reform görüşü** | A: tanıtım BEF | A: EFPIA/IFPMA karşılaştırma | A: 1262 SK m. 13 reform | A: tanıtım ex-post |
| **Immunology** | A: oto-immün mevzuat | A: biyolojik access | A: immün yargı | A: BTÜ yetki | A: biyolojik ürün ödeme politikası reformu | A: immün BEF | A: EULAR/ECTRIMS karşıl. | A: oto-immün kanun reform | A: immün ex-post |
| **Neurology** | A: nöro mevzuat | A: nöro access | A: nöro yargı | A: BTÜ yetki | A: nöro ödeme politikası reformu | A: nöro BEF | A: AAN/ECTRIMS karşıl. | A: nörolojik kanun reform | A: nöro ex-post |
| **RareDisease** | A: nadir hastalık mevzuat | A: orphan amend | A: orphan yargı | A: orphan yetki | **B: erken erişim/compassionate use mevzuatı reformu** | A: orphan BEF | **B: orphan rejim karşıl.** | A: nadir hastalık kanunu | A: orphan ex-post |
| **DrugIntelligence** | A: pipeline destekli mevzuat | A: pipeline-aware amend | **B: M&A intel** | A: yetki + pipeline | A: pipeline-destekli görüş | **B: pipeline-aware BEF** | A: pipeline karşılaştırma | A: pipeline-aware reform | **B: pipeline-aware ex-post** |

**Lejant:**
- **A:** Standart tetikleyici (mod konuya uyduğunda specialty layer çağrılır)
- **B:** Specialty layer'ın **PRIMARY** kullanım yeri (bu modda specialty layer **çekirdek** veridir)

### 13.2. Primary Use Case Cluster'ları

| Cluster | Specialty Layers | Mod-ların ağırlık merkezi |
|---|---|---|
| **Klinik onko-heme cluster** | Oncology + Hematology + RareDisease | M5 (OPINE) + M1 (DRAFT) + M3 (ANALYZE) — onko/heme spesifik geri ödeme politikası reformu, ATMP mevzuatı |
| **Regulatory core cluster** | Regulatory + DrugIntelligence | M1 (DRAFT) + M2 (AMEND) + M3 (ANALYZE) + M8 (TBMM) — temel ruhsat mevzuatı reform |
| **Market access cluster** | HTA + Regulatory + MedAffairs | M6 (RIA) + M5 (OPINE) + M9 (EX_POST) — BEF/DEA çekirdek + tanıtım mevzuatı reform uyumu |
| **Therapeutic specialty cluster** | Immunology + Neurology | M5 (OPINE) + M3 (ANALYZE) — yüksek maliyetli biyolojik tedaviler için ödeme politikası, erişim mevzuatı ve izleme göstergesi reformu |
| **Compliance + Audit cluster** | MedAffairs + Regulatory | M4 (COMPLY) + M5 (OPINE) — Mod 4 tanıtım mevzuatı reform uyumu + Mod 5 reform görüşü |

### 13.3. Karar Ağacı — Hangi Layer Tetiklenir?

```
Sorgu içeriği klinik mi? 
  ├─ Hayır → Specialty layer çağırma; cureolex standalone
  └─ Evet → Anahtar kelime analizi:
       ├─ "kanser, tümör, metastaz, NCCN, ESMO, ASCO" → Oncology layer
       ├─ "lösemi, lenfoma, myelom, CAR-T, BTK, ELN, IPSS" → Hematology layer
       ├─ "ruhsat, FDA, EMA, TİTCK, ICH, PIC/S, Reliance" → Regulatory layer
       ├─ "ICER, QALY, NICE TA, G-BA, CADTH, SGK SUT" → HTA layer
       ├─ "MSL, KOL, advisory board, EFPIA, promo, GPP3" → MedAffairs layer
       ├─ "MS, ALS, Alzheimer, SMA, ECTRIMS, AAN" → Neurology layer
       ├─ "romatoid, lupus, JAK, IL-17, EULAR" → Immunology layer
       ├─ "orphan, ODD, Orphanet, OMIM, ultra-rare, EAP" → RareDisease layer
       └─ "pipeline, M&A, AdisInsight, Synapse, milestone, PDUFA" → DrugIntelligence layer
```

Birden fazla layer aynı anda tetiklenebilir (cluster). Cureolex, çoklu tetik durumunda enriched query'de **layer önceliği** belirtir.

---

## 14. Sidecar JSON Şeması v2 (v2.3 YENİ)

Medical-research'ten Cureolex'a aktarılan `.data.json` sidecar dosyasının **v2.3 zenginleştirilmiş şeması**.

### 14.1. Şema Genel Yapısı

```json
{
  "schema_version": "2.3.1",
  "medical_research_version": "7.1",
  "cureolex_version": "2.6.0",
  "generated_at": "2026-05-22T17:00:00Z",
  "query_metadata": {
    "original_query": "...",
    "enriched_query": {...},
    "execution_time_ms": 12450,
    "connectors_used": ["pubmed", "epmc", "clinical_trials", "adisinsight"]
  },
  "evidence_grading": {...},
  "section_payloads": {...},
  "turkish_legislation_refs": {...},
  "yargi_ictihat_chain": {...},
  "ex_post_metrics": {...},
  "specialty_layer_activations": {...},
  "epistemic_honesty": {...},
  "citation_index": {...}
}
```

### 14.2. `evidence_grading` Bölümü

Her bulgu için GRADE etiketi + kaynak güvenilirliği:

```json
{
  "primary_endpoint_evidence": {
    "grade": "HIGH",
    "study_count": 3,
    "design": "Phase III RCT",
    "studies": [
      {"nct_id": "NCT0XXXXXXX", "design": "double-blind RCT", "n": 845, "primary_endpoint_hr": 0.65}
    ]
  },
  "secondary_endpoint_evidence": {
    "grade": "MODERATE",
    "study_count": 2,
    "design": "Single-arm + extension"
  },
  "real_world_evidence": {
    "grade": "LOW",
    "country_data": ["TR", "DE", "UK"],
    "study_count": 8
  }
}
```

### 14.3. `section_payloads` Bölümü (v2.3 — § 1-20 her birinin yapılandırılmış payload'u)

```json
{
  "section_1_summary": {
    "key_findings": [...],
    "grade_summary": {"HIGH": 5, "MODERATE": 8, "LOW": 3},
    "knowledge_gaps": [...]
  },
  "section_5_turkey": {
    "registries": [
      {"name": "REGISTURK-LUNG", "n": 1342, "year": 2024}
    ],
    "yoktez_theses": [
      {"id": "yt_xxxxx", "university": "İstanbul Üniv.", "year": 2024, "department": "İç Hastalıkları"}
    ],
    "rwe_publications": [
      {"vancouver_citation": "Yılmaz A, et al. ...", "doi": "10.xxxx", "country_focus": "TR"}
    ]
  },
  "section_7_tier0_synthesis": {
    "cochrane_reviews": [
      {"id": "CD0XXXXX", "title": "...", "last_updated": "2025-01", "grade_summary": {...}}
    ],
    "nice_systematic_reviews": [...],
    "epistemonikos_links": [...]
  },
  "section_13_regulatory": {
    "fda": {"approval_date": "...", "indication": "...", "label_url": "..."},
    "ema": {"chmp_opinion_date": "...", "epar_url": "...", "indication": "..."},
    "titck": {"ruhsat_date": "...", "barkod_list": [...], "endikasyon_tr": "..."},
    "reliance_status": {"wla_eligible": true, "tr_reliance_pathway": "..."}
  },
  "section_14_hta": {
    "nice_ta": {"id": "TA779", "decision": "recommend with criteria", "icer_threshold_met": true},
    "g_ba_iqwig": {"additional_benefit": "geringer", "amnog_negotiation_outcome": "..."},
    "sgk_sut": {"current_status": "SUT EK-4/A günceI", "annual_budget_impact_try": 2400000000}
  },
  "section_19_pipeline": {
    "originator": {"company": "...", "stage": "approved"},
    "biosimilars_in_development": [
      {"developer": "...", "stage": "Phase III", "expected_launch": "2027"}
    ],
    "competing_assets": [...]
  }
}
```

> ⚠️ **Aşağıdaki §14.4 ve §14.5 JSON blokları YALNIZCA örnektir (`_example_only`); tüm `mcp_verified` alanları `false`'tur. Gerçek kullanımda her kayıt Mevzuat/Hukuki Veritabanları MCP ile doğrulanmalı; doğrulanmadan `mcp_verified: true` yazılamaz.**

### 14.4. `turkish_legislation_refs` Bölümü (v2.3 YENİ — Mevzuat MCP teyit referansları)

```json
{
  "primary_legislation": [
    {
      "name": "5237 sayılı Türk Ceza Kanunu",
      "rg_date": "12/10/2004",
      "rg_number": "25611",
      "url": "https://www.mevzuat.gov.tr/...",
      "relevant_articles": ["m. 191"],
      "mcp_verified": false,
      "verification_status": "illustrative_placeholder_not_verified"
    }
  ],
  "regulations_in_force": [...],
  "circulars": [...],
  "constitutional_articles": ["Md. 17", "Md. 56", "Md. 90/5"],
  "international_treaties_md_90_5": [
    {"name": "ICESCR Md. 12", "tr_ratification_year": 2003, "gc_14_aaaq_applicable": true}
  ]
}
```

### 14.5. `yargi_ictihat_chain` Bölümü (v2.3 YENİ — Hukuki Veritabanları MCP teyit zinciri)

```json
{
  "aym_decisions": [
    {
      "case_no": "{{AYM E./K. no — MCP ile doğrulanacak; temsili}}",
      "decision_date": "2024-03-15",
      "subject": "Sağlık hakkı + Md. 17 + Md. 56",
      "outcome": "İptal",
      "url": "https://kararlarbilgibankasi.anayasa.gov.tr/...",
      "mcp_verified": false
    }
  ],
  "aym_bireysel_basvurular": [
    {
      "application_no": "2024/XXXXX",
      "decision_date": "2025-XX-XX",
      "subject": "...",
      "outcome": "İhlal var",
      "mcp_verified": false
    }
  ],
  "danistay_decisions": [...],
  "yargitay_decisions": [...],
  "aihm_turkey_decisions": [
    {
      "app_no": "13423/09",
      "case_name": "Mehmet Şentürk ve Bekir Şentürk c. Türkiye",
      "decision_date": "2013-04-09",
      "subject": "Md. 2 + sağlık hizmeti erişimi",
      "url": "https://hudoc.echr.coe.int/...",
      "mcp_verified": false
    }
  ],
  "cjeu_decisions": [...]
}
```

### 14.6. `ex_post_metrics` Bölümü (v2.3 YENİ — Mod 9 için)

```json
{
  "applicable_for_ex_post_evaluation": true,
  "elapsed_months_since_implementation": 28,
  "market_data": {
    "midas_data_available": true,
    "pre_implementation_market_size_try": 1200000000,
    "post_implementation_market_size_try": 1450000000,
    "growth_rate": 0.21
  },
  "reimbursement_data": {
    "sgk_total_spending_try": {"pre": 600000000, "post": 720000000},
    "rejection_rate": {"pre": 0.18, "post": 0.12},
    "average_processing_days": {"pre": 21, "post": 14}
  },
  "clinical_real_world_data": {
    "patient_cohorts_available": ["REGISTURK-LUNG", "TÜRKMSV"],
    "key_outcome_metrics": [...]
  },
  "judicial_review_outcomes": {
    "aym_iptal_count": 0,
    "danistay_iptal_count": 1,
    "aihm_violations": 0
  },
  "stakeholder_feedback": {
    "ttb_position": "...",
    "aifd_position": "...",
    "patient_associations": [...]
  }
}
```

### 14.7. `epistemic_honesty` Bölümü (v2.3 — çift sürüm)

```json
{
  "medical_research_self_disclosure": {
    "knowledge_gaps": [...],
    "uncertainty_flags": [...],
    "single_source_findings": [...],
    "version_limitations": "v7.1 + ClinicalTrials.gov v2 API"
  },
  "cureolex_self_disclosure": {
    "mcp_unavailability_during_query": [],
    "uncertain_interpretations": [...],
    "limitations_due_to_mode": "...",
    "version": "2.6.0",
    "sidecar_schema_origin": "2.3.1"
  },
  "combined_confidence": "MODERATE",
  "recommendation_for_user": "Çıktı kalitesi orta seviye; SGK iddialarında ek doğrulama önerilir."
}
```

### 14.8. Sidecar Tüketim Protokolü — Cureolex İç Akışı

Cureolex, sidecar JSON'u tükettikten sonra:

1. **Şema sürümü kontrolü** — `schema_version` ≥ "2.0" olmalı; "2.3" ideal
2. **Sürüm uyumluluk kontrolü** — `medical_research_version` ↔ `cureolex_version` matrisinde (Bölüm 17) kontrol edilir
3. **Veri bütünlüğü kontrolü** — Beklenen bölümler eksik mi? Eksiklik durumunda tekrar query veya graceful degradation
4. **Atıf otomasyonu** — `citation_index` direkt cureolex çıktısının "Kaynakça" bölümüne integrate edilir
5. **Epistemik etiket aktarımı** — `epistemic_honesty.combined_confidence` cureolex çıktısının Bölüm 9 (Bilgi Sınırı) bölümünde sergilenir

---

## 15. Cross-Skill Verification Gates (v2.3 YENİ)

Cureolex v2.6.0 SMP manifestinde 9 gate (G1-G9), medical-research v7.1 SKILL.md'sinde ~8 gate var. v2.3 ile bu gate'lerin **birlikte değerlendirildiği** çift-skill verification protokolü tanımlanır.

### 15.1. Birleşik Gate Matrisi

| Cureolex Gate | Medical-Research Karşılığı | Birleşik Test |
|---|---|---|
| **G1** 5210 şekli uyum | (yok — medical-research mevzuat üretmez) | Cureolex tek başına |
| **G2** 5210 maddi-anayasal | M-G3 İçtihat-doktrin temellendirmesi | Cureolex G2 + medical-research § 13 + § 9 entegre kontrol |
| **G3** Türk hukuk dili (R9) | (yok) | Cureolex tek başına |
| **G4** Anti-Pattern (27 madde) | M-G6 Atıf zinciri | Cureolex G4 + medical-research § 20 Vancouver citation cross-check |
| **G5** İçtihat + doktrin (R13) | M-G2 GRADE evidence + M-G5 Tier 0 sentez | Cureolex G5 + medical-research § 7 + § 9 entegre temellendirme |
| **G6** Uluslararası kaynak (R8/10/11/12) | M-G1 Connector kapsama + M-G7 Cross-jurisdiction | Cureolex G6 + medical-research § 6 + § 13.a-d entegre uyum |
| **G7** Epistemik dürüstlük | M-G8 Epistemik şeffaflık + bilgi boşlukları | **ÇİFT ZORUNLU** — her iki skill kendi sınırlarını ayrı raporlar; sonra birleştirilir |
| **G8** TBMM kapsam (Mod 8 etkin) | (yok — Mod 8 sadece cureolex) | Cureolex tek başına |
| **G9** EX_POST_EVALUATION kapsam denetimi (Mod 9 etkin) | M-G2 GRADE evidence + M-G7 real-world / cross-jurisdiction evidence + M-G8 epistemik şeffaflık | Cureolex G9 + medical-research §5 + §14.f + §19 + M-G8 birlikte PASS olmalı (Mod 9 klinik/HTA içeriyorsa sidecar `ex_post_metrics` zorunlu) |

### 15.2. Birleşik Gate Doğrulama Akışı

```
1. Cureolex G1-G9 her birini ayrı kontrol et → 9 boolean
2. Medical-Research M-G1-G8 her birini ayrı kontrol et → 8 boolean  
3. Birleşik tabloyu hesapla:
   - G1 (sadece cureolex) PASS gerekli
   - G2 + M-G3 → her ikisi PASS gerekli
   - G3 (sadece cureolex) PASS gerekli
   - G4 + M-G6 → her ikisi PASS gerekli
   - G5 + M-G2 + M-G5 → her üçü PASS gerekli
   - G6 + M-G1 + M-G7 → her üçü PASS gerekli
   - G7 + M-G8 → ÇİFT ZORUNLU; tek başına PASS yeterli değil
   - G8 → conditional (sadece Mod 8 etkinse)
   - G9 → conditional (sadece Mod 9 / EX_POST_EVALUATION etkinse); medical-research §5, §14.f, §19 ve epistemik belirsizlik etiketleriyle birlikte değerlendirilir; klinik/HTA içerikte sidecar `ex_post_metrics` eksikse G9 CONDITIONAL/FAIL döner
4. Genel hüküm:
   - Hepsi PASS → "BIRLEŞIK YAYINA HAZIR"
   - 1 FAIL (cureolex yanı) → ilgili cureolex remediation
   - 1 FAIL (medical-research yanı) → tekrar query veya kapsam genişletme
   - 1+ FAIL (her iki yanı) → tasarımı yeniden gözden geçir
```

### 15.3. Epistemik Dürüstlük Birleşik Raporu — Format

```markdown
## Çift Epistemik Dürüstlük Etiketi

### Medical-Research Tarafı (v7.1):
- Connector kapsamı: PubMed (2024-01..2026-05), ClinicalTrials.gov (n=42 hits), AdisInsight ✓
- Bilgi boşlukları: REGISTURK-LUNG 2025 yayını henüz girmemiş; Türk RWE bilgisi sınırlı
- Tier 0 sentez bulgusu: Cochrane CD0XXXX (2024 güncellemesi) + 1 NICE SR (TA779, 2024)
- GRADE özet: HIGH=3, MODERATE=5, LOW=2
- Tek-kaynak bulgular: § 19 pipeline verisinden 4 kalem AdisInsight tek kaynaklı

### Cureolex Tarafı (v2.3.0):
- Mevzuat MCP teyit: 5 birincil mevzuat + 3 yönetmelik teyit edildi
- Hukuki Veritabanları MCP teyit: 2 AYM kararı + 1 Danıştay kararı teyit
- YokTez MCP teyit: 3 ilgili tez bulundu
- Belirsiz yorum: 5210 Md. 4/c'nin "AB müktesebatı uyumu" yorumu doktrinde tartışmalı
- Mod kısıtlaması: COMPARATIVE_LAW modu Singapur HSA dahil edilmedi (cureolex kapsamı dışında veri)

### Birleşik Güven Seviyesi: MODERATE
- Öneri: Yetkili kurum ek danışma önerilir; SGK iddialarında saha doğrulaması yapılmalı; Singapur HSA verisi medical-research'ten ek query ile alınabilir.
```

---

## 16. Genişletilmiş Pipeline Kataloğu (v2.3 YENİ — P-9 ila P-16)

v2.2'de tanımlanan 8 pipeline'a (P-1 ila P-8) **8 yeni pipeline** eklenir. P-9 ile P-12, mevcut modların derinleştirilmesidir; P-13 ile P-16, **Mod 9 (EX_POST_EVALUATION)** ekseninde yeni pipeline'lardır.

### 16.1. P-9: EMA/FDA/TİTCK Paralel Ruhsat Mekaniklerinin Karşılaştırmalı Analizi

**Senaryo:** Üçlü paralel ruhsat rejimlerinin (FDA + EMA + TİTCK) mekanik karşılaştırması — Türkiye mevzuatının uyum/reform boşluklarının tespiti.

> ⚠️ **Kapsam dışı:** Belirli bir firmanın başvuru savunması/regülatör danışmanlığı cureolex kapsamı DIŞINDADIR. Burada yalnızca rejimlerin **karşılaştırmalı mevzuat analizi** yapılır.

**Akış:** medical-research § 13.a (FDA) + § 13.b (EMA) + § 13.c (TİTCK) → cureolex Mod 7 (COMPARATIVE_LAW) — *üçlü mekanik karşılaştırma + Türkiye-spesifik uyum/reform boşluğu* → carbon-html-report

**Specialty layer:** Regulatory + DrugIntelligence

### 16.2. P-10: TR Reliance Pathway Derinleşme

**Senaryo:** TR Reliance (Türkiye'nin uluslararası referans alma rejimi) için yeni yönetmelik veya tebliğ hazırlığı.

**Akış:** medical-research § 13.d (Reliance/WLA) + § 6 (Singapur HSA + Avustralya TGA + Swissmedic Reliance modelleri) → cureolex Mod 7 (COMPARATIVE_LAW) → Mod 1 (DRAFT) — *yeni TR Reliance Yönetmeliği*

**Specialty layer:** Regulatory + HTA

### 16.3. P-11: Biyobenzer Extrapolation / Geri Ödeme Politikası Reformu

**Senaryo:** Biyobenzer extrapolation ve geri ödeme kriterlerine ilişkin SUT/HTA politika reformu (genel düzenleme düzeyinde).

> ⚠️ **Kapsam dışı:** Belirli bir ürün için bireysel geri ödeme reddi savunması cureolex kapsamı DIŞINDADIR (→ onko-erisim/saglik-sigorta). Burada yalnızca **politika/mevzuat reformu** ele alınır.

**Akış:** medical-research § 7 (Cochrane biyobenzer SR) + § 8 (pivotal biyobenzer trial) + § 13.b (EMA biyobenzer rehberi) + § 14 (HTA biyobenzer fiyat müzakeresi) → cureolex Mod 1 (DRAFT) / Mod 6 (RIA) — *biyobenzer extrapolation/geri ödeme politikası reform metni*

**Specialty layer:** Regulatory + HTA (+ Hematology/Immunology — modaliteye göre)

### 16.4. P-12: ATMP (Advanced Therapy Medicinal Products) Mevzuat Çerçevesi

**Senaryo:** Gen tedavisi/hücre tedavisi/doku mühendisliği ürünleri için kapsamlı Türk mevzuat çerçevesi.

**Akış:** medical-research § 13.b (EMA ATMP Regulation 1394/2007) + § 13.a (FDA Cellular & Gene Therapy guidance) + § 9 (ASH/EHA ATMP guidelines) + § 18 (rare disease overlap) → cureolex Mod 1 (DRAFT) — *ATMP Yönetmeliği taslağı*

**Specialty layer:** Regulatory + RareDisease + Hematology

### 16.5. P-13: Tedavi Erişim Politikası Ex Post Değerlendirmesi (Mod 9)

**Senaryo:** SGK SUT EK-4/A güncellenmesi (örn. CAR-T eklenmesi) 24 ay sonra ex post değerlendirme.

**Akış:** medical-research § 5 (Türkiye RWE — CAR-T sonuçları) + § 14.f (SGK SUT 24 aylık veri) + § 19 (pipeline + competing therapies) → cureolex Mod 9 (EX_POST_EVALUATION) — *Etki Değerlendirme Raporu + revizyon önerisi*

**Specialty layer:** Hematology + HTA + DrugIntelligence

### 16.6. P-14: Klinik Araştırma Mevzuatı Ex Post (Mod 9)

**Senaryo:** Türk Klinik Araştırmalar Yönetmeliği güncellenmesi ardından 36 ay ex post; AB CTR uyumu denetimi.

**Akış:** medical-research § 5 (Türkiye klinik araştırma istatistikleri) + § 13.b (EU CTR) + § 13.c (TİTCK Klinik Araştırmalar Daire Başkanlığı raporları) + § 6 (karşılaştırmalı AB üye devleti uyumu) → cureolex Mod 9 (EX_POST_EVALUATION)

**Specialty layer:** Regulatory + MedAffairs

### 16.7. P-15: HTA Reform Politikası Ex Post (Mod 9)

**Senaryo:** Türkiye'de HTA kurumsallaşması ile ilgili 2024 mevzuat değişikliği — 24 ay sonra ex post.

**Akış:** medical-research § 14.a-e (NICE/CADTH/PBAC/IQWiG/HAS karşılaştırma) + § 14.f (SGK SUT entegrasyon) → cureolex Mod 9 (EX_POST_EVALUATION) — *HTA reform ex post*

**Specialty layer:** HTA + Regulatory

### 16.8. P-16: Promosyonel İletişim Mevzuatı Ex Post (Mod 9)

**Senaryo:** BTÜ-TF Yön. 29405 (Beşeri Tıbbi Ürünlerin Tanıtım Yönetmeliği) değişikliklerinin ex post değerlendirmesi.

**Akış:** medical-research § 15 (EFPIA/IFPMA/AİFD compliance benchmarks) + § 16 (MedAffairs operations data) + TİTCK Denetim Hizmetleri raporları (web fetch) → cureolex Mod 9 (EX_POST_EVALUATION)

**Specialty layer:** MedAffairs + Regulatory

---

## 17. Sürüm Uyumluluk Matrisi (v2.3 YENİ)

Medical-research + cureolex sürüm kombinasyonları için uyumluluk haritası.

### 17.1. Doğrulanmış Kombinasyonlar

| Cureolex ↓ / Medical-Research → | v6.0 | v7.0 | v7.1 | v7.2 (gelecek) |
|---|---|---|---|---|
| **v2.0** | ⚠ Eski API | ⚠ Eski API | ✓ Doğrulandı | ❓ Test edilmedi |
| **v2.1** | ⚠ Eski API | ⚠ Eski API | ✓ Doğrulandı | ❓ Test edilmedi |
| **v2.2** | ❌ Uyumsuz (R14 yok) | ❌ AdisInsight eksik | ✓ Doğrulandı | ❓ Test edilmedi |
| **v2.3** | ❌ Uyumsuz | ❌ Sidecar v2 yok | ✓ **Önerilen** | ⏳ Yeniden teyit gerekli |
| **v2.4** | ❌ Uyumsuz | ❌ Sidecar v2 yok | ✓ Doğrulandı | ⏳ Yeniden teyit gerekli |
| **v2.6.0** | ❌ Uyumsuz | ⚠ Sınırlı | ✓ **Doğrulandı (önerilen)** | ⏳ Yeniden teyit gerekli |

### 17.2. Geriye Uyumluluk Notları

- **Cureolex v2.0 + v2.1**: Medical-research'ün doğrudan çağrımı **resmi entegrasyon olmaksızın** mümkündür; R14 olmadığı için handoff manuel yapılır.
- **Cureolex v2.2**: R14 ilk sürüm; medical-research **v7.1 ile** çalışır. v6.0/v7.0'a graceful degrade desteklenmez (AdisInsight § 19 eksik).
- **Cureolex v2.3**: R14 v2 ile; sidecar JSON v2.3 şeması zorunlu; medical-research v7.1 ile minimum, v7.2 hazır olduğunda yeniden teyit gerekli.
- **Cureolex v2.4 – v2.6.0**: Kapsam saflaştırma (v2.4 — bireysel hak arama → `saglik-sigorta`/`onko-erisim`) + programatik veri katmanı (v2.5) + kapsam/routing ve R14 entegrasyon tutarlılığı (v2.5.3–v2.6.0) eklendi; medical-research **v7.1 ile doğrulanmıştır**; sidecar JSON v2.3.1 şeması; Mod 9 (EX_POST_EVALUATION) için `ex_post_metrics` alanı zorunlu; **v2.6.0 ile şema-doğrulanan üretim test/harness katmanı** (`schemas/` JSON Schema + `tests/` davranış süitleri + `source_registry.yaml` + `programmatic_source_healthcheck.yaml`) eklendi. v7.2 hazır olduğunda Bölüm 9 composability sözleşmesi yeniden teyit edilmelidir.

### 17.3. Versiyon Sapma Yönetimi (Graceful Degradation)

```
Cureolex v2.3 + medical-research v7.0 detect →
  ├─ § 19 (DrugIntelligence) AdisInsight olmadan eksik kalır
  ├─ § 5 Synapse.org olmadan dar
  ├─ Sidecar JSON v2.0 (eski) ile çalışır; v2.3 alanları boş geçer
  └─ Uyarı: "Medical-research v7.1+ önerilir; mevcut sürümde 2 specialty bölümü sınırlı"
  
Cureolex v2.3 + medical-research v7.2 detect (gelecek) →
  ├─ Yeniden teyit zorunlu (R14 §17.3'te schedule)
  ├─ Yeni alanlar (varsa) sidecar JSON v2.3+ ile uyumsuz olabilir
  └─ Uyarı: "Sürüm uyumluluğu test edilmedi; pilot kullanım önerilir"
```

### 17.4. Sürüm Senkronizasyonu Önerileri

| Cureolex sürüm | Medical-research minimum gerekli | Medical-research önerilen | Notlar |
|---|---|---|---|
| 2.0.0 | n/a | 7.1 | Manuel handoff |
| 2.1.0 | n/a | 7.1 | Manuel handoff |
| 2.2.0 | 7.1 | 7.1 | R14 ilk sürüm |
| 2.3.0 | 7.1 | 7.1+ | Sidecar v2.3 |
| 2.4.0 | 7.1 | 7.1+ | Kapsam saflaştırma (bireysel hak arama dışlandı); medical-research v7.1 ile doğrulandı |
| 2.6.0 | 7.1 | 7.1+ | Scope Guard + G1-G9 + sidecar v2.3.1; Mod 9 için `ex_post_metrics` zorunlu; medical-research v7.1 ile doğrulandı; **üretim test/şema harness** (schemas/ + tests/ + source_registry) |

---

## 18. v2.3 Genişletme Özet Sayacı

R14 v2.3 ile ilave edilen yeni bölüm satır sayısı:

| Bölüm | İçerik | Tahmini satır |
|---|---|---|
| §12 | § × Mod Matrix | ~150 |
| §13 | Specialty Layer × Mod Matrix | ~110 |
| §14 | Sidecar JSON Schema v2 | ~250 |
| §15 | Cross-Skill Verification Gates | ~100 |
| §16 | Genişletilmiş Pipeline (P-9 ila P-16) | ~150 |
| §17 | Sürüm Uyumluluk Matrisi | ~80 |
| **TOPLAM** | | **~840 satır eklendi** |

R14 v2.2: 969 satır → R14 v2.3: ~1.800 satır (yaklaşık iki katı).

---

## 19. Operasyonel Entegrasyon — Adım 0.5 Domain Classifier Sözlük Senkronizasyonu (v2.3-r1 YENİ)

Medical-research'ün Adım 0.5 Domain Classifier'ı, gelen sorguyu **sözlük tabanlı sinyal tespiti** ile dokuz eksen (0.5.A onkoloji, 0.5.B hematoloji, 0.5.C regulatory, 0.5.D HTA, 0.5.E medical affairs, 0.5.F immunology, 0.5.G neurology, 0.5.H rare disease, 0.5.I drug intelligence) üzerinde tarar; tetiklenen eksenlerin specialty bölümlerini (§11-§19) çıktıya enjekte eder.

**Cureolex için kritik tespit:** Enriched query üretirken bu sözlüklerin **doğru kelimelerini** içermek gerekir. Aksi halde medical-research ilgili specialty katmanını çağırmaz ve cureolex çıktısının çekirdek dayanağı eksik kalır.

### 19.1. Mod-Bazlı Sözlük Tetikleyici Haritası

Aşağıdaki tablo, **her cureolex modu için** medical-research'te hangi domain classifier ekseninin tipik olarak tetiklenmesi gerektiğini gösterir:

| Cureolex Modu | Tipik Tetiklenmesi Gereken Eksenler | Mod'un Sorgu Bağlamı |
|---|---|---|
| Mod 1 DRAFT | 0.5.C **(her zaman)** + 0.5.A/B/F/G/H (konuya göre) + 0.5.I (yeni mevzuat ileriye dönükse) | Yeni mevzuat hazırlığı — ruhsat + klinik alan + pipeline |
| Mod 2 AMEND | 0.5.C **(her zaman)** + 0.5.I (pipeline güncel durumu için) + ilgili klinik eksen | Mevcut mevzuat değişikliği |
| Mod 3 ANALYZE | 0.5.C + 0.5.D + 0.5.I (ana üçlü) + ilgili klinik eksen | Yürürlükteki mevzuatın analizi |
| Mod 4 COMPLY | 0.5.C **+ 0.5.E (MedAffairs zorunlu — compliance stack)** + ilgili klinik | Tanıtım mevzuatı reform uyumu (BTÜ-TF Yön. 29405) |
| Mod 5 OPINE | 0.5.D **(her zaman — HTA delili)** + 0.5.C + ilgili klinik eksen + 0.5.H (nadir hastalık görüşlerinde) | Reform sürecinde HTA/SUT politika görüşü, TBMM komisyonu bilimsel mütalaası, yönetmelik değişikliği paydaş görüşü |
| Mod 6 RIA | 0.5.D **(her zaman — BIA/ICER)** + 0.5.C + 0.5.I (pipeline projeksiyonu) | BEF/DEA paketi |
| Mod 7 COMPARATIVE_LAW | 0.5.C **(her zaman)** + 0.5.D + ilgili klinik eksen | Karşılaştırmalı hukuk analizi |
| Mod 8 TBMM_KANUN_TEKLIFI | 0.5.A-I **(tümü — kapsam genişliğine göre)** | TBMM kanun teklifi (kapsamlı reform) |
| Mod 9 EX_POST_EVALUATION | 0.5.C **+ 0.5.D + 0.5.I** + ilgili klinik | Yürürlükteki mevzuatın ex post değerlendirmesi |

### 19.2. Eksen-Spesifik Tetik Kelime Listeleri (Cureolex Enriched Query'sinde Kullanılması Gereken)

#### 19.2.A. Onkoloji ekseni (0.5.A) tetikleme — Cureolex tarafı

Onkoloji ile ilgili mevzuat hazırlığında enriched query'ye şu kelimelerden **en az 2-3 tanesi** girmelidir:

- **Konu adlandırma:** kanser, tümör, neoplazi, malign, karsinom, onkoloji, metastaz, evre, TNM, AJCC
- **Endpoint adlandırma:** ORR, PFS, OS, DFS, EFS, DOR, RECIST, iRECIST, MRD
- **Tedavi modalitesi:** immunoterapi, ICI, anti-PD-1/PD-L1/CTLA-4, ADC, antibody-drug conjugate, TKI, CDK4/6, PARP, hedefli tedavi
- **Biomarker:** PD-L1, CPS, TPS, TMB, MSI, MMR, dMMR, MSI-H, HRD, BRCA, HER2, EGFR, ALK, ROS1, NTRK, KRAS-G12C, BRAF
- **Tedavi sınıfı:** pembrolizumab, nivolumab, atezolizumab, durvalumab, ipilimumab, trastuzumab, T-DXd, sacituzumab, olaparib, palbociklib
- **Kılavuz adı:** NCCN, ESMO, ASCO, SIOG, EORTC, SABCS, ESMO-MCBS, ASCO Value Framework
- **Yerel tümör tipi:** NSCLC, SCLC, TNBC, HR+ meme, CRC, HCC, RCC, GBM, HNSCC, melanom, glioblastom

> **Operasyonel kural:** Cureolex Mod 5 OPINE veya Mod 1 DRAFT bağlamında, "akciğer kanseri tedavisinde immünoterapi geri ödemesi" gibi bir Türkçe konuyu enriched query'ye geçirirken **mutlaka** NCCN/ESMO/PFS/OS/ICI gibi metric ve kılavuz adlarını ekleyin. Aksi halde 0.5.A tetiklenmez ve § 11 (onkoloji genişletilmiş) çıkmaz.

#### 19.2.C. Regulatory Sciences ekseni (0.5.C) tetikleme

Bu eksen **cureolex'ın neredeyse tüm modlarında ◆ ZORUNLU** olduğu için enriched query her zaman bu kelimelerle zenginleştirilmelidir:

- **Ruhsat süreci:** ruhsat başvurusu, marketing authorization, MAA, MAH, FDA approval, EMA approval, TİTCK onay
- **Özel onay yolları:** accelerated approval (AA), conditional marketing authorization (CMA), breakthrough therapy (BTD), priority review (PR), orphan drug designation (ODD), PRIME, Project Orbis, adaptive pathway, fast track (FT)
- **Müzakere mekaniği:** AdComm, ODAC, CHMP, CHMP opinion, EPAR, briefing document, Type A/B/C meeting, scientific advice (SA), SAWP, protocol assistance
- **Dosya yapısı:** CTD, eCTD, Module 1/2/3/4/5, IND, BLA, NDA, 505(b)(1), 505(b)(2)
- **Post-marketing:** REMS, RMP, post-marketing commitment (PMC), post-marketing requirement (PMR), PSUR, PBRER, DSUR
- **Pharmakovijilans:** signal detection, FAERS, EudraVigilance, WHO VigiBase
- **Türkiye:** TİTCK, beşeri tıbbi ürünler yönetmeliği, klinik araştırmalar yönetmeliği

#### 19.2.D. HTA ekseni (0.5.D) tetikleme

Mod 5 OPINE + Mod 6 RIA + Mod 9 EX_POST'ta ◆ ZORUNLU. Enriched query:

- **HTA terminolojisi:** HTA, health technology assessment, sağlık teknolojisi değerlendirmesi (STD), maliyet etkililik, cost-effectiveness, cost-utility (CUA), budget impact (BIA), bütçe etkisi
- **Metrik:** ICER, incremental cost-effectiveness ratio, QALY, DALY, NMB, net monetary benefit, CEAC, cost-effectiveness acceptability curve, PSA, probabilistic sensitivity analysis
- **Ajanslar:** NICE, NICE TA, CADTH, PBAC, IQWiG, G-BA, Nutzenbewertung, HAS, AMNOG, ICER
- **Yapı:** Markov model, partitioned survival model (PSM), DES, discrete event simulation, time horizon, discount rate
- **Erişim mekaniği:** managed entry agreement, MEA, outcome-based agreement, OBA, risk-sharing scheme
- **Türkiye:** SGK SUT, MEDULA, geri ödeme komisyonu, fiyat tavanı, bedel iadesi

#### 19.2.E. Medical Affairs ekseni (0.5.E) tetikleme

Mod 4 COMPLY'de ◆ ZORUNLU (compliance stack). Enriched query:

- **MSL:** medical science liaison, MSL, medical advisor, field medical, scientific engagement, KOL engagement
- **Advisory board:** ad board, advisory board, MLR-compliant, MLR komitesi
- **Compliance:** EFPIA, IFPMA, FCPA, Sunshine Act, ToV (Transfer of Value), AİFD, İEİS, GPP3, ICMJE, PSC
- **HCP etkileşim:** speaker bureau, CME, continuing medical education, IIS, ISR, investigator-initiated study
- **Türkiye:** BTÜ-TF Yönetmeliği 29405, TİTCK Tanıtım Mevzuatı, AİFD Etik İlkeleri

#### 19.2.F-H. Diğer Eksenler (kısaca)

| Eksen | Kritik tetik kelimeleri |
|---|---|
| **0.5.B Hematoloji** | lösemi, AML, ALL, CLL, lenfoma, DLBCL, MM, MDS, WHO-HAEM5, ELN-2022, IPSS-M, R-ISS, CAR-T, BTK, ibrutinib, venetoclax, BCMA, bispesifik |
| **0.5.F Immunology** | romatoid artrit, RA, PsA, AS, axSpA, SLE, Crohn, UC, atopik dermatit, JAK, IL-17, IL-23, TNF, EULAR, ACR, GRAPPA |
| **0.5.G Neurology** | MS, RRMS, SPMS, PPMS, multiple sclerosis, ALS, Alzheimer, Parkinson, SMA, migren, DMT, ECTRIMS, AAN |
| **0.5.H Rare Disease** | nadir hastalık, rare disease, ultra-rare, orphan, ODD, OMP, Orphanet, OMIM, GARD, EAP, expanded access |
| **0.5.I Drug Intelligence** | pipeline, MoA, mechanism of action, AdisInsight, Synapse, M&A, deal, milestone, PDUFA, BLA, NDA, in-licensing, LoE, loss of exclusivity, patent cliff, first-in-class, biosimilar |

### 19.3. Multi-Domain Eylem Kuralı (Adım 0.5.J ile Uyum)

Medical-research v7.1'in 0.5.J kuralı: birden fazla eksen tetiklenebilir (cluster). Cureolex tarafında **5 primary use case cluster** §13.2'de tanımlanmıştı. Bu cluster'lar 0.5.J ile uyumludur:

| Cluster (R14 §13.2) | Tetiklenen Eksenler (0.5.x) | Tipik Cureolex Modu |
|---|---|---|
| Klinik onko-heme | 0.5.A + 0.5.B + 0.5.H | Mod 1, 5 |
| Regulatory core | 0.5.C + 0.5.I | Mod 1, 2, 3, 8 |
| Market access | 0.5.D + 0.5.C + 0.5.E | Mod 5, 6, 9 |
| Therapeutic specialty | 0.5.F + 0.5.G | Mod 3, 5 |
| Compliance + Audit | 0.5.E + 0.5.C | Mod 4, 5 |

### 19.4. Enriched Query Üretiminde Sözlük Tarama Adımı

Cureolex, medical-research'e enriched query göndermeden önce şu adımları uygular:

```
1. Kullanıcı sorgusunu Türkçe-İngilizce çift dilde paraleli tara
2. Mevcut Cureolex modunu tespit et (Mod 1-9)
3. Mod-tipik tetiklenmesi gereken eksen(ler)i §19.1 tablosundan al
4. Eksen(ler)in §19.2 tetik kelime listesinden mevcut sorguya 
   eksik olanları enriched query'ye **ekleme** (kullanıcının orijinal
   sorgusunu DEĞİŞTİRMEZ; sadece arka planda zenginleştirilmiş
   varyantı ekler)
5. Enriched query'yi medical-research'e gönder; sidecar JSON'da 
   `specialty_layer_activations` alanında hangi eksen(ler)in 
   tetiklendiğini gör
6. Eğer beklenen eksen tetiklenmedi ise:
   - Sözlüğe daha güçlü tetik kelimesi ekle (bu §19.2'deki listeden)
   - VEYA medical-research'e açık layer talebi (requested_layers 
     parametresi) gönder
```

### 19.5. Örnek Enriched Query — Mod 5 OPINE'da SUT Pembrolizumab Geri Ödeme Politikası Reformu

```json
{
  "original_query_tr": "SUT pembrolizumab MSI-H/dMMR endometriyum kanseri geri ödeme kriterini kanıt temelli reforme eden tebliğ taslağı için bilimsel reform mütalaası nasıl hazırlanır?",
  
  "enriched_query_for_medical_research": {
    "main_query": "Pembrolizumab MSI-H/dMMR endometrial cancer adjuvant + 2L treatment efficacy, ICER cost-effectiveness, SGK Turkey reimbursement comparison",
    
    "explicit_layer_request": ["oncology", "regulatory", "hta", "rare_disease"],
    
    "domain_classifier_pre_seed_keywords": {
      "0.5.A_onkoloji": ["MSI-H", "dMMR", "endometriyum kanseri", "endometrial cancer", "pembrolizumab", "anti-PD-1", "PD-L1", "CPS", "PFS", "OS", "ORR", "RECIST", "NCCN", "ESMO", "ESMO-MCBS"],
      
      "0.5.C_regulatory": ["FDA approval", "EMA approval", "TİTCK", "accelerated approval", "AA", "Project Orbis", "breakthrough therapy", "BTD", "MAH", "MAA", "post-marketing commitment", "PMC", "EPAR"],
      
      "0.5.D_hta": ["NICE TA", "CADTH", "PBAC", "IQWiG", "ICER", "QALY", "cost-effectiveness", "budget impact", "BIA", "SGK SUT", "geri ödeme komisyonu", "fiyat tavanı"],
      
      "0.5.H_rare_disease": ["MSI-H endometrial — relatif nadir alt-popülasyon", "ultra-rare biomarker subset", "orphan drug designation"]
    },
    
    "cureolex_legal_context": {
      "mode": "OPINE",
      "primary_legislation": ["SGK SUT", "5510 SK Md. 63", "3359 SK Sağlık Hizmetleri Temel Kanunu"],
      "constitutional_basis": ["Md. 17", "Md. 56", "Md. 90/5"],
      "international_treaties": ["ICESCR Md. 12 + AAAQ", "AİHS Md. 2 + 8"],
      "yargi_ictihat_focus": ["AYM sağlık hakkı ve etkili başvuru içtihat sinyali — bireysel başvuru formu DEĞİL", "Danıştay SUT/geri ödeme kriterleri belirlilik ve ölçülülük içtihadı", "AİHM sağlık hizmetine erişim ve pozitif yükümlülük içtihadı"],
      "comparative_law_targets": ["NICE TA: MSI-H tümör pembrolizumab", "G-BA AMNOG değerlendirmesi"],
      "scope_guard": {
        "policy_reform_only": true,
        "individual_application_drafting": false,
        "individual_sgk_denial_defense": false
      }
    },
    
    "requested_sections_priority": {
      "MANDATORY": ["§1", "§4", "§5", "§7", "§9", "§11", "§13", "§14", "§19"],
      "RECOMMENDED": ["§2", "§3", "§6", "§15"],
      "OPTIONAL": ["§8", "§10", "§17", "§18", "§20"]
    },
    
    "output_format": "Format E (Oncology Extended)",
    "citation_format": "Vancouver",
    "epistemic_dual_label": true,
    "version_compat": {
      "medical_research_min": "7.1",
      "cureolex": "2.6.0",
      "sidecar_schema": "2.3.1"
    }
  }
}
```

Bu enriched query, Adım 0.5.A + 0.5.C + 0.5.D + 0.5.H'yi **garanti** tetikler; §11 + §13 + §14 + §18 specialty bölümlerini çıktıya enjekte eder.

---

## 20. Reverse Channel — Medical-Research'ten Cureolex'a Feedback Sözleşmesi (v2.3-r1 YENİ)

R14 v2.2-v2.3 boyunca veri akışı **cureolex → medical-research → cureolex** şeklindeydi: cureolex enriched query gönderir, medical-research çıktı + sidecar üretir, cureolex tüketir. v2.3-r1 ile **medical-research'ün çıktıya iliştirdiği geri bildirim sinyalleri** sözleşmesi tanımlanır.

### 20.1. Reverse Channel'ın Gerekliliği

Medical-research, sorguya cevap üretirken çeşitli **belirsizlik, kapsam dışılık, alternatif yorum** durumlarıyla karşılaşır:

- **Belirsizlik:** "Bu konuda yüksek kanıt yok; Türkiye RWE eksik" gibi epistemik sınır
- **Kapsam dışılık:** "Bu sorgu medical-research'ün kapsamının dışında; cureolex için bağlamsal anlam yok"
- **Alternatif yorum:** "Sorgu pembrolizumab adjuvan ile metastatik arasında belirsiz; iki ayrı çıktı önerilir"
- **Retry önerisi:** "0.5.A onkoloji tetiklendi ama 0.5.D HTA da gerekli; HTA layer eklensin"

Bu sinyaller cureolex'ın çıktısının kalitesini etkiler. **Reverse channel** olmadan cureolex bu nüansları kaybeder.

### 20.2. Sidecar JSON `reverse_signals` Alanı

Sidecar JSON v2.3-r1'de yeni alan eklenir:

```json
{
  "schema_version": "2.3.1",
  ...
  "reverse_signals": {
    "uncertainty_flags": [
      {
        "section": "§14.f Türkiye SGK SUT",
        "type": "data_gap",
        "description": "SGK 2025 yılı MEDULA istatistikleri henüz public değil; 2024 verisi ile sınırlı kalındı",
        "impact_on_cureolex": "Mod 9 ex post için 12 aylık veri eksik; 2024 baz alındı not edildi"
      },
      {
        "section": "§13.c TİTCK Pozisyonu",
        "type": "single_source",
        "description": "TİTCK ruhsat tarihi sadece bir kaynaktan teyit edildi (resmî portal)",
        "impact_on_cureolex": "Kritik karar verirken ek doğrulama önerilir"
      }
    ],
    
    "out_of_scope_flags": [
      {
        "topic": "Hekim malpraktis bireysel davası",
        "reason": "medical-research'ün scope'u clinical/pharma research; bireysel hukukî dosya kapsamı dışında",
        "recommendation_for_cureolex": "Bu bölüm için lex-mercator veya Hukuki Veritabanları MCP doğrudan çağrılmalı"
      }
    ],
    
    "retry_triggers": [
      {
        "missing_layer": "0.5.H Rare Disease",
        "rationale": "MSI-H endometrial relatif nadir biomarker subset; rare disease layer açılarak orphan drug designation ve EAP yolları taranmalı",
        "suggested_keywords": ["MSI-H endometrial — ultra-rare biomarker subset", "tumor-agnostic ODD"]
      }
    ],
    
    "alternative_interpretations": [
      {
        "ambiguity": "Pembrolizumab MSI-H endometriyum — adjuvan vs metastatik 1L vs 2L",
        "interpretation_taken": "Adjuvan KEYNOTE-A18 + metastatik 2L KEYNOTE-158 birleşik incelendi",
        "alternative_paths": [
          "Sadece adjuvan KEYNOTE-A18 için ayrı çıktı",
          "Sadece metastatik (1L + 2L kombine) için ayrı çıktı"
        ]
      }
    ],
    
    "confidence_breakdown": {
      "overall_grade": "MODERATE",
      "high_grade_sections": ["§7", "§9"],
      "moderate_grade_sections": ["§5", "§13.c", "§14.f"],
      "low_grade_sections": ["§19"]
    }
  }
}
```

### 20.3. Cureolex'ın Reverse Signal İşleme Protokolü

```
1. Sidecar JSON yüklendiğinde, `reverse_signals` alanını ÖNCELİKLE oku
2. `uncertainty_flags` her birini:
   - Cureolex çıktısının ilgili bölümüne FOOTNOTE olarak ekle
   - Bölüm 9 "Bilgi Sınırı Uyarısı" bölümünde birleşik özetle
3. `out_of_scope_flags` her birini:
   - Kullanıcıya net olarak göster: "Bu konu için ek skill çağırılması önerilir: [X]"
   - Eğer önerilen skill mevcut composability zincirinde varsa otomatik çağrı yap (örn. lex-mercator)
4. `retry_triggers` her birini:
   - Eğer eksik layer kritik ise (◆ zorunlu Mod 5 OPINE'da 0.5.D), 
     enriched query'yi güncelleyerek medical-research'i tekrar çağır
   - Aksi halde "Önerilen ek katman: [X]; isteğe bağlı çağrılabilir" notu ekle
5. `alternative_interpretations` her birini:
   - Cureolex çıktısının Yönetici Özeti bölümünde "Bu çıktı [seçim] 
     yorumuyla üretilmiştir; alternatif yorumlar için tekrar sorgu öneririz" notu
6. `confidence_breakdown` çıktısının §15.3 (Çift Epistemik Dürüstlük 
   Birleşik Raporu) bölümünde sergilenir
```

### 20.4. Reverse Channel ile Cross-Skill Verification (R14 §15 Güncelleme)

§15.2 birleşik gate matrisine ek bir geçit eklenir:

> **G-Reverse:** Sidecar JSON'da `reverse_signals` mevcut + boş olmayan herhangi bir alt-alan (uncertainty_flags veya out_of_scope_flags veya retry_triggers) varsa, cureolex çıktısının Yönetici Özeti veya Bölüm 9 (Bilgi Sınırı) bölümünde **görünür biçimde** sergilenmiş mi? PASS/FAIL.

### 20.5. Reverse Channel — Pratik Faydaları

- **Şeffaflık:** Cureolex kullanıcısı, medical-research'ün belirsizliklerini doğrudan görür
- **Yetki sınırı netliği:** Hangi bölüm medical-research yetkisinde, hangi bölüm cureolex yetkisinde net olur
- **Tekrar sorgu mekanizması:** Eksik katman varsa otomatik retry mümkün olur
- **Çift epistemik dürüstlük birleşik etiket:** R14 §15.3 raporu reverse signals ile zenginleşir

---

## 21. v2.3-r1 Genişletme Özet Sayacı (GÜNCELLENDİ)

R14 v2.3-r1 ile ilave edilen yeni bölüm satır sayısı:

| Bölüm | İçerik | Tahmini satır |
|---|---|---|
| §12 (kalibre) | § × Mod Matrix — gerçek bölüm adlarına göre düzeltme | ~50 düzeltme |
| §13 | Specialty Layer × Mod Matrix | ~110 (v2.3) |
| §14 | Sidecar JSON Schema v2 | ~250 (v2.3) |
| §15 | Cross-Skill Verification Gates | ~100 (v2.3) |
| §16 | Genişletilmiş Pipeline (P-9 ila P-16) | ~150 (v2.3) |
| §17 | Sürüm Uyumluluk Matrisi | ~80 (v2.3) |
| **§19 (YENİ v2.3-r1)** | **Adım 0.5 Domain Classifier Sözlük Senkronizasyonu** | **~200** |
| **§20 (YENİ v2.3-r1)** | **Reverse Channel — Medical-Research'ten Cureolex'a Feedback Sözleşmesi** | **~150** |
| **TOPLAM** | | **~1.090 satır eklendi (v2.2 → v2.3-r1)** |

R14 v2.2: 969 satır → R14 v2.3: ~1.800 satır → **R14 v2.3-r1: ~2.060 satır.**

---

**Gelecek sürüm önerileri (v2.3+):**

- Medical-research v7.2 ile yeniden teyit
- Sidecar JSON şemasının Türkçe ek alanlarla genişletilmesi (`turkish_legislation_refs`, `yargi_ictihat_chain`)
- ATC kodu + ICD-11 entegre dispatch tablosu
- Promo-censor skill ile üçlü entegrasyon (medical-research § 15 + cureolex Mod 4 + promo-censor) — materyal PASS/FAIL hükmü promo-censor'a aittir; cureolex yalnızca tanıtım mevzuatı reform metni girdisi sağlar
- Onko-erisim skill ile entegrasyon (yalnızca toplulaştırılmış SUT/HTA reform politika sinyali; bireysel erişim/P-3 KAPSAM DIŞI)
- Auto-orchestration: cureolex'tan medical-research'e otomatik request üretimi + sidecar otomatik tüketim (cureolex v2.4 hedefi)

---

**Bu dosya, Cureolex v2.6.0 motorunda kullanılan, şablon/entegrasyon kökeni v2.3 olan medical-research bidirectional integration katmanıdır. Operasyonel uygulama için Bölüm 6 karar ağacı, Bölüm 4 mod-bazlı handoff protokolleri ve Bölüm 12-17 derin entegrasyon bölümleri bağlayıcıdır. Kalite kontrol için Bölüm 10.1 + Bölüm 15.2 zorunlu okumadır.**
