# report-style.md — Rapor House Style

## Dil & ton
- Türkçe, bilimsel-profesyonel düzyazı. Tam cümleler; madde işaretleri yalnız tablolarda/listelerde.
- Makine sızıntısı YOK (Katman A): MCP adı, ham JSON, tool çağrısı, "fon-mcp/Borsa" görünmez.

## Sayı disiplini
- Her sayı birim + as-of taşır: "Sharpe 1.4 (yıllık, gün-sonu/EOD, as-of 2026-06-16)".
- Yüzde/oran kaynak damgalıdır (provenance-standard §1).
- Yıllıklama temeli (252/52/12) belirtilir.

## Bulgu grameri
- Her bulgu: **iddia + kanıt + güven + karşıt-senaryo**. Örn. "Fon akranlarının üst %20'sinde
  (Sharpe 1.4 vs medyan 0.9); ancak son 1 ayda maxDD −12% ile akran ortalamasının altında —
  rejim riski sürerse bu görece üstünlük zayıflayabilir."
- Kesinlik dili YASAK ("kesin", "garanti", "mutlaka kazandırır").

## "Tavsiye diline çevirme" rehberi
| Kullanıcı ister | Yanlış (yasak) | Doğru (karar-destek) |
|---|---|---|
| "Bu fonu alayım mı?" | "Evet, alın." | "Risk profili X için şu fon, akran-üstü Sharpe + düşük TER ile öne çıkıyor; ancak Y senaryosunda ... Karar bağımsız değerlendirme gerektirir." |
| "Ne kadar koyayım?" | "%40 koyun." | "Dengeli profil için optimizasyon %X-%Y bandı önerir; kısıtlarınız ve risk toleransınıza göre değişir." |

## Bölüm iskeleti (Katman A)
1. Özet / karar-destek notu
2. Fon kimliği & yapısı (kategori, AUM, TER, yönetici, dağılım)
3. Risk/getiri profili (akran-göreli yüzdebirlikle)
4. Benchmark & makro bağlam (rejim)
5. Akran karşılaştırması
6. (Mod 4) Portföy tahsisi & senaryo matrisi
7. İzlenecekler & riskler
8. Provenance + **kanonik SPK feragati** (birebir)
