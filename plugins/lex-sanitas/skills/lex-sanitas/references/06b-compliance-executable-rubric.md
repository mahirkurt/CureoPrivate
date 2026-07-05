# 5210 Uyum Denetimi — Executable Rubric Tablosu (v2.3)

Bu dosya, **R6 (06-compliance-checklist.md)** dosyasının 21 noktalı kontrol listesine **somut PASS/FAIL/CONDITIONAL kriterleri**, **test prosedürleri** ve **remediation rehberi** ekleyen *executable* katmandır.

R6 = "Ne kontrol edilir?" (descriptive)  
R6b = "Nasıl kontrol edilir + Sonuç nasıl yorumlanır + Sapma varsa nasıl düzeltilir?" (executable)

**Kullanım:** Mod 4 (COMPLY) çıktısında her kontrol için bu rubric uygulanır; sonuçlar `compliance_audit` çıktısı format şablonu içinde sergilenir.

---

## Bölüm 1 — Rubric Felsefesi

### 1.1. Hüküm Tipolojisi

| Hüküm | Anlam | Aksiyon |
|---|---|---|
| **PASS** | Kontrol ölçütleri **eksiksiz** karşılanıyor; herhangi bir düzeltme gerekmez. | Yayına/onaya hazır. |
| **FAIL** | Kontrol ölçütleri ihlal edilmiş; **ret veya iptal riski yüksek**. | Yayın öncesi mutlaka düzeltilmesi gerekir. |
| **CONDITIONAL** | Kontrol kısmen karşılanıyor; eksiklik var ama kritik değil. | Düzeltme önerisi sunulur; yetkili kurum kararı ile yayınlanabilir. |
| **N/A** | Kontrol mevzuat tipine uygulanamaz (örn. tebliğde DEA aranmaz). | Aksiyon yok; gerekçe raporlanır. |

### 1.2. Risk Ağırlıkları

Her kontrolün ihlal hâlinde mevzuata getireceği risk derecesi:

| Risk seviyesi | Anlam | İlgili kontroller |
|---|---|---|
| **YÜKSEK** | Anayasal/idari iptal riski; doğrudan üst norm ihlali | K-1, K-8, K-17, K-18, K-20 |
| **ORTA** | Şekli iade veya tekrar inceleme riski | K-9, K-10, K-12, K-13, K-14 |
| **DÜŞÜK** | Kalite/profesyonel imaj riski | K-3, K-4, K-7, K-11, K-15, K-16 |
| **DEĞIŞKEN** | Mevzuat tipine/içeriğe bağlı | K-2, K-5, K-6, K-19, K-21 |

### 1.3. Geçiş Eşikleri

| Yayına/onaya hazır | Tüm 21 kontrol PASS veya N/A; CONDITIONAL ≤ 3, FAIL = 0 |
| Yayın öncesi düzeltme | FAIL = 1 (YÜKSEK risk) veya CONDITIONAL ≥ 4 (ORTA/YÜKSEK risk) |
| Kapsamlı revizyon | FAIL ≥ 2 veya YÜKSEK riskli kontrolde FAIL |
| Tasarımı yeniden gözden geçir | FAIL ≥ 5 veya K-1 / K-17 FAIL |

---

## Bölüm 2 — Maddi Uygunluk (5210 Md. 4) — 8 Kontrol

### 2.1. Kontrol 1: Üst Hukuk Normuna Uygunluk (Md. 4/a) — **YÜKSEK RİSK**

**Test prosedürü:**
1. Taslağın **üst norm zincirini** belirleyin: Anayasa → Kanun → KHK/CBK → Yönetmelik → Tebliğ.
2. Taslağın her ana hükmünü üst normun ilgili maddesi/maddeleri ile **bire-bir eşleştirme** tablosu çıkarın.
3. Mevzuat MCP üzerinden üst normun **güncel** sürümünü teyit edin (yürürlükteki sürüm).
4. Anayasa Md. 90/5 uyarınca **uluslararası antlaşma** ihlali olmadığını da denetleyin (ICESCR, AİHS, Oviedo, TRIPS).

**PASS:**
- Her hüküm üst normun ilgili maddesine atfedilebilir.
- Üst normda yetki veriliyor (örn. "Yönetmelik ile düzenlenir").
- Anayasa + AB müktesebatı + Md. 90/5 uluslararası taahhütlerle çelişmiyor.

**FAIL:**
- En az bir hüküm üst normun açık yetki verdiği alan **dışında**.
- Üst norm değişmiş ama taslak eski sürüme atıfta bulunuyor.
- Anayasa Md. 7 (yasama yetkisi devredilemez) ihlali — yönetmelik kanun benzeri yükümlülük öngörüyor.

