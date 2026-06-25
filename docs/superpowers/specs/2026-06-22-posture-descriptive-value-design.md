# Tasarım: Teknik-duruşun *betimsel* değeri — `regime_study.py`

**Tarih:** 2026-06-22
**Plugin:** `bist-analyst` (BIST Uzmanı)
**Tür:** Salt-araştırma analiz aracı (skill_study / walkforward_calibrate kardeşi)
**Durum:** Onaylandı (kullanıcı), implementasyon planı bekliyor

---

## 1. Motivasyon ve bilimsel soru

Önceki kalibrasyon programı üç katmanda **getiri-öngörüsü** sorusunu kapattı:

1. `walkforward_calibrate.py` — PARAMETRE: 3/13 yenilmiyor.
2. `skill_study.py` — MUTLAK SKILL: duruş skoru ileri **getiriyi** (yön) öngörmüyor; çok-dönem (v1.1.6, K=83 bağımsız blok) kesin: ρ̄≈0, CI[−0,07,+0,11], skill yok.

Bu çalışma **farklı** bir ekseni sınar: teknik-duruş kategorilerinin **betimsel/yapısal** değeri. Getiri *yönü* değil, getirinin **karakteri**:

- **Oynaklık (vol):** Aşırı duruşlar (Güçlü Yukarı/Aşağı) ileride daha yüksek gerçekleşmiş oynaklık mı önceliyor?
- **Rejim (trend/yatay):** Yönlü duruş, ileride trendli (yüksek efficiency-ratio) mi yoksa çalkantılı/yatay bir pencere mi önceliyor?

Bu hipotezler getiri-öngörüsünden **daha savunulabilir**, çünkü oynaklık *kümelenir* (otokoreledir) ve trend/yatay karakter ısrarcıdır — getirinin yönü gibi (martingale-benzeri) değildir.

### Ana metodolojik tuzak (tasarımın çekirdek nedeni)

Oynaklık otokorele olduğundan, **kontrolsüz** bir test sahte-pozitif verir: aşırı duruş zaten YÜKSEK mevcut-vol ile ilişkilidir, yüksek mevcut-vol da yüksek ileri-vol'a otokorele olur → "duruş vol öngörür" trivially çıkar ama bu motorun değeri değil, vol'ün hafızasıdır. Bu yüzden **birincil vol testi mevcut-vol temeli kontrollü** (kısmi korelasyon): duruş, σ_t'nin ÖTESİNDE *artımlı* bilgi taşıyor mu?

---

## 2. Mimari ilkeler

- **Tek yeni dosya:** `skills/bist-analist-kopilotu/scripts/regime_study.py`.
- **Sıfır motor değişikliği:** `technical_plus.py`, `backtest_posture.py` salt-okunur tüketilir. 3/13 varsayılanı, plugin davranışı, SMP/manifest semantiği **değişmez**. (skill_study/walkforward gibi araştırma aracı.)
- **Mantık çoğaltma yok:** Skorlama `backtest_posture(slice[:t+h])` çağrılıp satırlardan `score_norm`/`posture` okunarak alınır — motor mantığı yeniden yazılmaz, sızıntısızlık (look-ahead-free) aynen korunur.
- **Kanıtlanmış istatistik makinesini yeniden kullan:** `skill_study.py`'den import — `_t_two_sided_p` (Student-t df=K−1), `_betai`/`_betacf`, `nonoverlap_times`, `_slice`, `_mean`, `_std`. Bunlar gerekiyorsa ayrı bir küçük modüle (`_stats.py`) çıkarılmaz; doğrudan `from skill_study import ...` ile alınır (mevcut import deseni: dosya-yanı sys.path fallback).
- **Bağımlılık:** yalnız Python stdlib + `skill_study` + `backtest_posture` (+ dolaylı `technical_plus`).
- **Determinist & saf:** ağ yok, rastgelelik yok (self-test sentetiği sinüs/eğim tabanlı, `_synthetic_bars` deseni).

---

## 3. Birim ve bağımsızlık

v1.1.6'nın doğrulanmış blok tasarımıyla **birebir**:

- `nonoverlap_times(frames, h, min_setup)` → anlık-zamanlar t = min_setup, min_setup+h, … (h adımlı). Ardışık blokların ileri pencereleri **çakışmaz** → bloklar bağımsız.
- Her blok t = bir **kesit** (8 isim üzerinden). Blok-içi çağdaş (cross-name) korelasyon kabul edilir — her blok bir tahmin; bağımsızlık **bloklar arası** sağlanır → Student-t df=K−1 anlamlılığı namusludur.
- `min_setup ≥ 200` önerilir (SMA200 tanımlı; motor kapsam-sınırlı değil).
- Vol/ER istatistiği için `h ≥ 5` gerekir (σ_fwd ve ER anlamlı olsun; h-bar → h−1 getiri). Varsayılan ufuklar: 5, 10, 20.

