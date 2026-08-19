#!/usr/bin/env python3
"""SessionStart — filo preflight + tarihsel akıl yürütme konvansiyonları. Fail-open."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit_context, env_present, load_lock, read_payload  # noqa: E402

BANDS = {
    "academic-core": "Akademik çekirdek",
    "primary-source": "Birincil kaynak",
    "fulltext": "Tam-metin şelalesi",
    "legal-history": "Tarihsel yasama",
    "terminology": "Terminoloji",
    "epidemiology": "Epidemiyoloji",
    "turkiye": "Türkiye kolu",
    "support": "Destekleyici",
    "web": "Web (üçüncül)",
    "substrate": "Substrat",
}

CRITICAL = {
    "PUBMED_MCP_API_KEY": "MeSH K01.400 dönem-kilitli arama YAPILAMAZ (kapsam kaybı)",
    "OTTOMAN_ARCHIVES_MCP_API_KEY": "dijitalleştirilmiş birincil kaynağa programatik erişim KAPALI",
    "OPENALEX_MCP_API_KEY": "beşeri bilimler literatürü + atıf-grafı ekol haritası KAPALI",
}


def main():
    read_payload()
    lock = load_lock()
    servers = lock.get("servers", [])

    missing, present = [], []
    for s in servers:
        env = s.get("auth_env")
        if not env:
            present.append(s["name"])
        elif env_present(env):
            present.append(s["name"])
        else:
            missing.append((s["name"], env, s.get("tier", "?")))

    lines = ["[historia-medicinae] Küresel tıp tarihi araştırma protokolü aktif."]
    lines.append(
        f"Filo: {len(servers)} server — {len(present)} kullanılabilir, {len(missing)} anahtarsız."
    )

    crit = [(n, e) for n, e, _ in missing if e in CRITICAL]
    if crit:
        lines.append("KRİTİK EKSİK:")
        for name, env in crit:
            lines.append(f"  · {name} ({env}) → {CRITICAL[env]}")
        lines.append(
            "  Çözüm: oturumu `doppler run -p cureohub -c dev_personal -- claude` ile başlatın."
        )
    if missing:
        lines.append(
            "Anahtarsız katmanlar manifestoda `skipped: anahtar yok` olarak BEYAN EDİLİR "
            "(sessiz atlama G0 ihlalidir)."
        )

    lines.append(
        "KALICI BLOKLAR (anahtarla çözülmez, ölçülmüş): Library of Congress manifest 403 · "
        "NLM Digital Collections Akamai bot kapısı · Perseus/Scaife CTS ölü · HathiTrust "
        "tam-metin 403 (Bib API açık) · Europeana anahtarı sunucuda yok · BHL anahtarı yok. "
        "Bu yüzeylerden içerik UYDURULMAZ → erişim yol haritası verilir."
    )
    lines.append(
        "ÜÇ ADLANDIRILMIŞ TUZAK (her çıktıda taranır): (1) RETROSPEKTİF TANI — modern tanı "
        "etiketi varsayılan olarak KULLANILMAZ; kullanılacaksa dört kapı (gereklilik · kanıt "
        "türü · ayırıcı tanı · işaretleme) ve hipotez beyanı zorunlu. (2) PRESENTİZM — "
        "'henüz bilmiyorlardı / nihayet ulaştılar / ilkel' kalıpları yasak. (3) DİFÜZYONİZM — "
        "Avrupa-dışı gelenek 'Avrupa tıbbına giden aşama' olarak anlatılmaz."
    )
    lines.append(
        "ÖLÇÜLMÜŞ ARAÇ TUZAKLARI: `ottoman_search_iiif` sıralaması Osmanlı-öncelikli → küresel "
        "sorguda gürültü, başlık/tarih ile ele. `med-terminologies:find_equivalent` "
        "`match_score` TERS çalışır (consumption→tüberküloz hiç dönmez) → skor sıralamada "
        "KULLANILMAZ. Dijital korpusta boş sonuç YOKLUK KANITI DEĞİLDİR (ölçülmüş %30 OCR hatası)."
    )
    lines.append(
        "BAĞLAM EKONOMİSİ: ham gövde >6KB → `tarih-tarama-distilleri` (Tier 1); tek belge >30KB → "
        "`anamnesis` ingest: collection=`histmed:run:<12hex>` + doc_id `hmrun:<12hex>:<kanonik>` "
        "(ön-ek `histmed:run:` / `hmrun:`). Kapsamsız hybrid_query/graph DENY; atıf `doc_id::idx`. "
        "Ham tam-metin dökümü yok."
    )
    lines.append(
        "ÇIKTI: her substantif yanıt G0 kapsam manifestosu taşır (25 server + 3 companion + "
        "3 delegasyon satırı, `hit/empty/degraded/skipped:<gerekçe>`). Gerekçesiz skip yasak."
    )
    lines.append(
        "DELEGASYON: Osmanlıca el yazması paleografi/HTR → vekayinuvis · çağdaş klinik "
        "geçerlilik → evidentia · RELATIO çıktı-QA → sci-audit. Kurulu değilse dürüstçe beyan."
    )

    emit_context("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail-open
