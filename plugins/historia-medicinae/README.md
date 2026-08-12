# Historia Medicinae

**Küresel tıp tarihi araştırma protokolü** — Mezopotamya ve Greko-Romen dünyadan İslâm
geleneğine, Latin Batı'dan Güney ve Doğu Asya'ya, sömürge tıbbından çağdaş küresel sağlığa
uzanan kapsamda birincil-kaynak-öncelikli araştırma ve iki dilli akademik rapor üretimi.

Türkiye bu kapsamın **bir bölgesi**dir, dışında değil — ancak Osmanlıca el yazması zanaatı
`vekayinuvis`'e delege edilir.

---

## Neden var

Ekosistemde `evidentia` çağdaş klinik kanıt, `vekayinuvis` Osmanlı–Türk arşivi, `lex-sanitas`
yürürlükteki TR sağlık normu için var. **Küresel tıp tarihi** hiçbirinin kapsamında değildi.

Bu plugin'i diğer bir "araştırma asistanı"ndan ayıran şey, alanın kendi metodoloji
literatürünü **uygulanan kural** hâline getirmesidir. Üç adlandırılmış tuzak:

1. **Retrospektif tanı** — geçmişteki hastalığa modern etiket yapıştırmak. Bu bir dil modelinin
   en güçlü varsayılan hatasıdır ("1348 Floransa'da şişlik ve ateş" → sessizce "veba").
   Plugin bunu **yasaklamaz**, dört kapılı karar prosedürüne bağlar.
2. **Presentizm/teleoloji** — "henüz mikrop teorisini bulamamışlardı."
3. **Difüzyonizm** — Avrupa-dışı geleneği "Avrupa tıbbına giden aşama" olarak anlatmak.

Üçü de `Stop` hook'uyla **çıktı üzerinde taranır**; düz yazı öğüt değil, işleyen kapıdır.

---

## Kurulum

```
/plugin marketplace add mahirkurt/CureoPrivate
/plugin install historia-medicinae@cureonics-marketplace
```

Anahtarlar Doppler'dan gelir:

```bash
doppler run -p cureohub -c dev_personal -- claude
```

Filo durumunu görmek için: `/historia-medicinae:durum`

---

## Komutlar

| Komut | Mod | Ne yapar |
|---|---|---|
| `/historia-medicinae:start` | — | Oryantasyon + filo kontrolü + mod yönlendirme |
| `/historia-medicinae:durum` | — | Filo doctor: anahtarlar, bloklar, delegasyonlar |
| `/historia-medicinae:kaynak-avi` | SOURCE_HUNT | Kaynak envanteri + erişim yol haritası |
| `/historia-medicinae:salgin` | MORBUS | Salgın ve hastalık biyografisi |
| `/historia-medicinae:kurum` | INSTITUTIO | Kurum ve meslekleşme tarihi |
| `/historia-medicinae:kavram` | CONCEPTUS | Fikir ve kavram tarihi |
| `/historia-medicinae:etik` | ETHICA | Etik ve karanlık bölümler |
| `/historia-medicinae:hekim` | PROSOPOGRAPHIA | Hekim biyografisi ve ağlar |
| `/historia-medicinae:tedavi` | THERAPEUTICA | Tedavi, ilaç, teknoloji tarihi |
| `/historia-medicinae:politika` | SANITAS_PUBLICA | Kamu sağlığı politikası ve hukuk tarihi |
| `/historia-medicinae:historiyografi` | HISTORIOGRAPHIA | Tarihyazımı incelemesi |
| `/historia-medicinae:metin` | EDITIO | Tarihsel tıp metni okuma |
| `/historia-medicinae:rapor` | RELATIO | Akademik rapor derlemesi |

**Metodoloji skill'leri** (mod bağımsız):

| Komut | Ne yapar |
|---|---|
| `/historia-medicinae:retrodiagnoz` | Modern tanı etiketi karar prosedürü (dört kapı + atıf soyağacı) |
| `/historia-medicinae:kaynak-elestirisi` | Ölüm cetveli/mortalite serisi/kurumsal kayıt güvenilirliği |
| `/historia-medicinae:iiif-tarama` | Dijital birincil kaynak avı + ölçülmüş yetenek matrisi |

---

## Filo — 25 server, beş bant

