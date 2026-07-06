# Etkileşim Deseni Kataloğu — Mekanikler, Veri Şeması, Erişilebilirlik

> Her oyun/quiz/yarışma/flashcard türü için: ne işe yarar, hangi pedagoji
> ilkesine hizmet eder, `MODULE_DATA` segment şeması, erişilebilirlik kuralları.
> Şablon (`assets/module-template.html`) çekirdek desenleri (teach, mcq,
> flashcards, match, fillblank, brainbreak, summary) hazır içerir; gelişmiş
> desenler (order, sorting, hotspot, timeline) buradaki şemaya göre eklenir.

## Ortak segment alanları
Her segment şu temel alanları taşır:
```js
{ type, id, title, pictogram /* icon-pictogram-svg.md'den anahtar */, instructions /* kısa TR yönerge */ }
```
Her etkileşim segmenti **anında geri bildirim** (doğru/yanlış + açıklama) ve
**XP** üretir (ped İlke 3). XP varsayılan: doğru = +10, ilk denemede doğru = +5
bonus; **yanlış ceza yok** (§3 etik).

---

## 1. `teach` — Öğretim segmenti (etkileşim değil, omurga)
**Pedagoji:** Parçalama (İlke 1), ikili kodlama (İlke 7).
**Ne:** Tek kazanıma odaklı, kısa, görselli anlatım. Kaynağa sadık (SKILL.md §7).
```js
{
  type: "teach", id, title, pictogram,
  body: [ "<p>...</p>", "<ul><li>...</li></ul>" ], // sade HTML, yaş-uygun
  keyTerms: [ { term: "fotosentez", def: "bitkinin ışıkla besin üretmesi" } ],
  visual: { kind: "pictogram"|"svg", ref: "anahtar" | "<svg>...</svg>" } // opsiyonel
}
```
**Kural:** body ekran başına 4–6 kısa birimi aşmaz; aşarsa böl. Anahtar terimler
görsel işaretlenir (`<mark class="term">`). Her teach'ten sonra etkileşim gelir.

## 2. `mcq` — Çoktan seçmeli quiz / yarışma
**Pedagoji:** Geri-getirme pratiği (İlke 8), OTR (İlke 2), anında ödül (İlke 3).
```js
{
  type: "mcq", id, title, pictogram,
  questions: [
    {
      stem: "Soru metni",
      options: ["A", "B", "C", "D"],   // 3–4 seçenek
      correctIndex: 2,
      explanation: "Doğru cevabın neden doğru olduğu (kaynaktan)",
      sourceRef: "teach-segment-id"     // doğrulanabilirlik (SKILL.md §7)
    }
  ]
}
```
**Erişilebilirlik:** Seçenekler `role="radio"` benzeri buton listesi; klavyeyle
seçilebilir (Tab + Enter/Space); seçim sonrası doğru yeşil+onay ikonu, yanlış
kırmızı+ikon ve doğru olan işaretlenir; açıklama `aria-live="polite"` ile okunur.
**Yarışma varyantı:** Seri doğru (streak) sayacı; kişisel rekor; süre **opsiyonel**
(varsayılan kapalı). Ceza yok; yanlışta açıklama + devam.

## 3. `flashcards` — Aralıklı tekrar destesi
**Pedagoji:** Geri-getirme + aralıklı tekrar (İlke 8).
```js
{
  type: "flashcards", id, title, pictogram,
  cards: [ { front: "terim/soru", back: "tanım/cevap", hint: "opsiyonel ipucu" } ]
}
```
**Mekanik:** Kart çevrilir (flip); öğrenci "Biliyorum" / "Tekrar et" işaretler.
"Tekrar et" kartlar deste sonunda yeniden gösterilir (basit aralıklı tekrar:
bilinmeyen yakında, bilinen ertelenir). Tüm kartlar "biliyorum" olunca tamamlanır.
**Erişilebilirlik:** Flip butonla ve klavyeyle; kart içeriği metin (görsel değil),
ekran okuyucuya açık; renk dışı durum (ikon+metin).

