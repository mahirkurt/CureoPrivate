# Voice-First Naming — Phonetic Identity for the ASR Era

> **On-demand load.** Consumer, DTC, podcast, voice commerce, smart speaker dağıtım hedefi olan briefler için.

---

## 1. Paradigma: Ses-İlk Ekosistemin Yükselişi

2026 itibariyle:
- **Smart speaker penetrasyonu** ABD hanelerinde ~%45, global ~%28
- **Voice commerce** ABD'de $40B+ yıllık; Avustralya $8.2B; Türkiye henüz nascent ama büyüyor
- **Podcast reklam pazarı** global $4B+ (2025 Interactive Advertising Bureau)
- **TikTok/Reels/Shorts** audio-forward video dominansı (tik→ses→memory)

Bu istatistikler `brand-maker` için şu anlama gelir: İsim artık **yalnız okunmuyor**; **söyleniyor** ve **duyuluyor**. Bouba-Kiki klasiği yeterli değil; modern gereklilik ASR (Automatic Speech Recognition) fidelity'sidir.

---

## 2. ASR Temelleri — Markanın İsmini Makine Nasıl "Duyar"

Yaygın ASR modelleri: Whisper (OpenAI), Google STT, Apple Neural Engine, Amazon Transcribe, Azure Speech. Her biri **farklı bias'lar** taşır:
- Accent tolerance farklı (Whisper en iyi; Google US-accent biased)
- Homophone disambiguation farklı
- Brand name lexicon override mekanizmaları farklı (Alexa, "Pronunciation Lexicon Specification" olarak W3C standardı takip eder)

**Alexa problemi**: Amazon'un 2016 launch'unda Alexa marka ismi **insan isimleri** ile çakıştı (Alexa Chung, Alexa Bliss vb.). Amazon 2023+ bu çakışmayı wake-word training ile çözdü. Lesson: **Wake-word collision** olası isimleri test et.

### ASR Bias'ları

Marka ismi üzerinde yaygın ASR hataları:
- Ünsüz cluster yanlış transcribe edilir ("Brkng" → "Breaking" hatası)
- İlk fonem palatalize sesler ("Ş", "Ç", "Tç") Türkçe-dışı ASR'da kayıp
- Terminal schwa ("ə") İngilizcede beklenmezse hatalı
- Unusual stress pattern (accent) yanlış syllable boundary

---

## 3. Fonetik Kriterler — Klasik vs Ses-İlk

### Klasik (phonetic-laws.md'den korundu)
- Bouba-Kiki: round vs spiky fonetik
- Sound symbolism: K-X-Z tech, L-M-N premium
- Vowel-consonant akış
- Hece sayısı 2-4 ideali

### [v2.0] Ses-İlk Ek Kriterler
- **ASR transkripsiyon kesinliği**: Finalist 10 defa ASR'a gönderilse 10/10 doğru çıkar mı?
- **Homofonik rakip yokluğu**: Loomio vs Lumio vs Lumino gibi "adjacent brand" var mı?
- **Voice query retrieval optimality**: "Alexa, order [NAME]" temiz mi?
- **Podcast host telaffuz akıcılığı**: Ad-read sırasında tökezlemeye neden olur mu?

---

## 4. 5-Soru Voice-First Test

Her finalist için `asr_simulation.py` scripti aşağıdaki 5 soruyu test eder:

### Soru 1: Homofonik rakip var mı?

Metaphone / Double Metaphone encoding ile 500+ famous mark corpus'una karşı kontrol:
- "Lumio" → Metaphone "LM" → Loomio (LM) çakışıyor
- "Platelio" → Metaphone "PLTL" → çakışma yok

**Skorlama**: 0 rakip = 2 puan; 1 low-prominence = 1; 1+ high-prominence = 0

### Soru 2: Hece sayısı ≤ 3 mü?

Voice retention literature (Cialdini, Heath): Kulağın işlem kapasitesi 2–4 hece optimal. 5+ hece voice commerce'te kayıp.

- "Oat-ly" = 2 hece ✓
- "Peloton" = 3 hece ✓
- "Per-plex-i-ty" = 4 hece ⚠️ (borderline — brand'ın entity clarity'si kompanse eder)
- "Su-per-cal-i-fra-gi-lis-tic" = 8 hece ✗

### Soru 3: İlk fonem ASR-güvenli mi?

Dangerous first phonemes (ASR-biased):
- **Ş, Ç, Tç** (palatalize Türkçe sesler) — Whisper-dışı çoğu ASR bozulur
- **Th- (θ)** — non-native speakers kadar ASR için de risk
- **Q-** (clicking) — Afrika-dışı dillerde ender

Safe first phonemes:
- **L, M, N, R** — yumuşak, universal
- **K, T, P** — sert, universal
- **S, F** — fricative, ASR-güvenli

### Soru 4: Vokal-ünsüz oranı ≥ 0.45 mi?

Doğal konuşma cadence için VC ratio optimum 0.45–0.60. Çok düşük (<0.40) = cluster-heavy, ASR zor. Çok yüksek (>0.65) = baby-talk/absurd.

Örnek:
- "Oatly" = 2V/3C = 0.40 (borderline)
- "Peloton" = 3V/4C = 0.43 (OK)
- "Notion" = 3V/3C = 0.50 (ideal)
- "Lumio" = 3V/2C = 0.60 (optimal)

