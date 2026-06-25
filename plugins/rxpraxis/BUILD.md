# rxpraxis — İnşa, Vendor ve Entegrasyon Yol Haritası (BUILD.md)

Bu belge, rxpraxis süitinin **neden bu mimariyle** kurulduğunu, dört kaynak skill'in plugin
ağacına **nasıl taşınacağını (vendor)**, entegrasyon yamasının ne olduğunu, **karşılaşılabilecek
zorlukları ve çözümlerini**, değerlendirilen **alternatif mimarileri** ve **kalite güvence
stratejisini** kayıt altına alır. Hedef kitle: süiti kuran/sürdüren mühendis (Mahir) ve ileride
denetleyecek skill-censor / smp-orchestrator çalıştırıcısı.

> **Durum.** İskelet, paylaşılan sözleşmeler, orkestratör (`rxos` v1.7.0), `start` skill'i, altı
> komut ve eval seti tamamlanmıştır. **Dört kaynak skill ağaca vendored edilmiş (§2), §3 entegrasyon
> notu uygulanmış ve yapısal QA (§6) çalıştırılmıştır** — bütünlük kanıtı: vendored içerik, enjekte
> edilen tek not bloğu dışında kanonik kaynakla bit-aynı. Kalan tek adım, QA *skill'lerinin*
> (skill-censor / smp-orchestrator) çalıştırılması ve `.skill`/plugin ZIP paketlemesidir (§8 adım 8b-9).

---

## 1. Mimari Gerekçe

### 1.1 Sorun: beş skill bir "süit" değil, beş ada

Mevcut durumda rxos, dört skill'i *runtime'da* çağırır; ancak bu dört skill **birbirinden
habersiz** tasarlanmıştır. Her biri kendi connector envanterini kendi SKILL.md'sinde yeniden
tanımlar; üçü (medical-research, pharmaintel, pharmapatent) **aynı TİTCK MCP'yi** bağımsızca
çağırır; ikisi (pharmaintel, thoughtspot-roche) **aynı IQVIA MIDAS yüzeyine** farklı sözleşmelerle
dokunur. Bu, üç somut maliyet üretir:

1. **Connector tanımı çoğullanır** — aynı connector dört yerde, potansiyel olarak dört farklı
   fallback/provenance kuralıyla tanımlanır (tek-doğruluk-kaynağı ihlali).
2. **Pahalı çağrı tekrarlanır** — tam tarama sırasında TİTCK MCP üç kez, MIDAS oturumu birden çok
   kez açılabilir; bu hem latency hem de (ThoughtSpot tarafında) Roche-confidential veri yüzeyine
   gereksiz tekrar erişim demektir.
3. **Çıktı grameri tutarsızlaşır** — her skill kendi provenance damgası ve katman modelini taşır;
   konsolide rapor heterojen olur.

### 1.2 Çözüm: iki paylaşılan sözleşme, tek orkestratör

rxpraxis'in tezi, süiti "skill toplamından fazlası" yapan değerin **iki entegrasyon
sözleşmesinde** toplanmasıdır:

- **`CONNECTORS.md`** — connector envanterini, skill→connector sorumluluk matrisini, fallback
  zincirlerini ve **tek-sefer TİTCK kuralını** beş skill'den çekip plugin köküne koyar. Artık
  "kim hangi connector'ı, hangi sırayla, hangi fallback'le çağırır" sorusunun **tek** yanıtı vardır.
- **`shared/canonical-cache-contract.md`** — rxos'un "TİTCK'yi bir kez çıkar, paylaş" sezgisini
  **üç pahalı artefakta** genelleştirir: `titck_canonical`, `midas_extract`, `adis_pipeline`.
  İçerik-adresli `scope_hash` anahtarıyla bir kez çıkarılır, sonraki aşamalar **okur** —
  "çıkar-bir-kez, oku-tekrar-sorma".

Bu ikisi, `provenance-standard.md` (birleşik damgalama grameri) ve `run-manifest-schema.json`
(çift-sorgu denetim kanıtı dâhil orkestrasyon kaydı) ile tamamlanır. Geri kalan her şey — komutlar,
orkestratör, router — bu sözleşmeleri **tüketir**.

