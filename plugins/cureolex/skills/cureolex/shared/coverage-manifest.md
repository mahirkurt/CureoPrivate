# Kapsam Manifestosu (G0) — biçim ve örnek

**Amaç:** "wire edilmiş tüm araçlar her sorguda çalıştı" iddiasının doğrulanabilir kanıtı. Her cureolex çıktısı bu bloğu taşır (başta veya sonda). Eksik satır = **G0 FAIL**.

## Kurallar

- Wire edilmiş **21 MCP** + **3 companion** (Yarg/Open_Law/Ansvar — satırları HER manifestoda zorunlu, bağlı olsun olmasın) + **evidentia** (klinik-boyut varsa) + **sci-audit** (her çıktı) için **birer satır**.
- Durum sözlüğü: `hit N` (N kayıt döndü) · `empty` (çalıştı, sonuç yok) · `degraded` (fetch fallback / `mcp_verified=false`) · `skipped: <gerekçe>` (anahtar yok / mod için N/A).
- `skipped` gerekçesi zorunlu ve denetlenebilir olmalı ("anahtar yok", "saf idari norm — klinik-sıfır", "companion bağlı değil"). **Gerekçesiz skip yasak.**
- **Kurulu/bağlı katman atlanamaz:** evidentia kuruluyken klinik-boyutlu sorguda, sci-audit kuruluyken herhangi bir çıktıda, companion bağlıyken tetiklenmiş bağlamda `skipped` yazmak **meşru değildir** (G0 FAIL — Stop hook tamamlatır). `skipped: … bağlı/kurulu değil` yalnız gerçek yoklukta doğrudur.
- **Companion skip'inin kapı etkisi manifesto satırında görünür:** `Yarg → skipped: companion bağlı değil ⇒ G5 CONDITIONAL` · `Open_Law → skipped: companion bağlı değil ⇒ UK metni ep.legislation_uk (G6'yı düşürmez)` · Ansvar skip'inde etkilenen yargı satırları `manual_required` kalır, tablodan silinmez.
- **Wire'lı Fedlex** companion DEĞİLDİR; manifesto karşılaştırmalı katmanında durur. CH bağlamı yoksa `skipped: mod için N/A`. G6 skip'i `eurlex → skipped/degraded` satırındadır.
- Manifesto, `legal-distiller`'ın döndürdüğü `coverage` bloğundan türetilir; alt-ajan çağrılmadıysa doğrudan araç çağrılarından derlenir.

## Örnek

```
### Kapsam Manifestosu (G0) — Mod: DRAFT · Konu: ATMP (ileri tedavi tıbbi ürünleri) yönetmelik taslağı
TR mevzuat çekirdeği
  mevzuat              → hit 7   (1262 SK, 3359 SK, Beşeri Tıbbi Ürünler Ruhsat Yön., …)
  resmi-gazete         → hit 3   (RG 11/12/2021-31686 ruhsat yön. yürürlük teyidi)
  saglikbakanligi      → hit 1   (TİTCK ATMP kılavuz taslağı — soft-law)
  titck                → hit 4   (ATMP ATC/ürün envanteri, search_titck_guidelines)
  tbmm                 → empty   (teklif düzeyi yok — yönetmelik)
  detsis               → hit 1   (TİTCK resmî ad + DETSİS no)
Karşılaştırmalı katman
  health-policy        → hit 5   (US 21 CFR 1271, AU TGA biologicals, ES BOE)
  german-law           → hit 3   (AMG §4b, GewebeG; EU 1394/2007 basis)
  eurlex               → hit 1   (CELEX 32007R1394 — G6)
  fedlex               → skipped: mod için N/A (CH karşılaştırma kapsamında değil)
  uk-legal             → skipped: mod için N/A (UK içtihat/Hansard gerekmedi)
  ich-guidelines       → hit 2   (Q5A(R2), S12 gene therapy)
  intl-treaty          → degraded: snapshot  (treaty_status ICESCR/ICCPR/CEDAW/CRC/CRPD + coe_treaty_signatories Oviedo 164 / MEDICRIME 211; live_coe:false; intl_treaty_info bir kez)
  eudamed              → empty   (ATMP ilaç sınıfı — cihaz DB N/A, yine de tarandı)
  oecd                 → hit 1   (sağlık Ar-Ge harcama göstergesi — RIA girdisi)
Doktrin + tam-metin şelalesi
  yok-akademik         → hit 4   (ATMP regülasyon doktrin makaleleri — künye/metadata)
  yoktez               → hit 1   (ATMP hukuku doktora tezi, tez-no teyitli)
  literatur            → hit 2   (DergiPark tam metin: 2 makale pdf_to_html)
  openathens           → skipped: oturum doğrulanmamış (Tier 3 lisanslı band kapalı)
  annas-reader         → skipped: şelale sırası korundu (Tier 4 yalnız Tier 3 denendikten sonra)
Companion
  Yarg                 → hit 2   (Danıştay 10.D ruhsat iptali emsali)
  Open_Law             → skipped: companion bağlı değil ⇒ UK metni ep.legislation_uk (G6'yı düşürmez)
  Ansvar               → skipped: companion bağlı değil (Mod 7'de CH/FR/… yargısı yoktu — kapsam etkisi yok)
Delegasyon
  evidentia            → hit     (klinik kanıt: CAR-T/gen tedavi GRADE, sidecar reverse_signals okundu)
  sci-audit            → hit     (atıf-adli 0 uydurma; TR imla 3 düzeltme; istatistik N/A)
Büyük-veri substratı (Tier 2)
  anamnesis            → collection=cureolex:sess:<id> · ingest 2 belge (mevzuat:1262/1, celex:32007R1394) · 9 bounded query
```

Büyük-veri satırı (Tier 2) kullanıma göre değişir:
- Büyük tam-metin ingest edildiyse: `anamnesis → collection=cureolex:sess:<id> · ingest N belge (doc_id'ler) · M bounded query`
- Getirim küçük kaldıysa: `anamnesis → skipped: gerekmedi (küçük getirim)`
- Anahtar yoksa: `anamnesis → skipped: anahtar yok (bounded-chunk fallback)`

Not: `empty` ve `skipped` **başarısızlık değil**, kapsamın dürüst kanıtıdır — mühim olan hiçbir server'ın sessizce atlanmamasıdır.

## Conscious excludes (bir kez — sessiz omit yasak)

Canlı yüzeyde var ama Cureolex `tools_used`'a **bilerek** almaz (`fleet.yaml` `conscious_excludes`):

| Exclude | Ne | Coverage davranışı |
|---|---|---|
| german premium | case_law / prep / history / diff / recent | upgradeRequired + resmi portal link — BGH uydurma yok; premium artefakt yok (2026-08-18) |
| ChatGPT `search`/`fetch` | alias yüzeyler | Native `rg_*` / `sb_*` / `semantic_search` |
| ÜTS | wire yok | Cihaz → eudamed; TİTCK ilaç |
| fedlex peripheral | `fedlex_get_recent_publications` / `termdat_get_concept` | AS izleme + Termdat kavram — RIA omurgası değil |
| detsis/yok peripheral | coğrafya/foto/browse | `skipped: mod için N/A` |

> **Not (2026-08-18 / 3.8.6):** UHRI (`uhri_search`/`uhri_fetch_document`) ve uk-legal `legislation_*` **tools_used**'ta — conscious exclude DEĞİL. Fedlex Vernehmlassung üçlüsü Mod 6 RIA'da SR get sonrası; TR DRAFT usulü değil.

Bu tablo dışında `tools_used` satırı **atlanamaz** — empty/degraded beyanlı süpürülür.
