# Referans 16 — Bağlam Yönetimi ve Büyük-Veri Operasyonel Protokolü

Bu dosya, `shared/context-economy-contract.md` sözleşmesinin **operasyonel yürütme kılavuzudur** — hangi durumda hangi katmanı, hangi araç parametreleriyle çağıracağını adım adım tanımlar. Tam-filo (20 kaynak MCP her sorguda) çalışırken bağlamı boğmadan **en doğru ve kapsamlı** getirimi sağlar.

## A. Karar ağacı — bir belge geldiğinde

```
Belge/getirim geldi
├─ Küçük (≤6KB) ve tek-mod kullanımı? → ana pencerede kullan (Tier 0), evidence_ledger'a işle
├─ Büyük (>6KB) veya çok-mod/çok-kapı kullanımı?
│   ├─ anamnesis anahtarı VAR? → Tier 2: ingest_document(doc_id=<kanonik>) → hybrid_query bounded dilim
│   └─ anamnesis anahtarı YOK? → §C bounded-chunk fallback (madde_tree → hedef chunk)
└─ Çok-server ham süpürme? → Tier 1: sharded distiller (§B), ana pencereye yalnız zarf
```

## B. Sharded tam-filo dağıtımı (paralel distiller)

Her sorguda 4 shard'ı **paralel** dağıt (bağımsız görevler — tek turda). Her shard bağımsız distiller çağrısıdır; ana pencere 4 kompakt zarfı G0 manifestosunda birleştirir.

**S1 — TR çekirdek** (`legal-distiller`):
> "Konu: <T>. Mod: <M>. Şu server'ları süpür: mevzuat, mevzuat-bilgisi, resmi-gazete, saglikbakanligi, titck, tbmm, detsis. TR-mevzuatta KEYWORD arama. Büyük metinleri sen tüket; bana ≤15 bulgu + coverage (her server hit/empty/degraded/skipped) döndür. Kanonik id'leri (mevzuat_no+tur+tertip) not et."

**S2 — Karşılaştırmalı** (`comparative-law-researcher`):
> "Konu: <T>. Yabancı katman: health-policy, german-law, ich-guidelines, intl-treaty, eudamed, oecd (+bağlıysa Open_Law, Ansvar, Fedlex_Swiss — CH'de SR-numaralı birincil metin Fedlex'ten, Ansvar CH bulgusu çerçeve-teyit; CH kapsam dışıysa coverage'a 'skipped: mod için N/A' yaz). Programatik kimlik (CELEX/ECLI/ELI/AKN/SR) zorunlu; URL'siz bulgu döndürme. Mukayese matrisi + coverage döndür."

**S3 — Doktrin/içtihat** (`legal-distiller`):
> "Konu: <T>. Server: yok-akademik, literatur (DergiPark tam-metin), yoktez (wire'lı — tez doktrini + tez no/başlık/yazar teyidi), Yargı (bağlıysa), Türk Patent (bağlıysa — IP kesişimi; IP-boyut yoksa coverage'a 'skipped: mod için N/A' yaz). Doktrin + içtihat zinciri (AYM/Danıştay/Yargıtay). ≤10 bulgu + coverage. İçtihat reform-GEREKÇE sinyalidir; dava dilekçesi değil."

**S4 — Klinik** (evidentia `evidence-synthesizer` / `/evidentia`): zenginleştirilmiş sorgu (composition-contract §1).

Zarflar geldikten sonra ana pencere yalnız 4 zarf + birleşik G0 manifestosu görür; ham getirim distiller pencerelerinde kalır.

## C. Bounded-chunk fetch (anamnesis yoksa veya hedef madde biliniyorsa)

Büyük mevzuatı **asla** limitsiz `max_chars` ile getirme. Sıra:

