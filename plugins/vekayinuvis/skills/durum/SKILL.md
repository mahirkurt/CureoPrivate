---
name: durum
description: Vekayinüvis tam-filo MCP durumunu ve G0 kapsam manifestosu iskeletini denetler.
disable-model-invocation: true
---

`vekayinuvis` plugin durumunu denetle. Kullanıcı isteğe bağlı bir konu etiketi
belirtebilir; belirtmezse `preflight` varsayılır.

> **Host ön-koşulu:** Bu skill `python3` + `curl` ile yerel bir doktor script'i çalıştırır
> ve **yalnızca Claude Code / yerel kabukta** (Bash aracı mevcutken) işler. **claude.ai'de
> Bash yoktur → bu script çalışmaz.** claude.ai'de connector durumunu görmek için
> `/vekayinuvis:start` akışını kullan (bağlı araçları listeler + `devarsiv_server_info` ile
> araç envanter-drift ve `devarsiv_session_status` ile HP oturum canlılığını MCP üzerinden
> probe eder — Bash gerektirmez).

1. Paket kökünü `${CLAUDE_PLUGIN_ROOT}` üzerinden bul.
2. Aşağıdaki komutu çalıştır (`$ARGUMENTS` kullanıcının belirttiği konu
   etiketine karşılık gelir; boşsa `preflight`):

```bash
TOPIC="$ARGUMENTS"
if [ -z "$TOPIC" ]; then TOPIC="preflight"; fi
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vekayinuvis_doctor.py" --topic "$TOPIC" --live --write-manifest
```

3. Çıktıyı özetle:
   - 17 zorunlu server satırı var mı? (çekirdek 3 · akademik 6 · tam-metin 2 ·
     yasama/mevzuat 3 · destekleyici 2 · substrat 1; `marmara` bu turda wire
     edilmedi — manifestoya dahil değil, bkz. CONNECTORS.md § 1 not.)
   - Hangi connector `hit`, hangisi `degraded`, hangisi `skipped`?
   - `devlet-arsivleri` için `devarsiv_session_status` canlı probe sonucunu bildir
     (`session alive` veya `session_required`).
   - `--live` çıktısındaki üç ek satırı oku ve raporla (§ Doctor çıktı biçimi):
     `[envanter]`, `[engines]`, `[vnc]`.
   - Eksik anahtarları secret değeri göstermeden env var adıyla bildir.

Bu skill araştırma çıktısı üretmez; belge görüntüsü, OCR/HTR veya tam metin çekmez. Yalnız
marketplace kurulumunun connector wiring / credential / G0 manifest ön-denetimini ve
`devlet-arsivleri` oturum canlılığını kontrol eder.

## Doctor çıktı biçimi — `--live` ek bölümleri (v3.0.0)

Mevcut server satırlarının altına (`--json` modunda `live_checks` dizisi olarak,
metin modunda "Canlı ek kontroller" başlığı altında) `devlet-arsivleri` üzerinden
tek bir `devarsiv_server_info` çağrısı + bir noVNC HEAD isteğiyle üretilen üç
etiketli bölüm eklenir. Yalnız `--live` bayrağıyla görünür; offline modda yoktur.

- **`[envanter]`** — `devarsiv_server_info` yanıtındaki `tools` dizisinin **6 araç
  grubunu** (arama · süpürme · belge · sepet · arşiv · OCR · durum) kapsayıp kapsamadığını
  ölçer. **Magic-number YOK** — kesin araç sayısı deploy'a göre değişir (`devarsiv_ocr_image`
  gibi eklemeler büyütür, deep_search grubu ileride ekler); ölçülen şey grup-kapsamıdır:
  - `[envanter] OK — 7/7 grup mevcut` — kapsam tam.
  - `[envanter] DRIFT: <grup> grubu yok — claude.ai connector'ını yeniden bağlayın` —
    bir grup TÜMÜYLE yoksa (ör. hiç `*_ocr_*` aracı yok); araç listesi client tarafında
    cache'lenmiş olabilir, kullanıcıya connector'ı claude.ai'da kopar/yeniden bağla uyarısı ver.
  - `[envanter] SORUN: <gerekçe>` — handshake/call başarısız (curl hatası, http
    kodu, parse hatası, yanıtta `tools` alanı yok); bu bir drift kanıtı değil,
    probe'un kendisinin çalışmadığının kanıtıdır — `devlet-arsivleri` satırının
    G0 durumunu (hit/degraded/skipped) etkilemez, ayrı bir tanı sinyalidir.
- **`[engines]`** — aynı `devarsiv_server_info` yanıtından `ocr.engines.transkribus`
  ve `ocr.engines.escriptorium` durum string'lerini olduğu gibi iki satır hâlinde
  basar (örn. `[engines] transkribus: available`, `[engines] escriptorium:
  unavailable: ...`). `ocr.engines` alanı yoksa/parse edilemezse tek satır
  `[engines] SORUN: <gerekçe>` yazılır.
- **`[vnc]`** — `https://devarsiv-vnc.cureonics.com/vnc.html` adresine (satın alma
  akışının noVNC girişi) HEAD isteği atar:
  - `302` (Cloudflare Access yönlendirmesi) → `[vnc] OK (Access-gated)`.
  - timeout / 5xx / herhangi beklenmedik kod → `[vnc] SORUN`.

Bu üç satır belge görüntüsü, OCR/HTR veya tam metin üretmez — yalnız connector
envanter-drift'i, OCR motor sağlığı ve noVNC erişilebilirliğinin dürüst, otomatik
kanıtıdır.
