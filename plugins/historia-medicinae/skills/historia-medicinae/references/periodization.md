# Periyodizasyon ve Tarihlendirme Disiplini

**DAİMA YÜKLENİR.**

---

## 1. Periyodizasyon bir araçtır, bir gerçeklik değil

"Ortaçağ tıbbı", "Rönesans tıbbı", "modern tıp" gibi dönemler **analitik araçlardır** ve büyük
ölçüde Avrupa deneyiminden türetilmiştir. Bir Çin, Hint veya İslâm bağlamına uygulandıklarında
çoğu kez **anlamsızdır** (Song hanedanı tıbbı "ortaçağ" değildir).

**Kural:** dönem adı kullanılıyorsa (a) hangi coğrafya için geçerli olduğu, (b) hangi ölçüte
göre sınırlandığı belirtilir. Bir bölge için başka bir bölgenin dönemlendirmesi kullanılmaz.

---

## 2. Çalışma dönemlendirmeleri (öneri, dogma değil)

### Avrupa/Akdeniz ekseni
| Dönem | Kabaca | Ölçüt |
|---|---|---|
| Antik yakın-doğu | ~MÖ 3000 – MÖ 500 | Çivi yazılı ve papirüs tıp metinleri |
| Klasik | ~MÖ 500 – MS 200 | Hippokratik külliyat, Galen |
| Geç antik & Bizans | 200 – 1100 | Derleyici gelenek, Oribasius, Paul of Aegina |
| Latin Batı üniversite tıbbı | 1100 – 1500 | Salerno/Montpellier/Padova, *articella* |
| Erken modern | 1500 – 1750 | Anatomik yenilenme, Paracelsusçu tartışma, matbaa |
| Klinik/hastane tıbbı | 1750 – 1870 | Paris kliniği, patolojik anatomi, istatistik |
| Laboratuvar tıbbı | 1870 – 1945 | Bakteriyoloji, deneysel fizyoloji, hastane laboratuvarı |
| Çağdaş | 1945 – | Antibiyotik, RKÇ, moleküler tıp, küresel sağlık kurumları |

### İslâm dünyası ekseni
Erken tercüme hareketi (8.–10. yy) · klasik sentez (Rāzī, İbn Sînâ, Zehrâvî; 9.–11. yy) ·
bîmâristân kurumsallaşması · geç dönem yerel gelenekler ve Osmanlı katmanı (→ `turkiye-layer.md`).

### Doğu Asya ekseni
Klasik korpus (*Huangdi Neijing*) · Song reformları ve matbu tıp · *bencao* geleneği ·
Japonya'da *kanpō* ve Meiji dönüşümü (1868+) · 20. yy'da "geleneksel Çin tıbbı"nın **kurgulanışı**
(bu bir 20. yy projesidir, kesintisiz bir gelenek değil).

### Güney Asya ekseni
Klasik Ayurveda külliyatı (*Caraka*, *Suśruta*) · Unani'nin gelişi · sömürge karşılaşması ve
"yerli tıp"ın hukuki kategori hâline gelişi · bağımsızlık sonrası kurumsallaşma.

---

## 3. Takvim ve tarihlendirme

| Sistem | Nerede | Araç/Kural |
|---|---|---|
| Miladî (Gregoryen) | Kanonik hedef | Her tarih Miladî karşılığıyla verilir |
| Jülyen | 1582 öncesi Avrupa; İngiltere **1752'ye kadar**; Rusya 1918'e kadar | Geçiş tarihi **ülkeye göre değişir** — hangi takvimde olduğu belirtilmeden tarih verilmez |
| Hicrî kamerî | İslâm dünyası | `ottoman_convert_date` / `ottoman_parse_ottoman_date` |
| Rumî / Malî | Osmanlı idarî-malî | Aynı araçlar; Miladî ile **13 gün** farkı ve yıl başı kayması |
| Çin/Japon devir adları | Doğu Asya | Hanedan + devir (*nengō*) adı korunur, Miladî eklenir |
| Seleukos, *ab urbe condita* | Antik | Dönüşüm gerekçesiyle verilir |

**Sert kural — çift tarih.** Miladî olmayan bir kaynak tarihi aktarılırken **özgün biçim +
Miladî karşılık** birlikte yazılır: `1265 (H. 1265 / M. 1848-49)`. Hicrî yıl Miladî iki yıla
yayılabilir — tek bir Miladî yıla indirgemek **veri uydurmaktır**; ay/gün bilinmiyorsa aralık
verilir.

**Jülyen tuzağı:** "14 Eylül 1752" İngiltere'de yoktur (takvim geçişinde atlanmıştır). Bir
İngiliz kaynağında 1752 öncesi tarih varsa Eski Usûl/Yeni Usûl (O.S./N.S.) belirtilir; ayrıca
yıl başı 25 Mart olduğundan Ocak–Mart tarihleri iki yıllıdır (`1719/20`).

---

## 4. Dönem-kilitli arama

Periyodizasyon yalnız yazım değil **getirim** meselesidir. PubMed'de MeSH `K01.400` ağacı
(yüzyıl tanımlayıcıları) bir sorguyu döneme kilitler; OpenAlex'te yayın yılı ≠ konu dönemi
olduğu için topic + anahtar terim birlikte kullanılır. Ayrıntı: `search-strategy.md`.
