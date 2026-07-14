---
description: Üretilen modülü edupedia.cureonics.com'da yayınlar ve public bağlantıyı verir
argument-hint: <modul.html yolu>
---

# /edupedia:yayinla

Üretilmiş bir modül HTML'ini `edupedia.cureonics.com` sitesine yayınlar.

## Girdi

`$ARGUMENTS` — yayınlanacak `.html` dosyasının yolu. Verilmemişse bu oturumda en son
üretilen modülü kullan; o da yoksa kullanıcıdan yol iste (tahmin etme).

## Yol seçimi (ÖNCE BUNU KARAR VER)

Bu komutun iki yolu vardır — hangisi kullanılacağı, oturumda bağlı araç listesinde
`edupedia_publish` aracının görünüp görünmediğine göre belirlenir (`../.mcp.json`'daki
`edupedia` connector'ı bağlıysa görünür):

- **Yol A — MCP aracı (TERCİH EDİLEN):** `edupedia_publish` aracı mevcutsa doğrudan onu
  çağır. Manifest KURMA — sunucu manifesti `run_id`/`requested_scope` alanlarından kendisi
  kurar; sen yalnız düz alanları (`html`, `run_id`, `subject_slug`, `grade`, `topic`,
  `mode`, `outcome_codes`, opsiyonel `slug`/`title`) verirsin.
- **Yol B — REST (yedek):** `edupedia_publish` aracı yoksa (connector eklenmemiş — tipik
  Claude Code oturumu), mevcut `POST /api/publish` + `EDUPEDIA_PUBLISH_TOKEN` akışı
  kullanılır.

Her iki yolda da: **sunucudan `url` dönmediyse ASLA "yayınlandı" deme.**

---

## Yol A — MCP aracı (`edupedia_publish`)

### Ön koşul

HTML dosyasının yanında (varsa) run-manifest JSON'u okunur:
`<html-adı>.manifest.json` (bkz. `../shared/canonical-cache-contract.md §1`, şema
`../shared/run-manifest-schema.json`). **Manifest bu yolda ZORUNLU değildir** — claude.ai'de
model HTML'i doğrudan üretip dosyaya hiç yazmadan `edupedia_publish`'i çağırabilir; o
durumda aşağıdaki alanlar geçerli üretim koşumunun bağlamından (kazanım kodu, ders/sınıf/
konu, üretilen mod) alınır. Hangi kaynaktan gelirse gelsin **hiçbir alan uydurulmaz** —
eksik/belirsizse kullanıcıya sor.

### Adımlar

1. HTML içeriğini oku (dosya varsa) veya üretim çıktısındaki HTML metnini doğrudan kullan.
2. Aşağıdaki alanları belirle — manifest varsa `manifest.run_id` ve
   `manifest.requested_scope.*`'tan, yoksa geçerli üretim koşumundan:
   - `run_id` — manifest'ten; yoksa `Edupedia-YYYYMMDD-<ders>-<konu>-v<N>` NORMATİF kalıbında
     üret (bkz. `../shared/run-manifest-schema.json` `properties.run_id.pattern`).
   - `subject_slug`, `grade`, `topic`, `mode`, `outcome_codes` — `requested_scope`'tan
     (manifest yoksa: `/edupedia:modul`/`/edupedia:mufredat` üretim akışında zaten çözülmüş
     olan ders slug'ı, sınıf, konu, mod ve kazanım kodları).
   - `slug` (opsiyonel ama önerilir) — HTML dosya adından veya konu başlığından, `yayinla.md`
     Yol B'deki "Slug türetme" kuralıyla aynı normalize kurallarla (`^[a-z0-9][a-z0-9-]{1,63}$`);
     boş bırakılırsa sunucu `run_id`'den türetmeyi dener.
   - `title` (opsiyonel) — genellikle gerekmez; sunucu HTML `<title>`'ından çıkarır.
3. `edupedia_publish` aracını çağır:
   `edupedia_publish(html=<html metni>, run_id=<run_id>, subject_slug=<slug>, grade=<sınıf>,
   topic=<konu>, mode=<mod>, outcome_codes=<kod listesi>, slug=<opsiyonel>, force=false)`.
4. Dönen JSON'u ayrıştır:
   - **`{"error": ..., "status_code": ...}`** ise yayın reddedildi:
     - `status_code == 422` → kalite kapısı sunucuda düştü. Hata mesajındaki düşen
       kapıları kullanıcıya göster, yine de yayınlansın mı diye sor. Onaylarsa aynı çağrıyı
       `force=true` ile tekrarla.
     - Diğer kodlar (400/401/413) → hata mesajını olduğu gibi göster, uydurma açıklama
       ekleme; gerekiyorsa (ör. 400 geçersiz slug) düzeltip tekrar dene.
   - **`{"slug", "version", "url", "forced", "gates"}`** içeriyorsa BAŞARILI: dönen `url`'yi
     kullanıcıya göster (paylaşılabilir public bağlantı), sürüm numarasını söyle. `version > 1`
     ise eski sürümün `/m/<slug>/v<N-1>` altında durduğunu belirt. `forced: true` ise
     kullanıcıya bu sürümün kapı-atlamalı işaretlendiğini hatırlat.

---

## Yol B — REST (`POST /api/publish`, yedek)

### Ön koşullar

1. `EDUPEDIA_PUBLISH_TOKEN` ortam değişkeni gerekir. Yoksa **dur** ve kullanıcıya söyle:
   oturumu `doppler run -p cureohub -c dev_personal -- claude` ile başlatması gerekir.
   Token'ı kullanıcıdan isteme, uydurma.
2. HTML dosyasının yanında (aynı dizin) run-manifest JSON'u olmalı: **varsayılan ve tek
   sözleşme** `<html-adı>.manifest.json` (örn. `hucre-modul.html` →
   `hucre-modul.manifest.json`; dosya adı sözleşmesi normatif olarak
   `../shared/canonical-cache-contract.md §1`'de tanımlıdır; şema
   `../shared/run-manifest-schema.json`). Bu dosya `/edupedia:modul` / `/edupedia:mufredat`
   üretim akışının son adımında yazılır (bkz. `../commands/modul.md` Adım 5,
   `../commands/mufredat.md` Adım 4). **Manifest yoksa** kullanıcıya söyle: elle yayın için
   CureoHub'daki `scripts/publish_edupedia_module.py` bayraklı modunu kullanabilir.
   Manifest'i sen uydurma.

### Adımlar

1. HTML + manifest'i oku. Manifest'teki olası `quality_gates` alanı (varsa) yalnız
   istemcinin yerel ön-kontrol notudur — **kapıların OTORİTESİ değildir**: sunucu HTML'i
   yayın sırasında kendisi ölçer ve bu alanı yok sayar. Bu yüzden burada manifest'i okuyup
   FAIL arama; hangi kapıların düştüğü ancak Adım 3'teki 422 yanıtından öğrenilir.
2. `POST https://edupedia.cureonics.com/api/publish` — `force: false` ile — istekte **HER
   ZAMAN açık bir `slug` alanı gönder** (sunucunun `run_id`'den slug türetmesine güvenme;
   bkz. "Slug türetme" aşağıda):

```bash
python3 - <<'PY'
import json, os, re, sys, urllib.request, urllib.error

_TR_MAP = str.maketrans({
    "ç": "c", "Ç": "c",
    "ğ": "g", "Ğ": "g",
    "ı": "i", "İ": "i",
    "ö": "o", "Ö": "o",
    "ş": "s", "Ş": "s",
    "ü": "u", "Ü": "u",
})
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")


def derive_slug_from_filename(html_path):
    """Dosya adından slug türetir. Kalıba uymazsa None döner — asla uydurmaz."""
    stem = os.path.splitext(os.path.basename(html_path))[0]
    s = stem.translate(_TR_MAP).lower()
    s = re.sub(r"[\s_]+", "-", s)       # boşluk/alt-çizgi -> tire
    s = re.sub(r"[^a-z0-9-]", "", s)    # kalan geçersiz karakterleri at
    s = re.sub(r"-{2,}", "-", s)        # ardışık tireleri tekille
    s = s.strip("-")[:64].rstrip("-")   # baş/son tire kırp, 64 ile sınırla
    return s if _SLUG_RE.fullmatch(s) else None


html_path, manifest_path = sys.argv[1], sys.argv[2]
explicit_slug = sys.argv[3] if len(sys.argv) > 3 else None

slug = explicit_slug or derive_slug_from_filename(html_path)
if not slug:
    print(
        "HATA: dosya adından geçerli bir slug türetilemedi ('"
        + os.path.basename(html_path)
        + "'). Lütfen kullanıcıdan açık bir slug isteyin (^[a-z0-9][a-z0-9-]{1,63}$ deseni) "
        "ve bu betiği 3. argüman olarak o slug ile tekrar çalıştırın.",
        file=sys.stderr,
    )
    sys.exit(2)

payload = {
    "html": open(html_path, encoding="utf-8").read(),
    "manifest": json.load(open(manifest_path, encoding="utf-8")),
    "slug": slug,
    "force": False,   # kapı düştüyse ve kullanıcı onayladıysa True
}
req = urllib.request.Request(
    "https://edupedia.cureonics.com/api/publish",
    data=json.dumps(payload).encode(),
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer " + os.environ["EDUPEDIA_PUBLISH_TOKEN"],
        # ZORUNLU: Cloudflare, urllib'in varsayilan "Python-urllib/x.y" User-Agent'ini
        # bot sayip 403 (error code 1010) dondurur. Bu satiri kaldirma.
        "User-Agent": "edupedia-publisher/1.0 (+https://edupedia.cureonics.com)",
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        print(json.dumps(json.loads(r.read()), ensure_ascii=False))
except urllib.error.HTTPError as e:
    print("HATA", e.code, e.read().decode(), file=sys.stderr); sys.exit(1)
PY
```

**Slug türetme:** slug HER ZAMAN HTML dosya adından türetilir (uzantısız, küçük harf,
Türkçe karakterler ASCII'ye normalize edilmiş — ç→c, ğ→g, ı/İ→i, ö→o, ş→s, ü→u — boşluk/
alt-çizgi tireye çevrilmiş, geçersiz karakterler atılmış, baş/son tire kırpılmış, 64
karakterle sınırlanmış). Türetilen sonuç `^[a-z0-9][a-z0-9-]{1,63}$` desenine uymuyorsa
(ör. dosya adı `---.html` gibi tamamen geçersizse) **betik DURUR** ve kullanıcıdan açık bir
slug ister — asla uydurmaz. Kullanıcı bir slug verirse betiği 3. argüman olarak o slug ile
çalıştırın. **Not — slug ile run_id gövdesi çelişebilir:** dosya adından türetilen slug ile
manifest'teki `run_id`'nin gövdesi (`Edupedia-YYYYMMDD-<ders>-<konu>-v<N>` kalıbındaki
`<ders>-<konu>` kısmı) farklı olabilir (ör. dosya `hucre-fen5.html` → slug `hucre-fen5`,
ama run_id gövdesi `fen5-hucre`) — bu bir hata değildir. Sunucu açık `slug` gönderildiğinde
onu kullanır, `run_id`'yi slug türetmek için hiç ayrıştırmaz; `run_id` yalnız manifest kimliği
olarak kalır.

3. Yanıt **422** dönerse: kalite kapısı sunucu tarafında düştü demektir — hangi kapıların
   düştüğü yanıt gövdesinde gelir (bu bilgi SUNUCUDAN öğrenilir, manifestten değil). Düşen
   kapıları kullanıcıya göster ve yine de yayınlansın mı diye sor. Onaylarsa Adım 2'deki
   isteği `force: true` ile tekrarla.
4. Başarılıysa dönen `url`'yi kullanıcıya göster (paylaşılabilir public bağlantı) ve
   sürüm numarasını söyle. Bu bir yeniden yayınsa (`version > 1`), eski sürümün
   `/m/<slug>/v<N-1>` altında durduğunu belirt.

### Hata durumları (Yol B)

- **400** — geçersiz manifest veya slug (ör. `slug` deseni `^[a-z0-9][a-z0-9-]{1,63}$`'a
  uymuyor, ya da manifest zorunlu alan eksik/hatalı tip). Adım 2'deki slug türetmesi zaten
  bunu önlemeye çalışır; yine de 400 dönerse hata mesajını kullanıcıya göster ve açık,
  geçerli bir `slug` ile tekrar deneyin.
- **401** — token geçersiz. Doppler'daki `EDUPEDIA_PUBLISH_TOKEN`'ı doğrula.
- **422** — kalite kapısı sunucuda düştü (bkz. Adım 3). Hangi kapılar olduğunu göster;
  modülü düzeltmeyi öner. Kullanıcı ısrar ederse `force: true` ile tekrar dene.
- **413** — modül 25 MB'ı aştı (muhtemelen Tier-2 gömülü görseller). Görselleri
  seyreltmeyi öner.
- **Sunucuya ulaşılamıyor** — Pi kapalı olabilir. Yerel HTML dosyasına dokunma; kullanıcıya
  durumu bildir, sonra tekrar denemesini söyle.

---

## Genel hata durumu (her iki yol)

Hiçbir durumda başarı uydurma — sunucudan `url` dönmediyse "yayınlandı" deme. Yol A'da
hata `edupedia_publish`'in JSON gövdesindeki `error`/`status_code` alanlarında gelir; Yol
B'de HTTP durum koduyla gelir — anlamları (400/401/413/422/erişilemez) aynıdır, yukarıdaki
"Hata durumları (Yol B)" listesi her iki yol için de geçerlidir.
