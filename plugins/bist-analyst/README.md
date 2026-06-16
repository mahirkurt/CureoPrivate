# BIST Uzmanı

> **Borsa İstanbul analist kopilotu.** Tek bir gerekçeli brifingde teknik durum,
> temel görünüm, KAP haber/duygu akışı ve TCMB makro rejimini sentezler.
> **Karar destek sağlar; yatırım danışmanlığı/tavsiyesi değildir.**

BIST Uzmanı, `bist-analist-kopilotu` becerisini ve onun veri omurgası olan
**Borsa MCP** bağlayıcısını tek, kurulabilir bir Claude Code eklentisi olarak
paketler. Eklentiyi kurduğunuzda beceri ve bağlayıcı birlikte gelir; ayrı ayrı
"custom connector" eklemenize gerek kalmaz.

---

## Ne yapar

Dört modda çalışır (`bist-analist-kopilotu` içinde):

| Mod | Ne zaman | Çıktı |
| :-- | :-- | :-- |
| **1 — Tek hisse derin analizi** | "GARAN analiz et", "THYAO yorum" | Çok zaman dilimli teknik + sektör-normalize temel + KAP duygu + makro çerçeve + senaryo matrisi |
| **2 — Haftalık tarama** | "bu hafta hangi hisseler", "yüksek momentumlu BIST" | Gerekçelendirilmiş izleme listesi (alım listesi değil, araştırma gündemi) |
| **3 — KAP / olay yorumu** | yeni KAP açıklaması, sert fiyat/hacim | Olay sınıfı + materyalite + olası yön + reaksiyon penceresi |
| **4 — İzleme listesi gözetimi** | "izleme listemi gözden geçir" | Snapshot-arası deterministik değişim, önceliğe göre sıralı |

Her brifing **yayına hazır, kendine yeten bir belgedir**: bilimsel Türkçeyle,
makine-dili sızıntısı olmadan, kaynaklar resmî adı ve tarihiyle, her sonuç güven
düzeyi ve karşıt senaryoyla, ve sonda zorunlu feragatle.

---

## Kurulum

```bash
# 1) Marketplace'i ekleyin (GitHub kısayolu)
/plugin marketplace add mahirkurt/marketplace

# 2) Eklentiyi kurun
/plugin install bist-analyst@cureonics-marketplace
```

Kurulumdan sonra:

- Beceriler ad alanıyla görünür: `/bist-analyst:bist-analist-kopilotu` ve
  `/bist-analyst:start`.
- Paketli **Borsa MCP** sunucusu (`borsa`) ilk oturumda yapılandırılır. Remote
  bir MCP sunucusu olduğu için **per-server onay** istenebilir; onaylayın.

> **Zaten ayrı bir "Borsa" connector'ınız varsa:** Yinelemeyi önlemek için
> standalone connector'ı kaldırabilirsiniz; bağlayıcıyı artık eklenti sağlar.

---

## Veri omurgası — Borsa MCP

Paketli bağlayıcı (açık kaynak, FastMCP) şunları kapsar: KAP haberleri,
gün sonu (EOD) fiyat/teknik, İş Yatırım/borsapy tabanlı tarayıcı + FX, TEFAS,
**TCMB EVDS + enflasyon**.

- **TCMB EVDS makro katmanı:** EVDS API anahtarı Borsa MCP'de **sunucu-tarafında**
  ayarlıdır; kullanıcı kurulumu gerektirmez. Politika faizi, TÜFE, kur, ödemeler
  dengesi, beklenti anketleri ve REER gibi seriler doğrudan çekilir.
- **Önemli sınır:** Fiyat verisi büyük ölçüde **gecikmeli/gün sonu**'dur; **gün
  içi emir defteri/derinlik/PİTE içermez.** Günlük ve haftalık ufuk için yeterli;
  gün-içi mikro-yapı iddiası üretilmez.

---

## Birlikte çalıştığı bileşenler (composability)

| Bileşen | Durum | Rol |
| :-- | :-- | :-- |
| **Borsa MCP** | ✅ Paketli (`.mcp.json`) | Birincil veri omurgası — zorunlu |
| **carbon-html-report** | ◻ Ayrı kurulur | Brifingi IBM Carbon biçimli A4 HTML belgeye döker |
| **carbon-pptx** | ◻ Ayrı kurulur | Brifingi sektör-bağımsız sunuma döker |
| **Finmap MCP** | ◻ Ayrı / opsiyonel | Tamamlayıcı borsa istatistikleri (pazar/sektör görünümü) |
| **Interactive Brokers (IBKR)** | ✕ Tasarım gereği kapsam dışı | Gerçek-zaman/gün-içi; bu eklentinin EOD kapsamına aykırı |

> Çıktı biçimleme becerileri (`carbon-*`) bilinçli olarak **paketlenmedi**: bunlar
> alanlar-arası genel becerilerdir ve SMP ekosisteminizde tek kanonik kopya olarak
> tutulmalıdır. Eklenti bunlarla composable çalışır, çoğaltmaz.

---

## Uyum ve sınırlar

- Her çıktı, becerinin `references/compliance.md` dosyasındaki **feragat metniyle**
  biter.
- Kişiye özel al/sat/hedef-fiyat yönlendirmesi yapılmaz; talep gelse bile
  karar-destek diline çevrilir.
- Üçüncü-taraf hedef fiyatları ve "güçlü alış" tavsiyeleri brifinge yön verici
  olarak taşınmaz; yalnızca "doğrulanmamış / üçüncü-taraf" etiketiyle nötr bağlam
  olarak anılır.
- KVKK ve kaynakların kullanım koşullarına uyulur.

---

## Sürüm

Bkz. `CHANGELOG.md`. Anlamsal sürümleme (MAJOR.MINOR.PATCH) izlenir. `plugin.json`
içindeki `version` yükseltilmedikçe kullanıcılar güncelleme **almaz**.

## Lisans

MIT — bkz. `LICENSE`.