### Soru 5: Brand noun collocation ASR logs'unda temiz mi?

Voice commerce typical queries:
- "Buy me a [NAME]"
- "Order [NAME]"
- "Play [NAME]"
- "Show me [NAME]"

Her finalist için 4 collocation ASR test edilir; accuracy ≥ 85% gerekli.

---

## 5. Voice Commerce Specific Considerations

### 5.1 Wake-word Collision

Alexa / Hey Google / Siri / Hey Claude komutları sonrasındaki ilk kelime **hassastır**. Marka ismi bu slotla çakışmamalı.

**Yüksek risk isimler**:
- Wake-word fonetik benzeri: "Lex" (→ Alexa?), "Siri-" başlangıç, "Hey X"
- İnsan ismi yaygın: Alex, Sarah, Mike (sesli komut'ta karışıklık)

**Düşük risk**:
- Distinctive coined (Anthropic, Vercel, Perplexity)
- Tek-hece sert (Arc, Groq, X)

### 5.2 Category Default Disambiguation

"Order coffee" sorgusunda hangi marka? Voice assistant "default brand" politikası:
- Amazon Alexa → Amazon Fresh default
- Google → kullanıcı geçmişi + ticari anlaşmalar
- Apple Siri → Apple Wallet-integrated merchants

Marka ismi, kategori content'inden **silueti keskin çıkarmalı** — aksi takdirde "dietitian app" dediğimde default'a düşer.

### 5.3 Voice SEO Paradigm Shift

Text SEO keyword → voice SEO full question + conversational phrase.
- Text: "best nutrition tracker"
- Voice: "What's the best app to track my meals?"

Marka ismi voice-query'de geçmiyorsa cite edilmiyor. İsim **conversational context'e kancalanmalı**.

---

## 6. Podcast Reklam İsim Performansı

Podcast ads 2024–2026 döneminde "brand discovery channel" olarak #1:
- Host-read spots: insani, güvenilir, akılda kalıcı
- 30-sec ads content'ın %80'i marka ismi tekrarı ile

**Host read-out akıcılığı kriterleri**:
- Hece sayısı 2-3 optimal (host 8 saniyede 3× tekrar edebilir)
- Sert ünsüz başlangıç (K-, T-, P-) podcast dinleyicisi odaklanmasına yardım
- "Go to [NAME] dot com" patternde akıcı mı? → URL readability + marka ismi flow
- Sonic branding extension hazırlığı — audio logo eklenebilir mi?

**Örnek**:
- ✓ "Go to Peloton dot com"
- ✓ "Head over to Athletic Greens dot com" (borderline long but works)
- ✗ "Go to Brkng dot io" (telaffuz kesiliyor)

---

## 7. Script Çağrısı Protokolü

```bash
# Basic simulation
python /mnt/skills/user/brand-maker/scripts/asr_simulation.py "Finalist1"

# Multi-accent (us, uk, au, tr)
python /mnt/skills/user/brand-maker/scripts/asr_simulation.py --accent us,uk,au,tr "Finalist1"

# Homophone-focused deep check (500+ famous mark corpus)
python /mnt/skills/user/brand-maker/scripts/asr_simulation.py --homophone-check "Finalist1"
```

Script çıktısı Post-Digital Scorecard Eksen 3'e yazılır.

---

## 8. Örnek Vaka Analizleri

### 8.1 Spotify vs Pandora — Voice Discoverability

- **Spotify** = 3 hece, distinctive, clear ASR → voice winner
- **Pandora** = 3 hece, mitolojik, clear ASR → voice winner
- İki marka da voice-safe; ancak Spotify'ın Wall-Street-friendly profil'i Pandora'yı geride bıraktı (voice-izolle değil)

### 8.2 Peloton vs Tonal — Audio-First DTC

- **Peloton** = 3 hece, açık -on bitiş, voice-friendly, podcast-era sembol
- **Tonal** = 2 hece, açık, voice-friendly
- İki marka da excellent voice-first; farkı marketing bütçesi açtı

### 8.3 Liquid Death — Podcast Ad Pioneer

- "Liquid Death" = 3+1 hece, iki kelime, kolay ASR
- Punk aesthetic + contrarian naming + aggressive podcast advertising → 2024-2026 growth rocket
- **Ders**: Voice-first başarı = distinctive name + podcast investment + category unexpected

### 8.4 Pharma DTC — Dupixent, Skyrizi Voice Ad

- **Dupixent** (dupilumab, Sanofi/Regeneron) = "Du-pix-ent" 3 hece, çeviri-nötr
- **Skyrizi** (risankizumab, AbbVie) = "Sky-ri-zi" 3 hece, uplift ses
- İkisi de TV + podcast ads'te voice-clear; pharma DTC norm

---

## 9. Kaynaklar

- Interactive Advertising Bureau. (2025). *Digital Audio and Podcast Advertising Revenue Report*.
- W3C. (2016). *Pronunciation Lexicon Specification (PLS) v1.0*.
- Stephen Arnold Music. (2026). *Sonic Branding Trends: The Audio-First Era*.
- WellSaid Labs. (2025). *Sonic Identity Whitepaper: Voice UX for Consumer Brands*.
- Maven Marketing Australia. (2026). *Voice Commerce in AU: $8.2B Opportunity*.
- Spellbrand. (2026). *AI Naming Stack Voice Optimization*.
