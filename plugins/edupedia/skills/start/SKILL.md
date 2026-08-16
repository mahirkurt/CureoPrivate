---
name: start
description: edupedia süitine giriş ve yönlendirme. Bağlı İKİ MCP connector'ını (maarif-mufredat müfredat/kazanım, egitim-kaynak açık eğitsel kaynak RAG içerik-zenginleştirme) kontrol eder, flagship carbon-edupedia skill'ini ve komutları tanıtır, kullanıcının niyetine göre doğru komuta yönlendirir. İlk kez süitle çalışırken, hangi connector'ın bağlı olduğunu görmek için, ya da "edupedia nedir / nereden başlamalıyım / hangi komutu kullanmalıyım / connector'ım bağlı mı / Maarif MCP çalışıyor mu / egitim-kaynak bağlı mı" türü oryantasyon sorularında kullanın. Tetikleyiciler — edupedia başlat, süit oryantasyonu, connector kontrolü, "ne yapabilirsin", "nereden başlayayım", "Maarif Modeli modülü nasıl üretirim", "kazanımdan modül nasıl".
version: 1.2.0
last_updated: 2026-08-16
---

# edupedia — Başlangıç ve Yönlendirme

edupedia, **MEB Türkiye Yüzyılı Maarif Modeli kazanımlarından DEHB-dostu, erişilebilir,
kazanım-izlenebilir etkileşimli öğrenim modülleri** üreten bir Claude plugin'idir. Kullanıcıyı
süitle tanıştırıp doğru araca yönlendirin. Aşağıdaki adımları sırayla izleyin.

> Connector envanteri, kimlik/PDF uyarıları, provenans ve Tier-1/Tier-2 görüntü-dayanak politikası
> için tek doğruluk kaynağı: [../../CONNECTORS.md](../../CONNECTORS.md). Tek-sefer disiplini ve
> `get_figure` yetenek-probu: [../../shared/canonical-cache-contract.md](../../shared/canonical-cache-contract.md).

## Adım 1 — Karşılama

Şu mesajı gösterin:

```
edupedia — MEB Maarif Modeli Etkileşimli Öğrenim Modülü Süiti

MEB Türkiye Yüzyılı Maarif Modeli (2024) kazanımlarından DEHB-dostu, IBM Carbon v11 ile
biçimli, erişilebilir (WCAG 2.1 AA), emojisiz ama ikon/piktogram/SVG zengini, tek-dosya
ETKİLEŞİMLİ öğrenim modülleri üretir. Kazanım kodundan/ders+sınıftan modül üretir, resmî
beceriyi (Kavramsal Beceriler KB2.x) etkileşim desenine haritalar, kazanım-izlenebilir
provenans damgalar (G-CURRICULUM).

Kapsam: yalnız Türkiye MEB · fen/matematik/sosyal/Türkçe/tarih/fizik/kimya/biyoloji ·
ilkokul/ortaokul/lise. Kapsam dışı: yabancı müfredat (IB/Cambridge), genel React UI,
statik baskı raporu.
```

## Adım 2 — Bağlı MCP Connector'ını Kontrol Et

Bağlı araçları listeleyip raporlayın. `maarif-mufredat`'ın **canlı** mı yoksa **bağlı değil** mi
olduğunu açıkça belirtin (CONNECTORS.md §6 pre-flight).

**Maarif Modeli MCP (`maarif-mufredat` · `https://mufredat.cureonics.com/mcp`) — süitin omurgası:**
Dört işlevsel araç kümesi (otoritatif **21 araç**):
- **A · Keşif** — `list_subjects`, `get_subject`, `list_education_levels`, `list_curriculum_programs`, `get_curriculum_program`, `server_info`
- **B · Kazanım** (çekirdek kaynak) — `list_learning_outcomes`, `search_learning_outcomes`, `search`
- **C · Beceri çerçevesi** — `list_frameworks`, `get_framework` (KB2.x → etkileşim haritalama)
- **D · Belge + medya** — `list_document_kinds`, `list_documents`, `get_document_text`, `list_textbooks`, `list_guides`, `list_reports`, `list_videos`, `get_video`
- **Görsel yolu** — `search_figures` + `get_figure` (**Tier-2** yeteneği, §Adım 2 alt-kontrol)