**CONDITIONAL:**
- Üst norm var ama yetki sınırı *grimsi*; yorumla geniş alana yayılıyor.
- Md. 90/5 uluslararası taahhütlerle uyum *kısmen* sağlanmış; bazı yönlerde boşluk var.

**Remediation:**
- FAIL → Üst normun açık yetki vermediği hükümleri kaldır veya kanun seviyesine taşı; kanun teklifi (Mod 8) önerisi.
- CONDITIONAL → Üst norm yetki sınırına uygun yorumla yeniden formüle et; gerekçede yetki zincirini açıkça belirt.

**Atıf:** R1 (5210) + R13 (anayasa içtihatı) + R10 (BM uluslararası sağlık hukuku)

---

### 2.2. Kontrol 2: Düzenleme Amacına Uygunluk (Md. 4/b) — **DEĞIŞKEN RİSK**

**Test prosedürü:**
1. Taslağın **amaç maddesini** (Md. 1) tespit edin.
2. Her ana hükmün **amaca hizmet edip etmediğini** soru-cevap formatıyla denetleyin.
3. Amaç dışı hüküm tespit edilirse, Md. 4/c (çoklu kaynak gözetimi) ile çatışma olup olmadığını da denetleyin.

**PASS:**
- Her hüküm amaç maddesinin kapsamında.
- Amaç ile uygulama mekaniği arasında bağlantı net.

**FAIL:**
- En az bir hüküm amaç dışı (örn. "ilaç ruhsat sürecini düzenleyen" tebliğde tıbbi cihaz hükmü).
- Amaç maddesi ile uygulama maddeleri arasında **çelişki** var.

**CONDITIONAL:**
- Amaç-hüküm bağlantısı zayıf; gerekçe gerektiriyor.

**Remediation:**
- FAIL → Amaç dışı hükümleri ayrı bir mevzuata taşı; veya amaç maddesini genişletmek için yetkiyi gözden geçir.

**Atıf:** R1 + R4 (madde yapısı)

---

### 2.3. Kontrol 3: Çoklu Kaynak Gözetimi (Md. 4/c) — **DÜŞÜK RİSK**

**Test prosedürü:**
1. Aynı konuda yürürlükte olan **diğer mevzuatları** tespit edin (Mevzuat MCP cross-reference).
2. Yeni taslağın bu kaynakla **çelişip çelişmediğini** denetleyin.
3. **AB müktesebatı** ile uyumu R8 + R12 referans alarak değerlendirin.

**PASS:**
- Yürürlükteki diğer mevzuatla çelişki yok.
- AB müktesebatıyla uyum var (Md. 4/c operasyonel yansıması — bkz. Kontrol 20).

**FAIL:**
- Mevcut yürürlükteki mevzuatla doğrudan çelişen hüküm.
- AB müktesebatı uyumlu olması gereken alanda boşluk veya çelişki.

**CONDITIONAL:**
- Eski mevzuatı zımnen ilga eden hüküm ama bu açıkça belirtilmemiş (K-13 ile çapraz denetim).

**Remediation:**
- FAIL → Çelişen mevzuatı açıkça yürürlükten kaldır (K-13 ile birlikte); veya çelişen hükmü düzelt.

**Atıf:** R1 + R8 + R12

---

### 2.4. Kontrol 4: Mevzuat Enflasyonu Temizliği (Md. 4/ç) — **DÜŞÜK RİSK**

**Test prosedürü:**
1. Yeni taslakla **konusunda zaten yürürlükte** olan mevzuatın **gerekli olup olmadığını** denetleyin.
2. Eğer mevcut mevzuat yeterliyse, yeni taslağın gerekçesini sorgulayın.

**PASS:**
- Yeni taslak gerçek bir boşluğu dolduruyor veya mevcut mevzuatın **etkisiz kısmını** revize ediyor.
- Mevcut mevzuat ile **mükerrer** değil.

**FAIL:**
- Yeni taslak mevcut mevzuatın **kopyası** veya çok küçük farkla tekrarı.

**CONDITIONAL:**
- Yeni taslak gerekli ama mevcut mevzuat ile **konsolidasyon** daha verimli olabilirdi.

**Remediation:**
- FAIL → Yeni taslağı geri çek veya mevcut mevzuatı revize etmek için Mod 2 (AMEND) kullan.
- CONDITIONAL → Mevcut mevzuatın yürürlükten kaldırılarak yeni taslakla konsolide edilmesi önerisi (Md. 18-19 değişiklik tekniği).

**Atıf:** R1

---

### 2.5. Kontrol 5: Tek Metin Bütünlüğü (Md. 4/d) — **DEĞIŞKEN RİSK**

**Test prosedürü:**
1. Taslak **tek bir konuyu** kapsayıp kapsamadığını denetleyin.
2. Birden fazla konuyu birleştiren taslak için her konunun **birbirine bağlı** olup olmadığını sorgulayın.

