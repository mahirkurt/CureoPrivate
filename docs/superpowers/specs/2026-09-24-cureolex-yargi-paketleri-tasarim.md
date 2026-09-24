# cureolex 4.0 — Çekirdek / Yargı Bölgesi Paketi Ayrımı

**Tarih:** 2026-09-24 · **Hedef sürüm:** cureolex 3.9.0 → 4.0.0 · **Dal:** `feat/cureolex-jurisdiction-packs`
**Girdi:** kullanıcının "Diğer ülkelere taşımak bir yeniden mimarlama işidir" planı (9 öneri, 4 faz).

## 1. Planın teşhisi — dosyalara karşı doğrulama

Plan uygulanmadan önce her teşhis iddiası diskteki dosyalarla karşılaştırıldı.

| # | Plan iddiası | Ölçüm | Sonuç |
|---|---|---|---|
| 1 | 31 dosyanın 29'unda TR terimi | `references/` + `templates/` = 31 dosya, **31'inde** TR terimi | **Doğru yönde, daha güçlü** |
| 2 | `jurisdiction` 12 değerli kapalı liste, `id_kind` kapalı | `EU CH DE FR UK US CA AU JP TR WHO INTL` (12) · `id_kind` 11 değer | **Birebir doğru** |
| 3 | Kaynak kaydı katman eksenli; anayasa 1, birincil mevzuat 7 | `constitution: 1` · `primary_legislation: 7` | **Birebir doğru** |
| 4 | G1, G2, G3, G8 Türk normuna bağlı | doğru — **ama G4 (TR anti-pattern listesi) ve G5 (AYM/Danıştay/Yargıtay) de bağlı** | **Eksik** |
| 5 | "G7/G10/G11 doğrulayıcı", "G10 güncellik kapısı" | cureolex'te **yalnız G0–G9 vardır**. G10–G16 **socius-vigil** plugin'ine aittir | **YANLIŞ — iki plugin'in numaralandırması karışmış** |
| 6 | "Mevcut 61 test vakası" | `tests/*.yaml` = **98 vaka / 7 süit** | **YANLIŞ sayı** |
| 7 | "AU" hem Avustralya hem Afrika Birliği olamaz | ISO 3166-1'de `AU` = Avustralya | **Doğru** |

### Kapı numaralandırması (madde 5'in sonucu)

cureolex'te G10 ve G11 bulunmadığı için yeni kapılar **sıradaki numaraları** alır:

| Plandaki ad | cureolex 4.0 |
|---|---|
| "G10 güncellik kapısı" (var sanılan) | **G10 — Güncellik / belirli-tarihte-yürürlük** (YENİ) |
| "G12 yargı bölgesi tutarlılığı" | **G11 — Yargı bölgesi tutarlılığı** (YENİ) |

Plan G12 demişti; G10/G11 boş bırakılıp G12 açmak numaralandırmada delik bırakırdı.

### Doğrulanan dış olgular (plugin'e girmeden önce)

- **ISO 3166-1:** `EU` ve `UK` *istisnaen ayrılmış* kodlardır (UK, Birleşik Krallık'ın talebiyle; resmî
  alfa-2 kodu `GB`). Kullanıcı-atanabilir aralık: `AA`, `QM–QZ`, `XA–XZ`, `ZZ`. [Wikipedia ISO 3166-1 alpha-2]
- **WHO GBT:** RS (ulusal düzenleyici sistem) + sekiz işlev: **MA** (kayıt ve pazarlama izni),
  VL (vijilans), MC (piyasa gözetimi), LI (tesis ruhsatı), RI (düzenleyici denetim), LT (laboratuvar),
  CT (klinik araştırma denetimi), LR (seri serbest bırakma). Olgunluk 1–4; düzey 3 = "istikrarlı, iyi
  işleyen ve bütünleşik düzenleyici sistem" (asgari hedef). Rev VI incelemesinde **268 alt gösterge**
  (PAHO "yaklaşık 300" der — revizyona bağlı). [Frontiers Med 2020;7:457]
  - ⚠️ Bellekte "RL" vardı; doğrusu **MA**. Doğrulama olmasaydı plugin'e yanlış kod girerdi.

## 2. Kapsam — neyin bu sürümde yapıldığı, neyin yapılamayacağı

