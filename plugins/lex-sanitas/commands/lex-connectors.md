---
description: Lex Sanitas tam-filo bağlantı durumu — wire edilmiş 19 hukuk/regülasyon MCP + 5 companion (Yargı/Open Law/Ansvar/Fedlex Swiss/Türk Patent) + evidentia/sci-audit zorunlu delegasyonun CANLI erişilebilirliğini gerçek MCP prob'uyla raporlar. Hangi katman hazır, hangisi anahtar bekliyor, hangisi yapılandırma arızası taşıyor gösterir. Argüman gerekmez ("taze" derseniz cache atlanır).
argument-hint: (argüman gerekmez — "taze"/"fresh" derseniz 24 saatlik cache atlanır)
allowed-tools: Read, Bash, Task
---

# /lex-connectors — Tam-Filo Bağlantı Durumu

Lex Sanitas'ın **tam-filo ilkesi** (wire'lı tüm araçlar her sorguda çalışır) için hangi katmanın gerçekten hazır olduğunu **canlı prob'la** raporla — env-var varlığına bakarak DEĞİL.

> **Neden canlı prob:** anahtarın env'de bulunması o server'ın çalıştığını KANITLAMAZ. 2026-08-02'de TİTCK kapılandı; plugin onu "public" saymaya devam etti ve katman aylarca 401 aldı — env'e bakan bir kontrol bunu yapısal olarak göremezdi. Bu komut gerçek bir MCP `initialize` isteği atar.

## Yürütme

1. **Filoyu oku.** [`fleet.yaml`](../fleet.yaml) tek gerçek kaynaktır; [`fleet.lock.json`](../fleet.lock.json) onun makine-okunur türevidir (`counts` + server/companion/delegasyon listeleri). `.mcp.json` de bunlardan üretilir — **elle düzenlenmez**.

2. **Canlı prob'u koştur.** Kullanıcı "taze"/"fresh"/"güncel" dediyse `--fresh` ekle; aksi hâlde 24 saatlik cache kullanılır (ağ trafiği yok):

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/fleet_probe.py" --json
   ```

   Taze koşum ~12 sn sürer (en yavaş server `anamnesis` ~11 sn); cache'li koşum anlıktır.

3. **Her satırı durumuyla raporla.** Prob'un beş durumunu **ayırt ederek** yaz — bu ayrım komutun asıl değeridir:

   | Durum | Anlamı | Aksiyon |
   |---|---|---|
   | `ok` | hazır, `initialize` 200 döndü | — |
   | `auth_missing` | anahtar süreç ortamında yok (ağa çıkılmadı) — **meşru degrade** | `doppler run -p cureohub -c dev_personal -- claude` ile başlat |
   | `unauthorized` | sunucu 401/403 verdi — **YAPILANDIRMA ARIZASI, degrade değil** | `fleet.yaml`'i düzelt → `python3 tools/gen_fleet.py`; anahtar emekli olmuş olabilir |
   | `unreachable` | timeout / bağlantı hatası / 5xx | upstream sorunu; manifestoda `degraded: erişilemedi` |
   | `error` | 200 ama geçersiz JSON-RPC | sunucu sürümü uyumsuz olabilir |

4. **Katmanlara göre grupla** (`fleet.lock.json`'daki `tier` alanı):
   - **TR primer/idari** (`primary`/`secondary`/`support`, shard S1): mevzuat · mevzuat-bilgisi · resmi-gazete · titck · tbmm · saglikbakanligi · detsis
   - **Karşılaştırmalı/uluslararası** (`comparative`, shard S2): health-policy (**semantic_search** doğal-dil çok-dilli keşif US/JP/AU/CN + 8 ülke fetch + legal_distill) · german-law · ich-guidelines · intl-treaty · eudamed · oecd
   - **Doktrin** (`doctrine`, shard S3): yok-akademik (künye) · **yoktez** (tez tam-metni + G7 atıf doğrulaması — v3.5.0'da wire'landı, artık companion DEĞİL) · **literatur** (DergiPark makale tam-metni)
   - **Tam-metin şelalesi** (`fulltext`, shard S4): **openathens** (Tier 3 lisanslı) → **annas-reader** (Tier 4 son çare, yalnız analiz). Şelale sırasını raporda belirt.
   - **Büyük-veri substratı** (`substrate`): anamnesis — RAG/GraphRAG evidence_index (kaynak değil, bağlam-ekonomisi Tier 2)
   - **Companion (wire edilemez — claude.ai connector):** Yargı · Open Law · Ansvar · Fedlex Swiss · Türk Patent
   - **Delegasyon:** evidentia (klinik kanıt) · sci-audit (atıf-adli + dil)

5. **Kapı etkisini göster.** Eksik katmanın maliyetini açıkça yaz:
   - `Yargı bağlı değil ⇒ G5 en fazla CONDITIONAL (içtihat zinciri doğrulanamaz)`
   - `Open Law bağlı değil ⇒ G6 CONDITIONAL (CELEX doğrulaması german-law→WebFetch'e degrade)`
   - `Ansvar bağlı değil ⇒ Mod 7'de CH/FR/IT/NL/SE/DK/FI/AT/PL satırları manual_required`
   - `Fedlex Swiss bağlı değil ⇒ Mod 7 CH birincil-metin satırı Ansvar çerçeve-taramasına degrade + manual_required`
   - `Türk Patent bağlı değil ⇒ IP-boyutlu satır manual_required`
   - `yoktez erişilemiyor ⇒ G7 YÖK-Tez atıf doğrulaması yapılamaz; tez atıfları illustrative_placeholder_not_verified → KULLANILMAZ`
   - `literatur erişilemiyor ⇒ doktrin metadata-only'ye düşer (atıf yapılabilir, içerik alıntılanamaz)`
   - `openathens erişilemiyor ⇒ lisanslı band kapalı; annas-reader OTOMATİK AÇILMAZ (şelale sırası korunur)`
   - `evidentia kurulu değil ⇒ klinik iddialar unverified` · `sci-audit kurulu değil ⇒ çıktı-QA manuel`

6. **Yapılandırma bütünlüğünü de bildir.** Filo `fleet.yaml`'den türetilir; bütünlük kapısı repo-düzeyi bir GELİŞTİRME aracıdır (kurulu plugin'de bulunmaz). Kaynak depoda çalışıyorsan:

   ```bash
   python3 tools/fleetkit/check_drift.py --all
   ```

   `exit 0` = türetilmiş dosyalar güncel, sürümler tutarlı, vendor'lı prob kanonikle bayt-özdeş, düzyazı sayıları gerçekle uyuşuyor. Kurulu plugin'den koşuyorsan bu adımı `skipped: repo dışı` olarak bildir — `fleet.lock.json`'daki `counts` yine de manifestoda kullanılabilir.

