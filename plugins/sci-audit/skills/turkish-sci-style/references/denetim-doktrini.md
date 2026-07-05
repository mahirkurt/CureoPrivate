# Türkçe Bilimsel Yazım Denetimi — Doktrin (axis G)

Bu doküman, `tr_sciaudit.py` çekirdeğinin denetim doktrinini genelleştirir.
Herhangi bir LLM-üretimi Türkçe bilimsel metni (makale, tez bölümü, derleme,
rapor, özet) güvenli ve deterministik biçimde tarar. **Alan-bağımsızdır** —
hiçbir projeye, veri kümesine veya konuya bağlı değildir.

## Amaç

Türkçe bilimsel metni yedi alt-eksende taramak:

1. G1 biçimsel yazım (encoding, noktalama, tekrar, diyakritik),
2. G2 okunabilirlik/üslup (cümle-paragraf uzunluğu, Ateşman),
3. G3 akademik register (birinci kişi, konuşma dili, İngilizce sızıntı),
4. G4 nedensellik/genelleme aşımı dili,
5. G5 ondalık virgül ve `p` değeri yazımı (APA-TR),
6. G6 kısaltma/terim tutarlılığı (ilk-geçişte-açılım, whitelist, TDK),
7. G7 opsiyonel morfoloji (Zemberek).

Bu araç bilimsel doğruluk, istatistiksel uygunluk, kaynak doğrulama,
intihal/benzerlik veya klinik yorum doğruluğu **sertifikası vermez**. Bu
katmanlar sci-audit'in A–F eksenleriyle ayrı kapatılır.

## Sıkılık modları

- `draft` — hızlı ön-denetim (G6 kısaltma taraması kapalı).
- `certification` — tam denetim; G6 kısaltma tutarlılığı + çok-düşük Ateşman
  uyarısı devreye girer.

`--fail-on error` ile: `warning`/`info` bulguları otomatik bloklayıcı değildir;
editör sertifika raporunda neden kabul edildiklerini belirtir. **`error` bulgusu
varsa kapı kapanmaz** — bu, rapor sonucuna yansıtılır; hiçbir araç bunu uydurma
bir "geçti" ile geçiştirmez.

## Katman eşlemesi

| Alt-eksen | Repo-local karşılık | Durum |
|---|---|---|
| G1 biçimsel/dilbilgisel | encoding artefact, noktalama boşluğu, tekrar eden sözcük, diyakritik sinyali | Aktif (ağsız) |
| G2 okunabilirlik/üslup | cümle/paragraf uzunluğu, Ateşman skoru | Aktif (ağsız) |
| G3 akademik register | nedensellik aşımı, birinci kişi, konuşma dili, İngilizce terim sızıntısı | Aktif (ağsız) |
| G4 nedensellik | nedensel ifade kalıpları | Aktif (ağsız) |
| G5 sayı biçimi | ondalık nokta uyarısı + İngilizce p-değeri (ERROR/blocker) | Aktif (ağsız) |
| G6 terminoloji | kısaltma insan-inceleme sinyali + whitelist + TDK lookup | certification'da aktif; TDK opsiyonel |
| G7 morfoloji | Zemberek örneklemi | Paket varsa aktif, yoksa `unavailable` |

## Provider davranışı (güvenli fallback sözleşmesi)

| Provider | Varsayılan | Aktifleştirme | Başarılı durum | Güvenli fallback |
|---|---|---|---|---|
| Deterministik G1–G6 | Açık | — | Her ortamda çalışır (web dahil), ağ gerektirmez | Yok — daima mevcut |
| TDK | Kapalı | `--enable-tdk --terms ...` | `sozluk.gov.tr/gts` sınırlı terim kontrolü | HTTP hatası `error` provider statüsü; deterministik denetim sürer |
| GECTurk | Kapalı | `--enable-gecturk --gecturk-url ...` | Self-host endpoint JSON yanıtı | URL yoksa public API varsayılmaz → `unavailable` |
| Zemberek | Kapalı | `--enable-zemberek` | Örnek kelime morfolojisi | Paket yoksa `unavailable`; rapor bloklamaz |
| LLM-yargıç | Kapalı | `style-judge` alt-ajanı | Register/akıcılık/terim rubriği (Claude-native) | Deterministik G ekseni tek başına ayakta |

## Güvenlik ve gizlilik

- Deterministik çekirdek tamamen yereldir; metni hiçbir harici API'ye
  göndermez. Yalnız açıkça verilen dosyayı okur.
- **Grok/xAI adapter'ı deterministik çekirdekten çıkarılmıştır.** Web-native
  çözüm `style-judge` Claude alt-ajanıdır. Grok yargıcı yalnız `reliability/`
  altındaki opsiyonel CI-eval katmanında bırakılır; orada bile `GROK_API_KEY`
  yoksa metin gönderilmeden `unavailable` döner — gizlilik sözleşmesi korunur.
- TDK lookup yalnız sınırlı terim listesiyle çalışır; sözlüğün tamamı
  indirilmez.
- GECTurk için belgelenmemiş public API tahmini yapılmaz; yalnız repo-local
  self-host endpoint veya doğrulanmış kurumsal endpoint kullanılır.
- Raporlar yalnız türetilmiş metrik ve kısa kanıt parçaları içerir.

## Ateşman okunabilirlik formülü

Ateşman (1997): **okunabilirlik = 198,825 − 40,175 × (hece/kelime) − 2,610 ×
(kelime/cümle)**. Yüksek skor = kolay. Etiketler: ≥90 çok kolay, ≥70 kolay,
≥50 orta, ≥30 zor, altı çok zor. Certification'da <25 skor bir uyarı üretir
(bilimsel içeriğin zorluğu haklı mı?).

## APA-TR sayı biçimi

- Türkçe bilimsel metinde ondalık ayırıcı **virgül**dür: `3,14` (`3.14` değil).
- p-değeri APA-TR: `p<0,001`, `p=0,03`. Türkçe metinde İngilizce ondalık-noktalı
  p-değeri (`p<0.05`) **blocker**'dır; Stop hook'u da bunu tur sonunda yakalar.
- Sürüm numaraları ve tanımlayıcılar (ör. `2.0.1`, DOI) ondalık kuralından
  muaftır; deterministik çekirdek bunları uyarı düzeyinde işaretler, editör
  değerlendirir.

## Genelleştirme kuralı

Projeye özgü kısaltma whitelist'leri ve terim listeleri **koddan çıkarılmıştır**;
`--abbreviations` ve `--terms` parametreleriyle çalışma anında verilir. Çekirdek
yalnız alan-bağımsız genel bilimsel/istatistiksel kısaltmaları tanır.
