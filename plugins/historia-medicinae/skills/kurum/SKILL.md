---
name: kurum
description: "INSTITUTIO modu — tıp kurumlarının ve mesleğin tarihi: hastane, tıp fakültesi, bîmâristân, dispanser, tımarhane, meslek örgütü, lisanslama ve diploma rejimi, hemşirelik ve ebeliğin meslekleşmesi. Kullanın: 'X hastanesinin tarihi', 'tıp fakültesi kuruluşu', 'hekimlik mesleğinin doğuşu', 'Medical Act 1858', 'Flexner Raporu', 'bimaristan', 'tabipler odası tarihi', 'diploma/lisans rejimi' sorularında."
argument-hint: "<kurum veya meslek> [dönem] [coğrafya]"
allowed-tools: Read, Glob, Grep, WebFetch, Task
disable-model-invocation: false
---

# INSTITUTIO — Kurum ve Meslekleşme Tarihi

Flagship protokolü `INSTITUTIO` moduyla çalıştır.

## Zorunlu yüklemeler

```
view ../historia-medicinae/references/quellenkritik.md
view ../historia-medicinae/references/kuresel-cerceve.md
view ../historia-medicinae/references/source-typology.md
```

## Ayrım: niyet, kuruluş, işleyiş

Üçü **ayrı kaynak** ister ve karıştırılamaz:

| Katman | Soru | Kaynak |
|---|---|---|
| **Niyet** | Devlet/vakıf ne yapmak istedi? | Nizamnâme, yasa, vakfiye, kuruluş kararı — *uygulamayı kanıtlamaz* |
| **Kuruluş** | Ne zaman, hangi kararla, hangi bütçeyle? | Yasama kaydı, resmî yayın, arşiv künyesi |
| **İşleyiş** | Fiilen ne oldu? Kim kabul edildi, kim çalıştı? | Hastane/hasta defteri, personel kaydı, denetim raporu, dönem basını |

> "Nizamnâme şunu emrediyordu" cümlesi **kurumun öyle işlediğini göstermez.** Bu ayrımın
> yapılmaması bu modun en sık hatasıdır.

## Meslekleşme ekseni

Meslekleşme bir **kapanma** sürecidir: kim hekim sayılır, kim dışarıda kalır. İzlenecek
göstergeler — lisans/diploma zorunluluğu, sicil (register), meslek örgütü tekeli, eğitim
standardı, rakip pratisyenlerin (berber-cerrah, ebe, şifacı, attar) hukuki konumu, kadınların
ve azınlıkların mesleğe girişi.

Yasama bandı burada **birincil kaynaktır**, atlanamaz:
- **Hansard** (`uk-legal`) — Medical Act 1858 müzakeresi mesleğin hukuken nasıl tanımlandığını
  zabıttan gösterir.
- **GovInfo/Congress** (`health-policy`) — ABD lisanslama ve eğitim reformu kaydı.
- **TBMM + mevzuat + Resmî Gazete** — 1219 sayılı Kanun (1928) müzakeresi; Türkiye kolu.

## Küresel çerçeve uyarısı

Bîmâristân, *xenon*, Latin *hospitale*, Hint hastane kanıtı ve modern klinik **aynı kurumun
evreleri değildir**. "Hastanenin doğuşu" tek bir soyağacı olarak anlatılmaz
(`kuresel-cerceve.md` — anti-difüzyonizm).

## Getirim planı

openalex + pubmed-epmc (`Historical Article` + kurum adı) · paper-search (kurum monografları) ·
IIIF (kuruluş belgeleri, yıllık raporlar, salnameler) · yasama bandı · openathens → annas-reader ·
Türkiye kolu (literatur/yoktez/devlet-arsivleri).

⚠️ Osmanlı kurumsal kronolojisi ve mevzuat korpusu `vekayinuvis`'te tam olarak vardır —
**tekrar üretilmez**, çağrılır (`turkiye-layer.md`).

## Çıktı

G0 manifestosu · kuruluş tarihleri çift takvimle · niyet/işleyiş ayrımı görünür.