### Her (isim, blok t) için türetilen büyüklükler

| Büyüklük | Tanım | Kaynak |
|---|---|---|
| `score_norm` (işaretli) | duruş skoru ∈[−1,+1] | `backtest_posture` satırı (motor) |
| `\|score_norm\|` (aşırılık) | merkez-Nötr'den uzaklık | yukarıdakinin mutlağı |
| σ_t (mevcut vol) | bars[t−W:t] günlük log-getiri std'si, **W=20** sabit | saf fiyat (stdlib) |
| σ_fwd (ileri vol) | bars[t:t+h] günlük log-getiri std'si | saf fiyat |
| ER_fwd (ileri rejim) | \|close_{t+h}−close_t\| / Σ\|close_i−close_{i−1}\| over (t,t+h] ∈[0,1] | saf fiyat |

**Not (W=20 gerekçesi):** Mevcut-vol temeli, ileri-pencere uzunluğundan (h) bağımsız, kararlı bir ~1-aylık tahmin olsun diye sabit 20 işlem günü. Kontrol rank/regresyon üzerinden yapıldığından pencere-uzunluğu uyuşmazlığı önemli değil; tek gereken σ_t'nin t-öncesi ölçülebilir (sızıntısız) olması. Tüm log-getiriler `ln(close_i/close_{i−1})`; sıfır/negatif kapanış guard'lı atlanır.

---

## 4. Testler

### Test 1 — `vol_extreme` (BİRİNCİL, kontrollü)
Her blok t: 8 isim kesitinde **kısmi Spearman** ρ(|score_norm|, log σ_fwd | log σ_t).

Kısmi Spearman, üç ikili Spearman'dan:
```
ρ_xy·z = (ρ_xy − ρ_xz · ρ_yz) / sqrt((1 − ρ_xz²)(1 − ρ_yz²))
```
x=|score_norm|, y=log σ_fwd, z=log σ_t. Payda ~0 (|ρ_xz|→1 veya |ρ_yz|→1) ise blok atlanır (None). Geçerli kesit için ≥4 isim gerekir.

Blok kısmi-ρ listesi → `skill_study._finalize` deseniyle: ρ̄, SE=sd/√K, t=ρ̄/SE, p=Student-t(t,K−1), verdict.
**Pozitif & anlamlı ⇒ duruş aşırılığı, mevcut-vol ötesinde ileri-vol bilgisi taşır → betimsel değer doğrulanır.**

### Test 1b — `vol_asymmetry` (İKİNCİL, betimsel)
Her blok t: kısmi Spearman ρ(işaretli score_norm, log σ_fwd | log σ_t).
**Negatif ⇒ kaldıraç/asimetrik-vol etkisi** (aşağı-duruşlar daha yüksek ileri-vol önceliyor). Mean/SE/t/p raporlanır; betimsel yorum.

### Test 1c — `vol_bucket_eta2` (ÇAPRAZ-KONTROL, sağlamlık)
TÜM (isim,t) gözlemi havuzlanır, σ_t'ye göre **tercil** (3 kovan). Her kovan içinde 5 duruş seviyesi (`_POSTURE_LEVELS`) arasında log σ_fwd için **Kruskal-Wallis H** → η² = (H − k + 1)/(n − k), k=grup sayısı. Kovan-η²'leri ve KW-p raporlanır.
**p İYİMSER** (havuzlama seri/kesitsel bağımlılığı yok sayar; tıpkı `pooled_hit_p`) — açık uyarı metniyle; birincil ölçüt blok t-testidir.

### Test 2 — `regime_trend` (BİRİNCİL)
Her blok t: 8 isim kesitinde Spearman ρ(|score_norm|, ER_fwd).
Blok-ρ listesi → `_finalize` deseni (ρ̄/SE/t/p/verdict).
**Pozitif & anlamlı ⇒ aşırı yönlü duruşlar trendli (vs çalkantılı) pencere önceliyor.**

### Çoklu karşılaştırma & yorum
- İki birincil test × 3 ufuk → her birincil p için **Šidák** düzeltilmiş p de raporlanır (v1.1.6 deseni).
- Yorum etiketleri "betimsel ilişki VAR/YOK" (return-skill DEĞİL). `_finalize` verdict'i ince bir etiket-katmanıyla bu dile uyarlanır; K<4 → "yetersiz güç" kapısı korunur.
- 1b ve 1c ikincil/betimsel — Šidák ailesine girmez, ayrı sunulur.

---

## 5. Çıktı sözleşmesi

