# carbon-edupedia — Test Vakaları (evals)

Bu dizin, skill-creator metodolojisine uygun **tetikleyici + beklenen-davranış**
test vakalarını içerir (`evals.json`). Vakalar üç pozitif modu (MODULE,
CURRICULUM, GAME/QUIZ) ve bir anti-tetikleyici/disambiguation senaryosunu kapsar.

## Doğrulama

Üretilen her modül, paketteki mekanik kapı paketinden geçmelidir:

```bash
python scripts/validate_module.py <module.html>
```

Hedef: **FAIL kapıları geçer, 0 uyarı** (G-EMOJI, G-CARBON, G-A11Y,
G-INTERACT, G-SELFCONTAINED, G-CONTRAST, G-SVG, G-WELLBEING, G-VOICE, G-AUDIO,
G-CURRICULUM, G-TOKEN). Carbon token otoritesi ayrıca:

```bash
python scripts/sync_carbon_tokens.py --template <module.html>
```

ile @carbon/themes 11.75.0'a karşı denetlenir (sapma yok beklenir).

## Notlar

- `CURRICULUM` vakası **Müfredat MCP** orkestrasyonu gerektirir; bağlantı
  yoksa skill offline yola döner ve modülü yine bağımsız üretir.
- Vakalar canlı çalıştırma değil, davranış sözleşmesidir; gerçek üretim
  çıktıları `/mnt/user-data/outputs/` altında tutulur.
