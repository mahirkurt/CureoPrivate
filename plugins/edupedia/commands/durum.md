---
description: Maarif Modeli MCP connector'ının sağlığını ve Tier-2 (get_figure) yeteneğini raporlar
argument-hint: "(argüman gerekmez)"
---

`maarif-mufredat` connector'ının sağlık kontrolünü yap. Bu, `edupedia:start` skill'inin Adım 2'sini
komut olarak yüzeyler. Modül üretmez — yalnız durum raporlar.

## Yürütme protokolü

1. **Pre-flight / canlılık** (`../CONNECTORS.md §6`): `server_info` çağır. Yanıt verirse
   connector **canlı**; korpus sürümünü (`corpus_version`, `build_date`) ve sayımları (ders,
   kazanım, çerçeve, figür) raporla. Hata verirse **bağlı değil / erişilemez** — kullanıcıya
   Settings → Connectors'tan `maarif-mufredat`'ı etkinleştirmesini söyle ve `carbon-edupedia`'nın
   MCP'siz (offline, kullanıcı kaynağı) yolla da çalıştığını hatırlat.

2. **Araç kümesi** (`../CONNECTORS.md §1`): Hangi araçların çağrılabilir olduğunu dört kümeye
   göre raporla — A·Keşif · B·Kazanım · C·Beceri çerçevesi · D·Belge+medya. Otoritatif sayı **21**.

3. **Tier-2 yeteneği** (`../CONNECTORS.md §3.1` + `../shared/canonical-cache-contract.md §4`):
   `get_figure` araç listesinde **var mı**? Varsa Tier-2 (resmî görsel gömme) **mevcut** — bir
   `search_figures(query, subject)` denemesiyle bir aday `figure_id` bulup
   `get_figure(figure_id, include_image=false)` metadata yolunu (Tier-1 zenginleştirme) doğrula.
   Yoksa `tier2_status: unavailable` (yalnız Tier-1).

4. **Kanonik-önbellek durumu:** Bu oturumda üretilmiş kanonik artefaktları (`subject_registry`,
   `outcomes_extract`, `framework_map`, `figure_probe`) ve `connector_call_ledger`'ı
   (`single_shot_enforced`) özetle.

## Çıktı

Kısa durum kartı: connector canlılığı + korpus sürümü · çağrılabilir araç kümeleri (A/B/C/D, 21) ·
`get_figure` mevcut mu (Tier-2 yeteneği) · kanonik-önbellek durumu. Eksik connector'ın etkisini
söyle (yoksa modül offline yola döner, üretim bloke olmaz).
