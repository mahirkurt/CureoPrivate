---
description: Üretilen modülü edupedia.cureonics.com'da yayınlar ve public bağlantıyı verir
argument-hint: <modul.html yolu>
---

# /edupedia:yayinla

Üretilmiş bir modül HTML'ini `edupedia.cureonics.com` sitesine yayınlar.

## Girdi

`$ARGUMENTS` — yayınlanacak `.html` dosyasının yolu. Verilmemişse bu oturumda en son
üretilen modülü kullan; o da yoksa kullanıcıdan yol iste (tahmin etme).

## Ön koşullar

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

## Adımlar

1. HTML + manifest'i oku.
2. Manifest'teki `quality_gates` içinde `FAIL` varsa **önce kullanıcıya söyle** (hangi
   kapılar düştü) ve yine de yayınlansın mı diye sor. Onaylarsa `force: true` gönder.
3. `POST https://edupedia.cureonics.com/api/publish` — istekte **HER ZAMAN açık bir `slug`
   alanı gönder** (sunucunun `run_id`'den slug türetmesine güvenme; bkz. "Slug türetme"
   aşağıda). `force` argümanı, Adım 2'de kullanıcı onaylarsa `True` yapılır:

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

4. Başarılıysa dönen `url`'yi kullanıcıya göster (paylaşılabilir public bağlantı) ve
   sürüm numarasını söyle. Bu bir yeniden yayınsa (`version > 1`), eski sürümün
   `/m/<slug>/v<N-1>` altında durduğunu belirt.

## Hata durumları

- **400** — geçersiz manifest veya slug (ör. `slug` deseni `^[a-z0-9][a-z0-9-]{1,63}$`'a
  uymuyor, ya da manifest zorunlu alan eksik/hatalı tip). Adım 3'teki slug türetmesi zaten
  bunu önlemeye çalışır; yine de 400 dönerse hata mesajını kullanıcıya göster ve açık,
  geçerli bir `slug` ile tekrar deneyin.
- **401** — token geçersiz. Doppler'daki `EDUPEDIA_PUBLISH_TOKEN`'ı doğrula.
- **422** — kalite kapısı düştü. Hangi kapılar olduğunu göster; modülü düzeltmeyi öner.
  Kullanıcı ısrar ederse `force: true` ile tekrar dene.
- **413** — modül 25 MB'ı aştı (muhtemelen Tier-2 gömülü görseller). Görselleri
  seyreltmeyi öner.
- **Sunucuya ulaşılamıyor** — Pi kapalı olabilir. Yerel HTML dosyasına dokunma; kullanıcıya
  durumu bildir, sonra tekrar denemesini söyle.

Hiçbir durumda başarı uydurma — sunucudan `url` dönmediyse "yayınlandı" deme.