Plan 12+ aylık, bir kısmı kod olmayan bir yol haritasıdır. Kod olarak uygulanabilen her şey bu
sürümde yapılır; insan, kurum veya dış veri gerektiren kalemler **açıkça ertelenir** ve uydurulmaz.

| Öneri | Bu sürümde | Ertelenen / kod dışı |
|---|---|---|
| 1 Çekirdek–paket ayrımı | `jurisdictions/` · paket şeması · TR ilk paket (aktif) · kapılar paket parametreli · mod adları genelleşti (`PARLIAMENTARY_BILL`, TR takma adı korundu) | Dosyaların fiziksel taşınması (Faz 0b — yol değişikliği gerilemesi riski) |
| 2 Kimlik modeli | `jurisdiction` ISO 3166-1/2 + `ORG:` ulusüstü ad alanı · `id_kind` += `akn`/`ecli`/`urn-lex` + `x-` uzantısı | AKN **dönüştürücü motoru** (ayrı bir proje) |
| 3 Bağlayıcı sözleşmesi | soyut erişim arayüzü · TR mevzuat MCP eşlemesi · A/B/C düzeyleri (kayıttaki "D-sınıfı" ≈ B) | Yeni ülke adaptörleri (mcp-builder işi) |
| 4 Yetenek bayrakları + güven tavanı | beş bayrak · tavan kuralları (veri) · doğrulayıcı hesaplar | — |
| 5 Yargı tutarlılığı kapısı | **G11** + defter alanları | — |
| 6 Evrensel legistik rubrik | 12 aile · R6b'nin 21 kontrolü eşlendi · TR parametreleri | UK/DE/FR kılavuz içerikleri (plan bunları doğrulamadığını söyledi) → `unverified` |
| 7 GBT / aktarım / reliance modları | üç mod · şablon · işlev iskeleti (doğrulanmış 9 işlev) | GBT gösterge veri seti (WHO kaynağı gerekir) · DOG pilotu |
| 8 HTA / maliyet | paket kurum haritası · evidentia'ya bağlamla aktarım · bağlam-uygunluk kontrolü | evidentia plugin kodu (ayrı plugin) |
| 9 Doğrulama + yönetişim | TR altın/adversarial vakalar · paket doğrulayıcı · yayım kuralı | uzman paneli · yerel hukuk ortağı · lisans/vakıf · CETS 225 etki değerlendirmesi · konteyner dağıtımı |

**Faz 1 paketleri (GB · DE · CH):** `status: draft` olarak iskelet hâlinde eklenir; yetenek bayrakları
mevcut bağlayıcıların **ölçülmüş** durumundan türetilir. Uzman paneli değerlendirmesi olmadan `active`
olamazlar — doğrulayıcı bunu zorlar.

## 3. Faz 0 çıkış ölçütü (düzeltilmiş)

Planın ölçütü "mevcut 61 test vakası değişmeden geçer" idi; gerçek sayı **98**. Ölçüt:

- `tests/run_suites.py` → mevcut **98 vaka** değişmeden geçer (yeni vakalar eklenebilir).
- `hooks/test_hooks.py` → başlangıçta **120 PASS / 1 FAIL**. Tek FAIL önceden vardı
  (`fleet.lock.json 22 sunucu` bekliyor; `adecc17` bir bağlayıcıyı kaldırdı, lock 21). Sabit sayı
  kilitten türetilecek şekilde düzeltilir — plan zaten "sayı tutarsızlıklarının giderilmesi"ni içerir.
- `check_drift --all` ve `check_marketplace` temiz.
- Türkiye'de gerileme yok: TR paketi mevcut davranışın **birebir** tanımıdır.

## 4. Bilinen belge tutarsızlığı (bu işin dışında, raporlanır)

İlk taslakta "SKILL.md bayat" diye yazmıştım — **yanlıştı.** `fleet.yaml`'daki `uk-legal` kaydı UK
`legislation_search → _get_toc → _get_section` zincirinin **2026-08-18'de düzeltildiğini** söyler
(kök neden: pinli paketin `curl_cffi impersonate=chrome` istemcisi HTTP 437 veriyordu; loopback
`legislation_http_fix` httpx + tarayıcı-benzeri UA ile değiştirdi) ve doğrular: Medicines Act 1968 →
`ukpga/1968/67`, s.1 metni.

