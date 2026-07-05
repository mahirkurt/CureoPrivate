# Kapsam Manifestosu (G0) — biçim ve örnek

**Amaç:** "wire edilmiş tüm araçlar her sorguda çalıştı" iddiasının doğrulanabilir kanıtı. Her lex-sanitas çıktısı bu bloğu taşır (başta veya sonda). Eksik satır = **G0 FAIL**.

## Kurallar

- Wire edilmiş **14 MCP** + **3 companion** (Yarg/Open_Law/Ansvar — satırları HER manifestoda zorunlu, bağlı olsun olmasın) + **evidentia** (klinik-boyut varsa) + **sci-audit** (her çıktı) için **birer satır**.
- Durum sözlüğü: `hit N` (N kayıt döndü) · `empty` (çalıştı, sonuç yok) · `degraded` (fetch fallback / `mcp_verified=false`) · `skipped: <gerekçe>` (anahtar yok / mod için N/A).
- `skipped` gerekçesi zorunlu ve denetlenebilir olmalı ("anahtar yok", "saf idari norm — klinik-sıfır", "companion bağlı değil"). **Gerekçesiz skip yasak.**
- **Kurulu/bağlı katman atlanamaz:** evidentia kuruluyken klinik-boyutlu sorguda, sci-audit kuruluyken herhangi bir çıktıda, companion bağlıyken tetiklenmiş bağlamda `skipped` yazmak **meşru değildir** (G0 FAIL — Stop hook tamamlatır). `skipped: … bağlı/kurulu değil` yalnız gerçek yoklukta doğrudur.
- **Companion skip'inin kapı etkisi manifesto satırında görünür:** `Yarg → skipped: companion bağlı değil ⇒ G5 CONDITIONAL` · `Open_Law → skipped: companion bağlı değil ⇒ G6 CONDITIONAL (CELEX degrade: german-law→WebFetch)` · Ansvar skip'inde etkilenen yargı satırları `manual_required` kalır, tablodan silinmez.
- Manifesto, `legal-distiller`'ın döndürdüğü `coverage` bloğundan türetilir; alt-ajan çağrılmadıysa doğrudan araç çağrılarından derlenir.

## Örnek

```
### Kapsam Manifestosu (G0) — Mod: DRAFT · Konu: ATMP (ileri tedavi tıbbi ürünleri) yönetmelik taslağı
TR mevzuat çekirdeği
  mevzuat              → hit 7   (1262 SK, 3359 SK, Beşeri Tıbbi Ürünler Ruhsat Yön., …)
  mevzuat-bilgisi      → hit 2   (çapraz-kontrol: kanun-no lookup 1262/3359)
  resmi-gazete         → hit 3   (RG 11/12/2021-31686 ruhsat yön. yürürlük teyidi)
  saglikbakanligi      → hit 1   (TİTCK ATMP kılavuz taslağı — soft-law)
  titck                → hit 4   (ATMP ATC/ürün envanteri, search_titck_guidelines)
  tbmm                 → empty   (teklif düzeyi yok — yönetmelik)
  detsis               → hit 1   (TİTCK resmî ad + DETSİS no)
Karşılaştırmalı katman
  health-policy        → hit 5   (US 21 CFR 1271, AU TGA biologicals, ES BOE)
  german-law           → hit 3   (AMG §4b, GewebeG; EU 1394/2007 basis)
  ich-guidelines       → hit 2   (Q5A(R2), S12 gene therapy)
  intl-treaty          → hit 1   (Oviedo CETS 164 — Md.90/5)
  eudamed              → empty   (ATMP ilaç sınıfı — cihaz DB N/A, yine de tarandı)
  oecd                 → hit 1   (sağlık Ar-Ge harcama göstergesi — RIA girdisi)
Doktrin + companion
  yok-akademik         → hit 4   (ATMP regülasyon doktrin makaleleri)
  Yarg                 → hit 2   (Danıştay 10.D ruhsat iptali emsali)
  Open_Law             → skipped: companion bağlı değil ⇒ G6 CONDITIONAL (CELEX degrade: german-law get_eu_basis)
  Ansvar               → skipped: companion bağlı değil (Mod 7'de CH/FR/… yargısı yoktu — kapsam etkisi yok)
Delegasyon
  evidentia            → hit     (klinik kanıt: CAR-T/gen tedavi GRADE, sidecar reverse_signals okundu)
  sci-audit            → hit     (atıf-adli 0 uydurma; TR imla 3 düzeltme; istatistik N/A)
Büyük-veri substratı (Tier 2)
  anamnesis            → ingest 2 belge (mevzuat:1262/1, celex:32007R1394) · 9 bounded query
```

Büyük-veri satırı (Tier 2) kullanıma göre değişir:
- Büyük tam-metin ingest edildiyse: `anamnesis → ingest N belge (doc_id'ler) · M bounded query`
- Getirim küçük kaldıysa: `anamnesis → skipped: gerekmedi (küçük getirim)`
- Anahtar yoksa: `anamnesis → skipped: anahtar yok (bounded-chunk fallback)`

Not: `empty` ve `skipped` **başarısızlık değil**, kapsamın dürüst kanıtıdır — mühim olan hiçbir server'ın sessizce atlanmamasıdır.