> **✓ Motorda uygulandı (v1.1.0).** `renderFlashcards`: tek kart gösterilir → «Çevir»
> (ic-view) → «Biliyorum» (öğrenildi, +XP) / «Tekrar et» (ic-renew, kartı deste
> sonuna atar). Tüm kartlar öğrenilince segment biter. Her kart ustalığa sayılır.

## 4. `match` — Eşleştirme
**Pedagoji:** İlişkilendirme, OTR (İlke 2), ikili kodlama (görsel eşleştirme, İlke 7).
```js
{
  type: "match", id, title, pictogram,
  pairs: [ { a: "terim", b: "tanım" } ],   // a-b çiftleri; b'ler karıştırılır
  mode: "text"|"text-visual"               // text-visual: b tarafı piktogram olabilir
}
```
**Mekanik:** Sol sütun sabit, sağ sütun karışık; tıkla-tıkla (a seç → b seç) ya
da sürükle-bırak. Doğru eşleşme yeşil+kilitlenir; yanlış nazikçe geri döner
(ceza yok). **Erişilebilirlik:** Sürükle-bırak **dışında** tıkla-tıkla yedeği
zorunlu (klavye/dokunma erişilebilirliği); ARIA `aria-pressed`; her öğe metinli.

## 5. `fillblank` — Boşluk doldurma
**Pedagoji:** Geri-getirme, bağlamda üretim.
```js
{
  type: "fillblank", id, title, pictogram,
  items: [
    { text: "Su, ___ derecede kaynar.", answer: ["100", "yüz"], hint: "iki haneli sayı" }
  ],
  inputStyle: "type"|"choice"   // type: yazma; choice: kelime havuzundan seçme
}
```
**Mekanik:** `choice` tercih edilir (yazma yükü/dürtüsellik); kelime havuzundan
tıkla. `type` modunda cevap normalize edilir (büyük/küçük, boşluk, alternatifler).
Anında geri bildirim + ipucu butonu. **Erişilebilirlik:** Input `<label>` ile
ilişkili; choice havuzu buton listesi; ipucu `aria-live`.

## 6. `brainbreak` — Mola noktası
**Pedagoji:** Aşağı-uyarılma yönetimi, oturum-içi mola (ped §4; her ~8–10 dk).
```js
{ type: "brainbreak", id, title, pictogram, prompt: "30 saniye ayağa kalk ve omuzlarını gevşet.", durationSec: 30 }
```
**Mekanik:** Kısa hareket/nefes yönergesi; opsiyonel geri sayım; "Hazırım, devam"
butonu. Etkileşim/quiz değil; baskısız. DEHB'de **kritik** — atlanmamalı (uzun
modülde en az 1).

## 7. `checkpoint` / `summary` — Kontrol noktası ve özet
**Pedagoji:** Ustalık (mastery), öz-izleme/üstbiliş (ped §6).
```js
{
  type: "checkpoint", id, title, pictogram,
  recap: [ "kısa hatırlatma maddesi", ... ],   // kaynaktan
  mixedQuestions: [ /* mcq şemasındaki gibi karma geri-getirme */ ],
  selfAssess: ["Bunu öğrendim", "Tekrar etmeliyim"]  // öğrenci işaretler
}
```
Modül sonu **summary** ekranı motor tarafından otomatik üretilir: ulaşılan XP,
ustalık yüzdesi, rozet kasası, tekrar önerisi, öz-değerlendirme. Skor
*bilgilendirici* sunulur (etiketleyici değil); başarısızlık tekrara nazik davet.

---

## Gelişmiş desenler (şemaya göre eklenir)

