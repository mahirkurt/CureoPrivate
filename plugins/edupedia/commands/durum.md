---
description: Üç MCP connector'ının (maarif-mufredat, egitim-kaynak, modul-yayin) sağlığını ve Tier-2 (get_figure) yeteneğini raporlar
argument-hint: "(argüman gerekmez)"
---

Plugin'in **üç MCP connector'ının** sağlık kontrolünü yap. Bu, `edupedia:start` skill'inin Adım 2'sini
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

4. **Eğitim Kaynak RAG (`egitim-kaynak`) sağlığı:** `kb_server_info` çağır. Yanıt verirse
   **canlı** — faz (`phase`), getirme yöntemi (`retrieval`: `hybrid` = BM25+vektör RRF,
   `fts5-bm25` = embedding kapalı/yok), `embedding_model`, hizalama durumu (`alignment_built`)
   ve korpus sayımlarını (`stats`: `chunk_count`, `vector_count`, `source_count`) raporla.
   Yoksa **bağlı değil** → modül üretimi yerleşik bilgiyle sürer, kaynak zenginleştirme atlanır
   (asla uydurma kaynak). **`alignment_built: false` iken `kb_for_outcome` dürüstçe
   `alignment_not_built` döner** — kazanım hizalaması korpus derinleşene + insan denetimi geçene
   kadar bilinçli kapalıdır; bu bir arıza DEĞİL, no-fabrication gereğidir. O halde kazanım
   konusunu `kb_search`'e sorgu olarak verin.

5. **Modül Yayın (`modul-yayin`) sağlığı:** `edupedia_server_info` araç listesinde varsa çağır
   (`gate_count`, `max_upload_bytes`, `base_url`); yayın MCP yolu **canlı**. Yoksa `/edupedia:yayinla`
   `POST /api/publish` REST yedeğine düşer (`EDUPEDIA_PUBLISH_TOKEN` ile) — yayın yine mümkün.

6. **Kanonik-önbellek durumu:** Bu oturumda üretilmiş kanonik artefaktları (`subject_registry`,
   `outcomes_extract`, `framework_map`, `figure_probe`) ve `connector_call_ledger`'ı
   (`single_shot_enforced`) özetle.

## Çıktı

Kısa durum kartı, **üç connector** için canlılık:
- `maarif-mufredat`: korpus sürümü · araç kümeleri (A/B/C/D, 21) · `get_figure` (Tier-2 yeteneği)
- `egitim-kaynak`: faz · getirme yöntemi · hizalama durumu · chunk sayısı
- `modul-yayin`: MCP yolu mu REST yedeği mi
Ayrıca kanonik-önbellek durumu. Her eksik connector'ın etkisini söyle — hiçbiri üretimi bloke etmez
(Maarif yoksa offline yol; egitim-kaynak yoksa zenginleştirme atlanır; modul-yayin yoksa REST yayın).
