# Bölgesel Katmanlar

Bölgesel derinlik gerektiğinde yüklenir. Bağlayıcı çerçeve: `kuresel-cerceve.md`
(anti-difüzyonizm — hiçbir gelenek başka bir geleneğin "öncülü" değildir).

Her katman: **çekirdek kaynak türleri · dikkat edilecek tuzak · bu filodaki erişim yolu**.

---

## 1. Mezopotamya ve Mısır
- **Kaynak:** çivi yazılı tıp/büyü metinleri (*Diagnostic Handbook*), Ebers ve Edwin Smith
  papirüsleri.
- **Tuzak:** "büyü mü tıp mı" ayrımı moderndir; kaynakta ayrık değildir.
- **Erişim:** ikincil literatür (OpenAlex/Scholar) birincil; dijital faksimile için IIIF taraması.

## 2. Greko-Romen
- **Kaynak:** Hippokratik külliyat, Galen, Soranus, Dioscorides.
- **Tuzak:** **külliyat tek yazar değildir**; "Hippokrat dedi ki" cümlesi çoğu kez yanlıştır.
  Galen'in külliyatının büyük kısmı Arapça tercüme yoluyla korunmuştur — aktarım zinciri
  analizin parçasıdır.
- **Erişim:** ⚠️ Perseus/Scaife CTS API'si **ölü** (ölçüldü). Çalışan yollar: Perseus Hopper
  `xmlchunk` ve GitHub `PerseusDL/canonical-greekLit` (Hipokrat `tlg0627`, Galen `tlg0057`).
  Kritik edisyon için tam-metin şelalesi.

## 3. İslâm dünyası
- **Kaynak:** Rāzī (*Kitâb al-Hâwî*), İbn Sînâ (*el-Kânûn fi't-Tıbb*), Zehrâvî (*et-Tasrîf*),
  bîmâristân vakfiyeleri, hasta/personel kayıtları.
- **Tuzak:** "altın çağ → gerileme" anlatısı difüzyonisttir. Ayrıca *tıbbü'n-nebevî* ile
  felsefî-tıbbî gelenek **ayrı** damarlardır.
- **Erişim:** IIIF (Wellcome'da zengin Arapça/Farsça tıp yazması), TDV İA
  (`ottoman_get_islam_ansiklopedisi`), tam-metin şelalesi. Osmanlı alt-katmanı →
  `turkiye-layer.md`.

## 4. Güney Asya
- **Kaynak:** *Caraka Saṃhitā*, *Suśruta Saṃhitā*, Unani metinleri, sömürge sağlık raporları.
- **Tuzak:** "Ayurveda kesintisiz 5000 yıllık bir gelenektir" iddiası büyük ölçüde **modern bir
  inşadır**; sömürge döneminde hukuki-kurumsal kategori hâline gelişi analiz nesnesidir
  (DOI 10.1080/19472498.2021.2001198). Hastane kurumu için erken Hindistan kanıtı bağımsızdır
  (DOI 10.18732/hssa70).
- **Erişim:** OpenAlex + Scholar; sömürge raporları için `uk-legal` (Hansard'da Hindistan sağlık
  tartışmaları) ve IIIF.

## 5. Doğu Asya
- **Kaynak:** *Huangdi Neijing*, *bencao* külliyatı, Song matbu tıp metinleri, Japon *kanpō*,
  Kore *Donguibogam*.
- **Tuzak:** **"Geleneksel Çin Tıbbı" (TCM) 20. yüzyıl projesidir** — kesintisiz bir gelenek
  olarak sunulması anakronizmdir. Japonya'da Meiji dönüşümü (1868+) bir "modernleşme" değil,
  bir **rejim değişikliği** olarak analiz edilir.
- **Erişim:** `health-policy:japan_elaws_search` (modern Japon mevzuatı), OpenAlex, IIIF.

## 6. Latin Batı
- **Kaynak:** Salerno *articella*, üniversite müfredatı, *consilia*, veba risaleleri, cerrah
  loncası kayıtları.
- **Tuzak:** "karanlık çağ" klişesi; üniversite tıbbı ile pratisyen/berber-cerrah ayrımı.
- **Erişim:** IIIF (Wellcome + Gallica zengin), tam-metin şelalesi.

## 7. Afrika
- **Kaynak:** yerli şifa sistemleri (sözlü gelenek + etnografik kayıt), misyoner hastane
  kayıtları, sömürge tıp servisi raporları.
- **Tuzak:** kaynakların ezici çoğunluğu **dışarıdan** üretilmiştir; yerli aktör nesne olarak
  görünür. Postkolonyal okuma zorunlu (`kuresel-cerceve.md` §5).
- **Erişim:** OpenAlex T12778 (tropikal sağlık), `uk-legal` Hansard sömürge tartışmaları,
  ikincil literatür.

## 8. Amerika
- **Kaynak:** Mezoamerika ve And şifa gelenekleri (*Badianus* el yazması), Kolomb değişimi
  literatürü, kölelik ve plantasyon tıbbı, ABD federal kaydı.
- **Tuzak:** "bakir toprak" (*virgin soil*) salgın anlatısı eleştirilmiştir; nüfus çöküşünün
  yalnız mikrobiyolojik açıklaması yetersizdir.
- **Erişim:** `health-policy` (GovInfo/Congress tarihsel ABD kaydı), IIIF, OpenAlex.

## 9. Sömürge ve tropikal tıp (enine kesen katman)
- **Tuzak:** **"tropikal tıp"ın kendisi bir sömürge kategorisidir** — nötr bir tıbbî alt-dal
  gibi ele alınamaz.
- **Erişim:** OpenAlex T12778, Hansard, misyoner/koloni arşivleri (çoğu dijitalleşmemiş →
  erişim yol haritası).

---

## Kapsama kuralı

Küresel bir iddia ileri sürülüyorsa **konuyla ilgili en az iki bölgesel katman** taranmış
olmalıdır; taranmayan ilgili katman kapsam manifestosunda **gap** olarak yazılır.