**PASS:**
- Taslak tek bir konuyu veya birbirine sıkı bağlı konuları kapsıyor.

**FAIL:**
- Taslak konu bütünlüğü olmayan birden fazla konuyu içeriyor (örn. "ilaç ruhsat + reklamcılık + perakende fiyat" tek bir yönetmelikte).

**CONDITIONAL:**
- Konular ilişkili ama bağ zayıf; ayrı mevzuat daha temiz olabilirdi.

**Remediation:**
- FAIL → Bütünlüğü olmayan konuları ayrı mevzuatlara böl.

**Atıf:** R1 + R4

---

### 2.6. Kontrol 6: Kapsam Maddesi Netliği (Md. 4/e) — **DEĞIŞKEN RİSK**

**Test prosedürü:**
1. Taslağın **Md. 2 kapsam maddesini** kontrol edin.
2. Kapsamın **belirli, açık ve sınırlı** olup olmadığını sorgulayın.
3. Kapsam dışı kalan unsurları açıkça belirten **istisna** maddelerini denetleyin.

**PASS:**
- Kapsam maddesi belirli ve net.
- İstisnalar (varsa) açıkça sayılmış.

**FAIL:**
- Kapsam maddesi "ve benzeri", "ilgili tüm" gibi belirsiz ifadeler içeriyor (AYM belirlilik içtihadı ihlali).

**CONDITIONAL:**
- Kapsam genel olarak belirli ama bazı sınırlardaki vakalar tereddüt yaratıyor.

**Remediation:**
- FAIL → AYM belirlilik içtihadı uyarınca kapsam maddesini somutlaştır; "ve benzeri" yerine **tam liste** kullan.

**Atıf:** R1 + R4 + R13 (AYM belirlilik içtihadı)

---

### 2.7. Kontrol 7: Madde Kısalığı ve Sadeliği (Md. 4/f) — **DÜŞÜK RİSK**

**Test prosedürü:**
1. Her maddenin **ortalama uzunluğunu** ölçün (kelime sayısı).
2. Fıkra-bent yapısının **gereksiz karmaşık** olup olmadığını denetleyin.
3. R9 Bölüm 9 (15-noktalı dil kontrolü) kısalık alt kontrolünü uygulayın.

**PASS:**
- Maddelerin %80'i ≤ 80 kelime.
- Fıkra-bent yapısı zorunlu mantıksal ayrım için kullanılmış.

**FAIL:**
- Maddelerin çoğunluğu ≥ 150 kelime.
- Tek madde 3 + alt seviye fıkra/bent yapısı içeriyor.

**CONDITIONAL:**
- Bazı maddeler uzun ama içerik teknik gereklilik gerektiriyor.

**Remediation:**
- FAIL → Uzun maddeleri böl; alt bent yapısını sadeleştir.

**Atıf:** R1 + R4 + R9 Bölüm 9

---

### 2.8. Kontrol 8: Çoklu Görev Alanında Mutabakat (Md. 4/g) — **YÜKSEK RİSK**

**Test prosedürü:**
1. Taslağın etkilediği **tüm kurumları** tespit edin (TİTCK, SGK, KVKK, SB, vd.).
2. Hazırlık aşamasında bu kurumlardan **görüş alınıp alınmadığını** denetleyin (EK-1 Görüş Bildirimi).
3. AB Başkanlığı'ndan görüş alındı mı (AB müktesebatı uyumlu mevzuat için zorunlu).

**PASS:**
- Etkilenen tüm kurumlardan görüş alınmış.
- Görüşler taslakta yansıtılmış.
- AB Başkanlığı görüşü (varsa) alınmış.

**FAIL:**
- Etkilenen bir kurum görüş süreci dışında bırakılmış.
- AB müktesebatı uyumlu olması gereken taslakta AB Başkanlığı görüşü yok.

**CONDITIONAL:**
- Görüşler alınmış ama bazıları zayıf yansıtılmış.

**Remediation:**
- FAIL → Eksik kurumdan görüş al; taslağı revize et; EK-1 Görüş Bildirimi belgesini tamamla.

**Atıf:** R1 + R7 (mevzuat MCP workflow)

---

## Bölüm 3 — Şekli Uygunluk (5210 Md. 10-22) — 6 Kontrol

### 3.1. Kontrol 9: Gerekçeler Mevcut mu (Md. 10 + 23) — **ORTA RİSK**

**Test prosedürü:**
1. **Genel gerekçe** dokümanı var mı? (zorunlu)
2. **Her madde için madde gerekçesi** var mı? (zorunlu)
3. Madde gerekçesi madde metnini **tekrarlıyor mu** (anti-pattern 5)?
4. R9 Bölüm 9.0 (Yılmaz doktrini) + CMK Md. 232 + HMK Md. 297 paralelleri gözetildi mi?

