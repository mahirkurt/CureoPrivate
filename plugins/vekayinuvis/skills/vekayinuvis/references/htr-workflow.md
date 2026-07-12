# HTR İş Akışı — eScriptorium Üzerinden Yazma Transkripsiyonu

> `vekayinuvis` skill'inin **MANUSCRIPT_TRANSCRIBE** modunda etkinleşen ek
> referans. Ottoman Archives MCP'nin eScriptorium tool ailesi üzerinden bir
> Osmanlıca/Arapça yazmanın IIIF manifest'inden alınarak segmentlenmesi,
> Handwritten Text Recognition (HTR) ile transkribe edilmesi ve insan
> revizyonu için ihraç edilmesinin tam protokolünü sunar.

---

## 1. eScriptorium Hakkında — Kısa Tanıtım

**eScriptorium**, Paris Sciences et Lettres bünyesinde geliştirilen, açık
kaynaklı, IIIF-uyumlu bir el-yazması transkripsiyon platformudur. **Kraken
HTR motoru** ile çalışır ve özellikle Arap-Osmanlı yazıları için **OpenITI**
ve **RASAM** projeleri kapsamında eğitilmiş modeller mevcuttur. Ottoman
Archives MCP sunucusu, bir eScriptorium örneğine kimlik doğrulamalı API
köprüsü kurarak 10 ayrı tool ile dışarıdan kontrol edilmesine olanak
tanır.

> **Ön koşul.** eScriptorium MCP tool'ları yalnızca sunucu konfigürasyonunda
> `ESCRIPTORIUM_BASE_URL` + token tanımlıysa çalışır. Kullanıcı (Mahir Bey)
> kendi eScriptorium hesabı veya kurumsal hesap üzerinden bağlantı kurmuş
> olmalıdır. Bağlantı yoksa, skill, transkripsiyon yerine IIIF manifest +
> Vision-tabanlı satır-okuma alternatifine geçer (aşağıda § 7).

---

## 2. Tool Envanteri (10 eScriptorium Tool)

| Tool | İşlev | Tipik kullanım anı |
|------|-------|---------------------|
| `ottoman_escriptorium_list_projects` | Projeleri listele | Workflow başlangıcı |
| `ottoman_escriptorium_list_documents` | Belgeleri listele (proje filtreli) | Mevcut işi kontrol |
| `ottoman_escriptorium_list_models` | Segmentation + HTR modellerini listele | Model seçimi öncesi |
| `ottoman_escriptorium_create_document` | Yeni belge oluştur | Yeni yazma yüklendiğinde |
| `ottoman_escriptorium_import_iiif` | IIIF manifest'ten sayfa import | Belge oluşturulduktan hemen sonra |
| `ottoman_escriptorium_segment` | Satır + bölge segmentasyonu tetikle | Import tamamlandıktan sonra |
| `ottoman_escriptorium_transcribe` | HTR koş (recognition) | Segmentation tamamlandıktan sonra |
| `ottoman_escriptorium_list_tasks` | Async task'ları listele | Polling için |
| `ottoman_escriptorium_get_document` | Belge + sayfalar + layer'lar | Sonuç çekme |
| `ottoman_escriptorium_get_transcription` | Belirli bir layer'ın metnini al | Final export |

> **Async mantığı.** `segment` ve `transcribe` çağrıları arka planda görev
> başlatır (task ID döner) ve hemen geri döner. Çalışmanın bitip bitmediği
> `list_tasks` ile polling yapılarak veya `get_document` ile sayfa
> sayısı/transcription line count kontrolüyle doğrulanır. Tipik sürelər:
> küçük yazma (10–30 folio) için segmentation 1–3 dk, transkripsiyon 5–15
> dk. Uzun yazmalar (200+ folio) yarım saatten birkaç saate çıkabilir.

---

## 3. Standart 7-Adımlı İş Akışı

### Adım 0 — Hedef yazmayı tespit et (IIIF veya resmî katalog)

Yazma **iki ayrı yolla** tespit edilebilir; ikisi de Adım 1'e aynı şekilde
akar (bir IIIF manifest'i veya bir devarsiv sayfa taraması, HTR pipeline'ının
girdisi olabilir):