Canlılık için `server_info` çağırıp korpus sürümünü (bilinen: corpus v1.4, build 2026-06-14)
raporlayın. **`get_figure` mevcut mu** doğrulayın: varsa Tier-2 (resmî ders-kitabı görseli gömme)
mevcuttur; yoksa yalnız Tier-1 (yazar-üretimli SVG) — her iki durumda da üretim çalışır.

**Eğitim Kaynak RAG MCP (`egitim-kaynak` · `https://egitim-kaynak.cureonics.com/mcp`) — TAMAMLAYICI:**
6 salt-okunur araç (`kb_search`, `kb_for_outcome`, `kb_get`, `kb_patterns`, `kb_sources`,
`kb_server_info`). **Anahtarsız — secret gerekmez.**

> **OTORİTE SIRALAMASI (kritik):** Modülün olgusal otoritesi **`maarif-mufredat`'tadır** — orada
> **105 MEB ders kitabı TAM METİN** (`list_textbooks` → `get_document_text`), 10.855 kazanım ve
> 22.414 figür var; resmî, müfredat-hizalı, pedagojik olarak kurgulanmış. `egitim-kaynak` bunun
> yerine geçmez, **üstüne ekler**: ek örnek, farklı anlatım, etkileşim malzemesi, meraklı öğrenci
> için derinlik. Bir olgu ders kitabıyla çelişiyorsa **ders kitabı kazanır**.

Bağlıysa modül üretiminde **`kb_search(konu)`** ile tamamlayıcı materyal çekin; bağlı değilse
üretim bloke olmaz, zenginleştirme atlanır (asla uydurma kaynak).

**Kaynaklar (2026-07-17 itibarıyla):**
- **PhET** (Colorado Üniversitesi etkileşimli simülasyonları) — **CC BY-NC 4.0, atıf ZORUNLU.**
  Korpusta **175 simülasyon** (canlı `kb_sources` ölçümü); tamamı Türkçe. *(Upstream 241 sim
  yayınlar; 237'si CC BY-NC — gerisi elenir — ve bu 237 kayıt yalnız **175 farklı** simülasyona
  aittir: PhET aynı simi birden çok kayıtla listeler, `name` üzerinden en güncel olan tutulur.
  Yani **237 kayıt sayısıdır, korpus içeriği değildir**.)* Etkileşimli modül üretirken **en
  değerli kaynak budur**: konuya uygun simülasyonu `kb_search` ile bulup modülde
  bağlantılayın/gömün. Fizik/kimya/matematik güçlü; **biyoloji ince** (fotosentez/mitoz YOK).
