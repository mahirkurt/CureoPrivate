---
description: Vekayinüvis tam-filo MCP durumunu ve G0 kapsam manifestosu iskeletini denetler.
argument-hint: "[opsiyonel konu etiketi]"
allowed-tools: ["Bash"]
---

`vekayinuvis` plugin durumunu denetle.

1. Paket kökünü `${CLAUDE_PLUGIN_ROOT}` üzerinden bul.
2. Aşağıdaki komutu çalıştır:

```bash
TOPIC="$ARGUMENTS"
if [ -z "$TOPIC" ]; then TOPIC="preflight"; fi
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/vekayinuvis_doctor.py" --topic "$TOPIC" --live --write-manifest
```

3. Çıktıyı özetle:
   - 13 zorunlu server satırı var mı?
   - Hangi connector `hit`, hangisi `degraded`, hangisi `skipped`?
   - `devlet-arsivleri` için `devarsiv_session_status` canlı probe sonucunu bildir
     (`session alive` veya `session_required`).
   - Eksik anahtarları secret değeri göstermeden env var adıyla bildir.

Bu komut araştırma çıktısı üretmez; belge görüntüsü, OCR/HTR veya tam metin çekmez. Yalnız
marketplace kurulumunun connector wiring / credential / G0 manifest ön-denetimini ve
`devlet-arsivleri` oturum canlılığını kontrol eder.