7. **Özet:** kaç katman `ok`, hangileri kullanıcı aksiyonu bekliyor (Doppler Bearer inject / claude.ai connector ekleme), hangileri **yapılandırma arızası** taşıyor (bunlar kullanıcı aksiyonu değil, kod düzeltmesi ister) ve bu eksikliklerin hangi kapıları CONDITIONAL'a düşürdüğü.

> Not: Bir server anahtar/bağlantı beklese bile plugin **graceful degrade** eder — o katman kapsam manifestosunda `skipped: anahtar yok` olarak beyan edilir, çıktı durmaz, asla uydurma yapılmaz. **Ters yüzü:** kurulu/bağlı bir katman (companion dahil) tetiklenmiş bağlamda ATLANAMAZ — bu G0 ihlalidir (`shared/composition-contract.md`).

## Anahtar env-var haritası

<!-- GEN:fleet-env-table BEGIN -->
| Server | Tier | Env-var (Doppler → Bearer) |
|---|---|---|
| `mevzuat` | primary | `MEVZUAT_MCP_API_KEY` |
| `mevzuat-bilgisi` | secondary | _(public — anahtar yok)_ |
| `resmi-gazete` | primary | `RESMI_GAZETE_MCP_API_KEY` |
| `titck` | primary | `TITCK_MCP_API_KEY` |
| `tbmm` | primary | `TBMM_MCP_API_KEY` |
| `saglikbakanligi` | primary | `SAGLIK_BAKANLIGI_MCP_API_KEY` |
| `detsis` | support | `DETSIS_MCP_API_KEY` |
| `health-policy` | comparative | `HEALTH_POLICY_MCP_API_KEY` |
| `german-law` | comparative | `GERMAN_LAW_MCP_API_KEY` |
| `ich-guidelines` | comparative | `ICH_MCP_API_KEY` |
| `intl-treaty` | comparative | `INTL_TREATY_MCP_API_KEY` |
| `eudamed` | comparative | `EUDAMED_MCP_MCP_API_KEY` |
| `oecd` | support | `OECD_MCP_API_KEY` |
| `yok-akademik` | doctrine | `YOK_AKADEMIK_MCP_API_KEY` |
| `yoktez` | doctrine | _(public — anahtar yok)_ |
| `literatur` | doctrine | _(public — anahtar yok)_ |
| `openathens` | fulltext | `OPENATHENS_MCP_API_KEY` |
| `annas-reader` | fulltext | `ANNAS_MCP_API_KEY` |
| `anamnesis` | substrate | `ANAMNESIS_MCP_API_KEY` |
| Yargı | companion | _(claude.ai connector — env anahtarı yok)_ |
| Open Law | companion | _(claude.ai connector — env anahtarı yok)_ |
| Ansvar | companion | _(claude.ai connector — env anahtarı yok)_ |
| Fedlex Swiss | companion | _(claude.ai connector — env anahtarı yok)_ |
| Türk Patent | companion | _(claude.ai connector — env anahtarı yok)_ |
<!-- GEN:fleet-env-table END -->

> anamnesis bir *kaynak* değil, bağlam-ekonomisi Tier 2 RAG substratıdır (büyük tam-metin ingest→bounded query). Anahtarı yoksa büyük belge işleme bounded-chunk fallback'e degrade eder (`references/16` §C) — plugin yine çalışır.
