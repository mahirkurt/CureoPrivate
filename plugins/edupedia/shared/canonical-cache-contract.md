# edupedia — Kanonik Artefakt Önbellek Sözleşmesi

**Belge sınıfı:** Normatif orkestrasyon sözleşmesi — plugin-düzeyi
**Sürüm:** 1.0.0
**Birlikte normatif:** `../CONNECTORS.md` §1 (araç envanteri) + §3 (Tier-1/Tier-2 görüntü-dayanak
politikası) · `./run-manifest-schema.json`

> **Sözleşmenin amacı.** Standalone `carbon-edupedia` skill'i `references/curriculum-integration.md
> §8.1`'de "token ekonomisi — gereksiz çağrıdan kaçın" kuralını verir (tipik modül 3–4 çağrı;
> aynı ders slug'ı tekrar çağrılmaz). Bu sözleşme o kuralı **denetlenebilir bir tek-sefer
> disiplinine** ve **kanonik artefakt önbelleğine** yükseltir (kullanıcının `rxpraxis` tek-sefer
> TİTCK kuralının analoğu). Aynı veri bir koşuda **bir kez** çekilir, önbelleğe alınır ve sonraki
> ihtiyaçlar önbellekten **okunur** — yeniden sorgulanmaz. Çift-sorgu `connector_call_ledger` ile
> kanıtlanır.

---

## 1. Kanonik Artefakt Kümesi

Koşu başına bir kez çekilir, içerik-adresli anahtarla önbelleğe alınır:

| Artefakt | Üreten araç(lar) | Tüketen aşamalar | Connector maliyeti |
|---|---|---|---|
| **`subject_registry`** | `list_subjects` + `get_subject(slug)` | Kazanım çekme, program metni, figür arama | 2 çağrı (ilk keşif) |
| **`outcomes_extract`** | `list_learning_outcomes(distinct_codes:true)` / `search_learning_outcomes` | Segment kurgusu, beceri haritalama, `curriculum` bloğu, G-CURRICULUM | 1 çağrı (hedef kazanım kümesi) |
| **`framework_map`** | `get_framework("beceriler/kavramsal-beceriler")` | KB2.x → etkileşim deseni haritalama (skill §4) | 1 çağrı (yalnız resmî beceri modülde gösterilecekse) |
| **`figure_probe`** *(opsiyonel, Tier-2)* | `search_figures` + `get_figure(include_image=false→true)` | Görsel dayanağı / gömme (CONNECTORS.md §3) | 1–2 çağrı, yalnız yetenek-probu ile |

Her artefakt koşumun run-manifest dosyasının `canonical_artifacts{}` bloğuna kaydedilir ve
içerik-adresli anahtarla işaretlenir. **Dosya adı sözleşmesi (normatif, tek tanım yeri):** run
manifest, üretilen HTML ile **aynı dizine**, aynı ad + `.manifest.json` uzantısıyla yazılır
(örn. `hucre-ve-organeller-fen-7-modul.html` → `hucre-ve-organeller-fen-7-modul.manifest.json`).
Çok-modüllü dizinlerde bu, `run_manifest.json` gibi sabit bir ad kullanmaktan farklı olarak
belirsizlik yaratmaz. Yazan adım: `/edupedia:modul` / `/edupedia:mufredat` üretim akışının son
adımı (bkz. `../commands/modul.md`, `../commands/mufredat.md`); tüketen: `/edupedia:yayinla`
(bkz. `../commands/yayinla.md`). Şema: `./run-manifest-schema.json`.

---

## 2. İçerik-Adresli Anahtar Şeması

```
<artifact_type>:<scope_hash>
```

- `artifact_type` ∈ {`subject_registry`, `outcomes_extract`, `framework_map`, `figure_probe`}
- `scope_hash` = SHA-256(normalize edilmiş kapsam)[:12]
  - **subject_registry:** `sha256(subject_slug)` *(örn. `fen-bilimleri-dersi`)*
  - **outcomes_extract:** `sha256(subject_slug + "|" + grade + "|" + topic_or_codes)`
  - **framework_map:** `sha256(framework_slug)` *(örn. `beceriler/kavramsal-beceriler`)*
  - **figure_probe:** `sha256(subject_slug + "|" + grade + "|" + figure_query)`

Aynı `scope_hash` için ikinci çağrı **yapılmaz**; önbellekteki artefakt döndürülür. Farklı
kapsam (farklı ders/sınıf/konu) farklı hash → yeni çıkarım (meşru).

---

## 3. Tek-Sefer Kuralı (single-shot)

- **Aynı ders/sınıf için `get_subject` bir koşuda BİR KEZ** çağrılır. İkinci ihtiyaç
  `subject_registry` önbelleğinden okur (`list_subjects` de aynı — slug bir kez çözülür).
- **Aynı kazanım kümesi için `list_learning_outcomes` / `search_learning_outcomes` BİR KEZ**
  çağrılır. `outcomes_extract` önbelleğe yazılır; segment kurgusu, beceri haritalama ve
  `curriculum` bloğu **aynı** artefaktı okur.
- **`get_framework` yalnız gerektiğinde** çağrılır: skill §4 haritalama tablosu çoğu durumda
  yeter; resmî beceri kodu/tanımı modülde **gösterilecekse** bir kez çekilir ve `framework_map`'e
  yazılır.
- Oturumda **birden çok modül** üretiliyorsa ders slug'ı ve sınıf listesi değişmez → aynı
  `subject_registry` yeniden kullanılır (koşu-içi; koşular arası paylaşım yapılmaz, §5).

**İhlal = bağlam/token israfı.** İkinci özdeş çağrı `connector_call_ledger`'da yakalanır ve
`single_shot_enforced: false` bayrağı düşer.

---

## 4. `get_figure` Yetenek-Probu (Tier-2) — normatif kod

CONNECTORS.md §3.1'in kanonik akışı burada makine-okunur olarak kodlanır:

```
probe:
  1. get_figure araç listesinde var mı?
       hayır -> tier2_status = "unavailable"; log "tier2_unavailable: tool_absent"; DUR (Tier-1).
       evet  -> devam.
  2. false-first (metadata):
       search_figures(query, subject[, grade istemci-tarafı filtre]) -> aday figure_id('ler)
       get_figure(figure_id, include_image=false) -> Tier-1 zenginleştirme
         (title, page_no, caption, pdf_url, kazanım-bağı). figure_probe artefaktına yaz.
  3. opportunistic-true (gömme):
       get_figure(figure_id, include_image=true) DENE:
         başarı -> base64 göm; tier2_status = "embedded"; sourceCitation'a pdf_url+page ekle.
         hata/413/timeout/boş -> tier2_status = "degraded"; log "tier2_degraded: <sınıf>";
                                  SESSİZCE Tier-1'de kal (modül BLOKE OLMAZ).
```

`tier2_status ∈ {unavailable, degraded, embedded}` → `run_manifest.tier2_status`.

> **Kural:** Tier-2 hiçbir zaman kritik yol değildir. Yetenek-probu geçmezse veya gömme
> başarısızsa üretim Tier-1 (yazar-üretimli SVG) ile **tamamlanır**. Görüntü-dayanak asla
> hard-fail üretmez.

---

## 5. Önbellek Yaşam Döngüsü

| Durum | Davranış |
|---|---|
| Aynı koşu içinde aynı `scope_hash` | Önbellekten döndür; çağrı yapma |
| Aynı koşu içinde farklı `scope_hash` | Yeni çıkarım (meşru kapsam farkı) |
| Koşu sonu | Artefaktlar koşuya özgüdür; koşular arası paylaşım **yapılmaz** (provenans bütünlüğü — her koşu kendi korpus-sürüm damgasını taşır) |
| Connector fallback (MCP erişilemez) | Artefakt `status: degraded` + caveat; modül offline yola döner (CONNECTORS.md §5) |

---

## 6. `connector_call_ledger` — çift-sorgu denetim kanıtı

Her Maarif MCP çağrısı (araç, argüman-özeti, önbellek isabet/iska) `run_manifest`'e yazılır:

```json
{
  "connector_call_ledger": [
    {"tool": "list_subjects",            "args_summary": "q=fen",                         "cache": "miss"},
    {"tool": "get_subject",              "args_summary": "fen-bilimleri-dersi",           "cache": "miss"},
    {"tool": "search_learning_outcomes", "args_summary": "hücre|5.Sınıf|distinct",        "cache": "miss"},
    {"tool": "get_framework",            "args_summary": "beceriler/kavramsal-beceriler",  "cache": "miss"},
    {"tool": "get_subject",              "args_summary": "fen-bilimleri-dersi",           "cache": "hit"}
  ],
  "single_shot_enforced": true
}
```

`single_shot_enforced = true` ⇔ hiçbir `(tool, scope)` çifti `cache:"miss"` olarak **iki kez**
görünmez (ikinci özdeş çağrı `cache:"hit"` olmalı). `false` ise A7 kabul kriteri düşer.

---

## 7. Minimal Koşu Manifesti

Şema: `./run-manifest-schema.json`. Zorunlu alanlar: `run_id`, `ts`, `plugin_version`,
`requested_scope`, `connector_call_ledger[]`, `canonical_artifacts{}`, `tier2_status`,
`quality_gates{}`.
