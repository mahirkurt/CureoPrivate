# Tetikleyiciler ve mod yönlendirmesi — bist-analist-kopilotu

Bu beceri **BIST hisseleri** için karar-destek brifingi üretir. Aşağıdaki tablo,
kullanıcı ifadelerini dört moddan birine yönlendirir. Şüphede tek bir soruyla
netleştirin; varsayım yapıp yanlış moda gitmeyin.

## Mod yönlendirme tablosu

| Kullanıcı niyeti | Tetik örnekleri (TR) | Tetik örnekleri (EN) | Mod |
| :-- | :-- | :-- | :-- |
| Tek hissede derinlemesine görünüm | "GARAN analiz et", "THYAO yorumla", "ASELS teknik+temel durum" | "analyze GARAN", "deep dive on THYAO" | **1** |
| Hafta için aday evreni | "bu hafta hangi hisseler öne çıkıyor", "yüksek momentumlu BIST", "haftalık tarama yap" | "weekly BIST scan", "high-momentum names this week" | **2** |
| Tek bir KAP açıklaması / olay | "şu KAP açıklaması ne anlama geliyor", "bedelsiz kararını yorumla", sert fiyat/hacim hareketi | "interpret this KAP disclosure", "what does this filing mean" | **3** |
| Verili sembol listesinin gözetimi | "izleme listemi gözden geçir", "şu 8 sembolde ne değişti" | "review my watchlist", "what changed in these tickers" | **4** |

## Disambiguasyon kuralları
- Sembol + "analiz/yorum" → **Mod 1**. Birden çok sembol + "tara/öne çıkan" → **Mod 2**.
- "KAP / açıklama / haber / bilanço sürprizi" tek olay etrafında → **Mod 3**.
- Önceki bir anlık görüntüye/listeye atıf ("değişen ne") → **Mod 4**.
- Mod belirsizse: "Tek hisse derin analizi mi, haftalık tarama mı istersiniz?" diye sorun.

## Adım 0 — Bağlayıcı sağlık kontrolü
Her analizden önce **Borsa** veri bağlayıcısının erişilebilir olduğunu küçük bir
sembol probu ile doğrulayın. Erişilemiyorsa canlı fiyat varsaymayın; yalnız
`web_search`/`web_fetch` ile, kaynak ve kısıtı açıkça belirterek sınırlı bağlam
verin. **Uydurma fiyat/rakam üretmeyin.**

## Kapsam dışı (kibarca reddet / yönlendir)
- **ABD hisseleri / yabancı borsalar** → kapsam dışı; yalnızca BIST.
- **Kripto varlıklar** → kapsam dışı.
- **TEFAS fonları** → kapsam dışı (bağlayıcıda veri olsa da bu beceri hisseye odaklıdır).
- **Gün-içi scalping / emir defteri / derinlik** → veri gün sonu (EOD); gün-içi mikro-yapı iddiası üretilmez.
- **Kişiye özel "kesin al/sat söyle" talebi** → karar-destek diline çevrilir; yatırım tavsiyesi verilmez (bkz. compliance.md).

> Çıktılar karar-destektir; yatırım danışmanlığı/tavsiyesi değildir.
