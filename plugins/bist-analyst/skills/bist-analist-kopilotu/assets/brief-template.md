<!--
  brief-template.md — Mod 1 (tek hisse derin analizi) brifing iskeleti.
  Skill bu iskeleti doldurur; {{...}} alanları gerçek değerlerle değiştirilir.
  report-style.md kurallarına uyar: bilimsel Türkçe, kendine yeten belge,
  makine-dili sızıntısı YOK (ham JSON / araç adı / "MCP" gövdede geçmez),
  her sayı birim + as-of tarihiyle, her sonuç güven + karşıt senaryoyla,
  sonda zorunlu kanonik feragat. Çıktı karar-destektir, yatırım tavsiyesi değildir.

  Diğer modlarda iskelet kırpılır:
   - Mod 2 (haftalık tarama): "Teknik görünüm" yerine aday tablosu; her aday için
     1-2 satır gerekçe; "Temel/Makro" özetlenir; senaryo matrisi liste düzeyinde.
   - Mod 3 (KAP/olay): "KAP & haber akışı" merkeze alınır (olay sınıfı + materyalite
     + olası yön + reaksiyon penceresi); teknik/temel bağlam destekleyici kalır.
   - Mod 4 (izleme listesi): snapshot-arası değişim tablosu öne çıkar; her sembol
     için yalnızca değişen boyutlar yazılır.
-->

# {{SEMBOL}} — Karar-Destek Brifingi
**Şirket:** {{SIRKET_ADI}} · **Sektör:** {{SEKTOR}} · **Endeks:** {{ENDEKS (örn. XU030/XBANK)}}
**Veri tarihi (as-of):** {{GG.AA.YYYY}} kapanış · **Veri niteliği:** gün sonu (EOD), gecikmeli olabilir

## 1. Karar-destek özeti
{{2-4 cümle: bütünleşik duruş (teknik + temel + KAP + makro), genel güven düzeyi
(Yüksek/Orta/Düşük) ve en kritik izlenecek unsur. Tavsiye dili kullanılmaz.}}

## 2. Teknik görünüm (çok zaman dilimli)
- **Haftalık (1W) trend:** {{trend okuması}}
- **Günlük (1d) kurulum:** {{RSI bölgesi, MACD histogram, hareketli ortalama dizilimi, Bollinger konumu, Supertrend/T3}}
- **Teknik duruş:** {{Güçlü Yukarı / Zayıf Yukarı / Nötr / Zayıf Aşağı / Güçlü Aşağı}} — *güven: {{Yüksek/Orta/Düşük}}*
- **Ayrışma / yanlış sinyal riski:** {{varsa not}}
- **Önemli seviyeler ({{GG.AA.YYYY}} kapanışına göre):** destek {{S1}}, {{S2}} TL · direnç {{R1}}, {{R2}} TL

## 3. Temel görünüm (sektör-normalize)
- **Değerleme:** {{F/K, PD/DD, FD/FAVÖK — sektör medyanına göre konum}}
- **Kârlılık:** {{ROE, ROA, net/FAVÖK marjı}}
- **Finansal sağlık:** {{kaldıraç, cari oran, net borç/FAVÖK}}
- **Büyüme:** {{satış/kâr YoY}} — *TL-enflasyon uyarısı: {{nominal mi reel mi}}*
- **Finansal kalite skoru:** {{0-100}} → {{Yüksek/İyi/Orta/Zayıf}} *(kapsam: {{%}})*
- **Üçüncü-taraf analist görünümü:** {{varsa}} — *doğrulanmamış / üçüncü-taraf bağlam; yönlendirici değildir*

## 4. KAP & haber akışı
- **Son dönem öne çıkan açıklamalar ({{tarih aralığı}}):** {{özet}}
- **Duygu eğilimi:** {{pozitif/nötr/negatif}} ({{skor}}) · **En materyal açıklama:** {{başlık}} — materyalite: {{Yüksek/Orta/Düşük}}
- **Olası etki:** {{yön + reaksiyon penceresi}} — *güven: {{...}}; karşıt senaryo: {{...}}*

## 5. Makro çerçeve (TCMB)
- **Rejim:** {{Sıkılaştırma / Gevşeme / Nötr-Yatay / Belirsizlik-Stres}}
- **Sinyaller:** politika faizi {{...}}, TÜFE {{...}}, USDTRY {{...}}, reel faiz {{...}}
- **Sektöre/şirkete yansıma:** {{iskonto oranı baskısı, sektör eğilimi}}

## 6. Senaryo matrisi
{{scenario-matrix-template.md doldurulur: Baz / Boğa / Ayı; her biri için tetikleyici,
teknik teyit, temel/makro koşul, geçersizlik seviyesi, güven.}}

## 7. İzlenecek seviyeler & tetikler
- {{seviye/olay 1}} · {{seviye/olay 2}} · {{yaklaşan KAP/bilanço/temettü tarihi}}

## 8. Feragat
Bu içerik yalnızca bilgilendirme ve karar-destek amaçlıdır; yatırım danışmanlığı, aracılık veya al/sat tavsiyesi niteliği taşımaz. Veriler büyük ölçüde gün sonu (EOD) ve gecikmeli olabilir; gün içi emir defteri/derinlik bilgisi içermez. Yatırım kararları; kişinin kendi risk profili, bağımsız araştırması ve gerektiğinde SPK lisanslı bir yatırım danışmanına danışılarak alınmalıdır. Geçmiş performans gelecekteki getirinin garantisi değildir.
