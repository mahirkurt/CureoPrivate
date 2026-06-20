# Cureosuite — Dış Dağıtım Bundle'ı (Tasarım)

- **Tarih:** 2026-06-20
- **Durum:** Onaylandı (uygulama planı bekliyor)
- **Sahip:** Mahir Kurt / Cureonics
- **Kaynak repo:** `mahirkurt/marketplace` (kanonik) → türetilen yeni repo: **`cureosuite`** (private)

## 1. Amaç

`bist-analyst`, `fon-uzmani` ve `rxpraxis` plugin'lerini, bağlı oldukları MCP
connector'larıyla birlikte, **yetkilendirilmiş dış kullanıcılara** dağıtılabilir
tek bir küratörlü bundle hâline getirmek. Kod public olarak **görünmemeli**;
erişim iki katmanlı yetkiyle (GitHub daveti + paylaşılan anahtar) kontrol edilmeli.

## 2. Kapsam dışı (YAGNI)

- Kişi-başı anahtar / multi-tenant key issuance (ileride; şimdilik tek anahtar).
- midas / IQVIA MIDAS / ThoughtSpot-Roche yeteneği (lisans + kişisel kimlik riski).
- `brand-ecosystem-core`, `vekayinuvis` (bu bundle'ın kapsamı yalnızca 3 plugin).
- Ödeme/abonelik, kullanım ölçümü, web portalı.

## 3. Pinlenen kararlar

| # | Karar | Seçim |
|---|---|---|
| 1 | Dağıtım şekli | Ayrı **private** GitHub marketplace deposu (`cureosuite`) |
| 2 | Kurulum yolu | GitHub **collaborator daveti** (read) → `/plugin marketplace add` |
| 3 | Gated MCP yetki modeli | **Tek paylaşılan statik Bearer** anahtarı (`CUREONICS_MCP_KEY`) |
| 4 | Repo görünürlüğü | **Private** (kod görünmez); davet = yetki katmanı 1 |
| 5 | midas | rxpraxis dış varyantından **tamamen çıkarılır** |
| 6 | Lisans | **Üç plugin de EULA** (bist-analyst dahil; MIT bırakılmaz) |

İki katmanlı yetki: **(L1)** private repoya collaborator daveti → kod erişimi;
**(L2)** out-of-band teslim edilen `CUREONICS_MCP_KEY` → gated MCP veri erişimi.

## 4. Repo yapısı

```
cureosuite/                            (yeni PRIVATE GitHub repo)
  .claude-plugin/marketplace.json      (3 plugin)
  README.md                            (içerik + hızlı kurulum)
  ACCESS.md                            (davet → kurulum → anahtar → env-var; connector tablosu)
  EULA.md                              (repo geneli kullanım şartları)
  plugins/
    bist-analyst/      (EULA · borsa public · MCP değişikliği yok)
    fon-uzmani/        (EULA · borsa public + fon-mcp gated)
    rxpraxis/          (EULA · midas/thoughtspot-roche STRIPPED → 6 connector)
  scripts/
    sync-from-canonical.sh             (kanonikten türet + lite dönüşümü uygula)
```

Kullanıcı akışı: collaborator daveti kabul → `/plugin marketplace add mahirkurt/cureosuite`
→ `/plugin install <ad>@cureosuite` → `CUREONICS_MCP_KEY`'i al + env-var ayarla → kullan.

## 5. Plugin varyantları

| Plugin | Türetme | Lisans | Bundle MCP'ler | Dönüşüm |
|---|---|---|---|---|
| **bist-analyst** | kopya | EULA | `borsa` (public) | LICENSE → EULA |
| **fon-uzmani** | kopya | EULA | `borsa` (public) + `fon-mcp` (gated) | LICENSE → EULA; `fon-mcp`'ye Bearer env-placeholder |
| **rxpraxis** (lite) | kopya + dönüşüm | EULA | `titck`, `titck-cache`, `mevzuat`, `pubmed`, `clinical-trials`, `biorxiv` | aşağıdaki strip listesi |

### 5.1 rxpraxis lite-dönüşümü (deterministik)

- `.mcp.json`'dan `midas` girdisini çıkar → 6 connector kalır.
- `skills/thoughtspot-roche/` dizinini sil.
- `commands/rxpraxis-midas.md` komutunu sil.
- `CONNECTORS.md`'den midas/ThoughtSpot satırları + fallback referanslarını çıkar.
- `shared/tool-manifest.json`'dan midas tool girdilerini çıkar.
- `skills/rxos/` orkestratör + `skills/start/` router'dan midas/thoughtspot
  yönlendirmelerini temizle (degrade değil, tam çıkarma).
- `.claude-plugin/plugin.json` `smp.source_skills`'ten `thoughtspot-roche` çıkar.
- `gated` MCP'lere (`titck`, `titck-cache`, `mevzuat`) Bearer env-placeholder ekle.

**Çıktı doğrulama:** `grep -ri "midas\|thoughtspot\|roche" plugins/rxpraxis` → 0 sonuç
(EULA/changelog tarihsel not hariç).

## 6. Yetkilendirme & anahtar (kritik bölüm)

### 6.1 Gated connector kümesi
`fon-mcp`, `titck`, `titck-cache`, `mevzuat`. (`borsa` public no-auth;
`pubmed`/`clinical-trials`/`biorxiv` kullanıcının kendi claude.com bağlantısı.)

### 6.2 Mekanizma
- Gated MCP `.mcp.json` girdilerine header eklenir:
  `"headers": { "Authorization": "Bearer ${CUREONICS_MCP_KEY}" }`.
- **Anahtar repoya yazılmaz** (git history hijyeni + rotasyon kolaylığı).
  Kullanıcı anahtarı out-of-band alır, lokalde env-var/Claude Code settings ile set eder.
- **Tek anahtar:** Tüm gated MCP'ler **aynı** Bearer'ı kabul etmeli.

### 6.3 ⚠️ Açık teknik iş kalemi (plan 1. adımı — BLOKLAYICI)
Gated Worker/Cloud Run MCP'lerinin bugün **gerçekten** Bearer gate zorunlu kıldığı
doğrulanmalı. İki alt-problem:
1. **Gate var mı?** `.mcp.json` bugün header'sız "auth-sürtünmesiz" kaydediyor →
   MCP'ler ya açık ya OAuth auto-grant olabilir. Açıksa "anahtar gate" gerçek
   koruma sağlamaz. Her gated MCP `/mcp` çağrısı **anahtarsız 401** vermeli.
2. **Tek anahtar uyumu:** `fon-mcp`, `titck`, `titck-cache`, `mevzuat` şu an
   farklı secret'lar kullanıyor olabilir (ör. `MCP_API_KEY` vs `MCP_SHARED_SECRET`).
   Tek `CUREONICS_MCP_KEY` için ya secret'lar birleştirilir ya da yeni ortak
   "suite key" her gated MCP'ye eklenir (mevcut secret'lar korunarak ek değer).

