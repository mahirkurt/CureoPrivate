# Arama Stratejisi — dönem-kilitli getirim

Getirim fazında yüklenir.

---

## 1. Neden serbest-metin arama yetmez

"cholera history" sorgusu üç ayrı şeyi karıştırır: (a) kolera hakkında **tarihsel** çalışma,
(b) koleranın **klinik** literatürü, (c) "history" kelimesini başka anlamda kullanan kayıtlar
(*patient history*). Tıp tarihi getirimi bu yüzden **yapısal tanımlayıcılara** dayanır.

---

## 2. PubMed — MeSH K01.400 tarih ağacı (ölçüldü)

`pubmed_lookup_mesh` ile doğrulanmış ağaç:

| Tanımlayıcı | Tree number |
|---|---|
| **History of Medicine** (D006666) | `K01.400.552` |
| History, Ancient | `K01.400.470` |
| History, Medieval | `K01.400.500` |
| History, Early Modern 1451-1600 | `K01.400.475` |
| History, Modern 1601- | `K01.400.504` |
| History, 19th Century | `K01.400.937` |
| History, 20th Century | `K01.400.968` |
| History, 21st Century | `K01.400.984` |

Ayrıca **yayın tipi**: `Historical Article` (ve `Biography`, `Portrait`, `Classical Article`).

### Kalıplar

```
# Konu + dönem kilidi
(cholera[MeSH]) AND ("History, 19th Century"[MeSH])

# Konu + tarihsel çalışma filtresi
(hospitals[MeSH]) AND (Historical Article[Publication Type])

# Kurum/kişi tarihi
("History of Medicine"[MeSH]) AND (Ottoman OR Turkey[Affiliation])
```

⚠️ **Anahtar yoksa** bu kilit kaybolur; arama serbest-metne düşer ve bu **kapsam kaybı** olarak
manifestoda beyan edilir (sessizce geçilmez).

⚠️ **PubMed tıp tarihinin tamamını kapsamaz.** Bull Hist Med, Med Hist, J Hist Med Allied Sci
indekslidir; ama *Isis*, *Osiris*, *Social History of Medicine*'ın beşeri-bilim ağırlıklı
içeriği ve **kitap bölümleri** görünmez. Bu boşluğu OpenAlex + Google Scholar kapatır.

---

## 3. OpenAlex — topic tabanlı getirim (ölçüldü)

Ölçülmüş tıp tarihi topic'leri:

| Topic ID | Ad | Eser sayısı |
|---|---|---|
| **T12324** | History of Medicine Studies | 123.520 |
| **T12990** | Medical History and Innovations | 288.100 |
| **T14475** | History of Science and Medicine | 117.643 |
| **T12778** | History of Medicine and Tropical Health | 25.224 |

Kullanım: `openalex_search_entities` ile topic filtresi + konu terimi. Kimlik belirsizliğinde
**önce** `openalex_resolve_name` (yazar/kurum adları çok anlamlıdır).

⚠️ **Yayın yılı ≠ konu dönemi.** OpenAlex'te tarih filtresi *makalenin* yayın yılını süzer,
*konunun* dönemini değil. Dönem daraltması konu terimiyle yapılır ("nineteenth-century",
"early modern", dönem adı) — filtreyle değil.

⚠️ Genel "digital humanities" / "disability history" sorguları **ölçülmüş biçimde** bilgisayar
bilimi ve edebiyat eleştirisine kayar; alan terimi eklenmeden kullanılmaz.

---

## 4. Monograf katmanı — Google Scholar / CrossRef

Tıp tarihinin taşıyıcı birimi **kitaptır**. `paper-search:search_google_scholar` ve
`search_crossref` bu katmanın tek geniş yüzeyidir.

**Yapısal kör nokta (ölçüldü):** pre-DOI monograflar hiçbir indekste çözülmez —
Rosenberg *Framing Disease* (1992), Arnold *Colonizing the Body* (1993), Porter "The Patient's
View" (1985, *Theory and Society*), Cunningham "Transforming plague" (1992, CUP bölümü).
Bunlar **bibliyografik künyeyle** atıflanır; tanımlayıcı **uydurulmaz**, `gap` olarak işaretlenir.

---

## 5. Bölgesel ve dil katmanı

| Katman | Araç | Not |
|---|---|---|
| Türkçe | `literatur` (DergiPark), `yoktez` | Osmanlı Bilimi Araştırmaları, Tıp Tarihi Araştırmaları, Lokman Hekim Dergisi — Batı indekslerinde **görünmez** |
| Coğrafi kırılım | `pubmed-epmc` `AFF:"<ülke>"` | Ulusal tıp tarihi yazımını yakalar |
| Çok dilli | OpenAlex | Başlık/abstract çok dillidir; özgün dilde terim de denenir |

**Kural:** küresel bir iddia için en az iki dil-bölge katmanı taranmış olmalıdır; yalnız
İngilizce tarama "küresel" değildir.

---

## 6. Birincil kaynak arama

Birincil kaynak için akademik arama **yetmez**; IIIF ve arşiv katmanı ayrı çalışır. Kaynak-başına
yetenek farkı ve doğru zincir: `iiif-capability-matrix.md`.

---

## 7. Arama günlüğü

Her substantif getirim için şu tutulur (OPS katmanında): sorgu metni · hedef server · dönem
kilidi · sonuç sayısı · elenme gerekçesi. Bu, "bulunamadı" ifadesini denetlenebilir kılar
(bkz. `quellenkritik.md` §6 — yokluk kanıt değildir).
