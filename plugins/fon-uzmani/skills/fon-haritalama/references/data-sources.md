# data-sources.md — Veri Kaynakları & Güven Merdiveni

## Kaynaklar
| Kaynak | Sağladığı | Güven |
|---|---|---|
| Borsa MCP `get_fund_data` | NAV serisi, getiri, AUM, kategori sıralaması, ISIN, kap_link | Yüksek (birincil) |
| Borsa MCP `screen_funds` | kategori/tür tarama | Yüksek |
| fon-mcp (TEFAS) | holdings, dağılım geçmişi, TER, fon akışı, EMK | Yüksek (TEFAS birincil) |
| fon-mcp (KAP fallback) | kurucu/yönetici/strateji | Orta (HTML ayrıştırma) |
| web_fetch (TEFAS/KAP) | son çare | Orta |

## Güven merdiveni (CONNECTORS.md §0)
Native MCP → REST → web_fetch → web_search (yalnız URL keşfi). Tier-0 sayısal iddia
(NAV/getiri/TER/ağırlık) birincil kaynağa çözülür.

## Tazelik
- NAV/dağılım gün-sonu (EOD), günlük yayımlanır.
- TER yıllık/periyodik. Registry nadiren değişir (7g önbellek).
- fon-mcp KV önbelleği TTL: registry 7g, costs 24s, holdings/snapshot 6s, history/flows 12s.

## Eksik veri kuralı
Alan alınamazsa metrik `null` + caveat; asla uydurulmaz. Fallback kullanıldıysa
`run_manifest.caveats[]` + rapor §Sınırlar.
