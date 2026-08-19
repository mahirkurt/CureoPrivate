---
description: KOL (Key Opinion Leader) haritalama — **opsiyonel zenginleştirme modülü** (medaffairs-ops). Yalnız soru KOL/uzman-haritası bağlamına girince çağrılır. Bir terapötik alan/molekül için OpenAlex→Semantic Scholar→EuropePMC yazar taraması, ABD PI doğrulaması (NPI), Türk akademisyen katmanı (YÖK Akademik) ile ortak-yazar ağı + etki sıralaması üretir; çıktı PRISMA raporuna işaretli ek olarak girer.
argument-hint: <terapötik alan / molekül / endikasyon>
---

# /evidentia-kol — KOL Haritası (Opsiyonel Zenginleştirme Modülü)

Alan/molekül: **$ARGUMENTS**

`medical-research`'ün **opsiyonel KOL zenginleştirme modülünü** (`references/medaffairs-ops-layer.md`)
yürüt. Bu modül çekirdek PRISMA hattının parçası **değildir**; yalnız soru KOL/uzman-haritası
bağlamına girince devreye girer ve çıktı SR raporuna **işaretli ek (KOL eki)** olarak eklenir,
çekirdek bölümlere değil.

## Kademe

Sıra bağlayıcı (`execution-map.md` P7 KOL). Native MCP first — OpenAlex **REST değil**.

1. **OpenAlex (bundled).** `openalex_resolve_name` → `openalex_search_entities` /
   `openalex_get_citation_graph` — üretken/etkili yazarlar, ORCID/ROR, atıf. Kanonik `kol_graph`.
2. **Semantic Scholar (bundled).** `get_author` / `get_paper_citations` — disambiguasyon +
   influential citations.
3. **pubmed-epmc / EuropePMC.** Yazar-bağlı yayın + klinik-çalışma yazarlığı.
4. **ABD PI (NPI companion, directory).** US klinisyen-KOL: `npi_search`/`npi_lookup`/`npi_validate`.
   Unloaded → `SKIP-REASON companion_unloaded`.
5. **YÖK Akademik (bundled).** `yok_search(term=…)` ⚠️ `query` DEĞİL → `authorId` → `yok_get_*`.
   YÖK Tez'den FARKLI.

Unreachable MUST/SHOULD → `SKIP-REASON`; kimlik icat edilmez.

## Çıktı (KOL eki)

- **Sıralı KOL listesi** (etki: yayın hacmi + atıf + son-yazarlık + klinik-çalışma rolü).
- **Ortak-yazar ağı** (kümeler/merkeziyet) — kanonik `kol_graph`'ten.
- **Coğrafi katman** — global + ABD (NPI-doğrulu) + TR (YÖK Akademik).
- Her KOL için provenans (hangi kaynak hangi sinyali verdi).

## Disiplin

- **Kimlik çapraz-doğrulama:** OpenAlex/S2 yazar-ID disambiguasyonu olmadan tek-isim eşleşmesi
  sunulMAZ (eş-isim riski).
- **Native-first:** OpenAlex/S2 bundled MCP; EPMC/YÖK Akademik native. REST yalnız MCP yoksa
  (`extended-api.md`). Tek-sefer (`kol_graph` paylaşılır).
- **Kapsam sınırı:** KOL kimliklendirme yapısal akademik kaynaklardan (OpenAlex/S2/EPMC/NPI/YÖK) yapılır;
  OSINT/web rekabet sinyali kapsam dışı → `pharmaintel`. Erişilebilirlik/etki bağlamı klinik
  KOL-sıralamasının temeli değildir.
- **Gizlilik:** kişi tanımlama için görsel/sorgu disiplinine uy; uydurma profil/iletişim **yok**.
