# Global Disaster Check — Multi-Language False-Friend Matrix

> **On-demand load.** Brief'te 3+ hedef pazar veya non-Latin alfabe coğrafyası varsa yüklenir. Bu dosya, küresel marka isminin **8 dilde** anlamsal/kültürel "felaket" riskini değerlendirir.

---

## Felsefe

Bir marka ismi yerel pazarda **mükemmel** olabilir; ama global lansmanda **felaket** olabilir. Tarihte yüksek profilli isim felaketleri:

| Marka | Pazar | Sorun |
|---|---|---|
| **Chevrolet Nova** | İspanyolca pazarlar | "no va" = "yürümez/çalışmaz" (mit, sınırlı kanıt; ama brand'in temkinli olmaması gerektiğine sıkça örnek verilir) |
| **Mitsubishi Pajero** | İspanyolca | "Pajero" → İspanyolca argo "mastürbasyon yapan" → adı *Montero* olarak değiştirildi |
| **Ford Pinto** | Brezilya Portekizcesi | "Pinto" → Brezilya argosu "küçük penis" |
| **Coca-Cola (1927 Çin lansmanı)** | Mandarin | Bazı bölgelerde "kekoukela" (蝌蚪啃蜡) → "balmumu yiyen iribaş" tercüme edildi → *kěkǒukělè* (可口可乐 - "lezzet ve neşe") olarak resmi karakterler atandı |
| **Vicks (öksürük damlası)** | Almanca | "Vicks" → Almanca'da "ficken" (sik-) telaffuzunu çağrıştırır → *Wick* olarak değiştirildi |
| **IKEA "Gosa Raps"** | İngilizce | Çocuk yastığı isim İngilizce dinleyen kulağa "tecavüz et" (rape) çağrıştırdı |
| **Schweppes Tonic Water** | İtalyanca (Milano) | Erken çevirilerde "Schweppes Toilet Water" — düzeltildi ama hatıra kaldı |
| **Honda Fitta** | İskandinav | "Fitta" → İsveç/Norveç argo "vajina" → *Honda Jazz* olarak global pazara |
| **Nokia Lumia** | İspanyolca | "Lumia" → İspanyolca argo "fahişe" çağrıştırdı (sınırlı bölgesel) |

**Sonuç**: Disaster check **opsiyonel değildir**. Bir markanın sıfırdan rebrand'i 50M+ USD'a mal olabilir.

---

## 8-Dilli Disaster Check Protokolü

Bu skill her finalist ismi aşağıdaki **8 dilde** kontrol eder. Diller, küresel pazar erişiminin **%80'ini kapsayan** stratejik seçimdir:

| Dil | Dünya Konuşan Sayısı | Coğrafya |
|---|---|---|
| English | 1.5B | Global lingua franca |
| Mandarin | 1.1B | Çin + diaspora |
| Hindi | 600M | Hindistan + güney Asya |
| Spanish | 560M | İspanya + Latin Amerika |
| Arabic | 400M | MENA bölgesi |
| French | 280M | Fransa + Frankofon Afrika |
| Russian | 260M | Rusya + Eski Sovyet |
| German | 130M | DACH bölgesi |
| Turkish | 90M | Türkiye + diaspora (Mahir spesifik talep ettiği için 9. dil olarak eklendi) |

### Check Kategorileri

Her isim 5 kategoride taranır:

#### Kategori 1: Küfür / Argo
İsim hedef dilde **küfür, müstehcen argo veya cinsel referans** içeriyor mu?

#### Kategori 2: Tabu / Kültürel Yasak
İsim **dini/politik/etnik tabu** içeriyor mu? (Örn: Hindistan'da "Beef-X" → tabu)

#### Kategori 3: Olumsuz Çağrışım
İsim **trajik, ölüm, hastalık, başarısızlık** çağrıştırıyor mu? (Örn: Çin'de "4" sayısı → ölüm; Japonya'da "shi" hecesi → ölüm)

#### Kategori 4: Önceden Var Olan Anlam
İsim hedef dilde **zaten kategori-jenerik bir kelime** mi? (Örn: "Apple" Çince'de "苹果" generic → marka olarak kayıt sorun değil ama farklılaşma zor)

#### Kategori 5: Telaffuz Felaketi
İsim hedef dilde **telaffuz edilemez** veya **gülünç bir karşılık** mı çıkarıyor? (Örn: İngilizce "Bimbo" Meksika'da büyük gıda markası ama ABD pazarında "aptal sarışın")

---

## Dil-Bazlı Hızlı Risk Profilleri

### English (EN) — Önemli Tetikleyiciler
**Yasak/argo kelimeler içeren** isimler kabul edilemez. İngilizce'nin global etkisi nedeniyle başka dilde temiz olsa bile **İngilizce check öncelikli**.

Sık görülen tuzaklar:
- "ass", "butt", "tit", "cock", "fanny" (UK argo "vajina")
- "screw" (taciz çağrışımı), "blow" (oral çağrışım), "dick"
- Test: Aday isim "WRD" gibi 3-harfli ünsüz yığını ise bir tarama yapın — *Crap, Damn, Fart, Hell* tipi içermesin

### Mandarin (ZH) — En Kritik Pazar
Mandarin **ton-tabanlı**dır. Aynı romanizasyon farklı tonlarda farklı anlam taşır. Ek olarak **karakter seçimi** ayrı bir disiplindir.

**Tehlikeli sesler**:
- "shi" (ş-i tonsuz) → "ölüm" (死) ile çakışır
- "si" (s-i tonsuz) → "ölüm" (死) çakışır
- "4" (sì) → ölüm tabu, ürün/firma adlarında kaçınılır
- Sesli +R (er-) → bazı bölgesel argolar

**Test**: Romanizasyon yaparak Mandarin sözlüğünde tarama (aşağıdaki script `disaster_checker.py` heuristic seviyede yapar).

### Hindi (HI)
**Tehlikeli sesler**:
- "bhen" / "bhain" → küfür çağrışımı (kız kardeş + cinsel)
- "lund" → küfür ("penis")
- "bhag" / "bhaag" → "kaç" — agresif tonlar

**Pozitif çağrışımlar**:
- "Om" / "Aum" başlangıçlı isimler — kutsal ses
- "Shri" başlangıcı → saygı

### Spanish (ES)
**Tehlikeli sesler**:
- "cojer/coger" → İspanya'da "almak", LatAm'de "becermek (vulgar)"
- "polla" → İspanya'da küfür "penis"
- "concha" → Arjantin/Uruguay'da "vajina (vulgar)" — ama İspanya'da "deniz kabuğu" (markada Concha y Toro şarap kullanır)
- "puta" — yaygın küfür "fahişe"
- "no va" sonu → "yürümez/çalışmaz"
- "fitta" — İsveç-İspanyol overlap, vulgar

**Pozitif çağrışımlar**:
- -o, -a sonları → doğal İspanyolca akış
- "Vista", "Bella", "Sol" — pozitif arketip kelimeler

### Arabic (AR)
Arapça **kök-örüntü morfolojisi**dir. Her 3-ünsüz kök bir anlam ailesi oluşturur. Felaket riskleri:

**Tehlikeli kökler**:
- "khara" / "kara" → "dışkı" — domain çağrışımı
- "zubb" → vulgar "penis"
- "kus" → vulgar "vajina" (Mısır lehçesi)

**Pozitif çağrışımlar**:
- "Nour" (نور) → ışık
- "Salam" → barış
- "Hayat" → hayat (Türkçe ile ortak)

**Önemli**: Sağdan sola yazıldığı için **logo tasarımına dikkat** (kapsam dışı ama trademark notu).

### French (FR)
**Tehlikeli sesler**:
- "con" → vulgar "vajina" / "aptal"
- "merde" → "boktan"
- "putain" → küfür

**Pozitif çağrışımlar**:
- "Belle", "Lumière", "Étoile" — premium çağrışımlar
- -elle, -ique sonları premium hisset­tirir

### Russian (RU)
**Tehlikeli sesler**:
- "блядь" (bliad) — küfür
- "пизда" (pizda) — küfür
- Türkçe "huy" → Rusça "хуй" (xuy) → küfür "penis"

**Önemli**: Rusça **Kiril alfabesi** kullandığı için Latin marka harf-bazlı transliterasyon eder. "Versace" → "Версаче" gibi yazılır; ses uyumu kritik.

### German (DE)
**Tehlikeli sesler**:
- "Fick" / "ficken" → vulgar
- "Mist" → "gübre/saçma" — aslında nispeten yumuşak ama markada negatif
- "Gift" → İngilizce "hediye" değil, Almanca'da **"zehir"**
- "Vicks" → "ficken" çağrışımı (gerçek tarih)

**Pozitif çağrışımlar**:
- "Werk", "Bau", "Kraft" — endüstriyel güç
- "Stern" → yıldız

### Turkish (TR)
**Tehlikeli sesler**:
- "amk" / -am sonları → küfür kısaltma çağrışımı
- "bok" → "dışkı"
- "gött" / "got" sonları → vulgar
- "siktir" — açık küfür
- "sik" hecesi içerme — agresif

**Pozitif çağrışımlar**:
- "Ay", "Sun", "Yıldız" → gök cisimleri
- "Su", "Deniz" → su elementleri

**Türkçe karakter yasağı (skill kuralı)**: Global isimde **ş, ğ, ç, ü, ö, ı** kullanılamaz. Bu skill'in sert kuralıdır.

---

## Disaster Check İş Akışı

Her finalist için aşağıdaki adımları uygulayın:

### Adım 1: Otomatik Tarama (script)
```bash
python /home/claude/brand-maker/scripts/disaster_checker.py "AdayIsim1" "AdayIsim2" "AdayIsim3"
```

Script aşağıdaki kontrolleri yapar:
- 8 dilde küfür/argo blocklist taraması
- Sayısal tabu kontrolü (Çince 4, Japonca 9)
- Telaffuz transliterasyonu heuristic
- "False friend" benzerliği (Levenshtein <2)

### Adım 2: Manuel Çapraz Kontrol
Script **heuristic** çalışır; sıfır false-positive değildir. Şüpheli sonuç çıkan adaylar için:
- [Google Translate](https://translate.google.com) — anlam çevirisi
- [Forvo](https://forvo.com) — yerel telaffuz örneği
- [Reverso Context](https://context.reverso.net) — bağlam içinde kullanım

### Adım 3: Yerel Uzman Doğrulaması (kritik pazarlar)
Mandarin, Arapça, Hindi, Japonca için **yerel native speaker doğrulaması** zorunludur. Skill bu doğrulamayı yapamaz; rapora **explicit yönlendirme yazın**:

> *"Bu ismin Mandarin ve Arapça pazarlarda lansmanı öncesi yerel dilbilimci doğrulaması zorunludur. Önerimiz: [Labbrand](https://www.labbrand.com) (Şanghay merkezli naming danışmanlığı), [Mubaloo](https://mubaloo.com) (MENA bölgesi)."*

---

## Disaster Check Sonuç Kategorileri

| Kategori | Anlam | Eylem |
|---|---|---|
| **GREEN** | 8 dilde temiz | Finalist için tam onay |
| **YELLOW** | 1 dilde yumuşak çağrışım (örn. nadir lehçe argosu) | Finalist olarak sunulabilir, raporda not |
| **ORANGE** | 1 dilde ciddi çağrışım veya 2+ dilde yumuşak | Tartışmalı; alternatif öner |
| **RED** | 1 dilde küfür/tabu çağrışım | **Eleyin** |

---

## Sayısal Tabu Hızlı Tablo

Bazı kültürlerde sayılar tabudur. Marka isminde sayı kullanılıyorsa kontrol et:

| Sayı | Tabu Kültür | Sebep |
|---|---|---|
| **4** | Çin, Japonya, Kore | "ölüm" ile homofon (sì 死, shi 死) |
| **13** | Batı | Hristiyan geleneği — Last Supper |
| **666** | Hristiyan dünya | "Number of the Beast" — Apocalypse |
| **9** | Japonya | "ku" → "kötü" / "ızdırap" çağrışımı |
| **0** | (Genel olarak nötr) | Ama "sıfırdan başlamak" çağrışımı |

**Pozitif sayılar**:
- **8** — Çin'de "zenginlik" (bā 八 ile fā 发 homofon)
- **7** — Batıda "şanslı"
- **3** — Hristiyan teslis, Hindu trimurti — kutsal evrensel

---

## Ek Kaynaklar (manuel doğrulama için)

| Kaynak | URL | Kullanım |
|---|---|---|
| Forvo (telaffuz) | https://forvo.com | Yerel native telaffuz |
| Google Translate | https://translate.google.com | Anlam çevirisi |
| Reverso Context | https://context.reverso.net | Bağlamsal kullanım |
| WIPO Global Brand Database | https://www3.wipo.int/branddb | Trademark çakışma + benzerlik |
| Wiktionary | https://www.wiktionary.org | Çoklu dil etimolojik analiz |
| Linguee | https://www.linguee.com | Profesyonel çeviri korpusu |

---

## Skill Disiplini Özeti

1. Her finalist için **8-dilli check zorunlu**
2. Script **otomatik first-pass**; manuel doğrulama **şart** kritik pazarlarda
3. **GREEN/YELLOW** finalist için yeterli; **ORANGE/RED** elenir
4. Mandarin/Arabic için yerel uzman tavsiyesi **rapora yazılır**
5. Sayısal isim önerirken tabular kontrol et