- **Vikipedi-TR** — CC BY-SA 4.0. **Arka plan ve örnek malzemedir, OTORİTE DEĞİLDİR.** Üçüncül
  kaynaktır ve Türkçe sürümü incedir (ölçüm: İngilizce'nin %9,6'sı kadar madde, ama yalnız
  **%1,8'i kadar aktif editör** → madde başına denetim ~5 kat az). Bir kazanımı Vikipedi'ye
  dayandırmayın; ders kitabına dayandırın.
- *Vikikitap 2026-07-17'de DÜŞÜRÜLDÜ* — 1.099 madde / **9 aktif editör**; bir wiki'nin
  güvenilirliği editör sayısından gelir.

**Getirme: BM25 önce, vektör YEDEK** (RRF füzyonu 2026-07-17'de kaldırıldı — ölçüm hibridi
3/8, saf BM25'i 6/8 verdi; RRF *uzlaşmayı* ödüllendirdiği için gürültülü vektör tarafı doğru
cevabı boğuyordu). Vektör yalnız BM25 metin kanıtı bulamayınca konuşur (`bge-m3`, Cloudflare
Workers AI). Sonuçlar `retrieval` (**gerçekte izlenen yol**: `fts5-bm25` / `vector-fallback`),
`score_kind` (`bm25`/`cosine`) ve her pasajda `license`/`quote_allowed` taşır; `match_kind`
üç değerli: `text` (sözlüksel kanıt) > `title_only` > `semantic` (**vektör tahmini** — gövde
sorguyu anmayabilir). Sıralama kademe-birincildir → **`score`'a göre yeniden sıralamayın**.
Sorgu 512 karakterde kesilir (`query_truncated`).

**`kb_for_outcome` HENÜZ KURULMADI** (dürüstçe `alignment_not_built` döner, asla uydurma hizalama):
kazanım-hizalaması, korpus müfredat konularını kapsayana **ve** insan denetimi geçene kadar
bilinçli olarak kapalıdır. Kazanımdan modül üretirken kazanım metnindeki konuyu `kb_search`'e
sorgu olarak verin. *(Ölçüm 2026-07-17: korpusu büyütmek tek başına yetmedi — 1758 vektörde bile
kazanım↔pasaj kosinüsleri konuyu değil "ikisi de uzun resmî Türkçe"yi ölçüyor; bu yüzden
hizalama bir eşik ayarıyla açılamaz.)*

Connector bağlı değilse: kullanıcıya Settings → Connectors'tan etkinleştirmesini bildirin ve
`carbon-edupedia`'nın **MCP olmadan da** (kullanıcının verdiği ders metniyle) çalıştığını, üretimin
bloke olmadığını söyleyin.

## Adım 3 — Süitin Yeteneğini Tanıt

| Bileşen | Ne Yapar |
|---|---|
| **carbon-edupedia** (flagship skill) | 8 mod, 16 kalite kapısı (yerel `validate_module.py`) — kaynaktan/kazanımdan tek-dosya etkileşimli HTML öğrenim modülü |
| **start** (bu skill) | Oryantasyon + connector kontrolü + niyet→komut yönlendirme |

## Adım 4 — Komutları Tanıt

| Komut | Ne Yapar | Argüman |
|---|---|---|
| `/edupedia:modul` | Kazanım kodundan modül üretir | `<kazanım-kodu>` (örn. FB.5.3.1.1) |
| `/edupedia:mufredat` | Ders+sınıf+konudan modül üretir | `<ders> <sınıf> <konu>` (örn. Fen 5 hücre) |
| `/edupedia:soru` | Bir veya birden fazla sınav sorusundan tek HTML üretir (fotoğraf veya metin) — konu anlatır + her soruyu çözer | `<soru fotoğrafı veya metni>` |
| `/edupedia:kazanim-bul` | Konu→kazanım keşfi + KB/etkileşim haritası (**üretim yok**) | `<konu> [sınıf] [ders]` |
| `/edupedia:durum` | Connector sağlık + Tier-2 (get_figure) kontrolü | — |

## Adım 5 — Niyete Göre Yönlendir

Kullanıcının ne üzerinde çalıştığını sorun ve yönlendirin:

1. **Kazanım kodu verildi** (`FB.5.3.1.1`) → `/edupedia:modul`.
2. **Ders + sınıf + konu** ("5. sınıf fen hücre") → `/edupedia:mufredat`.
3. **Sınav sorusu fotoğrafı veya metni verildi** ("bu soruyu çöz", "bu soruları çöz",
   "bunu anlamadım") → `/edupedia:soru` (bir veya birden fazla; tek HTML). Teslim
   yerel HTML'dir; sınav sorusu paylaşılmaz (telif).
4. **"Bu konuya hangi kazanımlar denk geliyor?"** (yalnız keşif) → `/edupedia:kazanim-bul`.
5. **Connector çalışıyor mu / Tier-2 var mı?** → `/edupedia:durum`.
6. **Kaynak metin yapıştırıldı** (MCP yok) → `carbon-edupedia` skill'ini **doğrudan** (MCP'siz)
   çağır; opsiyonel olarak ilgili kazanımla hizalama öner.

**Ayrım rehberi (disambiguation):**
- Statik baskı raporu / çalışma kâğıdı → `carbon-html-report`.
- Slayt → `carbon-pptx`.
- Genel React UI / web arayüzü → `frontend-design`.
- Yabancı müfredat (IB/Cambridge) → kapsam dışı (Maarif MCP yalnız Türkiye MEB).

Kullanıcının yanıtını bekleyin ve uygun komuta yönlendirin.
