---
name: salgin
description: "MORBUS modu — bir hastalığın veya salgının tarihi: nasıl deneyimlendi, adlandırıldı, açıklandı ve yönetildi. Veba, kolera, çiçek, tifüs, sıtma, frengi, 1918 gribi, verem, çocuk felci, HIV/AIDS, grip pandemileri, karantina ve tahaffuzhane rejimleri. Retrospektif tanı disiplini ZORUNLU. Kullanın: 'X salgınının tarihi', 'Kara Ölüm', 'kolera pandemisi', 'hastalık biyografisi', 'epidemi tarihi', 'karantina tarihi', 'aşı direnişi tarihi' sorularında."
argument-hint: "<hastalık/salgın> [dönem] [coğrafya]"
allowed-tools: Read, Glob, Grep, WebFetch, Task
disable-model-invocation: false
---

# MORBUS — Salgın ve Hastalık Biyografisi

Flagship protokolü `MORBUS` moduyla çalıştır.

## Zorunlu yüklemeler

```
view ../historia-medicinae/references/retrospective-diagnosis.md   # ZORUNLU
view ../historia-medicinae/references/historical-nosology.md
view ../historia-medicinae/references/quellenkritik.md
view ../historia-medicinae/references/kuresel-cerceve.md
```

## Beş katmanlı iskelet

Bir hastalık biyografisi şu beş katmanı **ayrı ayrı** kurar; karıştırmak en yaygın hatadır.

1. **Adlandırma katmanı** — dönemde ne deniyordu? Terim(ler), dilleri, anlam genişliği.
   Modern etiket burada **kullanılmaz**. Ad çoğu kez kanıttır ("Fransız hastalığı",
   "Asiyatik kolera", "İspanyol gribi" — hiçbiri nötr değildir).
2. **Açıklama katmanı** — dönem nedeni nasıl açıklıyordu? (humoral denge, miyazma, ilâhî ceza,
   kontenjyonizm–antikontenjyonizm tartışması, mikrop teorisi). Bu, bugünün bilgisiyle
   **düzeltilmez**; kendi mantığı içinde yeniden kurulur.
3. **Deneyim katmanı** — hasta, aile, mahalle ne yaşadı? Kaynaklar kurumsal olarak dolayımlıdır
   (heteroglossia formülasyonu, `quellenkritik.md` §4).
4. **Yönetim katmanı** — karantina, tahaffuzhane, cordon sanitaire, bildirim yükümlülüğü,
   zorunlu aşı, izolasyon. Burada **yasama bandı** ateşlenir: Hansard, GovInfo/Congress,
   uluslararası sanitary konvansiyonlar, TBMM/Resmî Gazete.
5. **Nicel katman (varsa)** — ölüm cetvelleri, mortalite serileri. `kaynak-elestirisi` skill'i
   **zorunlu**: seri patolojiyi değil sertifikayı yazanın bilgisini kodlar.

## Retrospektif tanı kapısı

Modern etiket ancak dört kapıdan geçerse kullanılır (gereklilik · kanıt türü · ayırıcı tanı ·
işaretleme). Ayrıntı `retrospective-diagnosis.md`. **Varsayılan: etiketleme yok.**

aDNA kanıtı varsa: yalnız **örneklenen bireyler/mezarlar** için geçerlidir; salgının tamamına
genellenmez.

## Getirim planı

| Katman | Server |
|---|---|
| Tarihyazımı | openalex (T12778, T12324) · pubmed-epmc (MeSH K01.400 + dönem) · semantic-scholar · paper-search · consensus |
| Birincil metin | ottoman-archives IIIF (**Wellcome öncelikli** — veba/kolera risaleleri) |
| Tam metin | openathens → annas-reader |
| Yönetim/yasama | uk-legal (Hansard) · health-policy · intl-treaty · mevzuat/tbmm/resmigazete |
| Terminoloji | med-terminologies (**yalnız doğrulama**, `match_score` kullanılmaz) |
| Nicel | who-gho (yalnız ≈1948+) · globocan (yalnız kanser, çağdaş kesit) |
| Türkiye | literatur · yoktez · devlet-arsivleri |

Ağır fan-out → `tarih-tarama-distilleri` alt-ajanı.

## Çıktı

G0 kapsam manifestosu zorunlu. Retro-hipotez geçtiyse gerekçesiyle beyan edilir.
"Bulunamadı" ifadeleri nerede/hangi terimle arandığını yazar.