**PASS:**
- Genel gerekçe + tüm madde gerekçeleri mevcut.
- Madde gerekçesi madde metnini tekrarlamıyor.
- Gerekçeler **somut ve özlü**.

**FAIL:**
- Madde gerekçesi eksik veya madde metninin **kopyası**.
- Genel gerekçe çok kısa veya boş şablon.

**CONDITIONAL:**
- Gerekçeler mevcut ama bazı maddeler için yetersiz.

**Remediation:**
- FAIL → Madde gerekçelerini yeniden yaz; `templates/madde-gerekce.md` ve `templates/genel-gerekce.md` şablonlarını kullan.

**Atıf:** R1 + R9 Bölüm 9.0 + Anti-pattern 5

---

### 3.2. Kontrol 10: Madde Sıralaması Md. 15'e Uygun mu — **ORTA RİSK**

**Test prosedürü:**
1. Taslak madde sıralamasını denetleyin:
   - Md. 1 — Amaç
   - Md. 2 — Kapsam
   - Md. 3 — Dayanak
   - Md. 4 — Tanımlar (varsa)
   - Md. 5+ — Esasa ilişkin hükümler
   - Son maddeler — Yürürlükten kaldırma + Yürürlük + Yürütme

**PASS:**
- Sıralama Md. 15 ile tam uyumlu.

**FAIL:**
- Sıralama ihlali (örn. tanımlar maddesi sonda).

**CONDITIONAL:**
- Geçici maddeler veya istisna sıralamalar Md. 15'in beklediği yerden farklı ama doğrulanabilir gerekçe var.

**Remediation:**
- FAIL → Maddeleri Md. 15 sıralamasına göre yeniden düzenle.

**Atıf:** R1 + R4

---

### 3.3. Kontrol 11: MADDE Numaraları ve Tipografi (Md. 13) — **DÜŞÜK RİSK**

**Test prosedürü:**
1. Madde numaralarının "MADDE 1-", "MADDE 2-" gibi format gözetilip gözetilmediğini denetleyin (büyük harf + tire).
2. Çerçeve maddelerde başlık yazılıp yazılmadığını denetleyin (anti-pattern 7).
3. Madde başlığında **noktalama** veya **altı çizili** format kontrolü (anti-pattern 6).

**PASS:**
- "MADDE 1-" formatı tutarlı.
- Çerçeve maddelerde başlık yok.
- Madde başlığında noktalama/altı çizili yok.

**FAIL:**
- Format tutarsız (örn. "Madde 1.", "1. Madde", "Md. 1").
- Çerçeve maddelerde başlık var.

**CONDITIONAL:**
- Format genelde uyumlu ama 1-2 madde formatı bozuk.

**Remediation:**
- FAIL → Tipografiyi standardize et.

**Atıf:** R1 + R4 + Anti-pattern 6-7

---

### 3.4. Kontrol 12: Atıf Formatı (Md. 21) — **ORTA RİSK**

**Test prosedürü:**
1. Her atıfta **tarih formatı** denetlenir: sıfırsız + eğik çizgi (örn. `1/3/2024`, **`01/03/2024` değil**) (anti-pattern 3).
2. Madde sıra sayıları **ses uyumu eki** denetlenir: "5 inci maddesi", "12 nci maddesi", "1 inci fıkrası" (anti-pattern 4 — kesme işareti yok).
3. **Alt düzeydeki mevzuata atıf** yasağı denetlenir (Md. 21/6 — anti-pattern 8).
4. Anti-pattern 19 (yargıya talimat yasağı, Md. 138/2) tarama.

**PASS:**
- Tüm atıflar Md. 21 formatına uygun.
- Tarih sıfırsız + eğik çizgi.
- Ses uyumu ekleri doğru.
- Alt düzeye atıf yok.
- Yargıya talimat ifadesi yok.

**FAIL:**
- Tarih `01/03/2024` formatında veya `5. maddesi` kesme işareti var.
- Kanunda yönetmeliğe somut atıf var.
- "Yargı organlarına talimat" ifadesi var.

**CONDITIONAL:**
- Atıfların büyük çoğunluğu doğru ama 1-2 tanesi yanlış.

**Remediation:**
- FAIL → Atıf formatını otomatize edilmiş tarama ile düzelt (R3 reçetesi).

**Atıf:** R1 + R3 (atıf tekniği) + Anti-pattern 3-4, 8, 19

---

### 3.5. Kontrol 13: Yürürlükten Kaldırma Açıklığı (Md. 21/8) — **ORTA RİSK**

**Test prosedürü:**
1. Eski mevzuatı yürürlükten kaldıran hükümlerin **somut atıf** içerdiğini denetleyin.
2. "Aykırı hükümler yürürlükten kaldırılmıştır" gibi muğlak ifadeler **yasaktır** (anti-pattern 2).

