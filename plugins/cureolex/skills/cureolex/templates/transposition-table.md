# Aktarım / Uyum Tablosu — ulusüstü norm → ulusal norm

**Mod:** TRANSPOSITION · **Kapılar:** G0, G1, G2, G6, G7, G10, G11 · **Paket:** ev yargı bölgesi paketi

> **Ne üretir:** bir ulusüstü normun (AB direktifi, uluslararası andlaşma, bölgesel model kanun)
> hükümlerinin ev yargı bölgesinde **nerede ve nasıl** karşılandığını madde-madde gösterir.
>
> **G11 önce gelir.** Aktarım tablosu yazmadan önce ulusüstü normun ev bölgesindeki HUKUKİ
> ROLÜ belirlenir ve kanıt defterine yazılır:
>
> | Durum | Ulusüstü normun rolü (`jurisdiction_role`) |
> |---|---|
> | Ev bölgesi AB üyesi, kaynak AB tüzüğü | `binding` (doğrudan uygulanır — aktarım tablosu gerekmez, uygulama tablosu yeter) |
> | Ev bölgesi AB üyesi, kaynak AB direktifi | `transposition_source` (bağlayıcı olan ulusal aktarım normudur) |
> | Ev bölgesi AB üyesi DEĞİL, gönüllü uyum | `comparative_benchmark` — tabloda "uyum hedefi", asla "yükümlülük" dili |
> | Onaylanmış andlaşma | `treaty_obligation` (onay durumu andlaşma bağlayıcısıyla doğrulanır) |
>
> Paketin `gate_params.G11` alanı ev bölgesinin konumunu (AB üyeliği, ikili anlaşmalar,
> alt birim ayrımı) taşır. Yanlış rol = G11 FAIL, CELEX doğrulanmış olsa bile.

---

## 0. Künye

| Alan | Değer |
|---|---|
| Kaynak norm | {{tam künye + kimlik (CELEX / ELI / andlaşma kimliği)}} — G6 ile doğrulanmış |
| Kaynak normun güncel hâli | {{konsolide sürüm tarihi; değişiklik zinciri}} (G10) |
| Ev yargı bölgesi | {{paket kodu}} · rol: {{binding / transposition_source / comparative_benchmark / treaty_obligation}} |
| Aktarım süresi | {{kaynak normdaki son tarih — yalnız binding/transposition_source için}} |
| Referans tarihi | {{ulusal normların hangi tarihteki hâliyle okunduğu}} |

## 1. Madde-madde aktarım tablosu

| Kaynak hüküm | Hükmün özü | Ulusal karşılık (künye + madde) | Norm düzeyi | Karşılama | Not |
|---|---|---|---|---|---|
| {{Md. x(y)}} | {{kısa, kaynaktan}} | {{ulusal norm + madde, yoksa "bulunamadı"}} | {{paket hiyerarşisi}} | Tam · Kısmi · Yok · Aşan (gold-plating) · Uygulanmaz | E… |

**Karşılama sözlüğü (sabit):**
- **Tam** — hükmün tüm unsurları ulusal normda var.
- **Kısmi** — unsurlardan biri eksik; eksik unsur Not sütununda adlandırılır.
- **Yok** — ulusal karşılık bulunamadı (arama kapsamı manifestoda).
- **Aşan** — ulusal norm kaynak normun gerektirdiğinden fazlasını düzenliyor (gold-plating); bilinçli politika tercihi olabilir, hata değildir — gerekçe aranır.
- **Uygulanmaz** — hüküm ev bölgesine uygulanmıyor (ör. yalnız üye devletlere yönelik kurumsal hüküm); neden yazılır.

## 2. Tanım uyumu

| Kaynak tanım | Ulusal tanım | Fark | Etki |
|---|---|---|---|

Tanım farkı, aynı kelimenin iki sistemde farklı kapsamı olmasıdır — çeviri eşdeğeri değildir. Çok dilli yargı bölgesinde (paket `languages` birden fazla `authentic: true`) her geçerli dil sürümü ayrı okunur.

## 3. Açıklar ve öneriler

| Öncelik | Kaynak hüküm | Açık | Önerilen ulusal düzenleme | Norm düzeyi | Yetki dayanağı |
|---|---|---|---|---|---|

Yetki dayanağı paketin norm hiyerarşisine göre kurulur: alt düzey normla üst düzey normun gerektirdiği bir düzenleme önerilmez (G2).

## 4. Uygunluk notu (yalnız `transposition_source`)

- Aktarım bildirim yükümlülüğü ve süresi — kaynaktan.
- İhlal/uyumsuzluk usulü — kaynaktan; bu rapor ihlal tespiti YAPMAZ.

## 5. Sınırlar

- Rol `comparative_benchmark` ise tablo başlığı "Uyum Analizi" olur ve metinde "aktarım yükümlülüğü" ifadesi KULLANILMAZ.
- Kapsam manifestosu + `confidence_label` (paket + tavan) zorunlu; insan denetimi zorunlu.
