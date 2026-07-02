---
description: Uçtan uca PRISMA sistematik/kapsam derleme koşumu — medical-research flagship'ini P0→P7 (protokol → arama stratejisi → getirim+dedup → tarama → çıkarım → yanlılık riski → GRADE → PRISMA raporlama) insan-onay kapılarıyla çalıştırır. Argüman = herhangi bir tıbbi araştırma sorusu (her uzmanlık, her soru tipi: tedavi/tanı/prognoz/etiyoloji/önleme).
argument-hint: <araştırma sorusu — herhangi bir tıbbi konu>
---

# /evidentia — Uçtan Uca PRISMA Derleme Koşumu

Kullanıcı sorusu: **$ARGUMENTS**

`medical-research` flagship skill'ini **P0→P7 eksiksiz** çalıştırın. Süit bağlamında
[`CONNECTORS.md`](../CONNECTORS.md) ve [`shared/canonical-cache-contract.md`](../shared/canonical-cache-contract.md)
**normatiftir**.

## Yürütme — PRISMA yaşam döngüsü (P0–P7)

1. **P0 Protokol** (`references/prisma-protocol.md`) — soru-tipini sınıfla; PICO/PECO + uygunluk
   kriterleri; derleme tipi (sistematik/kapsam/hızlı).
2. **P1 Arama stratejisi** (`references/search-strategy.md`) — kavram→MeSH/Emtree; veritabanı-başına
   sorgu; raporlanabilir arama dizesi.
3. **P2 Getirim + dedup** — bibliyografik çekirdek connector'larında (CONNECTORS.md §1.1) kapsamlı
   arama → tekilleştirilmiş kayıt seti + kaynak-bazlı sayılar.
4. **P3 Tarama** (`references/screening.md`) — başlık/özet → tam-metin; dahil/hariç + gerekçe.
   **İnsan-onay kapısı bağlayıcı.**
5. **P4 Çıkarım** (`references/data-extraction.md`) — tam-metin (`/evidentia-fulltext`) → anamnesis
   RAG → kanıt tablosu (retrieve-don't-dump).
6. **P5 Yanlılık riski** (`references/risk-of-bias.md`) — tasarıma göre RoB2 / ROBINS-I / QUADAS-2 /
   Newcastle-Ottawa / PROBAST / AMSTAR-2. **İnsan-onay kapısı bağlayıcı.**
7. **P6 Sentez + GRADE** (`references/evidence-grading.md`) — sonuç-bazlı GRADE kesinlik + SoF.
8. **P7 Raporlama** (`references/prisma-reporting.md`) — PRISMA 2020 / PRISMA-ScR akış diyagramı
   (gerçek sayılar) + kontrol listesi + çalışma-özellikleri + RoB özeti + Summary-of-Findings;
   temiz-kopya (VIZ/OPS yorum izolasyonu; araç-sızıntısı yok).

## Opsiyonel zenginleştirme (bağlam-tetiklemeli)

Adım 0.5 sınıflandırıcısı yalnız soru gerçekten o bağlama girince ilgili opsiyonel modülü yükler
(tedavi-alanı / ilaç-istihbaratı / regülatuar / HTA / KOL / Türkiye-pazarı / epidemiyoloji) →
çıktıya **işaretli ek** olarak girer, çekirdek SR raporunun kimliğini belirlemez. **Hiçbir modül
zorunlu değildir; çekirdek PRISMA hattı her koşulda çalışır.**

## Disiplin

- **Tek-sefer / kanonik önbellek** (canonical-cache-contract.md); openfda tekil+retry+skippable.
- **Çapraz-doğrulama** — hasta-etkili her iddia iki bağımsız kaynakla; topluluk-MCP çıktısı otoriter
  kaynak olmadan klinik karar olarak sunulmaz (CONNECTORS.md §5). DDI substance-overlap ayrımı.
- **No-fabrication** — bulunamayan veri "VERİ BULUNAMADI" + denenen sorgular; PRISMA akış sayıları
  connector toplam-sayı vermiyorsa sınırı dürüstçe not edilir; sessiz atlama yok.

## Ağır koşum

Geniş fan-out (çok kaynak + tam-metin korpus) bekleniyorsa `evidence-synthesizer` alt-ajanını
tetikle: ham connector gürültüsünü izole eder, ana pencereye yalnız damıtılmış kanıt paketi döner.

## Devir (Scope Guard)

Bireysel SGK/dava → `ius-salutis`/`onko-erisim`; MLR → `promo-censor`; ticari/IP →
`pharmaintel`/`pharmapatent`; yayın render → `carbon-html-report`/`carbon-pptx`.