## 8. `order` — Sıralama (sürükle-bırak / klavye)
**Pedagoji:** Süreç/dizi kavrayışı (tarihsel olay, deney adımı, matematik işlemi).
```js
{ type: "order", id, title, pictogram, prompt: "Olayları doğru sıraya diz", items: ["adım1", "adım2", ...] /* doğru sıra; gösterimde karışır */ }
```
> **✓ Motorda uygulandı (v1.2.0).** `renderOrder`: öğeler karışık tile listesi olarak
> gösterilir; öğrenci **sıradaki doğru** öğeyi seçer (tıkla/klavye). Doğru seçim
> yeşil + sıra numarasıyla kilitlenir (+XP); yanlışta nazik uyarı, ceza yok. Sürükle-
> bırak yerine bu "sıradakini-seç" deseni varsayılan olarak dokunma/klavye-erişilebilir.

## 9. `sorting` — Gruplama (kategori kutuları)
**Pedagoji:** Sınıflandırma (canlı/cansız, asit/baz, isim/fiil).
```js
{ type: "sorting", id, title, pictogram, prompt, bins: ["Kategori A", "Kategori B"], items: [ { label, bin: 0 } ] /* bin = doğru kategori indeksi */ }
```
> **✓ Motorda uygulandı (v1.2.0).** `renderSorting`: öğeler tek tek gösterilir; öğrenci
> öğeyi doğru **kutu** (tile) seçerek yerleştirir. Doğru → yeşil + sonraki; yanlış →
> uyarı + tekrar. Her öğe ustalığa sayılır.

## 10. `hotspot` — Etkileşimli görsel
**Pedagoji:** Görsel kavrayış, ikili kodlama (etiketli diyagram üstünde tıklama).
```js
{ type: "hotspot", id, title, svg: "<svg>...<g data-spot='cekirdek'>...</g></svg>", spots: [ { id: "cekirdek", label: "Çekirdek", info: "Hücrenin yönetim merkezi" } ] }
```
SVG `icon-pictogram-svg.md` kurallarına uygun; her hotspot klavyeyle odaklanabilir
(`tabindex`, `role="button"`, `aria-label`).

> **✓ Motorda uygulandı (v1.2.0).** `renderHotspot`: her `spot` için "Bul ve tıkla:
> {label}" sorulur; öğrenci SVG içinde `data-spot` taşıyan bölgeyi tıklar (veya Tab +
> Enter/Space). Doğru bölge yeşil çerçevelenir + `info` gösterilir (+XP); yanlışta
> nazik uyarı. Motor `[data-spot]` ögelerine otomatik `role/tabindex/aria-label` ekler.

## 11. `timeline` — Zaman çizelgesi
**Pedagoji:** Tarihsel/dizisel kavrayış.
```js
{ type: "timeline", id, title, prompt, events: [ { date, label, detail } ] }
```
> **✓ Motorda uygulandı (v1.2.0).** `renderTimeline`: dikey Carbon zaman çizelgesi —
> numaralı düğüm + `date` (mono etiket) + `label` (kalın) + `detail` (ikincil). Bir
> **display/başvuru materyalidir** (notsuz). Notlu sıralama gerekiyorsa `order` kullanın.

---

## Akış kurgu kuralları (motor)
- Segment sırası `MODULE_DATA.segments` dizisinin sırasıdır; motor sırayla sunar.
- **OTR kuralı:** İki `teach` arasında ≥1 etkileşim (mcq/match/fillblank/...).
- **Mola kuralı:** Toplam ≥6 segmentlik modülde ≥1 `brainbreak`.
- **Erken başarı:** İlk etkileşim kolay; zorluk kademeli artar.
- **Geri-getirme:** Modül sonunda `checkpoint` (karma sorular) önerilir.
- Her etkileşim XP üretir; ilerleme rayı her segment tamamında dolar.

## Genel erişilebilirlik (tüm etkileşimler)
- Klavye: Tab ile gez, Enter/Space ile etkinleştir; sürükle-bırak için daima
  klavye/tıklama yedeği.
- ARIA: durum `aria-live="polite"`; butonlar `aria-pressed`/`aria-label`.
- Durum çift-kanal: renk + ikon + metin (renk tek başına anlam taşımaz).
- Hedef ≥48px; odak halkası görünür; `prefers-reduced-motion` saygısı.
- Hiçbir etkileşim emoji kullanmaz; geri bildirim ikonu Carbon ikon setinden.
