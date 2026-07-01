# Screening (P3)

**Loaded:** Phase P3 — consumes P2'nin tekilleştirilmiş kayıt kümesini ve P0 uygunluk
kriterlerini (`prisma-protocol.md` §3); üretir `screening_log` (dahil/hariç+gerekçe),
P4 (`data-extraction.md`) ve P7 (`prisma-reporting.md` akış diyagramı) girdisidir.

**Authority basis:** PRISMA 2020 item 8–9 (selection process, akış diyagramı) ·
Cochrane Handbook v6.x ch. 4 (study selection) · JBI Scoping Review Methodology
(PRISMA-ScR study selection).

---

## 1. İki-aşamalı tarama

Tarama, tek bir geçişte değil **iki ayrı aşamada** yürütülür; her aşama P0'ın
uygunluk matrisine (`prisma-protocol.md` §3: tasarım/popülasyon/dil/yıl/yayın
tipi) karşı bağımsız uygulanır:

| Aşama | Girdi | Uygulanan kriter | Çıktı |
|---|---|---|---|
| **1 — Başlık/özet** | P2 tekilleştirilmiş kayıt kümesi | Kaba eleme: açıkça alakasız popülasyon/tasarım/konu | dahil-adayı (tam-metine geçer) / hariç / `maybe` |
| **2 — Tam-metin** | Aşama 1'den geçen kayıtlar (PDF/tam-metin gerektiğinde `fulltext-retrieval.md` cascade) | Tam uygunluk matrisi — beş eksenin tamamı tek tek denetlenir | dahil (kesin) / hariç (gerekçeli) |

Aşama 1 duyarlılık-öncelikli (yanlış-negatifi minimize et — belirsizlik
`exclude` değil `maybe` alır), Aşama 2 özgüllük-öncelikli (nihai karar burada
kesinleşir). Kriter aşama başladıktan sonra değiştirilemez; değişiklik yalnız
gerekçeli protokol sapması olarak kaydedilir (`prisma-protocol.md` §3 ile
tutarlı — post-hoc daraltma yasak).

---

## 2. Parti-parti işleme ve hariç gerekçesi

Kayıtlar tek seferde değil **N'li partiler** hâlinde işlenir (bağlam taşmasını
önlemek ve insan-onay kapısının [§3] yönetilebilir kalması için). Her kayıt üç
etiketten birini alır:

- **`include`** — tüm beş eksende uygun.
- **`exclude`** — PRISMA hariç kategorilerinden **biriyle etiketlenmiş gerekçe**
  zorunlu:
  - `wrong_population` — yanlış popülasyon (yaş/tanı/evre uyumsuz)
  - `wrong_design` — yetersiz tasarım seviyesi (vaka sunumu, editöryal)
  - `wrong_comparator` — karşılaştırıcı eşleşmiyor (yalnız PICO/PECO'da; PCC'de uygulanmaz)
  - `wrong_outcome` — birincil/ikincil sonlanım raporlanmamış
  - `wrong_language` — çeviri kapasitesi dışı dil + özet yetersizliği
  - (P0'da tanımlıysa) `wrong_publication_type`, `outside_date_range`
- **`maybe`** — özet/başlıktan karar verilemiyor → otomatik tam-metin
  değerlendirmesine (Aşama 2) taşınır, asla doğrudan `exclude` sayılmaz.

Her karar tek satırlık kanıt-izi taşır: `{record_id, stage, decision, reason_category, note}`.
Gerekçesiz `exclude` kabul edilmez — PRISMA 2020 madde 9 hariç-nedeni raporlama
zorunluluğuyla doğrudan uyumludur.

---

## 3. İnsan-onay kapısı (ZORUNLU)

Tool, her parti için **öneri** üretir (dahil/hariç/`maybe` + gerekçe) — bu öneri
nihai değildir. Kullanıcı, savunulabilir derleme normu gereği partinin nihai
dahil/hariç kararını **onaylamak zorundadır**:

- Tool önerisi kullanıcıya parti hâlinde sunulur (kayıt + önerilen etiket + gerekçe).
- Kullanıcı onayı olmadan hiçbir kayıt `screening_log`'a kesin `include`/`exclude`
  olarak yazılmaz.
- Kullanıcı bir öneriyi reddedip değiştirebilir (`override` — orijinal tool önerisi
  ile birlikte saklanır, sessizce üzerine yazılmaz).
- Belirsiz kalan her kayıt `maybe` etiketiyle tam-metin aşamasına devredilir;
  kapıyı atlamak için `maybe`→otomatik `exclude` **yasaktır**.

Bu kapı, tek-eleştirmen sınırının (§4) doğal telafisidir: nihai karar insan
onayından geçmeden PRISMA akışına giremez.

---

## 4. İkili tarama notu (dürüstlük)

Bu araç **tekil-eleştirmen** (single-reviewer) modelinde çalışır — ikinci,
bağımsız bir insan gözden geçirici tarafından çapraz kontrol **yapılmaz**.
Cochrane/PRISMA ideali çift-eleştirmen + uzlaşı/hakemdir (yanlı seçim riskini
azaltır); bu sınır **açıkça** raporlanır (`prisma-reporting.md` metodoloji
bölümü ve limitasyonlar), gizlenmez veya çift-eleştirmen yapılmış gibi
sunulmaz. Yüksek-riskli/yayın-eşiği çalışmalarda kullanıcıya ikinci bir insan
gözden geçiricinin bağımsız taramasını tekrarlaması **önerilir**.

---

## 5. Sayı defteri — `screening_log`

P7 PRISMA akış diyagramına birebir aktarılan makine-okur sayaç:

```jsonc
{ "screening_log": {
    "identified": 0,                 // P2 girdisi: veritabanı ham toplamı
    "deduplicated": 0,               // P2 sonrası tekil kayıt sayısı
    "title_abstract_screened": 0,    // Aşama 1'e giren kayıt sayısı
    "excluded_title_abstract": [
      { "reason_category": "wrong_population", "count": 0 }
    ],
    "full_text_assessed": 0,         // Aşama 2'ye (tam-metin) giren kayıt sayısı
    "excluded_full_text": [
      { "reason_category": "wrong_design", "count": 0 }
    ],
    "maybe_resolved_to_include": 0,
    "maybe_resolved_to_exclude": 0,
    "included": 0                    // P4 veri-çıkarımına devredilen nihai sayı
  } }
```

**No-fabrication notu:** her sayaç yalnız gerçekten işlenmiş kayıtlardan
türetilir; eksik/işlenmemiş bir aşama `null` bırakılır, tahmini sayıyla
doldurulmaz. `identified` + `deduplicated` farkı P2'nin dedupe mantığından
gelir (bu dosyanın kapsamı değil); `included` sayısı `excluded_*` toplamları
ile birlikte `identified`'i **birebir** karşılamalıdır — tutmuyorsa akış
tutarsızlığı olarak P7'ye taşınır, sessizce düzeltilmez.

---

## 6. Sonraki faz

Kesinleşmiş `include` kayıtları (§3'ten onaylanmış) P4 veri-çıkarımına
(`data-extraction.md`) devredilir; `screening_log` bloğu bütünüyle P7 raporlama
akış diyagramına (`prisma-reporting.md`) aktarılır.
