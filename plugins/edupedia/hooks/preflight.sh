#!/bin/bash
# edupedia SessionStart preflight — connector kadrosunu bildirir, çözülmeyen connector
# anahtarlarını YAKALAR. Fail-open: hiçbir koşulda oturumu bloklamaz (daima exit 0).
#
# Neden anahtar kontrolü: `.mcp.json` İKİ connector'ı bir ${VAR} bearer'ıyla bağlar —
# `egitim-kaynak` → `Bearer ${EGITIM_KAYNAK_MCP_API_KEY}` (2026-07-19 keyless→keyed;
# plugin-dışı Gemini/ChatGPT standalone için anahtarlandı) ve `modul-yayin` →
# `Bearer ${EDUPEDIA_PUBLISH_TOKEN}`. Değişken çözülmezse connector KURULUR ama her
# çağrıda 401 döner — sessiz, teşhisi zor bir arıza. Bu tam olarak `egitim-kaynak`'ın
# ESKİ başına gelen hataydı; keyed'e geçince aynı arıza sınıfı GERİ DÖNDÜ, o yüzden onu
# da burada kontrol ediyoruz. Anahtar DEĞERİ asla basılmaz — yalnız varlığı.

MSG="[edupedia] Üç connector: maarif-mufredat (OTORİTE — 105 MEB ders kitabı tam metin, authless) · egitim-kaynak (tamamlayıcı OER RAG, OAuth/Bearer — 2026-07-19 keyless→keyed; display adı 'Eğitim Kaynakları') · modul-yayin (yayın, token'lı; display adı 'Modül Yayını')."

MISSING=""
[ -z "${EGITIM_KAYNAK_MCP_API_KEY}" ] && MISSING="${MISSING} EGITIM_KAYNAK_MCP_API_KEY→egitim-kaynak"
[ -z "${EDUPEDIA_PUBLISH_TOKEN}" ] && MISSING="${MISSING} EDUPEDIA_PUBLISH_TOKEN→modul-yayin"

if [ -n "${MISSING}" ]; then
  MSG="${MSG} ⚠ Süreç ortamında çözülmeyen anahtar(lar):${MISSING} → ilgili connector çağrıları 401 döner. Çözüm: oturumu 'doppler run -p cureohub -c dev_personal -- claude' ile başlat. Üretim etkilenmez; yalnız ilgili katman düşer (egitim-kaynak yoksa OER içerik-zenginleştirme atlanır → maarif-mufredat ders kitabı otoritesi yeter; modul-yayin yoksa yayın düşer — /edupedia:yayinla REST yedeği de aynı token'ı ister)."
fi

MSG="${MSG} Canlılık + Tier-2 (get_figure) kontrolü: /edupedia:durum. MCP olmadan da offline üretim çalışır (asla uydurma kaynak)."

echo "$MSG"
exit 0
