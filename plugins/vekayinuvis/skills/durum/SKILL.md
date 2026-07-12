---
name: durum
description: Vekayinüvis tam-filo MCP durumunu ve G0 kapsam manifestosu iskeletini denetler.
disable-model-invocation: true
---

`vekayinuvis` plugin durumunu denetle. Kullanıcı isteğe bağlı bir konu etiketi
belirtebilir; belirtmezse `preflight` varsayılır.

1. Paket kökünü `${CLAUDE_PLUGIN_ROOT}` üzerinden bul.
2. Aşağıdaki komutu çalıştır (`$ARGUMENTS` kullanıcının belirttiği konu
   etiketine karşılık gelir; boşsa `preflight`):

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
   - `devarsiv_server_info` çıktısındaki `tools` uzunluğunun **22** olduğunu doğrula
     (10→22 araç genişlemesi; eksikse connector'ı claude.ai'da yeniden bağla uyarısı
     ver) ve SEPET/SATIN-ALMA, ARŞİV OKUMA, ASYNC OCR mod-map satırlarının
     (CONNECTORS.md § 7) G0 manifestosunda ayrı satır olarak yer aldığını kontrol et.
   - Eksik anahtarları secret değeri göstermeden env var adıyla bildir.

Bu skill araştırma çıktısı üretmez; belge görüntüsü, OCR/HTR veya tam metin çekmez. Yalnız
marketplace kurulumunun connector wiring / credential / G0 manifest ön-denetimini ve
`devlet-arsivleri` oturum canlılığını kontrol eder.

> **Not (ileri-referans — Task 8).** Bu skill'in doctor-çıktı **format** bölümü Task 8'de
> genişletilecektir: `scripts/vekayinuvis_doctor.py` v3'e eklenecek SEPET/SATIN-ALMA,
> ARŞİV OKUMA ve ASYNC OCR canlılık raporlama biçimleri bu bölüme işlenecektir. Şimdilik
> yukarıdaki dört maddelik özet ve mevcut G0 manifest çıktısı geçerlidir.
