# Değişiklik Günlüğü — carbon-edupedia

Bu proje [Semantik Sürümleme](https://semver.org/lang/tr/) kullanır.

## [3.2.0] — 2026-07-12

### Düzeltildi (kök neden) — `quality_gates` için deterministik köprü: `validate_module.py --json`

İnceleme bulgusu: 3.1.0'da manifest'in `quality_gates` alanını yayın-sunucusunun fail-closed
kalite kapısı besliyordu, ama `scripts/validate_module.py` yalnız ANSI-renkli konsol raporu
basıyordu — hiçbir JSON/yapılandırılmış çıktı modu yoktu. SKILL.md "`quality_gates` yalnız
`validate_module.py`'nin gerçek çıktısından doldurulur — uydurulmaz" diyordu ama bunu hiçbir
kod yolu ZORLAMIYORDU: model konsol metnini okuyup JSON'a elle transkribe ediyordu. Somut risk:
model betiği hiç çalıştırmadan (ya da yanlış okuyarak) tüm kapılara `"PASS"` yazabilir —
sunucunun fail-closed mantığı bunu yakalayamaz (girdi zaten "PASS" görünür), emojili/
erişilemez/kazanım-izlenemez bir modül siteye düşebilirdi. Bu davranışsal bir değişikliktir
(yeni CLI yeteneği, mevcut davranış korunur) → **SemVer MINOR bump**.

- **`scripts/validate_module.py` — yeni `--json` bayrağı:** stdout'a YALNIZ geçerli JSON
  basar — `{"G-EMOJI": {"status": "PASS"}, "G-A11Y": {"status": "FAIL", "detail": "..."}, ...}`
  — manifest `quality_gates` alanına doğrudan gömülebilir biçimde. `status` yalnız
  `PASS`/`FAIL`/`WARN`/`SKIPPED` olur; koşturulmayan/uygulanamayan bir kapı (imza yok /
  mod uymuyor / uygulanmaz dalı) `--json` çıktısında **her zaman `SKIPPED`** yazılır — iç
  konsol mesajı "PASS" dese bile (bu ayrım `Result.add(..., applicable=False)` ile izlenir;
  `R.rows`'un 3'lü tuple şekli — mevcut testlerin `for g,s,_ in rows` açımı için — DEĞİŞMEDİ).
  Aynı gate adı altında birden çok satır üreten tek kapı (`G-INTERACT`: correctIndex
  PASS/FAIL + opsiyonel açıklama-WARN'ı) en kötü duruma (FAIL>WARN>PASS) göre birleştirilir.
  Varsayılan (bayraksız) insan-okur konsol raporu ve çıkış kodu sözleşmesi (0=tüm FAIL
  kapıları geçti, 1=ihlal) **birebir** korunur — `--json` yalnız ek bir moddur.
- **`SKILL.md` §3 (madde 7) + Adım 5-6 + §12** — `quality_gates` alanının normatif tanımı
  değişti: artık `python scripts/validate_module.py --json <html>` çıktısının BİREBİR
  kendisi olarak tanımlanır ("elle yazma, konsol raporundan transkribe etme, hiçbir kapıyı
  PASS'a yükseltme").
- **`commands/modul.md` (Adım 5) + `commands/mufredat.md` (Adım 4)** — aynı normatif
  `--json` köprüsüne güncellendi; `mufredat.md`'deki eski "11 kapı" ifadesi mevcut 13 kapıya
  düzeltildi (davranışsal değil, belge tutarlılığı).
- **`shared/run-manifest-schema.json`** — `gate.status` enum'u zaten `PASS`/`FAIL`/`WARN`/
  `SKIPPED` idi (dokunulmadı — şema önceden de doğruydu, yalnız üretim tarafında zorlanmıyordu).
- **`skill-manifest.yaml`** — yeni `verification.json_output` girdisi; `outputs.run_manifest`
  açıklaması `--json` köprüsünü yansıtacak şekilde güncellendi; `skill.version` +
  `build.version` → 3.2.0.
- **`README.md`** — sürüm damgası 3.2.0'a hizalandı.

**Değişmedi:** 13 kalite kapısının adları, mantığı ve varsayılan konsol raporu (`R.report()`)
birebir korunur; `assets/module-template.html`; etkileşim motoru; pedagojik içerik;
`tests/test_gates.py`'nin tamamı (70 test) hiçbir değişiklik olmadan yeşil kalır.

## [3.1.0] — 2026-07-12

### Düzeltildi (kök neden) — run-manifest artık DİSKE yazılıyor (`/edupedia:yayinla` kırıktı)

`/edupedia:yayinla` komutu, üretilen HTML'in yanında bir run-manifest JSON'u bulmayı bekliyordu,
ama üretim zincirinin (`SKILL.md` §3 çıktı sözleşmesi, `commands/modul.md`, `commands/mufredat.md`,
`scripts/validate_module.py`) HİÇBİR ADIMI manifesti diske yazmıyordu — yalnız `.html` kaydediliyor,
kalite kapısı sonuçları yalnız konsola basılıyordu. Sonuç: `/edupedia:modul` koşumundan sonra
`/edupedia:yayinla` her zaman "manifest yok" dalına düşüyor, kullanıcıyı elle-CLI'ye yönlendiriyordu
(orada kalite kapıları `SKIPPED` yazılır) — "gerçek kalite-kapısı sonucuyla otomatik yayın" özelliği
fiilen çalışmıyordu. Bu davranışsal bir değişikliktir (yeni zorunlu artefakt) → **SemVer MINOR bump**.

- **Dosya adı sözleşmesi netleştirildi (tek tanım yeri):** üretilen HTML `<ad>.html` ise run-manifest
  **`<ad>.manifest.json`** (aynı dizin, yan yana) — sabit `run_manifest.json` adı **kullanılmaz**
  (çok-modüllü dizinlerde belirsizlik yaratmaz). Normatif tanım: `shared/canonical-cache-contract.md §1`;
  şema `shared/run-manifest-schema.json` (ve description'ı) bu sözleşmeye atıf yapacak şekilde güncellendi.
- **`SKILL.md` §3 (Çıktı sözleşmesi)** — madde 7 eklendi: üretim artık HTML ile birlikte
  `<ad>.manifest.json`'ı da yazar; `quality_gates` **yalnız** `scripts/validate_module.py`'nin gerçek
  çıktısından doldurulur (uydurma yok — koşulmayan kapı `SKIPPED`). Adım 6 (Kaydet ve sun) manifest
  yazma adımını yansıtacak şekilde güncellendi.
- **`commands/modul.md`** — yeni Adım 5 ("Manifest'i yaz") eklendi; yayın teklifi bölümünden ÖNCE
  gelir (yayın ona dayanır).
- **`commands/mufredat.md`** — Adım 4, `/edupedia:modul`'ün 2-5. adımlarını (manifest yazma dahil)
  uygulayacak şekilde güncellendi.
- **`commands/yayinla.md`** — manifest yolu iddiası netleştirildi: varsayılan ve tek sözleşme
  `<html-adı>.manifest.json`; bulunamazsa kullanıcıya sor / elle-CLI'ye yönlendir (mevcut
  no-fabrication davranışı korunur).
- **`skill-manifest.yaml`** — yeni `outputs.run_manifest` girdisi (mime `application/json`);
  `skill.version` + `build.version` → 3.1.0.
- **`README.md`** — carbon-edupedia sürüm damgası 3.1.0'a hizalandı; Yayınlama bölümüne
  manifest-yazma adımının açıklaması eklendi.

**Değişmedi:** `scripts/validate_module.py` kapı mantığı (13 kapı davranışı birebir korunur —
yalnız çıktısı artık ayrıca manifest'e de yazılıyor); `assets/module-template.html`; etkileşim
motoru; pedagojik içerik.

## [3.0.0] — 2026-07-07

### edupedia 3.0.0 — derin motor + şema yükseltmesi (23 görevlik seri)

Marka yeniden adlandırması + beş yeni segment tipi + iki yeni kalite kapısı +
oyunlaştırma/erişilebilirlik/kalıcılık genişlemesi. **Davranış geriye-uyumludur:**
mevcut 8 mod ve orijinal 11 kalite kapısı **korunur** (additif) — hiçbir mevcut
alan/segment/kapı kaldırılmadı ya da anlamı değiştirilmedi; yeni alanların
tamamı opsiyoneldir ve yoklukları eski modüllerde davranışı **birebir** aynı
bırakır (bkz. her maddenin geriye-uyum notu).

**Marka yeniden adlandırması**
- `paideia` → `edupedia`, `carbon-paideia` → `carbon-edupedia` (plugin dizini,
  skill adı/namespace, komut önekleri, sürüm damgaları). Bu CHANGELOG'un kendi
  geçmiş girişleri de dahil (`carbon-paideia`/`paideia` prose'u) rebrand edildi.

**Eklenen — 5 yeni segment tipi (`assets/module-template.html` + `references/module-architecture.md`)**
- **`hook`** — merak-boşluğu (curiosity-gap) kancası; `resolvesIn` hedeflediği
  `teach` render edilince **aynı akış içinde** kapanır (`data-hook-resolved`).
- **`worked`** — soluk-çözümlü örnek (fading worked example); `fadeFrom`
  altındaki adımlar salt-görünür, üzerindekiler `<input>` boşluğu + tek "Kontrol
  et" ile toplu değerlendirilir (math g=0.48, çözümlü-örnek ailesinin en güçlü
  alt-özelliği — Barbieri 2023).
- **`selfExplain`** — düşük-baskı öz-açıklama; serbest/notsuz taslak + isteğe
  bağlı model-açıklama aç/kapa. **Puanlama/XP/ceza YOK**, "Devam" koşulsuz etkin.
- **`sim`** — parametrik simülasyon/sanal manipülatif; 5 motor-içi SABİT preset
  (`pendulum`, `projectile`, `wave`, `numberScale`, `functionPlot` — `SIM_PRESETS`).
  `MODULE_DATA` yalnız `simType`+`params` seçer, hiç render kodu taşımaz; bilinmeyen
  `simType` → nazik/uydurmasız not, çökme yok. Keşfedici/puanlanmaz.
- **`conceptMap`** — kavram haritası kurucu; düğümler gerçek `<button>` (klavye
  yolu **zorunlu ve TEK yol** — sürükle-bırak hiç eklenmedi); kenarlar sırasız
  karşılaştırılır (`[A,B]`≡`[B,A]`); tam eşleşince (eksiksiz+fazlasız) tek seferde
  ödüllendirilir (`worked` ile aynı toplu-değerlendirme ilkesi).
- Ayrıca **`numberline`/`numberLine(spec)`** `interactive:true` genişlemesi:
  bayrak yoksa üretilen SVG byte-için-byte önceki sürümle aynıdır; bayrak varsa
  klavye-zorunlu (`role="slider"`, Ok tuşları/Home/End) bir tutamaç eklenir.

**Eklenen — 2 yeni kalite kapısı (`scripts/validate_module.py` → 11 → 13 kapı)**
- **G-FLOW** (koşullu — gamification imzası yoksa atlanır): açık kalan
  merak-boşluğu, kayıp-cezalandırıcı seri dili, uyarlanır-zorluk etiketlemesi,
  kaygılı (geri-sayımlı) tempo diski FAIL üretir.
- **G-CARBON-GRID**: statik kart/segment/tile'da gerçek (non-inset) `box-shadow`
  = layer-elevation ihlali (FAIL); 2×-grid konteyneri, en-boy oranı
  (`aspect-ratio`), >500ms koreografi eksikliği = WARN.

**Eklenen — oyunlaştırma/motivasyon genişlemesi**
- **Gain-only streak**: `resetStreak()` artık `state.streak`'i sıfırlamaz;
  yalnızca nötr "korundu" (`data-held`) işaretine alır — kayıp/ceza dili yok.
- **Stepper kilometre taşları + hedef-gradyanı**: `meta.milestones[]` →
  ilerleme rayında aksan noktası; son 1-2 segmentte "Son N durak" ipucu.
- **Opt-in tempo diski** (`learner.pacingDisk`, varsayılan **KAPALI**):
  geri-sayımsız/kaygısız, kapatılabilir.
- **Sefer mini-haritası** (`meta.quest.stations[]`): bahşedilmiş ilerleme
  (station 1 tamamlanmış başlar), gölgesiz/token'lı.

**Eklenen — görünmez taban-korumalı uyarlanır zorluk**
- `mcq.questions[]`/`fillblank.items[]` opsiyonel `tier?:1|2|3`. `state.perf`
  yuvarlanan penceresi: 2 ardışık yanlış-sonra-doğruda ipucu-önce + en-düşük-
  kalan-tier tercihi; 2 ardışık ilk-denemede-doğruda opsiyonel/atlanabilir
  "Meydan Oku" daveti. Kullanıcıya **hiçbir** görünür zorluk-etiketi yazılmaz
  (`FLOW_LABEL_RE` motor kaynağının kendisinde de eşleşmez).

**Eklenen — kalıcılık ve erişilebilirlik**
- **Çapraz-oturum Leitner** (flashcards): kutu 1–5, `localStorage` (try/catch
  degrade-safe, IndexedDB YASAK), modül-kimliği `D.meta.title`'dan türetilir.
- **Native MathML**: `visual:{kind:"mathml"}` → `mathmlFigure()`; `.body` zaten
  ham innerHTML olduğundan `<math>` motor değişikliği olmadan render olur.
- **TTS kapsamı genişletildi**: `hook`/`worked`/`selfExplain`/`sim`/`conceptMap`
  render'larının tamamı `ttsRow(...)` taşır.

**Eklenen — 3 yeni referans dosyası**
- `references/content-enrichment.md` — entegre-edilebilir zenginleştirme
  kaynakları + yapılamaz listesi.
- `references/carbon-excellence.md` — 15-madde uzman-vs-jenerik Carbon
  checklist'i; G-CARBON-GRID'in normatif kaynağı.
- `references/gamified-flows.md` — 4 akış şablonu (Keşif Döngüsü, Sefer,
  Antrenman, Birlikte Odak) + atıflı YAPMA listesi; G-FLOW'un normatif kaynağı.

**Eklenen — agent + hook'lar (plugin düzeyi)**
- `agents/module-auditor.md` — 4 eksenli statik+canlı denetim (validate_module
  13-kapı + carbon-excellence 15-madde + gamified-flows A/B/C/D + wellbeing/
  kaynak-sadakati); static G-FLOW'un SPA'da yakalayamadığı canlı akış
  değişmezlerini (hook kapanışı vb.) tamamlar.
- `hooks/hooks.json` + `preflight.sh` + `validate-module.sh` — `SessionStart`
  ve `PostToolUse` (Write|Edit) tetikleyicileri; her ikisi de **fail-open**
  (hiçbir yol kullanıcı akışını bloklamaz).

**Entegrasyon (bu sürüm)**
- `assets/module-template.html` demo `MODULE_DATA`'sına beş yeni segmentin
  birer canlı, kaynağa-sadık örneği eklendi (hook, worked, selfExplain,
  sim:numberScale, conceptMap) — şablon artık **13/13 kalite kapısından 0
  İHLAL, 0 uyarı** ile geçiyor (`tests/test_gates.py::test_full_template_passes_13_gates_with_new_segments`).
- `shared/run-manifest-schema.json` `quality_gates` bloğuna `G-FLOW` +
  `G-CARBON-GRID` eklendi (11 → 13 kapı).

## [2.8.0] — 2026-07-06

### edupedia PLUGIN ENTEGRASYONU

Standalone `carbon-edupedia` skill'i, `edupedia` plugin'inin flagship skill'i olarak paketlendi.
**Davranış / mod sayısı (8) / kalite kapıları (11) / pedagojik içerik / token otoritesi
(`@carbon/*`) DEĞİŞMEDİ** — yalnız sözleşmeler tek noktaya çekildi ve görüntü-dayanak politikası
netleştirildi (kullanıcının `rxpraxis` 1.7.0 dönüşümü felsefesiyle: davranış/kalite kapıları
değişmez, yalnız sözleşmeler merkezileştirilir).

**Değişti — `references/curriculum-integration.md` (cerrahi, additif):**
- §2 (Araç envanteri) başına **plugin-entegrasyon notu** eklendi: connector envanteri, kimlik/PDF
  uyarıları ve provenans standardının normatif kaynağı artık `../../CONNECTORS.md`; bu bölüm oraya
  referans verir (araç tablosu pedagojik referans olarak korundu). Canlı introspeksiyon (2026-07-06)
  otoritatif **21 araç** bildirir — dokümante 19-araç tabanına ek olarak `search_figures` **ve**
  `get_figure` canlıdır.
- **§2.1 Görüntü-dayanak politikası (Tier-1/Tier-2)** eklendi: Tier-1 (yazar-üretimli tema-duyarlı
  SVG + kazanım provenansı) yegâne garanti yol; Tier-2 (`get_figure include_image=true` → resmî
  görsel base64 gömme) best-effort, **yetenek-probuyla** (probe → false-first metadata →
  opportunistic-true → graceful Tier-1 fallback). `svg-authoring.md` doktriniyle tutarlı; herhangi
  bir hatada üretim Tier-1 ile tamamlanır, asla bloke olmaz.

**Değişmedi:** `scripts/validate_module.py` (11 kalite kapısı — G-CURRICULUM + G-SVG dahil),
`SKILL.md` pedagojik içeriği, `assets/`, token otoritesi. Plugin-düzeyi sözleşmeler:
`../../CONNECTORS.md`, `../../shared/canonical-cache-contract.md`, `../../shared/run-manifest-schema.json`.

## [2.7.0] — 2026-06-12

### Düzeltildi (kök neden) — figür yön okları: kendiliğinden hizalanan `vz-arrow` marker'ı

Figürlerdeki yön okları (ör. "Alan birim merdiveni" ×100/÷100) bozuk bir stille
render oluyordu: ok uçları, eğrinin bitiş noktasından/teğetinden elle (göz kararı)
yerleştirilmiş bağımsız `polyline` chevron'lardı; vertex eğriden kayıyor ve geliş
teğetiyle uyumsuz yöne bakıyordu. **Kök neden iki katmanlıydı:** (a) yeniden
kullanılabilir, kendiliğinden hizalanan bir ok-ucu primitifi yoktu; (b)
`references/svg-authoring.md` yazarları açıkça yanlış yönlendiriyordu ("oklar
`marker` yerine kısa `polyline`"). Her iki katman da giderildi.

**Eklendi — `assets/module-template.html` → v1.8.0**
- Global `<defs>` sprite'ına tek bir **`vz-arrow`** ok-ucu marker'ı eklendi:
  `orient="auto"` ile eğrinin bitiş teğetine otomatik döner, `stroke="context-stroke"`
  ile çizginin rengini devralır (tek marker hem mor `--accent` hem gri `--viz-axis`
  oklara hizmet eder). Artık ok-ucu konumu ve yönü garanti edilir.
- Şablonun kendi örnek figürü (su döngüsü: buharlaşma + toplanma okları) ve
  `vizChart` x-ekseni ok ucu, elle `polyline`'lardan `marker-end="url(#vz-arrow)"`
  yöntemine taşındı. **Şablonda artık 0 ad-hoc `polyline` ok ucu var.**

**Düzeltildi — `references/svg-authoring.md`**
- Yanlış "oklar `marker` yerine kısa `polyline`" yönergesi kaldırıldı; yön okları
  için `marker-end="url(#vz-arrow)"` zorunlu kılındı. Yeni **§3.1 "Yön okları —
  `vz-arrow` marker"** bölümü kullanım + gerekçe + yön kuralını (oku istenen yöne
  baktırmak için eğriyi o yönde bitir) belgeliyor.

**Düzeltildi — "Alan Ölçme Birimleri" modülü (örnek çıktı)**
- Merdiven figürünün ×100 (aşağı) ve ÷100 (yukarı) okları temiz çeyrek-tur eğrilere
  + `marker-end="url(#vz-arrow)"`'a çevrildi; ok uçları artık doğru yöne bakıyor,
  eğriye kusursuz bağlı ve tema rengini devralıyor. 11/11 kalite kapısı, 0 uyarı.

## [2.6.1] — 2026-06-12

### Düzeltildi — kod hijyeni + yönetişim (skill-censor PRE_RELEASE remediation)

skill-censor v1.8.0 PRE_RELEASE denetimi (Genel 9.4/10 EXEMPLARY) yalnız
**D5 (Kod Kalitesi) 5.5 < 6.0 tabanı** nedeniyle yayın kapısını engelliyordu;
giderildi. Üretilen modüllerin çıktısı/davranışı değişmedi (yalnız yardımcı
betikler, manifest yapısı ve test fikstürleri).

- **D5 — `scripts/sync_carbon_tokens.py`:** `refresh()` içindeki otorite-JSON
  okuma/yazma I/O'su `try/except OSError` ile sarıldı (önceki 2 MAJOR bulgu);
  tüm genel fonksiyonlara docstring eklendi (%0 → tam kapsam); `check()`
  fonksiyonu `_block_drift` + `_missing` yardımcılarına bölünerek siklomatik
  karmaşıklık 11 → ~5'e indirildi.
- **D5 — `scripts/validate_module.py`:** `gate_token_authority` iç token
  karşılaştırma döngüsü `_classify_token` yardımcısına çıkarılarak karmaşıklık
  13 → ~9'a indirildi; **11/11 kapı davranışı birebir korundu**.
- **D6 — `skill-manifest.yaml`:** `runtime.optional_connectors`,
  SMP-kanonik `runtime.mcp_servers` (`optional:` bucket) yapısına dönüştürüldü;
  böylece Müfredat MCP ve Figma MCP yapısal olarak tanımlı (önceki 3 MINOR
  "tanınmayan connector" bulgusu giderildi). Sunucu meta verisi (`when`,
  `transport`, `tools`) korundu.
- **D9 — `evals/`:** skill-creator metodolojisine uygun `evals.json` (4 vaka:
  MODULE, CURRICULUM, GAME/QUIZ, anti-tetikleyici) + `README.md` eklendi.
- **Yönetişim:** kök `CHANGELOG.md` kanonik `docs/CHANGELOG.md` ile yeniden
  senkronlandı; manifest `build.version` 2.0.0 → güncel sürüme hizalandı.

## [2.6.0] — 2026-06-12

### Geliştirildi — Anahtar kavramlar: dikey düzen (ince başlık üstte) (`assets/module-template.html` → v1.7.0)

"Anahtar kavramlar" bölümü tek satırlık "etiket + çipler" diziliminden, **üstte
ince başlık + altta terim ızgarası** düzenine geçirildi.

- `.terms` artık dikey (`flex-direction:column`): "Anahtar kavramlar" kendi
  satırında **ince başlık** olarak yer alır (font-weight 500, `text-secondary`,
  iki-nokta kaldırıldı), terim çipleri ise **alt satırda** yeni bir
  `.terms__list` ızgarasında (flex-wrap) dizilir.
- DefinitionTooltip, ikon/örnek ve erişilebilirlik davranışı korunur; yalnız
  yerleşim değişti. 11/11 kalite kapısı, 0 uyarı.

## [2.5.0] — 2026-06-12

### Düzeltildi/Geliştirildi — Titiz Carbon uyumluluk denetimi: tipografi, durum çipleri, rozetler (`assets/module-template.html` → v1.6.0)

Tüm stil unsurlarında Carbon v11 uyumluluk denetimi yapıldı ve üç sapma giderildi;
rozet sistemi DEHB-odaklı odaklanma için yeniden tasarlandı.

- **Mono font yalnız sayı/veri/kod.** IBM Plex Mono'nun düz metne sızdığı yerler
  Sans'a çevrildi: `.streak` sayaç kutuları, `.xp` çipi, `.streak-chip`, ve
  `.def-pop__ex-lbl` ("ÖRNEK" eyebrow). Artık yalnız **rakamlar** mono +
  `tabular-nums`; tüm sayaçlarda (`Soru/Cümle/Öğe/İpucu/Öğrenilen N / M`)
  toplam sayı da `<b>` ile sarılarak rakam hizalaması tutarlılaştırıldı.
- **İlerleme/durum çipleri nötr-gri ve kompakt.** `.streak` (örn. "Öğrenilen
  0/4 · Destede 4 kart") aksan-tint/aksan-strong yerine **gri** Carbon
  token'larına alındı (`layer-01` zemin · `border-subtle` kenar ·
  `text-secondary` metin), dolgu küçültüldü. Aksan rengi artık yalnız
  ödül/oyunlaştırma öğelerine (XP, seri çipi, kazanılan rozet) ayrılıyor —
  dikkat içerikte kalıyor.
- **Rozetler modüle özel, çeşitlendirilmiş, Carbon-ikonlu.** Kilitli rozetler
  artık jenerik yıldız yerine **kendi semantik ikonunu** gri tonda + küçük kilit
  rozetiyle gösteriyor; kazanılınca aksana dönüyor. Şema `icon` alanı kazandı
  (`pictogram`'a geriye-uyumlu geri-düşüş). Çalışma modülü rozetleri semantik
  ikonlara bağlandı (Alan Kâşifi → `ic-compass`, Keskin Göz → `ic-view`).
- **4 yeni Carbon rozet ikonu:** `ic-locked`, `ic-trophy`, `ic-target`,
  `ic-compass` (filled, `fill:currentColor`).
- **SKILL.md rehberi.** Mono-font politikası ve nötr durum-çipi kuralı netleştirildi;
  yeni **§11.6 — Rozet ekonomisi** modüle özel, çeşitli, Carbon-ikonlu rozet
  üretimini (palet + koşullar + DEHB gerekçesi) zorunlu kılar.

### Teknik
- Rozet render'ı `icon(b.icon||b.pictogram||"ic-star")` + kilit ikonu + `esc(label)`
  + durum `aria-label`'i kullanır; `.badge--locked`/`.badge__lock` stilleri eklendi.
- Light + g100, header rozet kasası + flashcard ilerleme çipi yeniden doğrulandı.
- Kalite kapıları korunur: **11/11 FAIL kapısı, 0 uyarı**.

## [2.4.0] — 2026-06-12

### Geliştirildi — Anahtar kavram kartına ikon + "Örnek" satırı (`assets/module-template.html` → v1.5.0)

DefinitionTooltip tanım kartı, kavram başına **küçük bir ikon/piktogram** ve
isteğe bağlı bir **"Örnek" satırı** ile zenginleştirildi. `keyTerms` şeması iki
opsiyonel alan kazandı: `icon` (sembol id) ve `example` (örnek metin). Alanlar
opsiyoneldir — verilmezse çip jenerik bilgi (ⓘ) ikonuna ve örneksiz karta düşer
(geriye dönük tam uyumlu). Motor ve kalite kapıları korunur (11/11, 0 uyarı).

- **Kavram ikonu.** Verildiğinde ilgili sembol hem **çipte** (jenerik ⓘ yerine)
  hem **kartın başlığında** (terimle birlikte) gösterilir; her kavram görsel
  olarak ayrışır (DEHB-dostu tanınabilirlik). Sembol id'si `[a-z0-9-]` ile
  sanitize edilir.
- **"Örnek" satırı.** Verildiğinde tanımın altında, ince bir ayraçla ayrılmış,
  `ÖRNEK` etiketli (mono, aksan) bir somut örnek satırı eklenir. `textContent`
  ile yazılır (XSS-güvenli); tema-duyarlı ayraç (`--def-pop-rule`).
- **3 yeni Carbon-stili sembol.** Ölçüm/geometri kavramları için filled SVG
  semboller eklendi: `ic-ruler` (cetvel/ölçme birimi), `ic-area` (birim kare),
  `ic-grid` (birim kareler ızgarası). `fill:currentColor` ile tema/aksan uyumlu.
- **Örnek modül.** "Alan Ölçme Birimleri" modülünün 6 anahtar kavramının tümü
  ikon + örnekle donatıldı (alan→ızgara, metrekare→kare, birim→cetvel, birim
  merdiveni/basamak→artış, dönüşüm→yenile).

### Teknik
- Popover yapısı `.def-pop__head` (ikon + terim) + `.def-pop__ex` (ÖRNEK satırı)
  ile yeniden düzenlendi; `show()` `data-icon`/`data-ex`'i doldurur, örnek yoksa
  satırı gizler.
- Render `data-icon`/`data-ex` taşır ve çipte `icon(t.icon||"ic-info")` basar.
- Light + g100, masaüstü + dar viewport ve klavye odağı yeniden doğrulandı.

## [2.3.0] — 2026-06-12

### Geliştirildi — Anahtar kavramlar: Carbon DefinitionTooltip (`assets/module-template.html` → v1.4.0)

Teach segmentlerindeki "Anahtar kavramlar" çipleri, üzerine gelindiğinde veya
klavye ile odaklanıldığında kavramı tanımlayan bir **tanım kartına** kavuşturuldu.
Önceki ilkel saf-CSS `::after` ipucu (sabit `#393939`, oksuz, ekran kenarında
kırpılan) yerini sağlam, tema-duyarlı bir Carbon **DefinitionTooltip** desenine
bıraktı. `MODULE_DATA` şeması (`keyTerms:[{term, def}]`) değişmedi; motor ve tüm
kalite kapıları korunur (11/11, 0 uyarı; geriye dönük tam uyumlu).

- **Tanım kartı.** Hover/odakta terim (aksan başlık) + tanım (gövde) içeren oklu
  bir kart açılır. Kart `position:fixed` + JS konumlandırma ile **ekran kenarına
  uyarlanır**: üstte yer yoksa alta döner (flip), yatayda viewport içine
  sıkıştırılır (clamp) — hiçbir konumda kırpılmaz. Ok çipin merkezini izler.
- **Tema-duyarlı (Carbon inverse).** Açık temada koyu kart (#393939 / açık metin),
  g100'de açık kart (#f4f4f4 / koyu metin); terim başlık rengi `color-mix` ile her
  iki zeminde kontrast-güvenli aksandan türetilir.
- **Erişilebilirlik.** Çip artık `<button>` olarak klavyeyle odaklanır; odakta kart
  açılır ve `aria-describedby="defPop"` (role="tooltip") bağlanır → ekran
  okuyucu terimi ve tanımını okur. `Esc` kapatır; `prefers-reduced-motion` geçişi
  kaldırır. Olay delegasyonu ile stage yeniden render edilse de çalışır.
- **Çip cilası.** Aksan-tonlu pill'lere ince aksan kenarlık + hover durumu (yumuşak
  gölge) eklendi; bilgi ikonu odakta/hover'da belirginleşir (etkileşim sinyali).

### Teknik
- Saf-CSS `.def-term::after` ipucu kaldırıldı; `.def-pop` (kart + ok), tema renk
  değişkenleri (`--def-pop-bg/fg/accent`) ve tek paylaşımlı popover IIFE'si eklendi.
- Render `data-term` taşır ve terimi `esc()`'ler; popover içeriği `textContent` ile
  yazılır (XSS-güvenli).
- Light + g100, masaüstü + dar viewport (560 px, clamp doğrulandı) ve klavye odağı
  test edildi.

## [2.2.0] — 2026-06-12

### Yeniden tasarlandı — İki katmanlı Carbon header (`assets/module-template.html` → v1.3.0)

Önceki tek-bantlı renkli header iki ardışık geri bildirimde ("çok büyük",
ardından "çok sıkışık") dengelenemedi; kök neden tüm bilgiyi (kimlik, küresel
kontroller, 11-adım ilerleme, rozetler) tek bir renkli banda yığmaktı. Header,
Carbon **katmanlama (layering)** ilkesi uygulanarak iki ayrı yüzeye bölündü.
Değişiklik yalnız sunum katmanındadır; motor, `MODULE_DATA` şeması ve kalite
kapıları değişmedi (11/11, 0 uyarı; geriye dönük tam uyumlu).

- **Katman 1 — Kimlik bandı.** Ders aksanının tam tonu (gradyan) + açık (beyaz)
  içerik: piktogram (Carbon tile benzeri kap), belirgin başlık (heading-04 ölçeği,
  1.5 rem/600) ve alt başlık; sağda XP/seri **Carbon Tag** çipleri + ince dikey
  ayraçla ayrılmış **ghost ikon düğme** kümesi (40 px).
- **Katman 2 — Durum şeridi.** Nötr Carbon `layer-01` yüzeyinde **ProgressIndicator**
  (numaralı): tamamlanan = aksan dolgu + tik, aktif = 2 px aksan halka, bekleyen =
  içi boş `border-strong` halka; bağlayıcı çizgiler tamamlandıkça aksana döner.
  Yanında "Bölüm N/M" başlığı, altında **Carbon Tag** rozetleri (kilitli = nötr çip,
  kazanılan = aksan çip).
- **Nefes alan yerleşim.** İki yüzey tek kapsayıcıda `overflow:hidden` ile köşelere
  kırpılır; tüm boşluklar Carbon 2x-grid ölçeğinden (`--sp-0X`). Bilgi grupları
  yarışmak yerine ayrışır — "sıkışık" algısı giderilir.

### Teknik
- HTML: `<header>` içine `.topbar__hero` (renkli) + `.topbar__status` →
  `.topbar__progress` (stepper + `rail-label`) + `.badges` sarmalayıcıları eklendi;
  motor `id`'leri (`#stepper`, `#badgeCase`, `#railText`) korundu.
- Tamamlanan adım tik/numara rengi tema-duyarlı `--cds-background`'a bağlandı →
  hem White (#6929c4 üzeri beyaz) hem g100 (#e8daff üzeri koyu) temada WCAG AA
  kontrast garantisi.
- `color-mix` ile aksan-türevli gradyan; nötr şerit ve rozetler tümüyle tema
  token'larıyla (`layer-01/02`, `border-strong/subtle`, `text/icon-secondary`).
- Light + g100, masaüstü + mobil (390 px, taşma yok) doğrulandı.

## [2.1.0] — 2026-06-12

### Geliştirildi — Şablon başlık (header) ve soru ekranı görsel tasarımı (`assets/module-template.html` → v1.2.0)

Kanonik şablonun üst çubuğu ve soru/etkileşim ekranı sekonder yapıları yeniden
tasarlandı. Değişiklikler **yalnız sunum katmanındadır**; etkileşim motoru,
`MODULE_DATA` şeması ve tüm kalite kapıları değişmeden korunur (mevcut modüllerle
geriye dönük tam uyumlu — 11/11 kapı, 0 uyarı).

- **Kompakt hero header.** Üst çubuk artık ders aksanının (tema rengi) tam tonunu
  bir dolgu gradyanı olarak kullanır; tüm içerik açık (beyaz) renge çevrildi.
  Başlık belirginleştirildi (700 ağırlık, sıkı izleme); piktogram cam kare rozete
  alındı. Önceki büyük banttan daha kompakt: padding ve dikey ayak izi düşürüldü,
  adım göstergesi daireleri 30→26 px, başlık 1.6→1.3 rem.
- **Kompakt sağ-üst kontrol kümesi.** XP/seri cam çipleri küçültüldü; ses, sesli
  okuma ve tema düğmeleri tek bir cam **araç-çubuğu pill'inde** (`.topbar__tools`,
  40 px hedef) gruplandı. Aktif toggle (örn. TTS) beyaz pill + aksan ikonla gösterilir.
- **Açık (light) içerik durumları.** Adım göstergesi (tamamlanan = beyaz daire +
  aksan tik, aktif = beyaz halka, bekleyen = saydam beyaz), bölüm etiketi ve
  rozetler (cam çip; kazanılan = parlak beyaz) mor zemin üzerinde yeniden boyandı.
  Klavye odağı beyaz halkaya çevrildi. Hem White hem g100 temada doğrulandı.
- **Soru ekranı sekonder yapı ayrıştırması.** `instructions` (ipucu) artık
  aksan-tonlu, sol-kenarlıklı bir **bilgi kutusunda** sunulur; segment-içi sayaç
  (`Soru N/M`, `Cümle N/M`, `Öğe N/M`, `İpucu N/M`) artık tek-biçimli bir
  **rozet/çip**. Bu, soru kökünü (birincil) sekonder rehber öğelerden net ayırır.

### Teknik
- `.topbar`, `.icon-btn`, `.step*`, `.badge*`, `.rail-label`, `.xp`, `.instructions`,
  `.streak` kuralları yeniden tanımlandı; `.topbar .streak-chip` / `.icon-btn--on` /
  `*-float` için yüksek-özgüllük temalı override'lar eklendi.
- HTML: üç yardımcı düğme `.topbar__tools` sarmalayıcısına alındı (motor düğmeleri
  `id` ile referans aldığından davranış değişmedi).
- Yalnız token-tabanlı renk + WCAG AA (beyaz/aksan dolgu ≈ 5:1); `color-mix` ile
  aksan-türevli gradyan/sınır (Chromium ≥120 · Firefox ≥115 · Safari ≥16).

## [2.0.0] — 2026-06-12

### Düzeltildi — Token sapma denetimi (7 sapma, `@carbon/*` npm otoritesiyle doğrulandı)
Tüm tema token'ları `@carbon/themes@11.75.0` · `@carbon/type@11.61.0` ·
`@carbon/motion@11.46.0` · `@carbon/layout@11.53.0` · `@carbon/colors@11.52.0`
paketlerinden **programatik çıkarımla** denetlendi; tespit edilen sapmalar
düzeltildi:

- ⚠ **KRİTİK — White `--cds-support-info`: `#4589ff` → `#0043ce`** (status-token:
  açık temalarda info = Blue 70). Eski değer beyaz zeminde ~3.7:1 kontrast verir —
  **AA başarısız**. `#4589ff` yalnız g100'de doğrudur. Bu regresyon artık
  `G-TOKEN` kapısında **FAIL** seviyesindedir.
- **g100 `--cds-button-primary-hover`: `#0353e9` → `#0050e6`** — otorite
  `button-primary-hover`'ı **tüm temalarda** `#0050e6` tanımlar.
- **White `--cds-layer-03`: `#e8e8e8` → `#f4f4f4`**; **g100 `--cds-layer-03`:
  `#4c4c4c` → `#525252`**.
- **`--cds-text-placeholder`** v10 düz grisinden v11 alfa değerlerine:
  white `rgba(22,22,22,.4)`, g100 `rgba(244,244,244,.4)`.
- **İki kademeli `border-subtle`**: `--cds-border-subtle-00` (zemin üstü:
  `#e0e0e0`/`#393939`) + `--cds-border-subtle-01` (layer-01 üstü:
  `#c6c6c6`/`#525252`); eski tek değişken `00`'a alias.
- **g100 bildirim zeminleri** özel koyu tintler → dördü de `#262626` (Carbon
  koyu bildirim deseni: nötr katman zemini; anlamı 3px durum çubuğu + ikon taşır).
- `references/carbon-child-system.md` §3 ders-aksan tablosu, motor
  `SUBJECT_ACCENT` tablosuyla çelişiyordu → motor kaynak alınarak uzlaştırıldı
  (tüm hex'ler `@carbon/colors` paletiyle doğrulandı).

### Eklendi — Token otorite altyapısı ve Figma görsel QA katmanı
- **Etkileşim-durumu token katmanı** (~20 yeni token, her iki temada):
  `layer-hover/active/selected-01`, `layer-accent-hover-01`, `field-hover-01`,
  `background-hover/active`, `border-tile/interactive`, `text-helper`,
  `icon-on-color`, `link-primary-hover`, `focus-inset`, `highlight`, `overlay`,
  `shadow`, `skeleton-background/element`. CSS bağlamaları: ghost/ikon buton
  hover-active, tile kenarı, koyu-tema bildirim çerçevesi,
  `::selection` vurgusu.
- **Tam hareket matrisi** — `@carbon/motion`'ın 6 süresi
  (`fast-01..slow-02`) + 6 easing'i (standard/entrance/exit ×
  productive/expressive) token olarak; tüm animasyonlar (`segIn`, `xpRise`,
  `xpPulse`, `badgePop`, `streakHit`, `streak-float`) jenerik `ease`
  yerine Carbon easing'lerine bağlandı.
- **Tam spacing ölçeği** `--cds-spacing-01..13` (+ `--sp-01..10` alias);
  `--ls-label:.32px` (`@carbon/type` label/code letter-spacing); `--tap:48px`
  = Carbon size **Large** olarak belgelendi.
- **`ACCENT_STRONG` resmî tag-çifti motoru** — `setAccent(hex)` bilinen aksan
  ailelerinde (blue/cyan/teal/green/magenta/purple/red/gray) `@carbon/themes`
  **tag token çiftlerini** (`tag-background-X`/`tag-color-X`) kullanır; aksan
  renkli metin her iki temada AA-garantili. Bilinmeyen hex'lerde `color-mix`
  yedeği korunur.
- **`assets/carbon-v11-authority.json`** — sürüm-damgalı, makine-okunur otorite
  anlık görüntüsü (4 tema seçili token'ları, tip, hareket, layout, 9 palet
  ailesi, tag çiftleri, bileşen token'ları).
- **`scripts/sync_carbon_tokens.py`** — `--check` (çevrimdışı: şablonu otorite
  JSON'a karşı diff'ler, ~44 token × 2 tema) ve `--refresh` (npm'den taze
  çıkarımla JSON'u günceller). Carbon yeni sürüm yayınladığında tek komutla
  senkron.
- **`G-TOKEN` kalite kapısı** (`validate_module.py`, 11. kapı) — üretilen
  modülün tema bloklarını gömülü otorite haritasına karşı denetler; sapma =
  WARN, white `support-info:#4589ff` = FAIL.
- **`references/figma-carbon-interop.md`** (yeni) — Carbon v11 Figma
  kütüphaneleri üzerinden **opsiyonel görsel QA protokolü**: `get_libraries →
  search_design_system → get_variable_defs` akışı, Figma değişken adı ↔
  `--cds-*` eşleme tablosu, sapma triyajı (npm kazanır), `figma-forge`
  composability (token'ları Figma Variables'a itme). Community dosyası kısıtı
  belgelendi (kullanıcı kopyası + dosya URL'si gerekir).
- **`references/carbon-child-system.md` v2** — provenans başlığı, üç katmanlı
  otorite zinciri, düzeltilmiş/karşılaştırmalı tablolar (tip otoritesi ↔ çocuk
  ölçeği sapma kolonu, iki kademeli border, durum token bölümü, tam
  hareket/spacing), motor-hizalı ders-aksan tablosu + resmî tag-çifti kolonları.
- Manifest: `figma-forge` pipe_to kenarı, Figma MCP opsiyonel konektörü,
  `G-TOKEN` kapısı, tam-sürümlü canonical_authorities.

### Değiştirildi
- Şablon font yedek zincirleri `@carbon/type` fontFamilies ile hizalandı
  (`system-ui,-apple-system,BlinkMacSystemFont` vb.).
- SKILL.md §10 yeniden yazıldı + **§10.1 Token otorite zinciri + Figma
  doğrulama** eklendi; §5 ve §13 güncellendi.

### Doğrulama
- `validate_module.py` güncellenmiş şablona karşı: **11/11 kapı GEÇTİ**
  (G-TOKEN: "@carbon/themes 11.75.0 ile birebir"), 0 uyarı.
- `sync_carbon_tokens.py --check`: **sapma yok — şablon otoriteyle birebir.**

## [1.9.0] — 2026-06-12

### Eklendi — Müfredat MCP entegrasyonu (Türkiye Yüzyılı Maarif Modeli)
Skill artık **MEB Müfredat MCP**'sini (tymm.meb.gov.tr; 60 ders, 11.295 kazanım,
13 beceri çerçevesi, 157 video) opsiyonel **kaynak ve doğrulama katmanı** olarak
kullanabilir. Önceki sürümlerde "derleme anında MCP yok" mutlaktı; bu sürümle
Müfredat MCP derleme anında çağrılarak kazanım çekilir, resmî beceri etkileşime
haritalanır ve provenans damgalanır — üretilmiş modül yine bağımsız/çevrimdışıdır.

- **Yeni referans `references/curriculum-integration.md`** — entegrasyonun beyni:
  19 Müfredat aracının dört işlevsel kümede orkestrasyonu (keşif → kazanım çekme →
  beceri haritalama → doğrulama); en-az-çağrı ilkesi; kazanım kodu anatomisi
  (`FB.5.3.1.1` = Ders·Sınıf·Ünite·Bölüm·Çıktı); hata/erişilemezlik geri-dönüş
  protokolü (graceful degradation); çalışılmış örnek (Fen 5 — Hücre).
- **Beceri → etkileşim deseni haritalama tablosu** (çekirdek katma değer) — Maarif
  Modeli **Kavramsal Beceriler** çerçevesinin (KB1/KB2/KB3) bütünleşik becerileri,
  `carbon-edupedia` etkileşim desenlerine yapıcı-hizalama (constructive alignment)
  ile bağlandı: KB2.7 Karşılaştırma → `match`+`vizTable`; KB2.5 Sınıflandırma →
  `sorting`; KB2.13 Yapılandırma → `order`+`relationFlow`; KB2.8 Sorgulama → `mcq`;
  KB3.2 Problem Çözme → `order`+`mcq`; vb. Kazanım üst-fiili tespit edilip beceri
  koduna ve oradan etkileşime eşlenir; kazanımın bilişsel düzeyine sadık kalınır.
- **Yeni CURRICULUM modu** (8. mod) — MEB kazanım kodundan veya ders+sınıf+konudan
  tam modül üretir. Ayrıca **Müfredat-duyarlılık tüm mevcut modlarda opsiyoneldir**:
  herhangi bir mod (MODULE/QUIZ/FLASHCARDS/...) Müfredat MCP'sinden kaynak çekip
  `curriculum` bloğu taşıyabilir.
- **`curriculum` veri bloğu** (MODULE_DATA opsiyonel uzantısı) — provenans katmanı:
  `framework`, `subjectSlug`, `grade`, `corpusVersion` ve `outcomes[]` (kazanım
  `code`, `text`, `skill` haritalaması, `mappedTo` segment id'leri). Motoru
  değiştirmez; geriye dönük uyumludur (mevcut motor görmezden gelebilir).
- **Yeni kalite kapısı G-CURRICULUM** (10. kapı, `scripts/validate_module.py`) —
  **koşullu**: yalnız mod CURRICULUM ise veya `curriculum` bloğu varsa tetiklenir,
  aksi halde atlanır (mevcut MCP'siz modüller etkilenmez). Denetler: CURRICULUM
  modunda blok zorunlu; `outcomes[]` `code`+`text` taşır; her `mappedTo` segment
  id'si `segments[]`'te mevcut (kazanım→segment izlenebilirliği, eksikse FAIL);
  `sourceCitation` kazanım/korpus referansı içerir (eksikse WARN). Pozitif, negatif
  (kırık eşleme → FAIL) ve atlama (MCP'siz modül → PASS-uygulanmaz) senaryolarıyla
  doğrulandı.
- **Kaynak-sadakati MCP'ye uyarlandı** — çekilen kazanım metni primer kaynak olur;
  modüldeki her olgu kazanıma/programa izlenebilir olmalı (uydurma yasak); kazanım
  kodları/beceri etiketleri çarpıtılamaz; `server_info` korpus sürümü kaynak
  damgasına eklenir.

### Değişti
- **SKILL.md**: §2'ye Müfredat tetikleyicileri; §5 referans tablosuna
  `curriculum-integration.md`; §6 mod tablosuna CURRICULUM + Müfredat-duyarlılık
  notu; §8'e "Adım 0.5 — Müfredat MCP keşfi (koşullu)"; §12'ye G-CURRICULUM; §13
  composability'ye Müfredat MCP `pipe_from`; §14 sınırlılıklarda "gerçek-zamanlı
  veri yok" Müfredat MCP istisnasıyla nüanslandı. Description Müfredat tetikleyici
  ve disambiguation ile güncellendi (1024 karakter sınırı korundu: 1011).
- **skill-manifest.yaml**: `version` 1.9.0; `optional_connectors`'a Müfredat MCP
  (19 araç); `composition.pipe_from`'a `mufredat-mcp`; `verification.gates`'e
  G-CURRICULUM (toplam 10 kapı); `references`'a curriculum-integration; inputs'a
  `mode` CURRICULUM + `curriculum_target`; `out_of_scope` MCP nüansı + Türkiye-dışı
  müfredat dışlaması.

### Sürüm gerekçesi (SemVer MINOR)
Geriye dönük uyumlu özellik eklemesi: yeni mod, yeni referans, yeni koşullu kapı
ve opsiyonel veri bloğu. Mevcut MCP'siz iş akışları ve modüller hiç etkilenmez;
etkileşim motoru (`assets/module-template.html`) değiştirilmedi.

### Düzeltildi — skill-censor FULL_AUDIT giderme döngüsü (2026-06-12)
`skill-censor v1.8.0` FULL_AUDIT sonucu (9.5/10 EXEMPLARY) üzerine tüm gidermeye
değer bulgular kapatıldı; yeniden denetimde **10.0/10 EXEMPLARY, 0 CRITICAL/MAJOR/MINOR**:
- **D2 (8.4→9.9):** SKILL.md frontmatter `description` sert 1024 karakter sınırına
  13 karakter kalmıştı (MAJOR F-M-001). 1011→945 karaktere kısaltıldı (≤950 güvenli
  tampon); tüm tetikleyiciler, Müfredat entegrasyonu ve disambiguation korundu.
- **D5 (9.0→10.0):** `validate_module.py` iki kapı fonksiyonu siklomatik karmaşıklığı
  >10'du (`gate_audio` 19, `gate_curriculum` 16). Saf-karar yardımcılarına ayrıştırıldı
  (`_audio_earcon_issues`, `_audio_tts_issues`, `_audio_pass_msg`; `_curriculum_collect`,
  `_curriculum_cite_ok`, `_curriculum_eval`) — davranış birebir korundu (POC 10/10).
- **D9 (9.4→9.9):** `evals/evals.json` test fixture seti eklendi (4 senaryo: CURRICULUM
  modu, tek-kazanım, MCP'siz MODULE/geriye-dönük-uyum, müfredat-duyarlı QUIZ) +
  `evals/files/` referans modülü.
- **D6 (8.4→9.9):** "Tanınmayan connector" bulguları (`Müfredat MCP` vb.) §12.3
  uyarınca yanlış-pozitif olarak doğrulandı — Müfredat MCP gerçek ve bağlı (19 araç
  canlı çağrıldı); denetçinin `mcp_registry.json`'ına `education_tr` kategorisinde
  eklendi.

## [1.8.0] — 2026-06-07

### Eklendi — Kesir/oran çubuğu (`fractionBar`, Matematik paketi)
- **Daire değil, alan/uzunluk (bar) modeli** olan yeni SVG görsel: üç mod — `kind:"fraction"`
  ({num,den}) tek kesir; `kind:"sum"` ({addends:[],den}) paydaları eşit kesir toplamı (otomatik
  denklem, ör. 3/4 + 1/4 = 1); `kind:"ratio"` ({ratio:[],labels?}) oran (ör. 2:3, opsiyonel renkli
  gösterge). Dolu hücre aksan/`--viz-*`, boş hücre `--cds-layer-01`, çerçeve `--cds-border-strong`;
  denklem Plex Serif + tabular (`.fb-eq`).
- **`role="img"` + `<title>`/`<desc>`** ve yalnız token renk → G-SVG uyumlu, tema-duyarlı (açık/koyu).
- Hem `teach` görseli (`visual.kind:"fraction"`) hem bağımsız `fraction` segment tipi olarak çağrılır;
  render dispatch'ına `fraction:renderFraction` eklendi.
- Kanıt temeli `references/subject-packs.md` §2(e): bar modeli daireden daha doğru kullanılır (Morano
  2020), Singapur "model yöntemi" / Bruner ikonik aşaması parça-bütün ve oranı destekler (Poh 2025),
  CRA temsil aşaması (Flores 2018); dürüst denge: büyüklük/bölme için sayı doğrusu üstündür (Hamdan
  2017, Sidney 2019) — `fractionBar` `numberLine` ile **tamamlayıcıdır**.

### Eklendi — Seri / combo göstergesi
- Ardışık doğru yanıtta üst çubukta **CVD-güvenli seri çipi** (`#streakChip`, `--reward-bg` zemin +
  metin-birincil sayı + yeni `ic-flash` ikonu); `renderStreak` / `bumpStreak` / `resetStreak`.
- **Kilometre taşları** (3·5·8·13·21·34): **mütevazı sessiz XP bonusu** (`addXP(n,{silent:true})`,
  earcon çakışması önlendi) + kutlama earcon'u + görsel kutlama (`.streak-chip--hit`, `streakFloat`).
- Beş etkileşimin doğru dallarına `bumpStreak()` (mcq, eşleştirme, boşluk doldurma, sıralama, gruplama,
  flashcard-biliyorum), yanlış dallarına `resetStreak()` bağlandı. **Flashcard "tekrar et" seriyi
  düşürmez** (nazik); hotspot seriye dâhil değil. Tüm kutlamalar `prefers-reduced-motion` duyarlı.
- Özet ekranına koşullu **"En uzun seri"** karosu (`state.bestStreak ≥ 2`); restart seriyi sıfırlar.
- `addXP` artık `addXP(n, opts)` imzalıdır (`opts.silent` ile sessiz ödül).

### Eklendi — Sesli okuma (TTS) alt-sistemi
- `speechSynthesis` ile **opsiyonel** "Oku" düğmeleri: `teach` anlatımı, soru kökü, `gloss`,
  `dialogue` ve `flashcard` arkası. Üst çubukta kulaklık düğmesi (`#ttsBtn`, yeni `ic-headphones`).
- **Varsayılan KAPALI** (`data-tts="off"`), talep-üzerine; **otomatik okuma yok**; aynı düğmeye basınca
  durur; mod kapanınca `speechSynthesis.cancel`. Tek olay delegasyonu (`[data-speak]`/`[data-lang]`).
- **Dil otomatik**: öğretim metni `meta.ttsLang||tr-TR`; hedef-dil içeriği konudan türetilir
  (Fransızca→`fr-FR`, İngilizce→`en-US`) ya da `spec.lang`/`card.lang` ile geçersiz kılınır. Hız 0.95.
- TTS açmak/kapamak quiz ilerlemesini etkilemez (yeniden render yok); metin daima ekranda kalır.
- Kanıt temeli `references/audio-system.md` §5 + `adhd-pedagogy.md` §15: TTS okuduğunu anlamayı
  destekler (Wood 2017 meta-analiz; Keelor 2023; Schiavo 2021); dürüst denge: herkese tek-beden değil
  (Silvestri 2021), öğretmenin tamamlayıcısıdır (Brunow 2021).

### Düzeltildi — Flashcard ipucu yerleşimi
- Kart arkasındaki ipucu artık satır-içi stil yerine ayrı, **ortalanmış** `.fc-hint` bloğunda
  (`ic-help` ikonu + "İpucu:" etiketi), tanımın altında (`.fc-back`/`.fc-back__def`). Önceki satır-içi
  yerleşim çakışması giderildi.

### Değişti — Doğrulama (G-AUDIO iki-katmanlı)
- `scripts/validate_module.py` **G-AUDIO** kapısı artık **earcon + TTS** katmanlarını ayrı denetler:
  TTS kullanılıyorsa `toggleTTS`/`#ttsBtn` kontrolü, `speechSynthesis.cancel` ve `data-tts="off"`
  varsayılanı **zorunlu**; reduced-motion ortak koşul; autoplay/loop yasağı korunur.
- Altı demo modülünün tamamı (matematik · fen · Türkçe · İngilizce · sosyal bilgiler · Fransızca)
  9 kapıdan **0 uyarı** ile geçer; `node --check` sözdizimi temiz.

## [1.7.0] — 2026-06-07

### Düzeltildi — Matematik dizgisi (kesir/operatör hizalama)
- **Blok matematik artık flexbox ile merkezlenir** (`.math.block` → `display:flex; align-items:center`):
  kesirler, operatörler ve çıplak sayılar ortak eksende hizalanır. Ekran görüntüsündeki "operatörler
  kesir merkezinin üstünde uçuyor" hatası giderildi (önceki `vertical-align:-0.55em` kaldırıldı; satır-içi
  kesirler için `.math:not(.block) .frac{vertical-align:middle}`).
- **Operatörler `.op` ile sarılır** (`=`, `+`, `−`, `×`, `÷`, `≤`, `≥`, `≠`, `±`): ikincil renk + tutarlı boşluk.
- **Kimya alt indisi düzeltildi**: çıplak `_`/`^` artık yalnız sayı veya tek harf yakalar →
  `H_2O` → H₂O (önceden H₂ₒ), `CO_2` → CO₂; `x^10` → x¹⁰ korunur.
- **Eşitsizlik glifleri düzeltildi**: `esc()` `<`'i kaçırdığı için `<=`/`>=` artık `&lt;=`/`&gt;=`
  üzerinden ≤/≥'ye çevrilir.

### Eklendi — İşitsel geri bildirim (earcon) sistemi
- **Web Audio earcon motoru** (`AudioFX`): tarayıcı-yerel sentezlenen kısa, hoş-değerlikli, düşük sesli
  motifler — `correct` (doğru/XP), `retry` (yanlış; nazik/**cezasız**), `reward` (modül tamamlama),
  `notify` (mola/onay). Sürekli arka plan müziği/gürültüsü **yok**.
- **Üst çubukta hoparlör düğmesi** (`#soundBtn`, authentic Carbon volumeUp/volumeMute ikonları);
  `prefers-reduced-motion: reduce` ise ses **varsayılan kapalı**; ilk etkileşimde `AudioContext` devreye alınır.
- Earcon'lar tüm doğru/yanlış dallarına (mcq/eşleştirme/boşluk doldurma/sıralama/gruplama/işaretleme/
  flashcard/checkpoint), mola hatırlatıcıya ve özet ödülüne bağlandı.

### Eklendi — Oyunlaştırma görselleri (ses ile eşli)
- **XP patlaması**: doğru cevapta "+N XP" çipi yükselip söner + sayaç nabzı (`pulseEl`/`xpFloat`).
- **Rozet kutlaması**: yeni rozet `badge--new` ile ölçeklenerek belirir. Tüm animasyonlar reduced-motion duyarlı.

### Düzeltildi — Rozet verme (gizli kimlik-uyuşmazlığı)
- Rozetler artık sabit kimlik yerine **`condition` alanına göre** verilir (`awardByCondition`):
  `module-complete` ve `flawless-mcq`. Böylece her demonun kendi rozet kimlikleri (ör. botanist/citizen/
  francophone) doğru biçimde açılır.

### Eklendi — Doğrulama ve doküman
- **G-AUDIO** kapısı (`validate_module.py`): ses varsa susturma kontrolü + reduced-motion + autoplay/loop
  yokluğu zorunlu. `references/audio-system.md` eklendi; `adhd-pedagogy.md` §14; SKILL.md §11.4.
- Kanıt (Consensus): çok-duyulu geri bildirim tercihi (Schubhan 2024), sert-ses uyarısı (Altmeyer 2022),
  sistematik ses tasarımı (Cao 2025); DEHB'de kısa-yeni-ses yararı (Tegelbeckers 2016/2022) vs. sürekli-ses
  dağıtıcılığı (Kong 2025; Söderlund 2012/2024; Lin 2022; Chen 2022; Baijot 2016).

### Doğrulama
- Altı demo JS geçerli; 9 kapı (G-EMOJI/G-CARBON/G-A11Y/G-INTERACT/G-SELFCONTAINED/G-CONTRAST/G-WELLBEING/
  G-SVG/**G-AUDIO**) yeşil. FULL_AUDIT hedef 10.0.

## [1.6.0] — 2026-06-07

### Eklendi — Derse-özel frontend güçleri: üç yeni disiplin ailesi
- **Fen Bilimleri** (teal): `labeledFigure` — numaralı çağrı-iğneli **etiketli diyagram** (hücre/
  bitki/devre) + sıralı açıklama listesi (erişilebilir SVG); `relationFlow` ile süreç zinciri
  (fotosentez); `vizChart`/`vizTable` ile veri/gözlem; `mathExpr` kimyasal alt indis (H₂O).
- **Sosyal Bilimler** — sosyal bilgiler · **din kültürü ve ahlak** · **yurttaşlık/insan hakları**
  (camgöbeği/yeşil): `relationFlow` (**sebep-sonuç** kavram zinciri), `infoCards` (kavram/değer/hak
  kartları ızgarası), `timeline` (hak belgeleri), `vizTable`.
- **Dil Bilimleri** — Türkçe · İngilizce · **Fransızca** (mor): `glossSentence` (**satır-arası
  çözümleme** + rol/cinsiyet **renk-kodu**, renk daima etiketle birlikte — CVD-güvenli),
  `dialogue` (iki konuşmacılı), `infoCards` (artikel), `vizTable` (çekim), `flashcards`.

### Eklendi — Motor
- Ortak görüntüleme-segment fabrikası `displaySeg`; yeni yapıcılar `labeledFigure`,
  `relationFlow`, `infoCards`, `glossSentence`, `dialogue`; yeni segment/`visual.kind`:
  `diagram`, `flow`, `cards`, `gloss`, `dialogue`.
- Genişletilmiş konu anahtarları/aksanları: `science`, `social`, **`civics`**, **`religion`**,
  `history`, `geography` (koyu teal), `turkish`, **`french`** (mor), `english`. Çözümleme sırası
  özel (french<english; civics/religion<social).

### Eklendi — Kanıt ve doküman
- `subject-packs.md` Fen/Sosyal/Dil bölümleriyle genişletildi; `adhd-pedagogy.md` §13 eklendi.
  Kanıt (Consensus): renk-kodlu dilbilgisi (Arzt 2016, Kostiuk 2025, Aljehani 2022), ikili kodlama
  (Wong 2019, Li 2019), kavram haritası meta-analizleri (Schroeder 2018, Nesbit 2006), etiketli
  diyagram/sinyalleme (Mayer 1989, Scheiter 2015, Richter 2016; uyarı: McTigue 2009).
- Üç yeni demo: `carbon-edupedia-fen-demo.html`, `carbon-edupedia-sosyal-demo.html`,
  `carbon-edupedia-dil-demo.html`.

### Doğrulama
- Altı demo JS geçerli; 8 kapı (G-EMOJI/G-SVG/G-CONTRAST/G-CARBON yeşil, 0 uyarı). FULL_AUDIT hedef 10.0.

## [1.5.0] — 2026-06-07

### Eklendi — İşlevsel renk politikası (kanıt-bilgili)
- Renk artık **işlevle** atanır: eylem (Blue 60 buton/bağlantı), durum (Carbon support),
  kategori (`--viz-1..5`), **ödül** (`--reward` sıcak altın — XP/yıldız), **odak çıpası** (aksan).
- **Wayfinding aksanı** (`--seg-accent`): etkinlik türü (anlatım=info, etkileşim=accent,
  mola=success, grafik/tablo=`--viz-2`) başlıkta renkle imlenir (signaling).
- Yeni Carbon **notification yüzey** token'ları (`--cds-notif-*-bg`) + `--cds-layer-03`;
  callout/feedback yüzeyleri color-mix yerine bu token'lara bağlandı (tam Carbon semantiği).
- `references/color-system.md`; `adhd-pedagogy.md` §12 (kanıt: Superbia-Guimarães 2022 ipucu
  yararı DEHB'de korunur; Wu 2006 az-uyarılma/Stroop çeldirici).

### Eklendi — Carbon öğe sadakati: tablo/diyagram/şekil
- **`vizTable(spec)`** — Carbon **DataTable** (`<caption>`, `<th scope>`, zebra, başlık
  `--cds-layer-accent-01`, sayısal sütun tabular/sağa hizalı, satır vurgusu); `table` segmenti
  + `visual.kind:"table"`. Ana örneğe hâl-karşılaştırma tablosu eklendi.

### Eklendi — Derse-özel frontend güçleri
- `meta.subject`/`meta.subjectKey` → **derse-özel kimlik aksanı** (math mor, fen teal, …) +
  `data-subject`. **Matematik paketi:** `mathExpr` (üs/alt indis, kesir, kök, operatör glifleri;
  Plex Serif + tabular rakam), `numberLine` (SVG sayı doğrusu), geometri SVG kuralları,
  Carbon değer tablosu. Yeni **matematik demosu** (`carbon-edupedia-math-demo.html`).
- `references/subject-packs.md`.

### Doğrulama
- Üç demo (genel/vitrin/matematik): JS geçerli; 8 kapı (G-SVG dâhil). FULL_AUDIT 10.0/10 EXEMPLARY.

## [1.4.0] — 2026-06-07

### Eklendi — Frontend & SVG yetkinliği (tema-duyarlı, erişilebilir, responsive)
- **Motor araçları:** `vizChart(spec)` (çubuk + çizgi grafik), `svgFigure(inner, caption)`
  ve `chart` segment işleyicisi (`renderChart`); `teach` görselleri (`svg`/`pictogram`/`chart`)
  artık erişilebilir `figure.viz` üzerinden işlenir.
- **Tema-duyarlı renk sistemi:** kategorik `--viz-1..5`, anlamsal `--viz-sun/water/cloud`,
  eksen/ızgara `--viz-axis/--viz-grid/--viz-track` (açık + koyu tema). Figür SVG'lerinde
  ham hex kaldırıldı; metin rengi CSS ile (`.viz text`, `.viz-muted`).
- **Örnek + vitrin SVG'leri tema-duyarlı yapıldı** (tanecik düzeni, su döngüsü, hotspot)
  ve altyazı eklendi; ana örneğe çubuk grafik, vitrine çizgi grafik segmenti eklendi.
- **Sakin giriş animasyonu:** segment başına tek, `prefers-reduced-motion` ile kapalı reveal.
- **`references/svg-authoring.md`** eklendi (SVG arketipleri + 4 değişmez kural + palet);
  SKILL.md §11.1/§11.2 (SVG sistemi + rafine-minimalizm frontend ilkeleri).

### Eklendi — Doğrulama
- **G-SVG kapısı** (`scripts/validate_module.py`): figür SVG'leri `role="img"`+başlık/etiket
  taşımalı (FAIL); ham-hex yerine token renk (WARN). Sprite/`@carbon` ikonları `aria-hidden`
  ile dışlanır.

### Doğrulama
- Ana şablon + vitrin: JS geçerli; 8 kapı (G-SVG dahil). FULL_AUDIT 10.0/10 EXEMPLARY.

## [1.3.1] — 2026-06-06

### Genişletildi — Kanıt üçgenlemesi (Ö1, Ö5) + mola dozu parametreleştirme
- `references/adhd-pedagogy.md` §10.1 eklendi: Ö5 mola dozu (Broad 2021 RCT —
  ~4 dk aktivite molası görev-üstü davranışı artırır; günde iki mola) ve Ö1
  problemli kullanım mekanizması/nozolojisi (Weinstein 2020 IGD↔DEHB yatkınlığı;
  Andreassen 2016 "bağımlı kullanım = olumsuz sonuç, süre değil"; Marin 2020 Young
  IAT; Brand 2024 AJP). Kaynakçaya 7 hakemli atıf (DOI'li).
- **Tasarım kuralı:** `brainbreak.durationSec` önerisi **120–240 sn**, hareket-yönergeli;
  uzun modülde (≥8 segment / ~20+ dk) en az iki mola. Örnek + vitrin molaları bu doza
  güncellendi (30/20 sn → 120 sn).

### Not — Bağlayıcı erişimi
- Consensus ve Scholar Gateway çağrı anında onay vermediğinden üçgenleme PubMed ile
  yapıldı; onay sağlandığında aynı sorgular bu iki kaynakta yinelenebilir.

### Doğrulama
- Ana şablon + vitrin: JS geçerli; 7 kapı; ana 0 uyarı. FULL_AUDIT 10.0/10 EXEMPLARY.

## [1.3.0] — 2026-06-06

### Eklendi — Kanıt-temelli esenlik (wellbeing) korumaları
- **Nazik mola hatırlatıcısı**: `learner.breakReminderMin` (vars. 20 dk; `0`=kapalı)
  süresi dolunca sakin, kapatılabilir bir bilgi kutusu (`#wellbeing`) gösterir —
  zorlayıcı değil, özerkliğe saygılı.
- **Sağlıklı kapanış**: özet ekranı "bugünlük bu kadarı yeterli" mesajıyla biter;
  "başka modül / devam et" baskısı yok. Özete geçişte mola zamanlayıcısı temizlenir.
- **Sabit-cetvel ödül** teyidi: XP öngörülebilir kalır (kumar-benzeri değişken-oran yok).
- **Yeni `G-WELLBEING` doğrulama kapısı**: cezalandırıcı/süre-baskısı dili (ör.
  "kaybettin", "süre doldu") → FAIL; ≥6 segmentlik modülde beyin molası yoksa / 
  `prefers-reduced-motion` yoksa → WARN.

### Eklendi — Akademik kanıt tabanı (medical-research v7.1 ile PubMed taraması)
- `references/adhd-pedagogy.md` §10 "Klinik kanıt temelli özen ilkeleri" (Ö1–Ö9):
  her özen ilkesi → PubMed kanıtı (DOI) → motordaki karşılık eşlemesi.
- §11 "Sorumlu kullanım" (bakım-veren/öğretmen notu).
- §8 Kaynakça'ya 10 hakemli klinik atıf (DOI bağlantılı) eklendi.
- SKILL.md §14'e kanıt-temelli sorumlu-kullanım maddesi.

### Kanıt (PubMed; atıflar DOI'lidir)
- Thorell 2022 (Eur Child Adolesc Psychiatry); Rodrigo-Yanguas 2022 (Front Psychiatry);
  Eirich 2022 (JAMA Psychiatry); Groves 2021 (Res Child Adolesc Psychopathol);
  Tripp & Wickens 2009 (Neuropharmacology); Wu 2024 (Neuropsychopharmacology);
  Zhu 2023 (Front Public Health); Qiu 2023 (Asian J Psychiatry); Zhao 2024 (JMIR);
  Cibrian 2024 (Front Digit Health).

### Doğrulama
- Ana şablon + vitrin: JS geçerli; 7 kapı (G-WELLBEING dahil); ana 0 uyarı.
- skill-censor FULL_AUDIT: 10.0/10 EXEMPLARY korunur.

## [1.2.1] — 2026-06-06

### Değişti — Görsel yüzey sistemi (tekdüzeliğin giderilmesi)
- `.lead` çekme-alıntı artık **aksan-tint çağrı kutusu** (4px sol bar, yuvarlatılmış,
  serif; metin `--text-primary` → her iki temada AA).
- Segment başlık piktogramı **aksan-tint ikon karosunda** (`.seg-ic`) — her segmente
  sakin bir renk çıpası; başlık altına ince ayraç.
- `.visual` ve `.terms` artık **yükseltilmiş çerçeveli yüzeyde** (`--cds-layer-02`).
- Yeni yeniden kullanılabilir **`.callout`** bileşeni (`--info`/`--success`) — teach
  gövdesinde renkli aside/notification.
- **Segment-türüne göre yüzey ritmi** (`data-seg`): brainbreak tamamen tint
  (sakinleştirici), checkpoint üst aksan kenarı, summary kutlama geçişi.

### İlke
- Renk *çoğaltılmadı*; ritim **Carbon katman + tek aksan tint** ile kuruldu. Amaç
  süs değil, segment türünü ele veren **mod ipucu** (DEHB: yapılandırılmış çeşitlilik,
  aşırı-uyarım değil). Kontrast: tüm tint zeminlerde metin `--text-primary` (AA).

### Doğrulama
- Ana şablon + vitrin: JS geçerli; 6 kapı (ana 0 uyarı); ikon referansları tam.
- skill-censor FULL_AUDIT: 10.0/10 EXEMPLARY korunur.

## [1.2.0] — 2026-06-06

### Eklendi — Öğrenme materyali türleri (Carbon-uyumlu uygulama)
- **flashcards** (`renderFlashcards`): aralıklı tekrar flip-kartları — «Çevir» →
  «Biliyorum»/«Tekrar et»; bilinmeyen kart deste sonuna atılır; her kart ustalığa sayılır.
- **order** (`renderOrder`): karışık öğelerden **sıradaki doğruyu seç** deseni;
  doğru seçim sıra numarasıyla yeşil kilitlenir; dokunma/klavye-erişilebilir.
- **sorting** (`renderSorting`): öğeleri tek tek doğru **kutuya/kategoriye** yerleştirme
  (`bins` + `items[{label,bin}]`).
- **hotspot** (`renderHotspot`): SVG diyagramda `data-spot` bölgesini bulup tıklama;
  `role/tabindex/aria-label` otomatik; Tab + Enter/Space ile erişilebilir.
- **timeline** (`renderTimeline`): dikey Carbon zaman çizelgesi (display/başvuru materyali).
- Varsayılan örnek modüle **flashcards** segmenti eklendi; tüm yeni türler için
  ayrı **vitrin demosu** (`carbon-edupedia-showcase.html`).

### Değişti
- `totalGradeable` artık flashcards/order/sorting/hotspot ögelerini de ustalık
  paydasına katar (timeline notsuzdur).
- `interaction-patterns.md` §3, §8–11: şemalar motordaki uygulamayla birebir
  hizalandı ve "uygulandı" olarak işaretlendi.

### Doğrulama
- Ana şablon + vitrin: JS `node --check` geçerli; 6 kapı GEÇTİ (vitrinde mcq
  olmadığından beklenen 1 G-INTERACT uyarısı); ikon referansları tam çözümleniyor.

## [1.1.0] — 2026-06-06

### Eklendi — Tasarım derinleştirme (Carbon'dan daha etkili yararlanma)
- **Gerçek Carbon varlıkları:** elle çizilen yaklaşık ikonlar, otantik
  `@carbon/icons` (15) + `@carbon/pictograms` (8) sprite'ı ile değiştirildi
  (npm-kaynaklı, `currentColor`, tek satır-içi sprite, 23 sembol).
- **Carbon ProgressIndicator (stepper):** basit ilerleme rayı yerine; tamamlanan/
  mevcut/bekleyen adım durumları, tamamlanan adıma tıklayıp geri dönme.
- **Carbon selectable Tile** deseni (MCQ/eşleştirme seçenekleri).
- **Carbon inline notification** anatomisi (geri bildirim) — `color-mix` ile
  tema-uyumlu düşük-kontrast zemin.
- **Carbon Tag + definition tooltip** (anahtar kavramlar tam-zamanında tanım).
- **Gray-100 (dark) teması** + üst çubukta ikon-buton geçişi (token-tabanlı,
  tema-duyarlı `setAccent`).
- **Carbon Charts paletli ustalık donutu** (özet, saf SVG).
- **IBM Plex Serif** vurguları (display başlık + `.lead` çekme-alıntı + özet).

### Düzeltildi
- **Kontrast (WCAG AA):** birincil butonlar artık Blue 60 kullanır (açık
  kategori aksanları beyaz metinle AA'yı geçmiyordu); aksan yalnız yapısal/
  dekoratif öğelerde, aksan-metin `--accent-strong` ile.

### Doğrulama
- 6 kalite kapısı (G-EMOJI/CARBON/A11Y/INTERACT/SELFCONTAINED/CONTRAST) GEÇTİ.
- JS `node --check` geçerli; 23 ikon referansının tümü sprite'ta çözümleniyor.

## [1.0.0] — 2026-06-06

İlk yayın.

### Eklenenler
- **Çekirdek yetkinlik:** Kaynak metinden DEHB-odaklı, IBM Carbon v11 ile
  biçimlendirilmiş, emojisiz, ikon/piktogram/SVG zengini tek-dosya etkileşimli
  öğrenim modülü üretimi. 7 mod (MODULE/QUIZ/FLASHCARDS/GAME/EXPLAINER/
  ASSESSMENT/SERIES).
- **`SKILL.md`** — kanonik işletim kılavuzu; çıktı sözleşmesi, kaynak-sadakati
  kuralı (§7), inşa iş akışı, kalite kapıları, composability, çocuk güvenliği.
- **`references/adhd-pedagogy.md`** — kanıt tabanı: Barkley, Sonuga-Barke,
  Sweller (CLT), Paivio/Mayer (ikili kodlama), CAST UDL, Deci & Ryan (SDT),
  Roediger & Karpicke (geri-getirme), gamification meta-analizleri. 8 tasarım
  ilkesi + etik sınırlar + ilke→modül köprü tablosu.
- **`references/module-architecture.md`** — `MODULE_DATA` şeması, segment akış
  kuralları, kalite öz-kontrol listesi.
- **`references/interaction-patterns.md`** — 11 etkileşim deseni (mcq, flashcard,
  match, fillblank, order, sorting, hotspot, timeline, brainbreak, checkpoint)
  veri şemaları + erişilebilirlik notları.
- **`references/carbon-child-system.md`** — Carbon v11 White teması token tablosu,
  ders kategorisi aksan paleti, IBM Plex tip ölçeği, hareket token'ları,
  gerekçeli çocuk-dostu uyarlamalar.
- **`references/icon-pictogram-svg.md`** — Carbon Icons/Pictograms sourcing,
  satır-içi sprite kalıbı, Carbon-uyumlu özgün SVG çizim kuralları, güvenli
  geometrik ikon seti.
- **`assets/module-template.html`** — Carbon-stilli, tam çalışan etkileşim motoru
  (teach/mcq/flashcards/match/fillblank/brainbreak/checkpoint + otomatik özet);
  örnek modül «Maddenin Hâlleri ve Su Döngüsü» ile dolu; XP/rozet/ilerleme rayı;
  satır-içi SVG ikon sprite; iki özgün Carbon-stili SVG diyagram.
- **`scripts/validate_module.py`** — 6 kapılı doğrulayıcı (G-EMOJI, G-CARBON,
  G-A11Y, G-INTERACT, G-SELFCONTAINED, G-CONTRAST).
- **`skill-manifest.yaml`** — SMP v1.0 manifesti: girdi/çıktı sözleşmeleri,
  pipe_from (francais-coach, medical-research, psychdev, vekayinuvis),
  pipe_to (carbon-html-report, pdf), doğrulama kapıları.

### Test
- Şablon JS motoru `node --check` ile sözdizimsel olarak doğrulandı.
- Şablon, `validate_module.py`'nin 6 kapısının tamamından geçti (0 uyarı).

### Bilinen sınırlar
- Statik baskı için değil (→ carbon-html-report). Durum bellekte (oturumlar
  arası ilerleme için opsiyonel `window.storage`). Olgu doğrulama yapmaz.
- Gelişmiş etkileşim desenleri (order, sorting, hotspot, timeline) şablonda
  iskelet olarak değil, referans şemasıyla belgelidir; üretimde eklenir.
