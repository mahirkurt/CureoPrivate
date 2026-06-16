# compliance.md — SPK Uyum & Kanonik Feragat

## Kanonik SPK Feragat Metni (BİREBİR)

Aşağıdaki metin her raporun sonunda **birebir** bulunmalıdır. `rapor_lint.py` bu metnin
anahtar ifadelerini (string-match) denetler; metin paraphrase edilemez, kısaltılamaz:

> Bu içerik yalnızca bilgilendirme ve karar-destek amaçlıdır; SPK yatırım danışmanlığı,
> portföy yöneticiliği veya al/sat tavsiyesi niteliği taşımaz. Fon getirileri geçmişe dönük
> olup gelecekteki getirinin garantisi değildir; NAV verileri gün-sonu (EOD) ve gecikmeli
> olabilir. Yatırım kararları; kişinin kendi risk profili, bağımsız araştırması ve
> gerektiğinde SPK lisanslı bir yatırım kuruluşuna/danışmanına danışılarak alınmalıdır.

## SPK Sınır Doktrini

- **Yapılır:** gerekçeli karar-destek, senaryo analizi, riske-göre-düzeltilmiş kıyas,
  akran konumlandırma, "izlenecekler".
- **Yapılmaz:** kişiye özel "şu fonu şu kadar al/sat", kesin getiri vaadi, "kesin/garanti"
  dili, zamanlama emri.
- Kişiselleştirilmiş al/sat talebi → karar-destek diline çevrilir: senaryo + tetikleyici +
  geçersizleşme koşulu.

## Veri Doğruluğu İlkeleri

- Her sayısal iddia kaynağa damgalanır (provenance-standard.md).
- NAV/fiyat gün-sonu (EOD); gün-içi iddia yasaktır.
- Geçmiş getiri gelecek garantisi değildir — her getiri ifadesinde ima edilir.
- Eksik veri → metrik `null` + caveat; uydurma yok.
