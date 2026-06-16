# Borsa bağlayıcısı — duman testi (smoke test)

Kurulumdan sonra `borsa` veri bağlayıcısının doğru bağlandığını doğrulamak için
aşağıdaki adımları sırayla çalıştırın. Amaç: her katmanın (sembol çözümleme,
anlık bilgi, teknik, KAP/haber, makro) erişilebilir olduğunu teyit etmek. Bu bir
manuel/agent-yürütümlü kontrol listesidir; üretim brifingi değildir.

> Not: Fiyat verisi gün sonu (EOD) ve gecikmeli olabilir. Test, **erişilebilirliği**
> doğrular; canlı gün-içi fiyat doğruluğunu değil.

## Adım 0 — Eklenti & bağlayıcı durumu
- [ ] `/plugin` arayüzünde **bist-analyst** etkin görünüyor.
- [ ] `borsa` veri sunucusu yapılandırılmış ve onaylanmış (remote/HTTP; per-server onay gerekebilir).

## Adım 1 — Sembol çözümleme
- [ ] `search_symbol(query="Garanti", market="bist")` en az bir sonuç döndürür ve GARAN sembolünü içerir.
- **Beklenen şekil:** sembol + şirket adı içeren liste.

## Adım 2 — Anlık bilgi
- [ ] `get_quick_info` GARAN için son kapanış, günlük değişim (%) ve hacim alanlarını döndürür.
- **Beklenen şekil:** sayısal alanlar dolu; tarih/as-of mevcut.

## Adım 3 — Teknik analiz
- [ ] `get_technical_analysis` GARAN için RSI, MACD ve hareketli ortalama benzeri göstergeler döndürür.
- **Çapraz kontrol:** `scripts/technical_helpers.py` ile yerel olarak yeniden türetilen değerler makul aralıkta (RSI 0–100) olmalı.

## Adım 4 — KAP / haber akışı
- [ ] `get_news` GARAN için son dönem açıklama/haber listesi döndürür.
- **Çapraz kontrol:** `scripts/kap_fetch.py normalize` çıktıyı tek biçime indirger; `scripts/kap_materiality.py` bir başlığı kategoriye atar.

## Adım 5 — Makro katman (TCMB EVDS)
- [ ] `get_evds_data` veya `get_macro_data` politika faizi / TÜFE / kur gibi en az bir seri döndürür.
- **Not:** EVDS anahtarı sunucu-tarafındadır; kullanıcı kurulumu gerektirmez. Bu prob başarısızsa makro çerçeve atlanır/uyarılır, ancak hisse analizi durmaz.

## Zarif düşüş (graceful degradation) beklentisi
Bağlayıcı erişilemiyorsa:
- [ ] Beceri canlı fiyat **varsaymaz**; uydurma rakam üretmez.
- [ ] Yalnızca `web_search`/`web_fetch` ile, kaynak ve kısıt açıkça belirtilerek sınırlı bağlam verir.
- [ ] Kullanıcıya `/plugin` üzerinden eklentinin etkin ve `borsa` sunucusunun onaylı olduğunu kontrol etmesi önerilir.

## Geçer ölçüt
Adım 1–4 yeşil → birincil veri omurgası çalışır (Mod 1–4 kullanılabilir).
Adım 5 kırmızı ama 1–4 yeşil → makro çerçeve hariç tüm modlar çalışır.
