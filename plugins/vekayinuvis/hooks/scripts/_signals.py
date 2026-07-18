"""Ortak arşiv-atıf sinyalleri — citation_discipline.py + stop_coverage.py paylaşır.

TASARIM KURALI (bu modülün varlık sebebi):

    Bir connector/araç/dosya ADININ geçmesi ATIF DEĞİLDİR.

Atıf, belirli bir belgeye yapılan iddiadır ve imzası somut bir KAYIT YERİ'dir: fon kodu +
kutu/gömlek numarası, çözülmüş bir BelgeGoster derin-bağlantısı, veya bir arşiv referans
kodu. Eski tetikleyiciler çıplak isim eşliyordu (`devarsiv`, `\\bgömlek\\b`, `DH\\.[A-Z]{1,4}`)
ve bu yapısal bir yanlış-pozitif üretiyordu: devlet-arsivleri MCP'sinin KENDİ KODU üzerinde
çalışmak — araç adları (`devarsiv_get_belge`), env değişkenleri (`DEVARSIV_STORE_PATH`), test
fixture'ları (`"fon": "DH.MKT"`), dosya yolları, commit mesajları — kaçınılmaz olarak hook'u
ateşliyordu. Ortada ne çift-tarih yazılacak bir tarih, ne dipnota konacak bir katalog URL'i
vardı; hook her mühendislik turunda "eksik disiplin" diye bağırıyordu.

Bir hook her turda ateşlerse herkes onu yok saymayı öğrenir — invaryantın TAMAMEN kaybı.
Az-hevesli ama doğru bir kapı, çok-hevesli ve gürültülü bir kapıdan kesinlikle iyidir.

Bu daraltma hook'un asıl işini zayıflatmaz: UYDURULMUŞ bir atıf da bir kayıt yeri taşır
(zaten onu atıf yapan şey odur) → gate'i geçer ve çift-tarih/URL/provenance denetimine girer.
Kayıt yeri OLMAYAN metin ise atıf değildir; çift-tarihlenecek tarihi, dipnotlanacak URL'i yoktur.
"""
import re

# Osmanlı Arşivi (BOA) tasnif kökleri — künye biçiminde kutu/gömlek ile birlikte aranır.
_FON = (
    r"(?:HAT|BEO|MV|ŞD|TŞR"
    r"|A\.[A-ZÇĞİÖŞÜ]{1,4}(?:\.[A-ZÇĞİÖŞÜ]{1,4})?"
    r"|DH\.[A-ZÇĞİÖŞÜ]{1,4}"
    r"|İ\.[A-ZÇĞİÖŞÜ]{2,4}"
    r"|Y\.[A-ZÇĞİÖŞÜ]{1,4}"
    r"|C\.[A-ZÇĞİÖŞÜ]{1,4}"
    r"|ML\.[A-ZÇĞİÖŞÜ]{1,4}"
    r"|MF\.[A-ZÇĞİÖŞÜ]{1,4})"
)

RECORD_LOCATORS = [
    # 1) BOA künye biçimi: fon kodu + kutu/gömlek — ör. "DH.MKT 1234/56", "BOA, İ.SH. 12/3".
    #    Bitişik \d+/\d+ şartı, şema/fixture'daki çıplak `"fon": "DH.MKT"`yi DIŞARIDA bırakır.
    re.compile(_FON + r"\.?\s*,?\s*\d+\s*/\s*\d+"),
    # 2) BCA yer bilgisi — ör. "030.10.123.45" / "030.10/123/45".
    re.compile(r"\b030\.\d{1,2}[./]\d{1,3}[./]\d{1,3}"),
    # 3) Çözülmüş katalog derin-bağlantısı. Hash/ItemId yalnız arama sonucundan gelir
    #    (uydurulamaz) → gerçek bir kayda işaret eder. Çıplak "BelgeGoster.aspx" YETMEZ.
    re.compile(r"BelgeGoster\.aspx\?[^\s\"'<>]*ItemId=\d+", re.IGNORECASE),
    # 4) Arşiv referans kodu — ör. "İ.SH.00001,00001.001".
    re.compile(r"[A-ZÇĞİÖŞÜ]{1,3}\.[A-ZÇĞİÖŞÜ]{1,4}\.\d{4,}\s*,\s*\d+\.\d+"),
    # 4b) Nokta-ayraçlı çok-parçalı BOA künyesi — ör. "HR.UHM.00048.00035", "A.MKT.MHM.0012.034".
    #     Fon(.tasnif)+ ardından ≥4-haneli kutu + gömlek. Şema konuşması ("fon.kutu.gömlek")
    #     \d{4,} şartıyla dışarıda kalır (harf-üçlüsü sayı içermez).
    re.compile(r"[A-ZÇĞİÖŞÜ]{1,4}(?:\.[A-ZÇĞİÖŞÜ]{1,4}){1,3}\.\d{4,}\.\d+"),
    # 5) Açık künye düzyazısı — "gömlek 5" / "gömlek: 5" / "gömlek no. 5". Sayı şartı,
    #    "fon/kutu/gömlek üçlüsü" gibi ŞEMA konuşmasını dışarıda bırakır.
    re.compile(r"\bgömlek\s*:?\s*(?:n[oO]\.?\s*)?\d+", re.IGNORECASE),
]


def has_record_locator(text):
    """Metin somut bir arşiv KAYDINA mı atıfta bulunuyor? (isim geçişi yeterli değil)"""
    return any(p.search(text or "") for p in RECORD_LOCATORS)