```text
(a) IIIF yolu:
ottoman_search_iiif(query="risale-i tıbbiye", sources=["gallica","internet_archive","princeton"])
↓
ottoman_fetch_iiif_manifest(manifest_url="<adayın manifest URL'i>")
↓
[Manifest metadata doğrulanır: dil, tarih, hat türü, folio sayısı]

(b) Resmî katalog (devarsiv) yolu — BOA/BCA/Diplomatik/ATASE el yazmaları:
devarsiv_search("<konu/terim>", arsiv=2)  → resmî katalog kayıtları (item_id/hash)
↓
devarsiv_get_belge_image(item_id, hash, arsiv=2) → sayfa taraması ImageContent
   (satın-alma durumundan bağımsız önizleme; satın-alınmışsa bkz. §7 devarsiv çift-motor)
↓
[Görüntü, IIIF manifest sayfası yerine doğrudan eScriptorium'a import edilebilir
 veya §7'deki devarsiv çift-motor OCR/HTR yoluna (Transkribus+eScriptorium) yönlendirilir]
```

> **Manifest seçim kriterleri (IIIF yolu)**: (i) tek yazma olmalı (compilation
> manifest değil) — değilse `ottoman_browse_iiif_collection` ile parçalanmalı;
> (ii) folio görselleri yüksek çözünürlük (≥ 2000 px en uzun kenar) olmalı;
> (iii) telif/kullanım hakkı `rights` veya `attribution` alanında açık
> belirtilmiş olmalı.

### Adım 1 — eScriptorium projeleri ve modelleri keşfet

```text
ottoman_escriptorium_list_projects()
ottoman_escriptorium_list_models()
```

Çıktıdan **uygun projeyi** (yoksa create_document parametresinde belirt) ve
**uygun model çiftini** (bir segmentation modeli + bir recognition modeli)
seç. Kraken modellerine bakarken model adlarında geçen anahtar kelimeleri
ara:

- **Segmentation**: `general`, `manuscript`, `arabic`, `ottoman`, `RASAM`
  ifadelerini içerenler — Arap-Osmanlı satır geometrisine eğitilmiştir.
- **HTR (recognition)**: `OpenITI_arabicPrint`, `RASAM_manuscript`,
  `ottoman_print_v2`, `mawred`, `naskh`, `nastaliq`, `diwani` gibi etiketler.

### Adım 2 — Yazma türü ↔ Model eşleştirmesi

| Yazma tipi / Hat | Tipik dönem | Önerilen recognition modeli |
|------------------|-------------|---------------------------------|
| **Matbu Osmanlıca** (Müteferrika sonrası matbaa baskı) | 1729 sonrası | `OpenITI_arabicPrintBeta_v1.5.0` veya benzeri matbu model |
| **Nesih** (resmi yazışma, salname, ilm-i hâl, divan kâtipliği) | XV–XX yy. | `RASAM_manuscript` veya genel Arap nesih modeli |
| **Rik'a** (XIX. yy. divan ve özel yazışma) | 1850 sonrası | Henüz uzmanlaşmış model yetersiz — `RASAM` + ağır insan revizyonu |
| **Ta'liq / Nesta'liq** (edebiyat, şiir, divan-ı hümâyûn'un bazı kalemleri) | XV–XIX yy. | Farsça nesta'liq modeli + insan revizyonu |
| **Divânî / Celî divânî** (ferman, berat) | XV–XX yy. | Şu an güvenilir model yok — fine-tuning veya manuel transkripsiyon |
| **Siyâkat** (hazine kalem yazısı, tahrir defteri, ruznamçe) | XIV–XIX yy. | Şu an güvenilir model yok — uzman insan paleografi gerekir |
| **Kûfî / Mağribî** (çok eski yazma, ender) | öncesi | Genel Arap modelleri uygunsuz; özel uzman gerekir |

> **Önemli uyarı.** **Siyâkat** ve **celî divânî**, paleografi uzmanları
> bile zaman alarak okuduğu özel kalem yazılarıdır. Bu hatlarda HTR çıktısı
> yaklaşık bir okuma olarak değerlendirilmeli, asla doğrudan yayınlanmamalı.

#### 2.1 devarsiv çift-motor için Transkribus model seçim tablosu (K3)

Adım 0'da **(b) devarsiv yolu** izlendiyse (BOA/BCA belgesi, eScriptorium'a
değil doğrudan `devarsiv_ocr_belge`/`devarsiv_ocr_archive_pages`/`devarsiv_ocr_submit`'e
`engine=` parametresiyle gidilir), model seçimi eScriptorium'un kendi Kraken
modelleri yerine **Transkribus** tarafında yapılır:

