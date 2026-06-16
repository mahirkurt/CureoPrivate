# Provenance Standardı (provenance-standard.md)

**Sürüm:** 1.0.0 · **Kapsam:** fon-uzmani süiti çıktıları.

Her sayısal iddia bir kaynağa damgalanır; uydurma/atıfsız iddia yasaktır.

---

## 1. Kaynak Tipine Göre Damga Grameri

| Kaynak | Gramer | Örnek |
|---|---|---|
| Borsa MCP | `[Borsa MCP / <tool> / <as-of ISO>]` | `[Borsa MCP / get_fund_data / 2026-06-16]` |
| fon-mcp | `[fon-mcp / <tool> / <as-of ISO>]` | `[fon-mcp / get_fund_holdings / 2026-06-16]` |
| KAP | `[KAP / <belge> / <fon kodu> / <tarih>]` | `[KAP / fon duyurusu / AFA / 2026-05-30]` |
| Kuant betiği | `[quant-analiz / <script> / <formül-vN>]` | `[quant-analiz / risk_adjusted / Sharpe-v1]` |
| Web (yalnız URL keşfi sonrası) | kaynak + erişim tarihi | `(tefas.gov.tr, erişim 2026-06-16)` |

**EOD beyanı:** her NAV/fiyat/metrik `(EOD/gün-sonu, as-of <tarih>)` damgası taşır.

---

## 2. Güven Derecelendirmesi

| Seviye | Anlam |
|---|---|
| **Yüksek** | Native MCP / birincil kaynak, doğrulanmış alan |
| **Orta** | Birincil kaynak ama tek-nokta veya türetilmiş (örn. net-flow) |
| **Düşük** | Fallback (KAP web_fetch) / kısmi veri |
| **Bilinmiyor** | Alan alınamadı → metrik `null` + caveat |

---

## 3. İki-Katmanlı Çıktı

- **Katman A (görünür):** okuyucu-yüzlü Türkçe bilimsel rapor. Makine sızıntısı YOK —
  ham `[MCP / tool / date]` damgaları, MCP adları, tool çağrıları ve JSON GÖRÜNMEZ. Kaynaklar
  insan-okur biçimde belirtilir: "Borsa veri bağlayıcısı", "TEFAS detay bağlayıcısı", "TCMB
  EVDS", "deterministik kuant motoru" + as-of tarihi. (Ham damgalar yalnız Katman B'dedir;
  rapor_lint.py Katman A'da MCP/tool adı bulursa raporu DÜŞÜRÜR.)
- **Katman B (render-dışı):** İç Denetim Kaydı, aşağıdaki sentinel çiftiyle sarılır ve
  hiçbir render hedefine (carbon-html/pptx) çıkmaz:

```
<!-- RENDER:EXCLUDE-FROM-HERE -->
OPS: <connector_call_ledger özeti, native-first uygulandı, fallback notları>
VIZ: <grafik spec — NAV-vs-benchmark, drawdown underwater, risk-getiri scatter, tahsis treemap>
PROV: <tüm damgalar + güven dağılımı + betik girdi-hash determinizm kanıtı>
<!-- RENDER:EXCLUDE-TO-HERE -->
```

Katman A her bölümün sonunda **kanonik SPK feragatini** (regulasyon-uyum/references/
compliance.md, birebir) taşır.