1. **Yapı:** `get_mevzuat_madde_tree(mevzuat_no, tur, tertip)` → madde başlıkları + numaraları (hafif).
2. **Zaman/ilişki:** gerekirse `get_mevzuat_timeline` (yürürlük) · `get_mevzuat_relations` / `ilga_zinciri` (dayanak/ilga kenarları).
3. **Hedef chunk:** `madde_acikla(madde_no)` VEYA `get_mevzuat_text(chunk_index=i, chunk_size=n)` / `(start_page, end_page)` / `(max_chars=<makul>)`.
4. **İndirme:** `download_mevzuat_document(include_base64=false)` → yalnız URL (base64 gövdesini ana pencereye çekme).

Parametre notu: `mevzuat_no`/`mevzuat_tertip` INTEGER. as_of tarihli geçmiş sürüm için `get_mevzuat_madde_tree(as_of_date=...)`.

## D. anamnesis (Tier 2) tam çağrı örneği

```text
# 1) Bir kez ingest (kanonik id ile — ikinci kez ingest edilmez):
anamnesis.ingest_document(
  doc_id="mevzuat:1219/1",            # kanonik cache anahtarı
  text=<tam kanun metni>,             # distiller/relay'den gelen tam gövde
  metadata={"tur":"kanun","rg":"1219","as_of":"2026-07-05"}
)
# 2) Çok-sorgulu, sınırlı, provenance-damgalı getirim (ana pencereye YALNIZ bunlar):
anamnesis.hybrid_query(
  doc_scope="mevzuat:1219/1",
  queries=["tabiplik yetkisi tanım", "diploma tescil", "yaptırım", "yürürlük hükmü"]
)
# 3) İlişki grafiği (madde ↔ dayanak ↔ değişiklik):
anamnesis.graph_neighbors(node="madde:8", rel="degisiklik")
anamnesis.subgraph(seed="mevzuat:1219/1", depth=1)
```

Getirim hep `{doc_id, madde/sayfa, snippet}` döner → `evidence_ledger` `E###` kaydına doğrudan bağlanır (provenance). RG OCR aynı disipline tabi: `rg_ocr_result` > eşik → ingest.

## E. Yabancı hukuk büyük-metin (karşılaştırmalı)

- **Kimlik-öncelikli:** CELEX (`32007R1394`), ECLI, ELI, Akoma Ntoso section id ile **bölüm-düzeyi** fetch; tam konsolide statute'u ana pencereye çekme.
- **Tam-metin karşılaştırma** gerekiyorsa → anamnesis'e ingest (doc_id=`celex:32007R1394`) → sadece karşılaştırılan maddeleri query et.
- `comparative-law-researcher` bu işi kendi penceresinde yapar; ana pencereye yalnız mukayese matrisi (hücre başına identifier) döner.

## F. Bütçe izleme ve evict

- Her mod fazı sonunda: ara getirimleri `evidence_ledger` kayıtlarına çök (extract), ham izleri **evict** et. Sonraki faz yalnız ledger + kanonik cache'i görür.
- Ana pencere damıtılmış getirimi ~25-30K karakteri aşarsa: en eski ham/uzun izleri at, distillate'leri daha da sıkıştır.
- Devre-kesici: PostToolUse `retrieve_dont_dump` hook'u 6KB üstü hukuk-metni çıktısında ingest/distiller yönlendirmesi enjekte eder — bu uyarıyı **uygula**, ham işleme geçme.

## G. Kapsam manifestosunda büyük-veri satırı

anamnesis kullanıldığında G0 manifestosuna ekle:
```
Substrat
  anamnesis            → ingest 3 belge (mevzuat:1219/1, celex:32007R1394, rg:33686) · 11 bounded query
```
Kullanılmadıysa (küçük getirim) veya anahtar yoksa:
```
  anamnesis            → skipped: gerekmedi (küçük getirim)   |   skipped: anahtar yok (bounded-chunk fallback)
```

Bu protokol, "tüm araçlar her sorguda çalışsın" talebini **bağlam-güvenli** kılar: hepsi ateşlenir, ham veri Tier 1/Tier 2'de tüketilir, ana pencere yalnız damıtılmış kanıt + kapsam kanıtı taşır.