Bayat olan **CureoHub `CLAUDE.md`** — hâlâ 2026-08-08 tarihli "legislation_* bilinçli olarak bağlanmadı,
kırık ölçüldü" notunu taşıyor. SKILL.md ve `fleet.yaml` günceldir. GB paketi wire'lı `uk-legal`
`legislation_*` zincirine dayanır; yedek `ep.legislation_uk` (`/data.akn`).

Bu, CureoHub'ın düzeltilmesi gereken bir belge borcudur (bu dalın kapsamı dışında).

## 5. Uygulama sonucu (2026-09-24)

### Yetenek bayrakları — bu oturumdaki birincil kaynak ölçümleri

| Paket | Ölçüm | Sonuç | Bayrak |
|---|---|---|---|
| GB | `legislation.gov.uk/ukpga/1968/67/section/1/2000-01-01/data.xml` | 200 · `dct:valid 1999-12-27` | `has_point_in_time: true` (yol `ep.legislation_uk`, wire'lı araç değil) |
| GB | `/ukpga/2012/7/notes/contents` | 200 · "Health and Social Care Act 2012 - Explanatory Notes" | `has_explanatory_memoranda: true` |
| CH | Fedlex SPARQL, `eli/cc/2001/422` üyesi `jolux:Consolidation` | 23 | `has_point_in_time: true` |
| CH | `/eli/cc/2001/422/de` | 200 | `has_authentic_translation: true` (de/fr/it) |
| CH | Botschaft getirimi (`fedlex_search_gazette`) | ölçülmedi | `has_explanatory_memoranda: false` (ölçülene dek) |
| DE | `gesetze-im-internet.de` | 000 (bu makineden erişilemedi) | bayraklar `fleet.yaml` german-law ölçümlerinden; `has_point_in_time: false` (premium-kapalı) |

### Doğrulama

- `tests/run_suites.py` → **110 vaka / 8 süit temiz** (98 mevcut vaka değişmeden geçti + 12 TR altın/adversarial).
  İki negatif şema vakası (TR-ADV-002 uydurma RG sayısı `verified` işaretli; TR-ADV-005 rolsüz yabancı kaynak)
  şemadan **düşüyor** — koşucu düşmezlerse "negatif vaka etkisiz" diye kırmızı verir.
- `tests/validate_packs.py` → 4 paket temiz. **Mutasyon sınaması: 8/8 enjekte kusur yakalandı** (taslak paketi active
  yapma · sahipsiz dosya · G11 beklenti sapması · parça aynası sapması · yanlış aileye K eşleme · dayanaksız bayrak ·
  companion'ı wired işaretleme · `UK` paket kodu).
- `hooks/test_hooks.py` → **121 PASS / 0 FAIL** (başlangıçtaki tek FAIL — sabit "22 sunucu" — kilit listesi ve
  `.mcp.json` ile çapraz türetildi).
- `check_drift --all` + `check_marketplace` temiz; `gen_fleet --check` temiz.

### Uygulama sırasında verilen kararlar

| Karar | Gerekçe | Yanlışsa maliyeti |
|---|---|---|
| Bayrak = "kaynak yayımlıyor **ve** filoda getirim yolu ölçüldü" | Şema tanımı yalnız "yayımlıyor" diyordu; ölçülmemiş yol iyimser beyana döner | CH/DE'de tavan gereğinden düşük — ölçüm yapılınca bayrak açılır |
| G11 statik denetimi AB üyeliğini paket alanından okur (`gate_params.G11.eu_member`) | AB tüzüğü DE'de binding, TR'de değil — kural koda gömülürse ikinci AB üyesi pakette yanlış-pozitif | Yeni AB üyesi paket bayrağı unutursa AB normu yanlışlıkla ihlal sayılır (kırmızı, sessiz değil) |
| `medical_sidecar` ve `confidence_label` cureolex sürüm deseni `^[2-9]\.` | 3.x'te zaten bayattı (`^2\.` / `^[23]\.`) — 4.0.0 çıktısı şemadan düşerdi | yok |
| Mod 10–12 sunucu kapsamı `fleet.yaml`'a işlendi (matris üretilir) | Düzyazıda tutmak matrisle sürüklenirdi | — |
| Web yüzeylerinde (skill-only yükleme) `jurisdictions/` yok → varsayılan TR davranışı | Skill paketini yeniden yapılandırmak kapsam dışı | claude.ai'de GB/DE/CH paketleri kullanılamaz — README'de beyan edildi |
