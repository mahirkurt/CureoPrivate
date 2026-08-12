---
name: hekim
description: "PROSOPOGRAPHIA modu — hekim biyografisi ve kolektif biyografi (prosopografi): kariyer, eğitim, kurum, ağ, patronaj, kuşak analizi. Hipokrat'tan İbn Sînâ'ya, Vesalius'tan Semmelweis'e, bir tıp fakültesi kuşağından sömürge hekimlerine. Kullanın: 'X hekiminin biyografisi', 'kim kimdi', 'prosopografi', 'hekim ağları', 'kuşak analizi', 'tıp okulu mezunları' sorularında."
argument-hint: "<kişi veya kuşak/grup> [dönem] [kurum]"
allowed-tools: Read, Glob, Grep, WebFetch, Task
disable-model-invocation: false
---

# PROSOPOGRAPHIA — Hekim Biyografisi ve Ağlar

Flagship protokolü `PROSOPOGRAPHIA` moduyla çalıştır.
Yükle: `source-typology.md` · `citation-and-transliteration.md` · `quellenkritik.md`.

## Bireysel biyografi iskeleti

Doğum/ölüm (çift takvim) · eğitim (kurum, hoca, derece) · görevler (tarih aralıklarıyla) ·
eserler (basılı/yazma, baskı yeri-yılı) · ağlar (hoca-öğrenci, patron, yazışma, meslek örgütü) ·
sonraki itibar (kim nasıl hatırladı — **bu ayrı bir tarihtir**).

⚠️ **Biyografi sözlükleri övgü türüdür** (*Sicill-i Osmânî*, tezkire, meslek anıları). Tarihler
ve görevler **çapraz doğrulanır**; hagiyografik dil aktarılmaz.

## Kolektif biyografi (prosopografi)

Bir kuşağı/grubu ortak değişkenlerle tablolaştır: doğum yeri, sınıf kökeni, eğitim yolu, ilk
görev, kariyer tavanı, ağ konumu. **Kim kapsam dışı kaldı** sorusu zorunludur (kadınlar,
azınlıklar, kırsal pratisyenler kaynakta çoğu kez yoktur — bu bir bulgudur, boşluk değil).

## Araçlar

| İhtiyaç | Araç |
|---|---|
| Yayın/atıf ağı | `openalex_resolve_name` (ad belirsizliği!) → `openalex_get_citation_graph` |
| Yapılandırılmış prosopografi | **Wikidata SPARQL** (authless, ölçüldü) — P106=Q39631 hekim + P569/P570. ⚠️ **P3'tür**: yönlendirme, kanıt değil |
| İlişki grafiği | `anamnesis:upsert_triples` → `graph_neighbors` / `subgraph` (kişi↔kurum↔eser↔olay) |
| Birincil kayıt | IIIF (portre, eser, yazışma) · arşiv künyesi · sicil kayıtları |
| Çağdaş tıp tarihçileri | `yok-akademik` (yalnız modern akademisyen haritası) |
| Türkiye | `devlet-arsivleri` (sicill-i ahvâl) + `yoktez` + `literatur`; Osmanlı şahsiyet külliyatı → `vekayinuvis` |

## Çıktı

G0 manifestosu · tarihler çift takvimle · her iddia kaynağa bağlı · doğrulanamayan bilgi
`[doğrulanmadı]` etiketiyle veya hiç yazılmaz.