**PASS:**
- Tüm yürürlükten kaldırma hükümleri **somut atıf** içeriyor (mevzuat adı + RG tarih/sayı + madde no).

**FAIL:**
- "Bu Yönetmeliğin aykırı hükümleri yürürlükten kaldırılmıştır" gibi muğlak ifade.

**CONDITIONAL:**
- Çoğunluğu somut ama 1-2 hüküm muğlak.

**Remediation:**
- FAIL → "Aykırı hükümler" yerine **tam mevzuat atfı** kullan.

**Atıf:** R1 + Anti-pattern 2

---

### 3.6. Kontrol 14: Değişiklik Tekniği (Md. 18-19) — **ORTA RİSK**

**Test prosedürü:**
1. Tek çerçeve madde ile **birden fazla bağlantısız mevzuatı** değiştirip değiştirmediğini denetleyin (anti-pattern 9).
2. **Mükerrer madde** oluşturulup oluşturulmadığını kontrol edin; yerine **ek madde** kullanılması (anti-pattern 10).
3. Değişiklik metninde **karşılaştırma cetveli** (eski hâl - yeni hâl) eki var mı?

**PASS:**
- Tek çerçeve madde, tek ilgili mevzuatı değiştiriyor.
- Mükerrer madde yok; ek madde tekniği kullanılmış.
- Karşılaştırma cetveli ek olarak hazırlanmış.

**FAIL:**
- Tek çerçeve madde ile birden fazla bağlantısız mevzuat değişikliği.
- Mükerrer madde var.

**CONDITIONAL:**
- Karşılaştırma cetveli mevcut ama eksik.

**Remediation:**
- FAIL → Değişiklikleri ayrı çerçeve maddelere böl; mükerrer madde yerine ek madde tekniği kullan; `templates/karsilastirma-cetveli.md`.

**Atıf:** R1 + R4 + Anti-pattern 9-10

---

## Bölüm 4 — Dil ve Gerekçe (5210 Md. 23, 25) — 2 Kontrol

### 4.1. Kontrol 15: Madde Gerekçesi Kalitesi (Md. 23) — **DÜŞÜK RİSK**

**Test prosedürü:**
1. Her madde için gerekçenin:
   - Madde metnini **tekrarlamadığını** (anti-pattern 5).
   - **Somut ve özlü** olduğunu.
   - Madde değişikliği ise eski-yeni karşılaştırması veya **değişiklik gerekçesi** içerdiğini.
   - HMK 297/CMK 232 paralellerini gözettiğini (R9 Bölüm 9.0).
2. R9 Bölüm 9 — 15-noktalı dil kontrolünü uygulayın.

**PASS:**
- Gerekçeler madde metnini tekrarlamıyor.
- Gerekçeler somut + özlü.
- Yılmaz doktrini üç doğru niteliği (yasaya uygunluk, gerçekliğe uygunluk, bağlantılı dile uygunluk) karşılanıyor.

**FAIL:**
- Gerekçeler madde metnini kopyalıyor.
- Gerekçeler boş şablon.

**CONDITIONAL:**
- Bazı gerekçeler güçlü, bazıları zayıf.

**Remediation:**
- FAIL → Gerekçeleri Yılmaz doktrini gözetilerek yeniden yaz.

**Atıf:** R1 + R9 Bölüm 9.0 + Anti-pattern 5, 21

---

### 4.2. Kontrol 16: Dil Kuralları (Md. 25) — **DÜŞÜK RİSK**

**Test prosedürü:**
1. Türkçe karşılığı olan yabancı terim kullanılıp kullanılmadığını denetleyin (Md. 25/3 — anti-pattern 11).
2. "Yasa" kelimesinin "kanun" yerine kullanılıp kullanılmadığını denetleyin (Md. 25/7 — anti-pattern 12).
3. Çok-anlamlı hukuki terim kullanımı denetlenir (anti-pattern 20 + R9 Bölüm 8.bis).
4. R9 Bölüm 9 (15-noktalı dil kontrolü) tam uygulanır.

**PASS:**
- Türkçe karşılığı olan yabancı terim yok.
- "Kanun" kelimesi tutarlı kullanılmış.
- Çok-anlamlı terim için **bağlam** veya **madde atfı** sağlanmış.

**FAIL:**
- "Fluide" yerine "akıcı" kullanılmamış.
- "Yasa" kelimesi kullanılmış.
- "Husumet" gibi çok-anlamlı terim tek başına kullanılmış.

**CONDITIONAL:**
- Çoğunluğu doğru ama 1-2 ihlal.

**Remediation:**
- FAIL → Yabancı terimleri Türkçe karşılığa çevir; "kanun" terimini tutarlı kullan; çok-anlamlı terimlere **bağlam** ekle.

**Atıf:** R1 + R9 Bölüm 8.bis + 9 + Anti-pattern 11-12, 20

---

