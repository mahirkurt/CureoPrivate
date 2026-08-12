# Kapsam Manifestosu (G0) — biçim ve örnek

**Amaç:** "wire edilmiş tüm araçlar bağlama uygun her sorguda çalıştı" iddiasının doğrulanabilir
kanıtı. Her substantif `historia-medicinae` çıktısı (SOURCE_HUNT, MORBUS, INSTITUTIO, CONCEPTUS,
ETHICA, PROSOPOGRAPHIA, THERAPEUTICA, SANITAS_PUBLICA, HISTORIOGRAPHIA, EDITIO, RELATIO) bu bloğu
taşır. Eksik satır = **G0 FAIL** (**Claude Code'da** Stop hook tamamlatır; **claude.ai'de plugin
hook'ları çalışmaz → bu kapıyı çıktıdan önce kendi disiplininle doğrula, manifestoyu sen ekle).

Tek-araçlı hızlı sorgu (ör. yalnız bir takvim çevirimi veya tek bir DOI çözümü) manifesto
gerektirmez.

## Kurallar

- Wire edilmiş **25 server** için birer satır — bağlı olsun olmasın. Bantlar:
  - **Akademik çekirdek (6):** openalex · pubmed-epmc · semantic-scholar · paper-search ·
    consensus · scholar-gateway
  - **Birincil kaynak (2):** ottoman-archives (IIIF motoru) · devlet-arsivleri
  - **Tam-metin şelalesi (2):** openathens · annas-reader
  - **Tarihsel yasama (6):** uk-legal · health-policy · intl-treaty · mevzuat · tbmm · resmigazete
  - **Terminoloji/epidemiyoloji (3):** med-terminologies · who-gho · globocan
  - **Türkiye kolu (3):** yoktez · literatur · yok-akademik
  - **Web (2):** exa · tavily
  - **Substrat (1):** anamnesis
- Ayrıca **3 companion** (PubMed · Paper Search · Elicit — claude.ai yüzeyi) ve **3 delegasyon**
  (vekayinuvis · evidentia · sci-audit) satırı.
- Durum sözlüğü: `hit N` (N kayıt döndü) · `empty` (çalıştı, sonuç yok) · `degraded`
  (fetch fallback / `mcp_verified=false` / session_required / kısmi yetenek) ·
  `skipped: <gerekçe>` (anahtar yok / mod için N/A / oturum düşük / plugin kurulu değil).
- `skipped` gerekçesi **zorunlu ve denetlenebilir** olmalı. **Gerekçesiz skip yasak.**
- **Bağlı/kurulu katman atlanamaz:** bir connector bağlıyken tetiklenmiş bağlamda `skipped`
  yazmak meşru değildir (G0 FAIL). `skipped: … bağlı değil` yalnız gerçek yoklukta doğrudur.
- **devlet-arsivleri özel:** anahtar bağlı olsa bile upstream oturum düşükse
  `degraded: session_required (HP noVNC re-login)` yazılır — bu **skip değil degrade**'dir.
- **anamnesis substrat satırı** her manifestoda mevcuttur; doc_id ön-eki **`histmed:`** olmalıdır
  (evidentia'nın `pmid:`/`doi:` ve lex-sanitas'ın `mevzuat:` ad-uzaylarıyla çakışmaz).

## IIIF özel kuralı — ölçülmüş yetenek, iddia edilen yetenek değil

`ottoman-archives` tek satır olarak raporlanır ama **kaynak-başına yeteneği eşit değildir**
(2026-08-11 ölçümü, bkz. `skills/historia-medicinae/references/iiif-capability-matrix.md`).
Manifestoda hangi kaynağın hangi düzeyde kullanıldığı parantez içinde belirtilir:

```
ottoman-archives → hit 12 (wellcome 5: manifest+sayfa-içi arama · gallica 4: yalnız manifest
                   · IA 3: yalnız manifest · loc: erişilemedi/403 · nlm: bot-kapısı)
```

`loc` ve `nlm` için `degraded`/`gap` yazmak **zorunludur** — "aranmadı" ile "arandı ama upstream
bloklu" farklı şeylerdir ve ikincisi kullanıcıya bir erişim yol haritası borcu doğurur.

## Örnek

```
### Kapsam Manifestosu (G0) — Mod: MORBUS · Konu: 1817–1824 birinci kolera pandemisinin Hindistan'dan Avrupa'ya yayılımı

Akademik çekirdek
  openalex          → hit 18  (T12778 History of Medicine and Tropical Health; atıf grafı 3 ekol)
  pubmed-epmc       → hit 7   (MeSH K01.400.937 "History, 19th Century" + Historical Article)
  semantic-scholar  → hit 5   (bağımsız indeks doğrulaması; 2 kayıt openalex'te yoktu)
  paper-search      → hit 9   (Scholar/CrossRef: monograf ve kitap bölümü katmanı)
  consensus         → hit 2   (bulaşıcılık-kontenjyonizm tartışması sentezi)
  scholar-gateway   → hit 3   (pasaj-düzeyi: "sanitary conference" argümanı, s. 114-118)
Birincil kaynak
  ottoman-archives  → hit 6   (wellcome 4: 1832 kolera risalesi, sayfa-içi "miasma" 11 isabet
                               · gallica 2: yalnız manifest · loc: degraded 403)
  devlet-arsivleri  → hit 4   (Karantina Meclisi kayıtları; oturum canlı)
Tam-metin şelalesi
  openathens        → hit 2   (Millet Kütüphanesi: Arnold, Colonizing the Body — tam metin)
  annas-reader      → skipped: gerekmedi (lisanslı bant yeterli)
Tarihsel yasama
  uk-legal          → hit 5   (Hansard 1832 Cholera Bill müzakeresi — birincil zabıt)
  health-policy     → empty   (GovInfo ABD kaydı bu dönem için sonuç vermedi)
  intl-treaty       → hit 1   (1851 Paris Sanitary Conference soy zinciri — snapshot, 412 gün)
  mevzuat           → skipped: mod için N/A (yürürlükteki TR mevzuatı kapsamda değil)
  tbmm              → skipped: mod için N/A (dönem TBMM öncesi)
  resmigazete       → skipped: mod için N/A (dönem 1920 öncesi)
Terminoloji / epidemiyoloji
  med-terminologies → degraded (find_equivalent match_score ters çalışıyor — yalnız DOĞRULAMA
                                için kullanıldı, eşleme otomatik kabul EDİLMEDİ)
  who-gho           → skipped: mod için N/A (WHO serisi 1948 öncesine uzanmaz)
  globocan          → skipped: mod için N/A (kanser dışı)
Türkiye kolu
  yoktez            → hit 3   (Osmanlı'da karantina doktora tezleri)
  literatur         → hit 4   (DergiPark: Osmanlı Bilimi Araştırmaları)
  yok-akademik      → skipped: mod için N/A (çağdaş akademisyen haritası kapsamda değil)
Web (üçüncül)
  exa               → hit 2   (Wellcome dijital sergi sayfası — yalnız yönlendirme, iddia taşımaz)
  tavily            → skipped: anahtar yok
Substrat
  anamnesis         → ingest 2 belge (histmed:openathens/arnold-1993, histmed:wellcome/b21294831)
                      · 9 bounded query
Companion
  PubMed            → skipped: claude.ai companion bağlı değil (wire'lı pubmed-epmc taşıdı)
  Paper Search      → skipped: claude.ai companion bağlı değil (wire'lı paper-search taşıdı)
  Elicit            → skipped: mod için N/A
Delegasyon
  vekayinuvis       → çağrıldı (Osmanlıca karantina nizamnâmesi el yazması → transkripsiyon)
  evidentia         → skipped: mod için N/A (çağdaş klinik geçerlilik sorulmadı)
  sci-audit         → çağrıldı (RELATIO öncesi atıf-adli + TR dil denetimi)
```

## Not

`empty` ve `skipped` **başarısızlık değil**, kapsamın dürüst kanıtıdır — mühim olan hiçbir
server'ın sessizce atlanmamasıdır. `degraded` de dürüst bir durumdur: katmanın atlanmadığını,
yalnız kısıtlı ya da ikame edilmiş olduğunu gösterir.

**Yokluk kanıt değildir.** Bir kaynakta sonuç bulunamaması "böyle bir belge yok" demek değildir;
özellikle dijitalleştirilmiş korpuslarda OCR hata oranı ölçülmüş biçimde yüksektir (Toon et al.
2016, *Medical History*, DOI 10.1017/mdh.2016.18 — eski dijital BMJ'de kelimelerin %30'una varan
OCR hatası). `empty` satırı bu yüzden "arandı, bulunamadı" der; "yoktur" demez.