| Belge türü | Model | CER | Not |
| --- | --- | --- | --- |
| El yazması genel (divani/rika) | **56496** OttomanTurkish_generic | ~%12 | Üretimdeki varsayılan (`DEVARSIV_TRANSKRIBUS_HTR_ID`) |
| Fetva / ilmiye el yazması | **169801** Ottoman Fatwa Manuscript | %5.94 | Fetva/kadı-sicili tipi eller için alternatif |
| Matbu (salname/gazete/nizamname) | **52502** OttomanTurkish_Print_1 | %7.2 | Matbu Osmanlıca; eScriptorium OpenITI print ile çapraz-kontrol |

`engine="both"` seçildiğinde Transkribus (bu tablo) + eScriptorium (yukarıdaki
Kraken tablosu) **paralel** koşar ve iki çıktı `transcriptions` altında yan
yana döner — bkz. `devlet-arsivleri-katalog.md` §7.1/§7.2 (K2/K3) ve §8.3
(üç-sütun transkripsiyon).

### Adım 3 — Belge oluştur ve IIIF'ten import et

```text
ottoman_escriptorium_create_document(
    project_slug="<seçilen-proje>",
    name="<yazma adı + folio kapsamı>",
    main_script="Arabic",        # Osmanlıca dahil
    line_offset=0,
    read_direction="rtl"          # sağdan sola
)
↓ (belge ID alındı)
ottoman_escriptorium_import_iiif(
    document_id=<id>,
    manifest_url="<IIIF manifest URL'i>",
    canvas_range=null              # tamamı için null, kısmi için liste
)
↓
[Async task başlar; list_tasks ile takip et]
```

### Adım 4 — Segmentation çalıştır