## Bölüm 5 — Yetki ve Kanunilik (5210 Md. 24) — 2 Kontrol

### 5.1. Kontrol 17: Yönetmelik / Tebliğ / Genelge Yetki Sınırı (Md. 24) — **YÜKSEK RİSK**

**Test prosedürü:**
1. Mevzuat tipinin **yetki sınırını** kontrol edin:
   - **Yönetmelik:** Kanunda yetki veriliyorsa, kanunda gösterilen ölçüde
   - **Tebliğ:** Yönetmelikte yetki veriliyorsa, yönetmelikte gösterilen ölçüde
   - **Genelge:** Kurum içi açıklama; üçüncü kişilere doğrudan yükümlülük getirilemez
2. Anti-pattern 1 (yönetmelikte kanun dışı yükümlülük) tarama.
3. Anayasa Md. 7 (yasama yetkisi devredilemez) denetimi.

**PASS:**
- Mevzuat tipinin yetki sınırı içinde kalıyor.
- Kanunda öngörülmeyen yükümlülük yok.

**FAIL:**
- Yönetmelikte kanun dışı yükümlülük (örn. mali yük) öngörülmüş.
- Tebliğde yönetmeliğin verdiği sınırın ötesine geçen düzenleme.
- Genelgede üçüncü kişilere yükümlülük.

**CONDITIONAL:**
- Yetki sınırı yorumla genişletilmiş ama açık ihlal yok.

**Remediation:**
- FAIL → Yetki dışı hükümleri çıkar; gerekirse kanun teklifi (Mod 8) ile yetki düzenlemesi öner.

**Atıf:** R1 + R13 (anayasa içtihatı) + Anti-pattern 1

---

### 5.2. Kontrol 18: Mali Yük Kanuniliği (Md. 24 + Anayasa Md. 73) — **YÜKSEK RİSK**

**Test prosedürü:**
1. Taslakta **vergi, harç, prim, ödeme** öngörülüyor mu?
2. Eğer evet, bu mali yük **kanun** seviyesinde mi düzenlenmiş?
3. Anayasa Md. 73/3 (vergi, resim, harç ve benzeri mali yükümlülükler kanunla konulur) ihlali var mı?

**PASS:**
- Mali yük yok veya mevcut mali yük kanunla konulmuş.

**FAIL:**
- Yönetmelik/tebliğ mali yük öngörüyor ve kanun dayanağı yok.
- Anayasa Md. 73/3 ihlali.

**CONDITIONAL:**
- Mali yük dolaylı (örn. başvuru ücreti) ve gerekçesi tartışmalı.

**Remediation:**
- FAIL → Mali yükü kanun teklifi (Mod 8) ile düzenle; veya yetki vermeyi kanun değişikliği ile sağla.

**Atıf:** R1 + R13 (AYM Md. 73 içtihatı)

---

## Bölüm 6 — Kalite Güvence (5210 Md. 26-27) — 1 Kontrol

### 6.1. Kontrol 19: DEA + BEF Mevcut mu? — **DEĞIŞKEN RİSK**

**Test prosedürü:**
1. Mevzuat tipine göre DEA + BEF zorunluluğu:
   - Kanun + KHK + CBK + Yönetmelik (mali etkili): **DEA + BEF zorunlu**.
   - Tebliğ + Genelge: **CONDITIONAL** — etki seviyesine bağlı.
2. DEA varsa, OECD Better Regulation prensiplerine uyum kontrolü.
3. BEF varsa, 5 yıllık projeksiyon var mı? Tüm paydaşlar (kamu, özel) hesaplanmış mı?

**PASS:**
- Mevzuat tipi gerektiriyorsa, DEA + BEF mevcut + kaliteli.

**FAIL:**
- Zorunlu olan mevzuat tipinde DEA veya BEF eksik.

**CONDITIONAL:**
- DEA/BEF mevcut ama yüzeyseI; OECD prensiplerine kısmen uyumlu.

**N/A:**
- Mevzuat tipi DEA/BEF gerektirmiyor (örn. teknik genelge).

**Remediation:**
- FAIL → Mod 6 (RIA) etkinleştirilir; `templates/dea-template.md` + `templates/bef-template.md` kullanılır.

**Atıf:** R1 + R5 (DEA/BEF) + Mod 6

---

## Bölüm 7 — AB Müktesebatı ve Uluslararası Karşılaştırmalı Uyum — 1 Kontrol

### 7.1. Kontrol 20: Karşılaştırmalı Uyum (Md. 4/c operasyonel yansıması) — **YÜKSEK RİSK**

**Test prosedürü:**
1. Taslağın **AB müktesebatıyla uyum gerektirip gerektirmediğini** belirleyin.
2. Eğer evet, ilgili AB regülasyonu/direktifi tespit edin (CELEX numarası).
3. EUR-Lex üzerinden **konsolide sürümü** teyit edin (anti-pattern 17).
4. Karşılaştırmalı tabloyu `templates/karsilastirma-uluslararasi.md` formatında hazırlayın.
5. WHO/ICH/PIC/S/IMDRF rehberleri ile uyum denetimi.