Bu adım tamamlanmadan "yetkili erişim" iddiası teknik olarak boştur.

## 7. Lisanslama
- Repo kökünde `EULA.md` + her plugin'in kendi `LICENSE` dosyası, aynı şartlar:
  kaynak-görünür-değil (private) · **yetkili kullanım** · **yeniden dağıtım yasak**
  · **garanti yok** · **"karar destek; SPK yatırım danışmanlığı / tıbbi-farma
  tavsiye değildir"** sorumluluk reddi · Cureonics IP saklıdır.
- `marketplace.json` ve `plugin.json` license alanları EULA referansına güncellenir.

## 8. Sync & drift önleme
`scripts/sync-from-canonical.sh` tek komutla deterministik üretir:
1. Kanonik `marketplace`'ten 3 plugin'i kopyalar.
2. rxpraxis'e §5.1 lite-dönüşümünü uygular.
3. Üç plugin'e EULA lisansını + gated MCP Bearer placeholder'larını yazar.
4. `cureosuite/.claude-plugin/marketplace.json`'u üretir.
Yeniden çalıştırılabilir → iki repo arası manuel drift yok.

## 9. Test / doğrulama
- **Manifest:** `plugin-validator` agent ile 3 manifest.
- **Strip teyidi:** rxpraxis'te §5.1 grep-clean (midas/thoughtspot/roche = 0).
- **Gated gate:** her gated MCP anahtarsız `tools/list` → 401; anahtarla → 200.
- **Tek anahtar:** `CUREONICS_MCP_KEY` ile 4 gated MCP'nin tümü 200.
- **Secret-leak:** repoda hiçbir Bearer/secret yok (`gitleaks` / grep).
- **E2E:** temiz ortamda davet → `marketplace add` → `install` → env key → bir komut.

## 10. Açık riskler
- **R1 (bloklayıcı):** Gated MCP'ler bugün gate zorunlu kılmıyorsa, §6.3 Worker/Cloud
  Run tarafı iş gerektirir; bu olmadan private repo + davet tek koruma katmanı kalır.
- **R2:** Private marketplace install, her dış kullanıcının GitHub hesabı + davet
  kabulü gerektirir; GitHub'sız kullanıcı bu yolla kuramaz (o durumda .mcpb fallback).
- **R3:** Tek anahtar → kişi-başı revoke yok; sızıntıda tüm anahtar döner (kabul edildi).
- **R4:** Kanonik rxpraxis güncellenince lite-dönüşüm yeniden çalıştırılmalı (sync script bunu karşılar).