`skill_study` ile tutarlı `--json` ve insan-okunur `render()`:

```json
{
  "horizons": [
    {
      "horizon": 5,
      "vol_extreme":  {"n_blocks": K, "mean_rho":.., "se_rho":.., "t_stat":.., "p_rho":.., "p_sidak":.., "verdict":".."},
      "vol_asymmetry":{"n_blocks": K, "mean_rho":.., "se_rho":.., "t_stat":.., "p_rho":.., "verdict":".."},
      "vol_bucket_eta2": {"buckets":[{"name":"alt","eta2":..,"kw_p":..}, ...], "note":"p İYİMSER ..."},
      "regime_trend": {"n_blocks": K, "mean_rho":.., "se_rho":.., "t_stat":.., "p_rho":.., "p_sidak":.., "verdict":".."}
    }
  ],
  "basis": "EOD günlük; örtüşmeyen bloklar; sabit varsayılan (3/13)",
  "disclaimer": "karar-destek; yatırım tavsiyesi değildir"
}
```

`render()` tablo: ufuk başına vol_extreme & regime_trend satırı (ρ̄/SE/t/p/p_sidak/verdict), altında asimetri + kovan-η² özeti ve İYİMSER-p uyarısı.

CLI (skill_study aynası): `--file`, `--pool name1 name2 …`, `--names`, `--horizons` (vars. 5,10,20), `--min-setup` (vars. 200), `--json`. `--pool` çok-dönem havuzlama (per-sample kırılım + bağımsızlık uyarısı, v1.1.6 deseni).

---

## 6. Doğrulama (TDD self-test)

Argümansız çalıştırıldığında self-test çalışır, iki sentetik kontrol:

- **Pozitif kontrol:** vol ve ER, duruş-aşırılığıyla GERÇEKTEN bağlı (aşırı eğim → yüksek noise genliği + yüksek ER) üretilen frames → `vol_extreme` ve `regime_trend` pozitif/anlamlı yakalamalı.
- **Null kontrol:** duruş ile vol/ER bağsız frames → "ilişki yok" (p≥0.05).

Self-test her iki beklentiyi doğrular (ok=True/False). Bu, betiğin gerçek bir sinyali yakalayabildiğini ve gürültüde sahte-pozitif vermediğini kanıtlar — sayısal eşik yerine yön/anlamlılık beklentisi.

---

## 7. Canlı koşum & dokümantasyon

1. v1.1.6 derin setini yeniden kur: 8 BIST (GARAN, AKBNK, ISCTR, THYAO, ASELS, KCHOL, TUPRS, SISE) + XU100, ~615 günlük bar, `adjust=true`, 30-günlük günlük chunk'lar, `stitch_daily.py` ile birleştir. **Partiler ≤5 agent** (rate-limit dersi).
2. `regime_study.py --file frames_deep.json --horizons 5,10,20 --min-setup 200`.
3. Bulguyu `references/methodology.md` + `CHANGELOG.md`'ye işle (skill_study deseni); `plugin.json` + `marketplace.json` sürüm artışı **feat** (yeni araç). Motor/varsayılan bit-özdeş; `claude plugin validate --strict`.

---

## 8. Kapsam dışı (YAPILMAYACAKLAR)

- `technical_plus.py`, `backtest_posture.py`, `walkforward_calibrate.py`, `skill_study.py`'nin DAVRANIŞINI değiştirmek (skill_study'den yalnız import; gerekirse en küçük, davranış-koruyan refactor — ama tercih: dokunmadan import).
- 3/13 varsayılanını veya herhangi bir motor eşiğini değiştirmek.
- SMP manifestini / plugin-seviyesi semantiği (sürüm artışı dışında) değiştirmek.
- Getiri-öngörüsü iddiası eklemek; bu araç **betimsel**, yön-tahmini değil.
- Canlı yatırım tavsiyesi dili; tüm çıktı "karar-destek" çerçeveli kalır.

## 9. Riskler & açık namuslu uyarılar

- **8-isim kesiti** blok başına az; her blok kısmi-ρ'su gürültülü — bloklar-arası t-testi toplar, ama tek ~2,5-yıllık BIST dönemi tek piyasa-erası. Çok-dönem `--pool` ile güç artırılabilir (bağımsızlık uyarısıyla).
- **Kısmi korelasyon doğrusal-monoton** kontrol varsayar; σ_t–σ_fwd ilişkisi şiddetli doğrusal-dışıysa artık-bağımlılık kalabilir → bu yüzden 1c (kovan-stratifiye, varsayımsız) çapraz-kontrol var.
- Pozitif çıksa bile **betimsel** — "şu duruşta vol/trend olasılığı yüksek" yapısal gözlemdir, alım-satım sinyali değildir.
