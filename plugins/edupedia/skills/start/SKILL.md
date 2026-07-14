---
name: start
description: edupedia süitine giriş ve yönlendirme. Bağlı Maarif Modeli MCP connector'ını (maarif-mufredat) kontrol eder, flagship carbon-edupedia skill'ini ve dört komutu tanıtır, kullanıcının niyetine göre doğru komuta yönlendirir. İlk kez süitle çalışırken, hangi connector'ın bağlı olduğunu görmek için, ya da "edupedia nedir / nereden başlamalıyım / hangi komutu kullanmalıyım / connector'ım bağlı mı / Maarif MCP çalışıyor mu" türü oryantasyon sorularında kullanın. Tetikleyiciler — edupedia başlat, süit oryantasyonu, connector kontrolü, "ne yapabilirsin", "nereden başlayayım", "Maarif Modeli modülü nasıl üretirim", "kazanımdan modül nasıl".
version: 1.0.0
last_updated: 2026-07-06
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

Connector bağlı değilse: kullanıcıya Settings → Connectors'tan etkinleştirmesini bildirin ve
`carbon-edupedia`'nın **MCP olmadan da** (kullanıcının verdiği ders metniyle) çalıştığını, üretimin
bloke olmadığını söyleyin.

## Adım 3 — Süitin Yeteneğini Tanıt

| Bileşen | Ne Yapar |
|---|---|
| **carbon-edupedia** (flagship skill) | 8 mod, 13 kalite kapısı (yayında SUNUCU ölçer) — kaynaktan/kazanımdan tek-dosya etkileşimli HTML öğrenim modülü |
| **start** (bu skill) | Oryantasyon + connector kontrolü + niyet→komut yönlendirme |

## Adım 4 — Komutları Tanıt

| Komut | Ne Yapar | Argüman |
|---|---|---|
| `/edupedia:modul` | Kazanım kodundan modül üretir | `<kazanım-kodu>` (örn. FB.5.3.1.1) |
| `/edupedia:mufredat` | Ders+sınıf+konudan modül üretir | `<ders> <sınıf> <konu>` (örn. Fen 5 hücre) |
| `/edupedia:kazanim-bul` | Konu→kazanım keşfi + KB/etkileşim haritası (**üretim yok**) | `<konu> [sınıf] [ders]` |
| `/edupedia:durum` | Connector sağlık + Tier-2 (get_figure) kontrolü | — |

## Adım 5 — Niyete Göre Yönlendir

Kullanıcının ne üzerinde çalıştığını sorun ve yönlendirin:

1. **Kazanım kodu verildi** (`FB.5.3.1.1`) → `/edupedia:modul`.
2. **Ders + sınıf + konu** ("5. sınıf fen hücre") → `/edupedia:mufredat`.
3. **"Bu konuya hangi kazanımlar denk geliyor?"** (yalnız keşif) → `/edupedia:kazanim-bul`.
4. **Connector çalışıyor mu / Tier-2 var mı?** → `/edupedia:durum`.
5. **Kaynak metin yapıştırıldı** (MCP yok) → `carbon-edupedia` skill'ini **doğrudan** (MCP'siz)
   çağır; opsiyonel olarak ilgili kazanımla hizalama öner.

**Ayrım rehberi (disambiguation):**
- Statik baskı raporu / çalışma kâğıdı → `carbon-html-report`.
- Slayt → `carbon-pptx`.
- Genel React UI / web arayüzü → `frontend-design`.
- Yabancı müfredat (IB/Cambridge) → kapsam dışı (Maarif MCP yalnız Türkiye MEB).

Kullanıcının yanıtını bekleyin ve uygun komuta yönlendirin.