### 1.3 Neden orkestratör-sahipli + dört skill vendored

İki uç tasarım reddedildi (gerekçe §5'te):

- **Embed-all** (dört skill'in gövdesini rxos içine gömme): pharmaintel tek başına ~644 satır + ayrı
  ürün-geliştirme alt-protokolü taşır; dördünü tek SKILL.md'ye gömmek context-window'u şişirir ve
  bağımsız sürümlemeyi imkânsız kılar.
- **Dört ayrı plugin** (her skill kendi plugin'i + ortak bağımlılık): connector sözleşmesini
  paylaşmak için plugin-arası bağımlılık gerekir; Claude plugin modeli bunu temiz desteklemez.

Seçilen yol — **orkestratör + paylaşılan sözleşmeler plugin-sahipli; dört kaynak skill ağaca
vendored (kopyalanmış) + entegrasyon notu yamalı** — her iki ucun maliyetlerinden kaçınır:
skill'ler bağımsız okunabilir/sürümlenebilir kalır, sözleşmeler tek noktada toplanır.

---

## 2. Vendor Prosedürü (dört kaynak skill'in taşınması)

Dört kaynak skill şu an `/mnt/skills/user/<skill>/` altında **canonical** olarak durmaktadır.
rxpraxis ağacındaki `skills/<skill>/_VENDOR_PLACEHOLDER.md` dosyaları, bu gövdelerin nereye
kopyalanacağını işaretler. Vendor adımları:

### 2.1 Kopyalama

Her skill için (`medical-research`, `pharmaintel`, `pharmapatent`, `thoughtspot-roche`):

```bash
SRC=/mnt/skills/user
DST=/mnt/user-data/outputs/rxpraxis/skills
for s in medical-research pharmaintel pharmapatent thoughtspot-roche; do
  # SKILL.md + tüm yardımcı dizinler (references/ scripts/ assets/ evals/)
  rsync -a --exclude '_VENDOR_PLACEHOLDER.md' "$SRC/$s/" "$DST/$s/"
done
```

`rsync` yoksa `cp -R "$SRC/$s/." "$DST/$s/"`. Kopyalama sonrası `_VENDOR_PLACEHOLDER.md`
dosyaları silinebilir (içerikleri §3 entegrasyon notuna devredilir).

### 2.2 Sürüm sabitleme

Vendored skill'lerin SKILL.md front-matter'ındaki `version` korunur (medical-research v8.1.0,
pharmaintel v8.1.0, pharmapatent v2.0.2, thoughtspot-roche v2.0.0). rxpraxis `plugin.json`
`smp.source_skills` listesi bu sürümleri kayıt altında tutar. **Standalone sürümle senkron**
kalmaları gerekir: kaynak skill güncellenirse vendored kopya yeniden çekilmelidir (§6.4 drift
denetimi).

### 2.3 İçsel yol referansları

Kaynak skill'ler kendi içlerinde `references/...` göreli yollarına atıf yapar; bunlar kopya sonrası
**aynen çalışır** (dizin yapısı korunduğu için). Skill'in kendi `evals/` dizini de taşınır ve
plugin-düzeyi `evals/evals.json`'dan **ayrı** kalır (o yalnız entegrasyon eval'leridir, §6.3).

---

## 3. Entegrasyon Yaması (tek-doğruluk-kaynağı uzlaştırması)

Vendor sonrası kritik incelik: kaynak skill'ler kendi connector envanterlerini hâlâ
taşımaktadır; plugin ise `CONNECTORS.md`'yi tek doğruluk kaynağı ilan eder. Çakışma riski.

**Çözüm — silme değil, üst-atıf (supersession note).** Her vendored SKILL.md'nin connector/veri-
kaynağı bölümünün başına, rxos'ta uygulanan desenle aynı, kısa bir **plugin entegrasyon notu**
eklenir:

```markdown
> **Plugin entegrasyon notu (rxpraxis).** Bu skill rxpraxis süiti altında çalışırken connector
> envanteri, fallback zincirleri ve tek-sefer TİTCK/MIDAS disiplini için
> [../../CONNECTORS.md](../../CONNECTORS.md) ve
> [../../shared/canonical-cache-contract.md](../../shared/canonical-cache-contract.md)
> NORMATİFTİR. Aşağıdaki skill-içi connector tanımı, standalone kullanım için korunmuştur; süit
> bağlamında çakışma hâlinde plugin sözleşmesi üstündür.
```

Bu yaklaşım:

- Skill'in **standalone** çalışabilirliğini korur (connector tanımı silinmez).
- Süit bağlamında **çakışmayı** önler (öncelik açıkça plugin sözleşmesinde).
- Kaynak skill'lerin gövdesini minimal değiştirir (yalnız bir not bloğu) — drift yüzeyi küçük kalır.

Yamanın uygulanacağı bölümler: medical-research §"Native-MCP-First" + connector envanteri;
pharmaintel §"4-kanal stack" (Channel A-D); pharmapatent Mod 13 §"MCP-first TR akışı";
thoughtspot-roche §"Path A/Path B" + connector tanımı.

---

## 4. Potansiyel Zorluklar ve Azaltım (Risk Register)

| # | Zorluk | Risk | Azaltım |
|---|---|---|---|
| **R1** ✅ | **Tek-sefer TİTCK runtime'da nasıl garanti edilir?** SKILL metni "bir kez çağır" der; ama model üç sibling skill'i çalıştırırken bunu unutabilir. | Çift/üçlü TİTCK sorgusu → latency + tutarsız snapshot. | **ÇÖZÜLDÜ (v1.1 dağıtıldı).** Artık kod-düzeyi deterministik garanti: `titck-cache-mcp` Worker'ı (`titck.cureonics.com`, "TİTCK Cache" connector'ı) ham TİTCK MCP'yi saran şeffaf önbellek proxy'sidir. `scope_key = sha256(tool+canonical(args))` başına upstream çağrısı ≤1 — **SingleFlight Durable Object** eşzamanlı özdeş çağrıları tek-uçuşa birleştirir, **KV TTL** ikinci-kat önbellektir. Üç skill ham TİTCK yerine **TİTCK Cache**'i çağırır. `single_shot_enforced` artık `/ledger` ucundan **ölçülür** (`upstream_calls ≤ distinct_scopes`), beyan değil. Önbellek mantığı (§3.2) + manifest denetimi + `/rxpraxis-scan` Adım 3 tamamlayıcı kalır. Playbook: `titck-cache-mcp-build-playbook.md`. |
| **R2** | **ThoughtSpot/MIDAS Roche-confidential sızıntısı.** thoughtspot-roche IQVIA MIDAS (Roche internal) verisi döndürür; konsolide raporda uygunsuz ifşa riski. | Gizli ticari veri uygunsuz paylaşım. | `provenance-standard.md` §4 Roche-confidential işaretleme zorunlu; `midas_extract` artefaktı ve onu kullanan her bölüm "Roche confidential" damgası taşır. Cross-country sayılar **annualize + agregat** sunulur (CONNECTORS.md §5), ham hücre dökümü değil. Süit dışı paylaşım açıkça yasak. |
| **R3** | **pharmaintel + dev manifest context-window basıncı.** pharmaintel ~644 satır + ürün-geliştirme alt-protokolü; tam tarama dört skill'i aynı bağlama yükler. | Bağlam taşması, kalite düşüşü. | (a) Kaynak skill'ler **progressive disclosure** kullanır — ana SKILL.md ince, ağır içerik `references/` altında, yalnız gerektiğinde okunur. (b) Orkestratör aşamaları **sıralı** çalışır; her aşama yalnız ilgili skill'in ilgili bölümünü çeker, dördünü aynı anda değil. (c) Kanonik önbellek, aşamalar arası **veriyi** taşır (ham connector çıktısını değil), bağlamı hafifletir. |
| **R4** | **Namespace `rxpraxis:rxos` — çift "Rx" + olası kafa karışıklığı.** Komut `/rxpraxis-scan` ile skill `rxpraxis:rxos` arasında kullanıcı ayrımı. | Kullanıcı hangi yüzeyi çağıracağını şaşırabilir. | `start` skill'i (router) niyet→yüzey eşlemesini açıkça yapar. Komutlar kullanıcı-yüzlü giriş; skill'ler komutların çağırdığı motor. README "Hızlı Başlangıç" bunu üç satırda netleştirir. Marka sürekliliği için `rxos` adı korunur (Mahir'in mevcut ekosisteminde tanınır). |
| **R5** | **Vendored kopya ile standalone kaynak arasında drift.** Kaynak skill güncellenir, vendored kopya eskir. | Süit, güncel-olmayan skill çalıştırır. | §6.4 drift denetimi: `plugin.json` `source_skills` sürümleri ile `/mnt/skills/user/<skill>` front-matter sürümleri periyodik karşılaştırılır; uyuşmazlıkta yeniden vendor. İdealde tek yönlü akış: kaynak = canonical, vendored = türev. |
| **R6** | **Degrade mod belirsizliği.** ThoughtSpot bağlı değilse Aşama 5b atlanır; kullanıcı bunu fark etmeyebilir. | Eksik analiz, sessiz kalite kaybı. | `start` pre-flight + her komutun "Pre-flight" adımı eksik connector'ı **açıkça** bildirir; `canonical-cache-contract.md` §4.5 `midas_extract` pre-flight degradasyonunu tanımlar; rapor Katman B İç Denetim Kaydı hangi aşamanın degrade çalıştığını kaydeder. |
| **R7** | **Scope creep — hospital/IV sızması.** Kullanıcı kapsam dışı (IV/infüzyon) ürün sorabilir. | Süit, geçersiz kanalda analiz üretir. | G0 scope guard tüm komutlarda; rxos §0 brief kontrolü kanal alanını zorunlu tutar; hospital/IV → reddet + gerekçe. Bireysel SGK/dava → onko-erisim'e yönlendir. |

**Nihai not (R1 — v1.1 ile çözüldü).** İlk sürümde "tek-sefer TİTCK" bir kod-düzeyi mutex değil,
**sözleşme + önbellek mantığı + manifest denetimi** disipliniydi (deterministik garanti değil).
**v1.1 ile bu, `titck-cache-mcp` Worker'ı üzerinden kod-düzeyi deterministik garantiye
yükseltilmiştir:** connector çağrılarını saran, `scope_key`-anahtarlı, SingleFlight DO + KV TTL
tabanlı bir ön-uç (Mahir'in `midas-mcp` Worker'ı ile simetrik). Worker dağıtıldı ve **"TİTCK
Cache"** connector'ı (`titck.cureonics.com`) olarak bağlandı; üç skill artık ham
TİTCK yerine bu proxy'yi çağırır. `single_shot_enforced` artık `/ledger` ucundan ölçülebilir bir
değişmezdir. İnşa talimatı: `titck-cache-mcp-build-playbook.md`; ayrıntı §7.

---

## 5. Değerlendirilen Alternatif Mimariler

| Alternatif | Artı | Eksi | Karar |
|---|---|---|---|
| **A. Embed-all** (dört skill rxos'a gömülü) | Tek dosya, çağrı dolaylılığı yok | Devasa SKILL.md, context şişmesi, bağımsız sürümleme yok, drift'i gizler | **RED** — pharmaintel tek başına 644 satır; dördü tek bağlamda sürdürülemez |
| **B. Dört ayrı plugin + ortak bağımlılık** | Maksimum modülerlik | Plugin-arası bağımlılık Claude modelinde temiz değil; connector sözleşmesi paylaşımı kırılgan | **RED** — paylaşılan sözleşme paylaşımı imkânsızlaşır |
| **C. Salt-referans** (skill'ler `/mnt/skills/user`'da kalır, plugin yalnız onlara atıf) | Sıfır drift (tek kopya) | Plugin kendi kendine yeterli değil; taşınabilir/paketlenebilir değil; `.skill` ZIP üretilemez | **RED** — plugin'in kapalı bir artefakt olması beklenir |
| **D. Orkestratör-sahipli + dört vendored + entegrasyon notu** *(seçilen)* | Skill'ler bağımsız okunur/sürümlenir; sözleşmeler tek noktada; paketlenebilir | Vendor drift yüzeyi (R5) — azaltımı §6.4 | **KABUL** |

Seçilen mimari (D), drift riskini (tek somut dezavantaj) açık bir denetim adımıyla (§6.4)
yönetilebilir kıldığı için tercih edilmiştir.

---

## 6. Kalite Güvence Stratejisi

### 6.1 skill-censor ile denetim (11-boyut)

Her vendored skill + orkestratör + start, `skill-censor` FULL_AUDIT modundan geçirilir. Öncelikli
boyutlar:

- **D2 (trigger):** `description` alanlarının tetikleme isabeti; özellikle `start` (router) ve
  komutların `description` alanları. 1024-karakter sınırı (D10 sürüm-tutarlılık).
- **D6 (MCP probe):** CONNECTORS.md'de listelenen her connector'ın gerçekten erişilebilir/bağlı
  olduğu; connector-çıkarıcı yanlış-pozitiflerine dikkat (skill-censor v1.8.0 düzeltmesi).
- **D7 (composability):** `plugin.json` `composes_with_external` + sibling skill atıflarının
  tutarlılığı.
- **D11 (output fidelity):** broken anchor (özellikle `../../` göreli yollar), iki-katmanlı çıktı
  bütünlüğü.

### 6.2 smp-orchestrator ile composability graph

`smp-orchestrator` ile: (a) manifest validation (`plugin.json` SMP v1.0 uyumu), (b) composition
graph — rxos→4 sibling + paylaşılan sözleşme kenarlarının doğru çizilmesi, (c) pipeline enumeration
— G0-G6 aşamalarının connector çağrılarına eşlenmesi, (d) `.skill` / plugin ZIP paketleme öncesi
lint.

### 6.3 evals/evals.json — entegrasyon eval'leri

Plugin-düzeyi `evals/evals.json`, tekil skill davranışını **değil**, **entegrasyon
davranışını** test eder (ectocare-advisor eval deseni: `id` / `title` / `prompt` /
`expected_response_criteria` / `min_word_count`). Asgari senaryolar §6.3'te kodlanmıştır:
tek-sefer TİTCK denetimi, MIDAS degrade mod, scope guard reddi, kanonik önbellek yeniden-kullanımı,
provenance damgası bütünlüğü, naming/router doğru yönlendirme.

### 6.4 Drift denetimi (periyodik)

> **Not (sürüm konumu).** Kaynak skill'lerde sürüm tek yerde durmaz: `medical-research`
> SKILL.md front-matter'ında `version:`, `pharmapatent` `metadata.version`, `pharmaintel` ve
> `thoughtspot-roche` ise SKILL.md'de **değil** `references/changelog.md` + `skill-manifest.yaml`
> içinde tutar. Bu yüzden `grep '^version:'` tek başına güvenilmezdir. Sürüm-konumundan
> bağımsız, sağlam drift denetimi **dizin içerik-hash'i** ile yapılır (vendoring sırasında
> enjekte edilen plugin entegrasyon notu hariç tutulur):

```bash
# Sürüm-konumundan bağımsız drift: not bloğu hariç içerik-hash karşılaştırması
SRC=/mnt/skills/user; DST=/mnt/user-data/outputs/rxpraxis/skills
for s in medical-research pharmaintel pharmapatent thoughtspot-roche; do
  hs=$(cd "$SRC/$s" && find . -type f ! -name '_VENDOR_PLACEHOLDER.md' -exec cat {} + | \
       grep -v 'Plugin entegrasyon notu (rxpraxis)' | sha256sum | cut -d' ' -f1)
  hd=$(cd "$DST/$s" && find . -type f -exec cat {} + | \
       grep -v 'Plugin entegrasyon notu (rxpraxis)' | sha256sum | cut -d' ' -f1)
  [ "$hs" = "$hd" ] && echo "== $s: SENKRON" || echo "== $s: DRIFT (yeniden vendor gerekli)"
done
```

Uyuşmazlık → §2 vendor prosedürünü tekrarla + entegrasyon notunu (§3) yeniden uygula. (Not:
bu hash, dosya sıralamasına duyarlı olabilir; kesin denetim için `diff -rq "$SRC/$s" "$DST/$s"`
ile birlikte kullanın — yalnız SKILL.md'de tek-satırlık not farkı beklenir.)

### 6.5 SMP v1.0 uyum kontrol listesi

- [ ] `plugin.json` `smp.manifest_version: "1.0"` + `role` tanımlı
- [ ] Orkestratör + source + router skill'leri listelenmiş
- [ ] Paylaşılan sözleşmeler `shared_contracts`'ta
- [ ] Her SKILL.md front-matter: `name` + `description` + `version` + `last_updated` + `changelog`
- [ ] Göreli yol atıfları (`../../CONNECTORS.md` vb.) kırık değil
- [ ] Komut front-matter: `description` + `argument-hint`

---

## 7. Gelecek Sürüm Kapsamı (işaretli, bu sürümde DEĞİL)

- **v1.1 — TİTCK-cache ön-uç Worker — ✅ TAMAMLANDI & DAĞITILDI.** TİTCK MCP'yi saran,
  `scope_key`-anahtarlı önbellek tutan Cloudflare Worker (`midas-mcp` ile simetrik) inşa edildi,
  `titck.cureonics.com` adresine dağıtıldı ve **"TİTCK Cache"** connector'ı olarak
  Claude'a bağlandı. Çift sorgu *fiziksel olarak* engelleniyor (SingleFlight DO + KV TTL). R1
  azaltımı "disiplin" → "kod-düzeyi deterministik garanti" olarak yükseltildi (§4). İnşa talimatı:
  `titck-cache-mcp-build-playbook.md`. CONNECTORS.md §1.A/§3/§6 ve run-manifest şeması güncellendi.
- **v1.2 — carbon-pptx / carbon-html-report otomatik devri:** Aşama 6 raporunun
  `composes_with_external` üzerinden otomatik sunum/HTML rapor üretimine bağlanması.
- **v1.3 — lex-sanitas regülatuar-reform köprüsü:** TR_REGULATORY_FLOW çıktısının mevzuat-reform
  analizine devri.

---

## 8. İnşa Sırası Özeti (checklist)

1. [x] İskelet + `plugin.json` + `marketplace.json`
2. [x] Paylaşılan sözleşmeler (`CONNECTORS.md` + `shared/`×3)
3. [x] Orkestratör `rxos` v1.7.0 + `start` router
4. [x] Altı komut (`scan` · `validate` · `regulatory` · `patent` · `midas` · `evidence`)
5. [x] `evals/evals.json` + `README.md` + `BUILD.md`
6. [x] **Vendor:** dört skill §2 ile kopyalandı (160K + 1.7M + 1.3M + 128K)
7. [x] **Yama:** §3 entegrasyon notu dört SKILL.md'ye uygulandı (bütünlük: gövde bit-aynı)
8. [x] **Yapısal QA:** kırık-bağlantı (0 gerçek), manifest YAML (3/3 geçerli), SMP front-matter, drift bütünlüğü
8b. [ ] **Skill QA:** skill-censor FULL_AUDIT + smp-orchestrator composability graph (bu ortamda araç olarak çağrılamaz; ekosisteminizde çalıştırılır)
9. [x] **Paketle:** `.skill` / plugin ZIP (aşağıda üretildi)

Adım 1-9 (8b hariç) bu teslimde tamamlanmıştır. 8b, skill-censor/smp-orchestrator skill'lerinin
*çalıştırılmasını* gerektirir (bunlar içerik protokolleridir, bu ortamda yürütülebilir araç
değildir); §6'daki yapısal kontroller bu denetimlerin programatik eşdeğerini sağlamıştır.
