# data-sources.md — Veri Kaynakları & Güven Merdiveni

## Kaynaklar
| Kaynak | Sağladığı | Güven |
|---|---|---|
| Borsa MCP `get_fund_data` | NAV serisi, getiri pencereleri, AUM, kategori sıralaması, ISIN, kap_link | Yüksek (birincil) |
| Borsa MCP `screen_funds` | kategori/tür tarama (getiri-sıralı) | Yüksek |
| fon-mcp (`fonGnlBlgSiraliGetir`) | günlük NAV/shares/investor/AUM zaman-serisi (`get_fund_flows`, `get_flow_leaders`, `resolve_fund`) | Yüksek (TEFAS birincil) |
| fon-mcp (`dagilimSiraliGetirT`) | varlık-sınıfı dağılımı anlık + tarihsel (`get_fund_holdings`, `get_allocation_snapshot/history`) | Yüksek (TEFAS birincil) |
| fon-mcp (`fonBilgiGetir`) | snapshot: kategori, AUM, kategori sırası, pazar payı, son fiyat (`get_fund_registry`, `get_fund_taxonomy`) | Yüksek (TEFAS birincil) |
| fon-mcp (`fonYonetimBazliBilgiGetir`) | TER **üst-sınırı** + yönetim ücreti + umbrella + founder_code (`get_fund_costs`) | Yüksek (TEFAS birincil, ÜST SINIR) |
| fon-mcp kurucu (PYŞ kısa adı, fon ünvanından türetilmiş) | `get_fund_registry.founder` | Orta (ünvan ayrıştırması — tam tüzel ünvan için KAP) |
| KAP fon sayfası web_fetch | tam tüzel ünvan / ISIN / strateji / yönetici / **gerçekleşen TER (KIID)** / aylık portföy raporu (line-item holdings) | Orta (HTML/PDF ayrıştırma) |
| web_fetch (TEFAS/KAP) | son çare | Orta |

## Güven merdiveni (CONNECTORS.md §0)
Native MCP → REST → web_fetch → web_search (yalnız URL keşfi). Tier-0 sayısal iddia
(NAV/getiri/TER/ağırlık) birincil kaynağa çözülür.

## Tazelik
- NAV/dağılım gün-sonu (EOD), günlük yayımlanır.
- TER üst-sınırı **yıllık** (genel kurul/tebliğ ile değişir; gün-içi değişmez). Registry
  nadiren değişir (7g önbellek). Gerçekleşen TER (KIID) yıllık.
- fon-mcp KV önbelleği TTL: registry 7g, costs 24s, holdings/snapshot 6s, history/flows 12s.

## Eksik veri kuralı
Alan alınamazsa metrik `null` + caveat; asla uydurulmaz. Fallback kullanıldıysa
`run_manifest.caveats[]` + rapor §Sınırlar.
