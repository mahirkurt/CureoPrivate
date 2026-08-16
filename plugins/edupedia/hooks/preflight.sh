#!/bin/bash
# edupedia SessionStart preflight — connector kadrosunu bildirir, çözülmeyen connector
# anahtarlarını YAKALAR. Fail-open: hiçbir koşulda oturumu bloklamaz (daima exit 0).
#
# Neden anahtar kontrolü: `.mcp.json` İKİ connector'ı bir ${VAR} bearer'ıyla bağlar —
# `maarif-mufredat` → `Bearer ${MUFREDAT_MCP_API_KEY}` ve
# `egitim-kaynak` → `Bearer ${EGITIM_KAYNAK_MCP_API_KEY}`. Değişken çözülmezse connector
# KURULUR ama her çağrıda 401 döner. Anahtar DEĞERİ asla basılmaz — yalnız varlığı.

MSG="[edupedia] İki connector: maarif-mufredat (OTORİTE — 105 MEB ders kitabı tam metin; Bearer) · egitim-kaynak (tamamlayıcı OER RAG, OAuth/Bearer; display adı 'Eğitim Kaynakları'). Plugin yayınlamaz; teslim yerel HTML."

MISSING=""
[ -z "${MUFREDAT_MCP_API_KEY}" ] && MISSING="${MISSING} MUFREDAT_MCP_API_KEY→maarif-mufredat"
[ -z "${EGITIM_KAYNAK_MCP_API_KEY}" ] && MISSING="${MISSING} EGITIM_KAYNAK_MCP_API_KEY→egitim-kaynak"

if [ -n "${MISSING}" ]; then
  MSG="${MSG} ⚠ Süreç ortamında çözülmeyen anahtar(lar):${MISSING} → ilgili connector çağrıları 401 döner. Çözüm: oturumu 'doppler run -p cureohub -c dev_personal -- claude' ile başlat. Üretim etkilenmez; yalnız ilgili katman düşer (egitim-kaynak yoksa OER içerik-zenginleştirme atlanır → maarif-mufredat ders kitabı otoritesi yeter)."
fi

MSG="${MSG} Canlılık + Tier-2 (get_figure) kontrolü: /edupedia:durum. MCP olmadan da offline üretim çalışır (asla uydurma kaynak)."

echo "$MSG"
exit 0