Import tamamlandığında (tüm canvas'ler `loaded` durumuna geldiğinde):

```text
ottoman_escriptorium_segment(
    document_id=<id>,
    model_pk=<segmentation modelinin PK'si>,
    override=true                   # önceki line/region kaldır
)
↓
[Async task; tamamlanması folio sayısı * 0.5–2 sn arası]
```

**Segmentation çıktısı**: her folio için satır poligonları (baseline) +
opsiyonel olarak bölge (region) sınırları. Manuel kontrol için 1–2 örnek
folio'yu eScriptorium web arayüzünden açıp **gözden geçirmek elzemdir** —
yanlış segmentation, sonraki HTR adımında kümülatif hata üretir.

### Adım 5 — HTR (Transkripsiyon) çalıştır

```text
ottoman_escriptorium_transcribe(
    document_id=<id>,
    model_pk=<recognition modelinin PK'si>,
    layer_name="auto_v1",            # versiyonlama için isimlendir
    parts=null                        # tüm sayfalar için null
)
↓
[Async task; folio sayısı * 5–30 sn arası]
```

> **İpucu.** Önce 3–5 örnek folio için `parts` parametresinde sınırlandırıp
> bir **pilot transkripsiyon** koşturmak daha verimli. Pilot CER (Character
> Error Rate) tahminine bakılarak model değişimi veya fine-tuning kararı
> verilir, sonra full run yapılır.

### Adım 6 — Sonuç çek ve dışa aktar

```text
ottoman_escriptorium_get_document(document_id=<id>)
↓
[Sayfa sayısı, line count, layer listesi doğrulanır]
↓
ottoman_escriptorium_get_transcription(
    document_id=<id>,
    layer_name="auto_v1"
)
↓
[Plain text + line metadata döner]
```

Çıktı, vekayinuvis raporunun **Ek B (Transkripsiyon)** bölümüne — ham hâliyle
ve yanına revize edilmiş hâliyle — eklenir.

---

## 4. Kalite Değerlendirme — CER/WER Tahmini

eScriptorium otomatik CER metriği yayınlamadığı için **örnekleme tabanlı
manuel değerlendirme** yapılır:

1. Transkripsiyon tamamlandıktan sonra **rastgele 5 folio** seç.
2. Her folio'da rastgele **10 satır** ground-truth ile karşılaştır.
3. Karakter bazında hata sayısını topla:
   - **CER = (toplam hata karakter) / (toplam karakter)**
   - **WER = (yanlış kelime) / (toplam kelime)**
4. Tipik referans aralıkları (RASAM ve OpenITI projelerinden):
   - **Matbu Osmanlıca**: CER %2–8, WER %5–15 (yayınlanabilir-ish)
   - **Nesih yazma**: CER %8–18, WER %20–40 (her sayfa kontrol gerekir)
   - **Rik'a/divânî**: CER %25+ (kullanılmaz; manuel)

> **Skill'in raporlama disiplini.** Her transkripsiyon, ACADEMIC_REPORT
> §8 (Süreç Notu) bölümünde mutlaka şu üç bilgiyle birlikte aktarılır:
> (i) kullanılan model adı + PK, (ii) örnekleme tabanlı tahmini CER,
> (iii) hangi folio'ların manuel revize edildiği.

---

## 5. İnsan Revizyon Protokolü

HTR çıktısı **hiçbir koşulda doğrudan akademik metne taşınmaz**. Sıralı
revizyon adımları:

1. **Otomatik post-processing**:
   - Tipik OCR/HTR hatalarını regex ile düzelt: hemze/elif karışıklığı, te
     mervuta vs te-meftuha, kef vs lâm-elif birleşimi.
   - Boşluk normalizasyonu (özellikle elif-lâm sonrası).
2. **Kelime-bazında sözlük doğrulaması**:
   - Redhouse, Devellioğlu, Şemseddin Sami, Kâmûs-ı Türkî sözlüklerinde
     bulunmayan kelimeler özel olarak işaretle.
3. **Bağlam-bazında okuma**:
   - Belge türü (vakfiye, mühimme, salname) standart formüllerini bilen
     gözle her sayfanın **giriş** ve **bitiş** formüllerini kontrol et.
4. **Üçüncü-göz**: mümkünse alandaki bir uzmanın 5–10 sayfayı kontrol etmesi.
5. **Versiyonlama**: revize edilmiş hâli yeni layer olarak yükle
   (`reviewed_v1`, `published_v1`), ham hâli silme.

---

## 6. Önerilen Async Polling Kalıbı

```pseudocode
function wait_for_task(document_id, task_kind, timeout=600):
    start = now()
    while now() - start < timeout:
        tasks = ottoman_escriptorium_list_tasks(document_id=document_id)
        relevant = filter tasks where kind == task_kind
        latest = max(relevant, by="created_at")
        if latest.status == "done":
            return SUCCESS
        if latest.status in ["error","failed","canceled"]:
            return FAILURE(latest.error_message)
        sleep(15)
    return TIMEOUT
```

Pratikte skill, segment + transcribe çağrılarından sonra **15 saniyelik
aralıklarla** polling yapar ve durumu kullanıcıya raporlar.

### 6.1 devarsiv yolunda sync/async kararı (K4)

Adım 0'daki **(b) devarsiv yolu** izlendiğinde, eScriptorium'un kendi
task/polling mantığı yerine devarsiv'in **kendi sync/async kuralı** uygulanır:

```text
≤5 sayfa VE tek motor  → devarsiv_ocr_archive_pages (sync, MULTIPAGE_MAX_PAGES)
>5 sayfa VEYA engine="both" tam belge → async kuyruk:
    devarsiv_ocr_submit(code, pages?, engine?, lang?, arsiv?)         → job_id
    ↓ poll
    devarsiv_ocr_result(job_id, include_text=false)                   → queued/running/done/error/stale
    ↓ done'da TEK SEFER
    devarsiv_ocr_result(job_id, include_text=true)
    ↓
    anamnesis ingest_document(doc_id="devarsiv:<code>", …)
    ↓
    sonraki sorgular anamnesis hybrid_query (bağlam ekonomisi)
```

`stale` dönerse **aynı parametrelerle resubmit** (arşiv PDF yerel; maliyet
tekrarlanmaz — yalnız OCR işi yeniden kuyruklanır). Bkz.
`devlet-arsivleri-katalog.md` §8.4 (async akış, → `skills/toplu-okuma`).

---

## 7. Fallback Yolu — eScriptorium Erişimi Yoksa

Eğer `ottoman_escriptorium_*` tool'ları konfigüre edilmemişse veya
`ESCRIPTORIUM_NOT_CONFIGURED` hatası dönüyorsa, MANUSCRIPT_TRANSCRIBE modu
düşük-erişim moduna geçer:

0. **BOA/BCA belgesi → devarsiv çift-motor (K2), önce bunu dene.** Kaynak
   Adım 0'daki (b) devarsiv yolundan geliyorsa (resmî katalogtan bir BOA/BCA
   kaydı), eScriptorium konfigüre olmasa bile **bağımsız bir yol** vardır:
   `devarsiv_ocr_belge`/`devarsiv_ocr_archive_pages`/`devarsiv_ocr_submit`'i
   `engine="both"` ile çağır — Transkribus (el yazması, K3 model tablosu) +
   eScriptorium (basılı, Kraken) **paralel** koşar (bkz. § 2.1, § 6.1 K4,
   `devlet-arsivleri-katalog.md` §7.1/§8.3). Bu yol başarısız/kullanılamaz
   dönerse aşağıdaki 1-5 adımlarına düş.
