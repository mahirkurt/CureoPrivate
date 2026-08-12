# Tıp Tarihyazımı Ekolleri — ve güncellik yargıları

HISTORIOGRAPHIA ve CONCEPTUS modlarında yüklenir.

> Bu dosyanın işlevi ekol *listelemek* değil, hangi pozisyonun **bugün canlı**, hangisinin
> **yeniden formüle edilmiş**, hangisinin **çekişmeli** olduğunu söylemektir. Aşılmış bir
> pozisyonu güncel diye aktarmak bu plugin'in somut hata modudur.

---

## 1. Ekoller ve durum

| Ekol | Çekirdek tez | Durum | Dayanak |
|---|---|---|---|
| **Whig / ilerlemeci tıp tarihi** | Tıp tarihi hatadan doğruya doğru ilerleyiştir | ❌ **Aşıldı** — ama LLM çıktısında sürekli geri sızar | — |
| **Sosyal tıp tarihi** | Tıp toplumsal ilişkiler içinde üretilir; hastalık toplumsal olarak çerçevelenir (Rosenberg) | ✅ Yerleşik | Rosenberg *Framing Disease* 1992 (**pre-DOI monograf** — künyeyle atıflanır) |
| **"Hastanın bakışı" / aşağıdan tarih** | Anlatı hekimden hastaya kaydırılmalı (Porter 1985) | ✅ **Canlı ama yeniden formüle edildi** | 30 yıl değerlendirmesi: *Med Hist* 2015, DOI 10.1017/mdh.2015.65 |
| ↳ *güncel formülasyon* | Tek geri kazanılabilir "hasta sesi" yerine **çok-sesli, çekişmeli kayıt** (heteroglossia) | ✅ Bugünkü hâli | *Med Humanit* 2019, DOI 10.1136/medhum-2019-011724 |
| **Foucaultcu / biyopolitik** | Klinik bakış, tıbbileştirme, beden üzerinde iktidar | ⚠️ **Çekişmeli — ne kanonik ne ölü** | Ruh sağlığı tarihyazımı 2025'te "Sisifos işi" olarak nitelendi: *Contemporary European History*, DOI 10.1017/s0960777325100945 |
| **Postkolonyal tıp tarihi** | Sömürge tıbbı bilgi-iktidar ilişkisi olarak analiz edilir | ✅ **Canlı** | Anderson 1998, *Bull Hist Med*, DOI 10.1353/bhm.1998.0158 |
| **Küresel sağlık tarihi** | Avrupa merkezden çıkarılır; karşılaştırmalı ve bağlantısal tarih | ✅ Canlı ve programatik | *Bull Hist Med* 2015, DOI 10.1353/bhm.2015.0116; *Med Hist* 2026, DOI 10.1017/mdh.2026.10056 |
| **İnşacı / kategori tarihi (Hacking)** | Tanı kategorileri "döngü etkisiyle" adlandırdıklarını dönüştürür | ✅ Canlı; retrodiagnoza yapıcı alternatif | *Soc Hist Med* 2016, DOI 10.1093/shm/hkw083 |
| **Toplumsal cinsiyet tarihi** | Tıbbî bilgi ve pratik cinsiyet rejimleriyle kurulur | ✅ Canlı — ⚠️ **metodolojik derleme boşluğu ölçüldü** | Aramada konu çalışmaları çıktı (ör. erkek histerisi/Charcot, DOI 10.1017/s0025727300052777), ekol değerlendirmesi çıkmadı → hedefli yeniden tarama gerekir |
| **Engellilik tarihi** | Engellilik tıbbî değil toplumsal-tarihsel kategoridir | ✅ Canlı — ⚠️ **metodolojik derleme bulunamadı** | Etik-komşu bir kayıt bulundu (tımarhane fotoğraflarının kapsayıcı yeniden kullanımı, DOI 10.1017/s0080440125100418); genel sorgu edebiyat/CS'ye kaydı |

---

## 2. İki ölçülmüş boşluk — dürüstçe beyan

Yukarıdaki tabloda **cinsiyet tarihi** ve **engellilik tarihi** satırları, bu plugin'in kurulum
turunda yapılan aramada **metodolojik derleme düzeyinde** karşılık bulamadı. Bu, o ekollerin
zayıf olduğu anlamına **gelmez** — arama stratejisinin o alanlarda yetersiz kaldığı anlamına
gelir. HISTORIOGRAPHIA modunda bu iki eksen çalışılıyorsa **hedefli yeniden tarama zorunludur**
ve sonuç bu dosyaya işlenir.

---

## 3. Konumlandırma prosedürü

Bir çalışmayı (veya kendi çıktını) konumlandırmak için dört soru:

1. **Fail kim?** Anlatının öznesi hekim mi, kurum mu, hasta mı, devlet mi?
2. **Hastalık nasıl ele alınıyor?** Değişmez biyolojik varlık mı, tarihsel olarak çerçevelenmiş
   kategori mi?
3. **Değişim nasıl açıklanıyor?** Keşif/dâhi mi, toplumsal talep mi, kurumsal çıkar mi,
   iktidar ilişkisi mi?
4. **Kim kapsam dışı?** Hangi coğrafya, sınıf, cinsiyet, ırk anlatıya girmiyor?

Cevaplar ekol haritasına düşürülür; **bir çalışma birden çok ekole ait olabilir**.

---

## 4. Atıf grafı ile ekol haritası

`openalex_get_citation_graph` bir çekirdek eserin etki alanını verir; kümeler çoğu kez ekollere
karşılık gelir. `openalex_analyze_trends` bir terimin/konunun zaman içindeki yayılımını gösterir
(diyakronik bibliyometri).

⚠️ **Kısıt:** grafın çözebildiği yalnız DOI'li literatürdür. Alanın kurucu monografları
(Rosenberg 1992, Arnold 1993, Porter 1985) bu grafta **yoktur** — ekol haritası yalnız atıf
grafına dayandırılamaz.