**PASS:**
- AB müktesebatı uyumu sağlanmış.
- Karşılaştırmalı tablo + atıf doğru.
- WHO/ICH/PIC/S/IMDRF rehberleriyle uyum var.

**FAIL:**
- AB müktesebatı uyumu gerektiren alanda boşluk veya çelişki.
- Eski/değişen CELEX sürümüne atıf (anti-pattern 17).
- Resmî olmayan İngilizce çeviri orijinal metin olarak sunulmuş (anti-pattern 18).

**CONDITIONAL:**
- Genel uyum sağlanmış ama bazı boyutlarda boşluk.

**N/A:**
- Taslak AB müktesebatı kapsamı dışında.

**Remediation:**
- FAIL → Karşılaştırmalı tabloyu güncelle; konsolide CELEX sürümünü kullan; gerekirse Mod 7 (COMPARATIVE_LAW) etkinleştir.

**Atıf:** R1 + R8 + R12 + Anti-pattern 16-18

---

## Bölüm 8 — Türk Hukuk Dili ve İçtihat-Doktrin Süzgeci (G-DİL) — 1 Kontrol

### 8.1. Kontrol 21: Dil + İçtihat + Uluslararası İnsan Hakları Süzgeci — **DEĞIŞKEN RİSK**

**Test prosedürü:**
1. **R9 Bölüm 9** — 15-noktalı dil kontrolünü uygulayın:
   - Tabaka seçimi (Tabaka A/B/C)
   - Md. 25 dil kuralları
   - Yabancı kelime kontrolü
   - Kısa cümle ilkesi
   - Edilgen/etken denge
   - Ses uyumu ekleri
   - Anti-pattern temizliği
2. **R13** içtihat-doktrin temellendirmesi kontrolü:
   - AYM içtihatı atfı (varsa)
   - Danıştay içtihatı atfı (varsa)
   - Yargıtay içtihatı atfı (varsa)
   - AİHM Türkiye kararı atfı (varsa)
   - Türk akademik doktrin (Hakeri, Aydın, Yıldız, Demir, vd.)
3. **Uluslararası insan hakları** süzgeci:
   - ICESCR Md. 12 + AAAQ Genel Yorum 14 uyumu
   - CRC Md. 24 (çocuk sağlığı, varsa)
   - CRPD Md. 25 (engelli sağlığı, varsa)
   - AİHS Md. 2/3/8/14 sağlık ekseni uyumu
   - Oviedo Sözleşmesi uyumu (varsa Türkiye onaylı boyut)

**PASS:**
- R9 Bölüm 9 — 15 nokta tamamen PASS.
- R13 katmanı temellendirme mevcut.
- Uluslararası insan hakları uyumu var.

**FAIL:**
- R9 dil kontrolünde ≥ 3 madde FAIL.
- R13 içtihat temellendirmesi tamamen eksik.
- ICESCR/AİHS/CRC/CRPD ile çelişki.

**CONDITIONAL:**
- R9 + R13 + uluslararası insan hakları kısmen karşılanmış.

**Remediation:**
- FAIL → R9 + R13 + R10 referansları gözetilerek metni yeniden yaz.

**Atıf:** R9 + R10 + R13

---

## Bölüm 9 — Rubric Uygulama Protokolü (Operasyonel Akış)

### 9.1. Sıralı Uygulama

Mod 4 (COMPLY) çıktısı üretilirken kontroller şu sırayla uygulanır:

```
Kontrol 1 (üst norm) → eğer FAIL ise Kontrol 2-21'e geçilmeden kapsamlı revizyon önerisi
Kontrol 1 PASS → Kontrol 2-8 (maddi uygunluk) → 
Kontrol 9-14 (şekli uygunluk) → 
Kontrol 15-16 (dil + gerekçe) → 
Kontrol 17-18 (yetki + mali) → 
Kontrol 19 (DEA + BEF) → 
Kontrol 20 (uluslararası uyum) → 
Kontrol 21 (dil + içtihat + insan hakları süzgeci)
```

### 9.2. Skor Kartı Formatı

Çıktıda her kontrolün durumu şu formatta sergilenir:

```
| Kontrol | Hüküm | Risk | Açıklama | Remediation öncelik |
|---|---|---|---|---|
| K-1 Üst norm | PASS | YÜKSEK | Anayasa Md. 7 + üst kanun yetki zinciri tam | — |
| K-2 Amaç uygun | CONDITIONAL | DEĞIŞKEN | Md. 5'in amaç bağlantısı zayıf | Düşük |
| K-7 Madde uzun | FAIL | DÜŞÜK | Md. 12-15 ortalama 180 kelime | Orta |
| K-9 Gerekçe | FAIL | ORTA | Md. 8 gerekçesi madde metni kopyası | Yüksek |
| ... | ... | ... | ... | ... |
```

