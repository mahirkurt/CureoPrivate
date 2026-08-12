# Akademik Rapor Şablonu — TR ve EN

RELATIO modunda yüklenir. Dil: `report_language` (userConfig veya `.claude/historia-medicinae.local.md`);
ikisi de yoksa **kullanıcıya sorulur**.

Sunum sözleşmesi: `../../../shared/composition-contract.md` §6 (iki katmanlı temiz kopya).

---

## A. Türkçe şablon

```markdown
# <Başlık: konu + dönem + coğrafya>

## Özet
<200-300 kelime: soru, kaynak temeli, ana tez, katkı>

## Anahtar kelimeler
<5-8>

## 1. Giriş ve sorun
<Soru neden önemli; hangi boşluğu dolduruyor>

## 2. Tarihyazımsal konum
<Hangi ekol(ler)e yaslanıyor, hangi tartışmaya giriyor — historiography-schools.md>

## 3. Kaynaklar ve yöntem
<Birincil kaynak temeli (kurum, seri, kapsam); ikincil literatür; arama stratejisi.
 KAMUYA AÇIK veritabanı/arşiv adları — araç günlüğü DEĞİL.
 Kaynak eleştirisi notu: gözlemci zinciri, kapsam dışı kalanlar.>

## 4. <Ana bölümler — konuya göre 2-5 bölüm>

## 5. Tartışma
<Bulguların tarihyazımsal anlamı; rakip yorumlar>

## 6. Sınırlılıklar
<Kaynak boşlukları; dijitalleştirme/OCR kısıtı; erişilemeyen koleksiyonlar;
 retrospektif tanı hipotezlerinin durumu>

## 7. Sonuç

## Kısaltmalar

## Kaynakça
### Birincil kaynaklar
### İkincil kaynaklar
```

---

## B. İngilizce şablon

```markdown
# <Title: topic + period + geography>

## Abstract
## Keywords
## 1. Introduction and problem
## 2. Historiographical position
## 3. Sources and method
## 4. <Main sections>
## 5. Discussion
## 6. Limitations
## 7. Conclusion
## Abbreviations
## Bibliography
### Primary sources
### Secondary sources
```

İngilizce raporda **Türkçe özet** eklenir (yazarın çalışma dili Türkçe olduğunda alan
konvansiyonu budur).

---

## C. Zorunlu unsurlar (dilden bağımsız)

1. **Kronoloji şeridi** — konu bir süreçse (`dataviz` skill'i grafik öncesi okunur).
2. **Kaynak envanteri tablosu** — kurum · seri · kapsam · erişim durumu.
3. **Sınırlılıklar bölümü** — boş bırakılamaz; en az kaynak boşluğu + dijital kısıt.
4. **Retro-hipotez beyanı** — çıktıda modern tanı etiketi geçtiyse gerekçesiyle.
5. **Çift tarih** — Miladî olmayan her tarihte.

## D. Görünmez katmanlar

```
<!-- VIZ: grafik direktifleri -->
<!-- OPS: G0 kapsam manifestosu · arama günlüğü · cömertlik notu · gap listesi -->
```

Görünür gövdede connector/araç adı, MCP, mod kodu, çağrı sayısı **bulunmaz**.

## E. Teslim

Dosya raporu → `carbon-html-report` (VIZ/OPS yorumlarını tüketip siler).
İstatistik/tablo ağırlıklıysa → `carbon-quarto-scientific`.
Finalize öncesi → `sci-audit` (atıf-adli + dil). Kurulu değilse çıktıda beyan edilir.
