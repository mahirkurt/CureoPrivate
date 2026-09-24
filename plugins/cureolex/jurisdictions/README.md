# Yargı bölgesi paketleri (cureolex 4.0)

cureolex 4.0'da iki katmana ayrıldı:

- **Çekirdek** — yargı bölgesinden bağımsız: mod iskeletleri, kapı mantığı (G0–G11), kanıt
  defteri, no-fabrication, kapsam manifestosu, bağlam ekonomisi.
- **Paket** — bir ülkeye (veya alt birime / ulusüstü yapıya) özgü her şey: norm hiyerarşisi,
  bağlayıcılar, yetenek bayrakları, legistik profil, dil profili, kurum haritası, kapı
  parametreleri, mod takma adları, altın/adversarial vakalar.

Başka bir ülkeye genişlemek çeviri işi değildir: o ülkenin paketini yazmaktır.

## Paketler

| Kod | Durum | Uzman paneli | Mod-bağımsız tavan | Not |
|---|---|---|---|---|
| `tr` | **active** | `grandfathered` | HIGH | 3.9.0 davranışının birebir tanımı. "Panelden geçti" DEMEK DEĞİLDİR. |
| `gb` | draft | not_started | LOW (CC-6, CC-8) | uk-legal wire'lı; belirli-tarih metni `ep.legislation_uk` yolundan (ölçüldü). |
| `de` | draft | not_started | LOW (CC-2, CC-4, CC-6, CC-8) | Federal düzey. gesetze-im-internet.de bu makineden erişilemedi → bayraklar temkinli. |
| `ch` | draft | not_started | LOW (CC-3, CC-4, CC-6, CC-8) | de/fr/it eşit geçerli; Fedlex'te HMG için 23 tarihli konsolide sürüm ölçüldü. |

Tavan sütunu `python3 tests/validate_packs.py` çıktısıdır; moda ve çıktı diline göre değişir
(ör. TR paketi İngilizce çıktıda CC-5 ile MODERATE'e iner).

## Dizin

```
jurisdictions/
├── _schema/
│   ├── jurisdiction_pack.schema.json     # paket sözleşmesi (JSON Schema 2020-12)
│   ├── supranational_codes.yaml          # ISO 3166 istisnaları · ORG: ad alanı · eski takma adlar
│   ├── confidence_ceiling_rules.yaml     # CC-1…CC-8 — yetenek bayrağı → güven tavanı
│   ├── legistic_rubric_families.yaml     # 12 evrensel aile + R6b K-1…K-21 eşlemesi
│   └── connector_contract.yaml           # 9 soyut bağlayıcı yeteneği · düzey A/B/C · TR eşlemesi
├── core_files.yaml                       # çekirdek dosya envanteri + ölçülmüş TR kirlenmesi
└── <kod>/
    ├── jurisdiction_pack.yaml
    └── golden_cases.yaml                 # (active paket için zorunlu)
```

## Kurallar

1. **Kod.** Ülke → ISO 3166-1 alfa-2 (`GB`, `UK` değil). Alt birim → ISO 3166-2 (`DE-BY`).
   Ulusüstü/uluslararası örgüt → `ORG:` ad alanı (`ORG:AU` = Afrika Birliği; `AU` = Avustralya).
   3.x'ten kalan `WHO` ve `UK` yalnız okuma için eski takma addır.
2. **Yetenek bayrağı = kaynağın yayımladığı VE filoda erişim yolu ölçülmüş olan.** Her bayrak
   bir `basis` taşır (şema en az 8 karakter ister). "Kaynak yayımlıyor ama getirim yolu ölçülmedi"
   → `false` (iyimser beyan yasağı). Bayrak bir tavan üretir; `confidence_label.combined_confidence`
   tavanı aşamaz.
3. **Yayım kuralı.** `active` ⇒ wire'lı S1 (`primary_legislation`, `status: wired`) bağlayıcısı
   + uzman paneli `completed` (ya da 3.x mirası için `grandfathered`) + `golden_cases`.
   Doğrulayıcı zorlar; pazarlık konusu değildir.
4. **Tam olarak bir kez.** `skills/cureolex/references/` ve `templates/` altındaki her dosya
   ya bir paketin `owned_files` listesinde ya da `core_files.yaml`'dadır — ikisinde birden değil,
   hiçbirinde yok da değil.
5. **Parça aynası.** Paketin `shards` alanı `fleet.yaml`'ın aynasıdır; tek kaynak `fleet.yaml`'dır.
6. **Legistik profil.** Aile anahtarları `legistic_rubric_families.yaml`'dan gelir. Doğrulanmamış
   kılavuz → `verified: false` + `anchor: UNVERIFIED` (G1 en fazla CONDITIONAL, CC-8). Rubrikte
   karşılığı olmayan aile → `coverage_gap: true` — uydurma kontrol eklenmez.
7. **G11.** Kanıt defteri `home_jurisdiction` taşır; farklı bölgeden gelen her kayıt
   `jurisdiction_role` beyan eder. Yabancı norm `binding` olamaz (istisna: paket
   `gate_params.G11.eu_member: true` beyan ediyorsa AB normu).

## Yeni paket eklemek

1. `<kod>/jurisdiction_pack.yaml` — `status: draft` ile başla.
2. Bayrakları birincil kaynağa karşı ölç; ölçüm tarihini `basis`'e yaz.
3. `python3 tests/validate_packs.py` — temiz olana kadar.
4. `golden_cases.yaml` — en az: mülga hüküm, uydurma resmî gazete künyesi, yanlış mahkeme
   hiyerarşisi, yargı bölgesi karışması, bağlayıcı uygunluğu.
5. `active`'e geçiş: uzman paneli + değerlendiriciler arası uyum (`inter_rater_agreement`) +
   (varsa) yerel hukuk ortağı. Bu adım koddan yapılamaz.

## Bilinen sınırlar (4.0)

- **Fiziksel ayrım yapılmadı.** TR'ye özgü dosyalar hâlâ `skills/cureolex/` altında; ayrım
  mantıksaldır (`owned_files`). Taşıma Faz 0b'dedir — yol değişikliği gerilemesi riski ölçülmeden
  yapılmadı.
- **Çekirdekte ölçülmüş TR kirlenmesi var** (`core_files.yaml`; en ağırı `references/14`, 151/1914 satır).
- **Web yüzeyleri.** claude.ai / ChatGPT'ye yalnız skill yüklendiğinde `jurisdictions/` dizini
  pakette bulunmaz; model varsayılan TR davranışıyla (3.x) çalışır ve paket-parametreli kapıları
  SKILL.md'deki TR değerleriyle uygular.
- **Kod olmayan işler ertelendi:** uzman panelleri, yerel hukuk ortakları, AKN dönüştürücü, yeni ülke
  adaptörleri, WHO GBT gösterge veri seti, DOG pilotu, lisans/vakıf yapısı.
