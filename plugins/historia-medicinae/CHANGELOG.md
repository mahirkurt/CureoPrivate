# Changelog — historia-medicinae

## 0.1.3 — 2026-08-17

- Anamnesis paylaşılan collection sözleşmesi: plugin id **`histmed`**. Her ingest
  `collection=histmed:run:<12hex>` + `doc_id=hmrun:<12hex>:<kanonik>` ister
  (eski çıplak `histmed:` / `pmid:` / `doi:` koşu-id'siz ingest `_legacy`).
  `doc_scope` yoktur; kapsamsız `hybrid_query` / `graph_*` DENY, scoped ALLOW.
  Atıf `doc_id::idx`. Ledger `.claude/anamnesis-histmed.json`. Stop'ta silinmez;
  SessionEnd + sonraki `/historia-medicinae` + startup yalnız kendi collection'ını
  temizler. `composition-contract.md` Evidentia satırı `evrun:` / `evidentia:run:`
  scratch; kendi satırı `histmed:run:`.
- **Stop kapıları yanlış-pozitif onarımı — iki ayrı kusur.** Canlı oturumda gözlendi:
  depo-bakımı turları G0 kapsam manifestosu istiyordu.
  (a) *Tur sızıntısı* — `transcript_text()` 400 satır geriye yürüyor, alakasız tur önceki
  tıp tarihi turlarından alan sinyali miras alıyordu. Sınır eklendi; **ama araç sonuçları
  transkriptte `role:"user"` taşır** (ölçüldü: 43 `user/tool_result`'a karşı 2 `user/text`),
  bu yüzden sınır yalnız `type:"text"` bloğu olan user mesajıdır — role'e bakan naif sürüm
  araç çağrılı turlarda metni hiç toplamaz ve kapıyı KÖRLEŞTİRİRDİ.
  (b) *Meta-tur* — `MORBUS`/`tıp tarihi` kelimelerini YAZMAK, o konuda araştırma yapmakla
  aynı sayılıyordu; dokümantasyon ve hook öz-kodu turları kapıyı tetikliyordu. Artık
  `turn_called_mcp()` gerçek connector çağrısı arar: çağrı yoksa raporlanacak kapsam da
  yoktur, kapı susar (vekayinüvis'in meta-tur baskılayıcısıyla aynı ilke).
  Yedi regresyon testi; fixture'lar gerçek transkript şekline (tool_use + tool_result)
  hizalandı — eski kurgular bu hataların ikisini de gizliyordu. Gerçek transkriptle
  doğrulandı: onarılmış kapılar sessiz, eski kopya ateşliyor.

## 0.1.2 — 2026-08-14

- OpenAthens `oa_fetch_pdf(doi|url)` ile hesap kapsamındaki sağlayıcılardan provider-nötr
  orijinal PDF; Anna's Reader `download_document(id=DOI|MD5)` ile PDF/EPUB ve desteklenen
  diğer formatlar pluginin S3 tam-metin shard'ına eklendi.
- Her iki teslim yolu kısa-ömürlü opaque resource link + SHA-256/provenance olarak ele alınır;
  link derhal tüketilir, uzun dosya `histmed:run:` / `hmrun:` ad alanıyla anamnesis'e ingest edilir.
- Yasal-öncelikli OpenAthens → Anna's sırası ve Anna's için yalnız-analiz telif kapısı korunur.

## 0.1.1 — 2026-08-12

- `displayName` "Historia Medicinae — Küresel Tıp Tarihi Araştırma Protokolü" → **"Historia
  Medicinae"**. Katalogdaki diğer dokuz plugin kısa ad kullanıyor (Vekayinüvis, Cureolex,
  Evidentia…); uzun ad marketplace listesinde tek istisnaydı. Uzun tanım `description`
  alanında kalıyor — kaybolan bilgi yok.
- Sürüm yükseltildi ki kurulu kopya (`installed_plugins.json`, sha'ya sabitlenmiş) tazelensin.

## 0.1.0 — 2026-08-11

İlk sürüm. Küresel tıp tarihi araştırma protokolü.

**Yapı**
- 17 skill: flagship `historia-medicinae` + `start`/`durum` + 11 mod skill'i
  (`kaynak-avi`, `salgin`, `kurum`, `kavram`, `etik`, `hekim`, `tedavi`, `politika`,
  `historiyografi`, `metin`, `rapor`) + 3 metodoloji/altyapı skill'i
  (`retrodiagnoz`, `kaynak-elestirisi`, `iiif-tarama`).
- 16 reference dosyası (1355 satır); 4'ü **daima** yüklenir
  (`connector-registry`, `kuresel-cerceve`, `quellenkritik`, `periodization`).
- 2 alt-ajan: `tarih-tarama-distilleri` (Tier-1 getirim izolasyonu),
  `anakronizm-denetcisi` (düşman denetimi).
- 4 hook (SessionStart preflight · PostToolUse retrieve-don't-dump · Stop G0 kapsam ·
  Stop anakronizm taraması); 18 test, ağ gerektirmez, hepsi fail-open.
- 25 server'lık filo, `fleet.yaml` tek gerçek kaynak.

**Metodoloji — alanın kendi literatürüyle temellendirildi**
- Retrospektif tanı **dört kapılı karar prosedürü** (Karenberg 2009 PMID 19591388 ·
  Arrizabalaga 2002 PMID 17191369 · karşı-tez *Asclepio* 2002 · Mitchell 2011 PMID 29539322).
  Yasak değil, işaretli izin. Devralınan etiket için **atıf soyağacı** kontrolü
  (Foxhall 2014 DOI 10.1017/mdh.2014.28). Adlandırılmış birey için ayrı etik rejim
  (Muramoto 2014 PMID 24884777). Yapıcı alternatif: Hacking döngü etkileri
  (*Soc Hist Med* 2016 DOI 10.1093/shm/hkw083).
- Kaynak eleştirisi: ölüm nedeni serileri patolojiyi değil sertifikayı yazanın bilgisini kodlar
  (Reid 2015 DOI 10.1080/1081602X.2014.1001768); nicelleştirme için **ICD10h**
  (*Soc Hist Med* 2025 DOI 10.1093/shm/hkaf077).
- Zulüm etiği: **kurban-merkezli anlatı** (Weindling 2016 PMID 26749461), **Viyana Protokolü**
  (Hildebrandt 2025 PMID 38441252), lekeli veri tartışması **çözülmemiş** olarak sunulur,
  Tuskegee **metafor disiplini** (Fairchild & Bayer 1999 PMID 10357678).
- Tarihyazımı **güncellik yargıları**: "hastanın bakışı" canlı ama heteroglossia olarak yeniden
  formüle edilmiş (DOI 10.1136/medhum-2019-011724); postkolonyal canlı (Anderson 1998
  DOI 10.1353/bhm.1998.0158); Foucault ekseni çekişmeli (DOI 10.1017/s0960777325100945).
- Küresel çerçeve tüzüğü: *Bull Hist Med* 2015 DOI 10.1353/bhm.2015.0116; anti-difüzyonizm.

**Ölçülmüş yetenekler (2026-08-11)**
- Wellcome Collection **sayfa-düzeyi tam-metin araması çalışıyor** — filodaki tek yüzey;
  zincir uçtan uca doğrulandı (`b3135631x` → 180 canvas; "dissection" → 3 koordinatlı isabet).
- IIIF motoru Osmanlı-dışında çalışıyor ("anatomy Vesalius" → 29, "plague treatise" → 28).
- MeSH `K01.400` ağacı ve OpenAlex tıp tarihi topic'leri (T12324/T12990/T14475/T12778) ölçüldü.

**Ölçülmüş bloklar ve tuzaklar (belgelendi, uydurma yasak)**
- LoC manifest 403 (evrensel) · NLM Akamai bot kapısı · Perseus/Scaife CTS ölü ·
  HathiTrust tam-metin 403 · Europeana ve BHL anahtarsız.
- `med-terminologies:find_equivalent` **skorlaması ters** (doğru ICD-11 isabetleri 0, yanlış
  sözlüksel isabetler 0.833; `consumption` → tüberküloz hiç dönmüyor) → skor sıralamada
  kullanılmaz.
- `ottoman_search_iiif` sıralaması Osmanlı-öncelikli → küresel sorguda gürültü.
- Dijital korpusta %30'a varan OCR hatası (Toon 2016 DOI 10.1017/mdh.2016.18) → **yokluk kanıt
  değildir**.

**Bilinen boşluklar**
- Cinsiyet tarihi ve engellilik tarihi için metodolojik derleme düzeyinde kaynak bulunamadı;
  HISTORIOGRAPHIA modunda hedefli yeniden tarama gerekir (`historiography-schools.md`'de beyan).
- Pre-DOI monograflar (Rosenberg 1992, Arnold 1993, Porter 1985, Cunningham 1992) filonun
  indekslerinde çözülmüyor — bibliyografik künyeyle atıflanır, tanımlayıcı uydurulmaz.