### 9.3. Genel Hüküm Üretimi

| Tüm 21 kontrol için | Genel hüküm | Aksiyon |
|---|---|---|
| Hepsi PASS veya N/A | **YAYINA HAZIR** | Yayın sürecini başlat |
| ≤ 3 CONDITIONAL, 0 FAIL | **YAYINA HAZIR** (uyarılarla) | Yayın öncesi CONDITIONAL'ları değerlendir |
| 1 FAIL (YÜKSEK risk) | **YAYIN ÖNCESİ DÜZELTME ZORUNLU** | İlgili kontrolü düzelt |
| 1 FAIL (ORTA/DÜŞÜK risk) | **YAYIN ÖNCESİ DÜZELTME ÖNERİLİR** | Düzeltme yap; düzeltilemezse yetkili kurum kararı |
| 2-4 FAIL | **KAPSAMLI REVİZYON** | Mod 2 (AMEND) handoff |
| ≥ 5 FAIL veya K-1/K-17 FAIL | **TASARIMI YENİDEN GÖZDEN GEÇİR** | Mod 1 (DRAFT) yeniden başlat |

### 9.4. Remediation Öncelik Matrisi

| FAIL kontrol | Öncelik | Tahmini düzeltme süresi |
|---|---|---|
| K-1, K-17, K-18 (YÜKSEK) | Acil | 1-2 gün |
| K-8, K-20 (YÜKSEK) | Yüksek | 2-5 gün |
| K-9, K-10, K-12, K-13, K-14 (ORTA) | Orta | 1-2 gün |
| K-3, K-4, K-7, K-11, K-15, K-16 (DÜŞÜK) | Düşük | < 1 gün |
| Çoklu FAIL | Toplam | Toplam + integration süresi |

---

## Bölüm 10 — Rubric Kullanım Örneği

**Senaryo:** TİTCK tarafından yayımlanmış bir yönetmeliğin Mod 4 (COMPLY) denetimi.

```
Lex-Sanitas Mod 4 (COMPLY) çıktısı:

# {Yönetmelik Adı} — 5210 Uyum Denetimi (Executable Rubric v2.3)

## Yönetici Özeti
- 21 kontrol: PASS=12, CONDITIONAL=5, FAIL=4, N/A=0
- Genel hüküm: **YAYIN ÖNCESİ DÜZELTME ZORUNLU**
- En kritik FAIL: K-17 (Yetki Sınırı) — yönetmelik mali yük öngörüyor

## Detaylı Sonuçlar
| K | Hüküm | Risk | Açıklama |
|---|---|---|---|
| K-1 | PASS | YÜKSEK | Üst kanun (1262 SK Md. X) yetki veriyor |
| K-2 | PASS | DEĞIŞKEN | Amaç-hüküm bağlantısı net |
| ... | ... | ... | ... |
| K-17 | FAIL | YÜKSEK | Md. 12 başvuru ücreti öngörüyor ama kanun dayanağı yok |
| ... | ... | ... | ... |

## Düzeltme Yol Haritası
1. (Acil) K-17: Md. 12 başvuru ücreti hükmünü çıkar; veya 1262 SK'da yetki düzenlemesi öner (Mod 8 handoff)
2. (Yüksek) K-8: AB Başkanlığı görüşü alınmamış; alınması gerekiyor
3. (Orta) K-9: Md. 5-7 gerekçeleri madde metnini tekrarlıyor; yeniden yaz
4. (Düşük) K-7: Md. 15 + 18 maddeler aşırı uzun; böl
```

---

## Bölüm 11 — Rubric Sürüm Notu

**v2.3.0** (22 Mayıs 2026): İlk sürüm — 21 noktalı 5210 uyum denetimi için executable rubric tablosu. R6 (descriptive checklist) ile köprü oluşturur.

**Gelecek sürüm önerileri (v2.4):**
- Otomatik tarama scriptleri (`scripts/rubric_check.py`) — bazı kontroller için (K-11 tipografi, K-12 atıf formatı, K-16 dil) regex tabanlı denetim
- Skor kartı JSON çıktısı (programmatic integration için)
- ML tabanlı anomali tespiti (K-2 amaç-hüküm bağlantı kuvveti)

---

**Bu rubric, Lex-Sanitas v2.3 Mod 4 (COMPLY) çıktılarının tekrar üretilebilir, objektif ve operasyonel olmasını sağlar. R6 (descriptive) ile birlikte kullanılır; her kontrolün ne olduğunu R6, nasıl ölçüldüğünü ve sapma halinde ne yapılacağını R6b sağlar.**
