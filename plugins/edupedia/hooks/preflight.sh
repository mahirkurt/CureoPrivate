#!/bin/bash
# edupedia SessionStart preflight — connector kadrosunu bildirir, çözülmeyen yayın
# token'ını YAKALAR. Fail-open: hiçbir koşulda oturumu bloklamaz (daima exit 0).
#
# Neden token kontrolü: `.mcp.json` `modul-yayin`'ı `Bearer ${EDUPEDIA_PUBLISH_TOKEN}`
# ile bağlar. Değişken çözülmezse connector KURULUR ama her çağrıda 401 döner — sessiz,
# teşhisi zor bir arıza. `egitim-kaynak`'ın başına tam olarak bu geldi: `.mcp.json` hiç
# var olmamış bir değişkeni referans veriyordu, connector baştan beri 401 alıyordu.
# Burada erken ve yüksek sesle söylüyoruz. Token DEĞERİ asla basılmaz — yalnız varlığı.

MSG="[edupedia] Üç connector: maarif-mufredat (OTORİTE — 105 MEB ders kitabı tam metin, authless) · egitim-kaynak (tamamlayıcı OER RAG, ANAHTARSIZ) · modul-yayin (yayın, token'lı)."

if [ -z "${EDUPEDIA_PUBLISH_TOKEN}" ]; then
  MSG="${MSG} ⚠ EDUPEDIA_PUBLISH_TOKEN süreç ortamında YOK → modul-yayin çağrıları 401 döner. Çözüm: oturumu 'doppler run -p cureohub -c dev_personal -- claude' ile başlat. Üretim etkilenmez; yalnız yayın adımı düşer (/edupedia:yayinla REST yedeği de aynı token'ı ister)."
fi

MSG="${MSG} Canlılık + Tier-2 (get_figure) kontrolü: /edupedia:durum. MCP olmadan da offline üretim çalışır (asla uydurma kaynak)."

echo "$MSG"
exit 0
