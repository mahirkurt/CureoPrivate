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
3. `POST https://edupedia.cureonics.com/api/publish`:

```bash
python3 - <<'PY'
import json, os, sys, urllib.request, urllib.error
html_path, manifest_path = sys.argv[1], sys.argv[2]
payload = {
    "html": open(html_path, encoding="utf-8").read(),
    "manifest": json.load(open(manifest_path, encoding="utf-8")),
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

4. Başarılıysa dönen `url`'yi kullanıcıya göster (paylaşılabilir public bağlantı) ve
   sürüm numarasını söyle. Bu bir yeniden yayınsa (`version > 1`), eski sürümün
   `/m/<slug>/v<N-1>` altında durduğunu belirt.

## Hata durumları

- **401** — token geçersiz. Doppler'daki `EDUPEDIA_PUBLISH_TOKEN`'ı doğrula.
- **422** — kalite kapısı düştü. Hangi kapılar olduğunu göster; modülü düzeltmeyi öner.
  Kullanıcı ısrar ederse `force: true` ile tekrar dene.
- **413** — modül 25 MB'ı aştı (muhtemelen Tier-2 gömülü görseller). Görselleri
  seyreltmeyi öner.
- **Sunucuya ulaşılamıyor** — Pi kapalı olabilir. Yerel HTML dosyasına dokunma; kullanıcıya
  durumu bildir, sonra tekrar denemesini söyle.

Hiçbir durumda başarı uydurma — sunucudan `url` dönmediyse "yayınlandı" deme.