| Bant | Server'lar |
|---|---|
| **Akademik çekirdek** | openalex · pubmed-epmc · semantic-scholar · paper-search · consensus · scholar-gateway |
| **Birincil kaynak** | ottoman-archives (jenerik IIIF motoru) · devlet-arsivleri |
| **Tam-metin şelalesi** | openathens (Tier 3 lisanslı) → annas-reader (Tier 4 son çare) |
| **Tarihsel yasama** | uk-legal (Hansard 1803+) · health-policy · intl-treaty · mevzuat · tbmm · resmigazete |
| **Terminoloji/epi** | med-terminologies · who-gho · globocan |
| **Türkiye kolu** | yoktez · literatur · yok-akademik |
| **Web (üçüncül)** | exa · tavily |
| **Substrat** | anamnesis (RAG/GraphRAG, `histmed:` ön-eki) |

Tek gerçek kaynak `fleet.yaml`; `.mcp.json` ve `fleet.lock.json` **üretilmiş** dosyalardır:

```bash
python3 tools/fleetkit/gen_fleet.py historia-medicinae
python3 tools/fleetkit/check_drift.py --all
```

---

## Ölçülmüş gerçekler (2026-08-11)

Bu plugin'in belgelenmiş yetenek iddiaları **canlı ölçümle** doğrulanmıştır; ölçülmemiş olan
"ölçülmedi" yazar.

**Çalışan:**
- IIIF motoru Osmanlı-dışında çalışıyor — "anatomy Vesalius" → 29, "plague treatise" → 28 gerçek
  isabet (Vesalius *Fabrica* 1555, Fuchs 1551, *A treatise of the plague* 1603/1721/1799).
- **Wellcome Collection sayfa-düzeyi tam-metin araması çalışıyor** — filodaki tek yüzey
  (`b3135631x` → 180 canvas; "dissection" → 3 koordinatlı isabet). Zincir uçtan uca doğrulandı.
- MeSH tarih ağacı `K01.400` — Ancient `.470` · Medieval `.500` · Early Modern `.475` ·
  Modern `.504` · 19th `.937` · 20th `.968` · 21st `.984`.
- OpenAlex tıp tarihi topic'leri: T12324 (123.520 eser) · T12990 (288.100) · T14475 (117.643) ·
  T12778 (25.224).
- Wikidata SPARQL ve Wellcome katalog API'si authless ve canlı.

**Bloklu (anahtarla çözülmez):**
- Library of Congress manifest **403** — evrensel, iki bağımsız ağdan ölçüldü.
- NLM Digital Collections — Akamai bot kapısı (202 / 0 bayt).
- Perseus/Scaife CTS — DNS ölü + 502 + SPA kabuğu. Alternatif: Hopper `xmlchunk` +
  GitHub `PerseusDL/canonical-greekLit`.
- HathiTrust tam-metin 403 (Bib API 200 — metadata açık).
- Europeana: sunucuda anahtar yok. BHL: ücretsiz anahtar alınmamış.

**Tuzak:**
- `med-terminologies:find_equivalent` **skorlaması ters** — doğru ICD-11 isabetleri
  `match_score: 0`, yanlış sözlüksel isabetler `0.833`; `consumption` → tüberküloz **hiç
  dönmüyor**. Skor sıralamada kullanılmaz.
- `ottoman_search_iiif` sıralaması "Ottoman-relevance first" → küresel sorguda gürültü.
- Dijitalleştirilmiş korpusta **%30'a varan OCR hatası** ölçülmüş → boş sonuç yokluk kanıtı değil.

---

## Bileşim

| Yön | Hedef |
|---|---|
| **Teslim** | `carbon-html-report` (rapor) · `carbon-quarto-scientific` (istatistik/tablo) · `dataviz` · `artifact-diagramming` |
| **Delegasyon** | `vekayinuvis` (Osmanlıca paleografi) · `evidentia` (çağdaş klinik) · `sci-audit` (çıktı QA) · `lex-sanitas` (yürürlükteki TR norm) |

Sözleşmeler: [`shared/composition-contract.md`](shared/composition-contract.md) ·
[`shared/coverage-manifest.md`](shared/coverage-manifest.md) ·
[`shared/context-economy-contract.md`](shared/context-economy-contract.md)

---

## Geliştirme

```bash
python3 hooks/test_hooks.py                              # 18 test, ağ yok
python3 scripts/historia_doctor.py [--live]              # filo preflight
python3 tools/fleetkit/gen_fleet.py historia-medicinae   # .mcp.json + fleet.lock.json üret
```

---

## Proje ayarları

Proje kökünde `.claude/historia-medicinae.local.md` — bkz.
[`docs/historia-medicinae.local.md.example`](docs/historia-medicinae.local.md.example).