1. IIIF manifest'i `ottoman_fetch_iiif_manifest` ile getir.
2. İlgili sayfaların yüksek-çözünürlüklü görsel URL'lerini topla.
3. **Vision-tabanlı satır okuma** ile sınırlı transkripsiyon yap
   (sadece kısa pasajlar için, tüm yazma için değil).
4. Raporda açıkça belirt: "Tam HTR pipeline'ı bu oturumda kullanılamadı;
   sınırlı vision-tabanlı okuma raporlanmıştır. CER tahmini yapılmamıştır;
   transkripsiyon **araştırma notu** seviyesindedir, yayın değildir."
5. Kullanıcıya öner: **DH ve OCR-D projeleri** veya doğrudan eScriptorium
   public instance üzerinden hesap açma yolu.

---

## 8. Etik ve Hukuki Notlar

- **Telif**: IIIF manifestleri sıklıkla CC0, CC-BY veya kurum-spesifik
  lisans taşır. Transkripsiyonu yayınlamadan önce **manifest `rights`
  alanını** ve kurumsal şartları kontrol et.
- **Atıf**: Transkripsiyon yayımlanırken hem **görsel kaynak (IIIF
  kurumu)** hem **HTR modeli (OpenITI / RASAM)** hem de **insan revizör**
  ayrı ayrı atıfla anılmalıdır.
