---
name: numeric-consistency
description: >-
  replicatio C katmanı — raporlama tutarlılığı (metabilim) denetimi. statcheck ile rapor edilen
  test istatistiği ↔ p-değeri tutarlılığını (yalnız APA-stili; çoklu-karşılaştırma düzeltmesini
  tanımaz), scrutiny ile GRIM/GRIMMER (tamsayı ortalama/SD'lerin N ile mümkün olup olmadığı) ve
  rsprite2 ile SPRITE (parametrelerle uyumlu dağılım var mı) çalıştırır. Bunlar TETİKLEYİCİ
  sinyallerdir, nihai hakem değildir. Kullanıcı rapor edilen p/ortalama/SD tutarlılığını sorduğunda
  kullanın. Tetikleyiciler — p-değeri tutarlılığı, statcheck, GRIM, GRIMMER, SPRITE, raporlanan
  sayı denetimi, reporting consistency, metascience, sayı tutarlılığı.
metadata:
  version: "0.1.0"
allowed-tools: Bash, Read, Glob
---

# replicatio — C Katmanı: Raporlama Tutarlılığı (Metabilim)

Rapor edilen sayıların kendi içinde matematiksel olarak tutarlı olup olmadığını denetler.
**Kritik çerçeve:** statcheck/GRIM/GRIMMER/SPRITE **tetikleyici sinyallerdir** — bir tutarsızlık
bayrağı "hata" kanıtı değil, **elle incelenmesi gereken** bir işarettir. Betik bu uyarıyı her
koşumda bir `_caveat` bulgusu olarak yazar; siz de raporda mutlaka belirtin.

## Yürütme

1. **Girdileri belirle.** İki bağımsız yol (biri veya ikisi):
   - **statcheck için** APA-stili istatistik içeren metin: `.txt/.md`, ya da `.pdf`/`.html`.
   - **GRIM/GRIMMER/SPRITE için** `mean,sd,n` (SPRITE için ek `min,max`) sütunlu bir CSV.

2. **Betiği sür:**
   ```bash
   Rscript "${CLAUDE_PLUGIN_ROOT}/scripts/03_numeric_consistency.R" \
     --text "<metin.txt|.pdf>" --stats "<stats.csv>" --out "$PWD/.replicatio/findings"
   ```
   (Yalnız birini geçmek serbesttir.)

3. **Bulguları oku** (`Read` → `.replicatio/findings/03_numeric_consistency.json`) ve yorumla:
   - **statcheck KARAR hatası** → CRITICAL (rapor edilen p anlamlılık eşiğini yanlış tarafa atıyor).
   - **statcheck tutarsızlık** → MAJOR (rapor edilen p, stat+df'den hesaplananla uyuşmuyor).
   - **GRIM/GRIMMER tutarsız** → MAJOR (ortalama veya ortalama+SD, N ile imkânsız).
   - **SPRITE: dağılım bulunamadı** → MAJOR (parametreler bir araya gelemiyor).

4. **Çerçeveyi koru.** Her tutarsızlığı "incelenmeli" diye sun, "sahtekârlık" diye değil. Olası
   masum nedenler: yuvarlama, eksik düzeltme bildirimi, kopya-yapıştır hatası, farklı N (eksik
   veri). statcheck'in çoklu-karşılaştırma düzeltmelerini tanımadığını açıkça yazın.

5. **Boşluk dürüstlüğü.** Girdi APA formatında değilse statcheck "test bulamadı" der — bunu
   "temiz" diye yorumlamayın; "taranamadı" diye raporlayın.

## Kapsam Dışı
- Modeli yeniden çalıştırıp p üretmek → bu C değil; bağımsız yeniden-hesap için `cross-validate` (F).
- Varsayım testleri → `assumption-audit` (B).

## Notlar
- SPRITE `rsprite2` paketindedir (scrutiny'de DEĞİL); `set_parameters()` + `find_possible_distributions()`.
  `min`/`max` (ölçek sınırları) verilmezse SPRITE atlanır (dürüst OBSERVATION).
- GRIM yalnız tamsayı-bileşenli ölçek ortalamalarında anlamlıdır; sürekli ölçümlerde yanlış-pozitif
  riskini not edin.