- **Kullanım izni**: BOA, Topkapı Sarayı Arşivi, TKGM Kuyûd-ı Kadîme
  belgelerinin (henüz IIIF'te değil) dijital görsellerinin elde edildiği
  yer ne olursa olsun, basılı/yayın amaçlı kullanım için kurumdan resmi
  izin alınması zorunludur.

---

## 9. Tipik Komut Sırası — Tam Örnek

Aşağıda Gallica'da bulunan bir XVIII. yy. matbu Osmanlıca risâlenin
30 folio'sunun tam transkripsiyonu için tipik tool dizilimi gösterilmiştir.

```text
1. ottoman_search_iiif(query="risale matbaa osmaniye", sources=["gallica"])
   → Hit listesi
2. ottoman_fetch_iiif_manifest(manifest_url="https://gallica.../manifest.json")
   → Manifest doğrulandı: 30 folio, matbu nesih, 1745
3. ottoman_escriptorium_list_projects()
   → "ottoman_print_v1" projesi mevcut
4. ottoman_escriptorium_list_models()
   → seg_model PK=12 (manuscript_general), htr_model PK=27 (OpenITI_arabicPrintBeta_v1.5.0)
5. ottoman_escriptorium_create_document(
        project_slug="ottoman_print_v1",
        name="Risale-i Tıbbiye [Gallica BNF Arabe 6739] ff. 1-30",
        main_script="Arabic", read_direction="rtl")
   → document_id=4521
6. ottoman_escriptorium_import_iiif(document_id=4521, manifest_url="...")
   → task=import-4521 (async)
7. [polling 30sn]
8. ottoman_escriptorium_segment(document_id=4521, model_pk=12, override=true)
   → task=segment-4521 (async)
9. [polling 60sn]
10. ottoman_escriptorium_transcribe(document_id=4521, model_pk=27, layer_name="auto_v1")
    → task=transcribe-4521 (async)
11. [polling 5dk]
12. ottoman_escriptorium_get_document(document_id=4521)
    → 30 folio, 487 satır, 1 layer "auto_v1"
13. ottoman_escriptorium_get_transcription(document_id=4521, layer_name="auto_v1")
    → Plain text + line metadata
14. [örnekleme CER kontrolü, manuel revizyon]
15. Rapora ekle: Ek B (Transkripsiyon ham + revize)
```

---

## 10. Hızlı Karar Akışı

```mermaid
flowchart TD
    A[Kullanıcı yazmadan transkripsiyon istedi] --> A1{Kaynak BOA/BCA resmî devarsiv kataloğu mu?}
    A1 -- Evet --> K[devarsiv çift-motor engine="both" dene — K2/K3; Transkribus+eScriptorium paralel]
    K -- Başarılı --> H
    K -- Kullanılamaz/degrade --> B
    A1 -- Hayır/Bilinmiyor --> B{IIIF manifest var mı?}
    B -- Hayır --> Z[Yazmanın IIIF olarak yayınlandığı yeri sor; aksi halde manuel transkripsiyon öner]
    B -- Evet --> C{eScriptorium konfigüre mi?}
    C -- Hayır --> Y[Fallback: vision-tabanlı sınırlı okuma + uyarı]
    C -- Evet --> D{Yazma türü ne?}
    D -- Matbu/Nesih --> E[Standart 7-adımlı akış, OpenITI/RASAM modeli]
    D -- Rik'a/Talik --> F[Pilot 5 folio + CER değerlendirme; gerekirse fine-tuning öner]
    D -- Divani/Siyakat --> G[Otomatik HTR güvenilir değil; manuel transkripsiyon öner; uzman göndermesi yap]
    E --> H[CER %15'in altındaysa rapora ekle]
    F --> H
    G --> H
    H --> I[ACADEMIC_REPORT §8 Süreç Notu'na model + CER + revize bilgisi yaz]
```

---

**Son uyarı.** HTR teknik bir hizalama aracıdır, yorumlayıcı bir araç
değildir. Vekayinüvis, transkribe edilen metni **anlamak**, bağlamlandırmak
ve ikincil literatürle ilişkilendirmek için **insan tarihçi** rolünü
üstlenmeye devam eder; transkripsiyon yalnızca o sürecin hızlandırıcı bir
katmanıdır.

---

## 11. LLM Görü-Okuma Güvenlik-Reddi Notu (Safety-Degrade)

Tarihî şiddet/esaret anlatılarında (savaş, sürgün, kıtlık, cariyelik, esaret
gibi konuları içeren belgeler) görü-tabanlı okuma/çeviri bazen bir güvenlik-
reddi (safety refusal) verebilir — bu davranış literatürde tanımlanmıştır
(**arXiv 2503.11898, likely**; kesin model/koşul eşlemesi bu skill için
doğrulanmamıştır, dolayısıyla "likely" işaretlidir). Karşılaşıldığında:

1. **Parça-böl**: pasajı daha küçük, tarafsız çerçeveli parçalara ayırıp
   yeniden dene (ör. tek cümle/tek satır bazında).
2. **Yeniden dene**: farklı bir çerçeveleme ile (akademik/arşivsel bağlam
   açıkça belirtilerek) tekrar iste.
3. **Olmadıysa dürüst "okunamadı" işareti**: içerik **asla atlanmış gibi
   gösterilmez** — hangi pasajın hangi nedenle okunamadığı raporda açıkça
   belirtilir (no-fabrication disiplini; sessiz atlama yasak).

### DUDU Teyit Notu (SPECULATIVE)

`UD_Ottoman_Turkish-DUDU` treebank'inin (Universal Dependencies projesi
kapsamında Osmanlı Türkçesi için önerilen bir bağımlılık ağacı bankası)
Universal Dependencies deposunda **teyit edilmesi gerekir** — bu skill için
varlığı/güncel durumu **doğrulanmamıştır (SPECULATIVE)**. Kullanılmadan önce
`universaldependencies.org` veya UD GitHub organizasyonu üzerinden canlı
teyit yapılmalı; teyit edilmeden bir HTR/paleografi iddiasının dayanağı
olarak sunulmaz.
