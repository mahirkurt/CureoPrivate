---
name: etik
description: "ETHICA modu — tıp etiğinin tarihi ve tıbbî zulmün kaydı: insan deneyleri, Nazi tıbbı, Birim 731, Tuskegee, öjeni ve zorla kısırlaştırma, sömürge tıbbî deneyleri, rıza kavramının doğuşu, Nürnberg Kodu → Helsinki → Belmont → Oviedo soyağacı. Kurban-merkezli anlatı ZORUNLU. Kullanın: 'Nürnberg Kodu', 'Tuskegee', 'Nazi tıbbı', 'insan deneyleri tarihi', 'öjeni tarihi', 'aydınlatılmış onam tarihi', 'sömürge tıbbı etiği', 'lekeli veri' sorularında."
argument-hint: "<vaka veya norm> [dönem] [coğrafya]"
allowed-tools: Read, Glob, Grep, WebFetch, Task
disable-model-invocation: false
---

# ETHICA — Etik ve Karanlık Bölümler

Flagship protokolü `ETHICA` moduyla çalıştır.

## Zorunlu yükleme

```
view ../historia-medicinae/references/ethics-of-atrocity.md    # ZORUNLU
view ../historia-medicinae/references/quellenkritik.md
view ../historia-medicinae/references/kuresel-cerceve.md
```

## Dört bağlayıcı norm

1. **Kurban-merkezli anlatı.** Bilinen kurbanlar **adlandırılır**; "denekler" diye anonim yığına
   indirgenmez. Failin bilimsel "katkısı" övgüyle aktarılmaz. Bu, 1990'lar sonrası alanın kabul
   gören çerçevesidir (Weindling et al. 2016, *Endeavour*, PMID 26749461).
2. **İnsan kalıntıları → Viyana Protokolü.** Holokost kökenli kalıntı/preparat/görüntü söz
   konusuysa protokol **adıyla** anılır ve uygulanır; doğaçlama ilke üretilmez
   (Hildebrandt 2025, *Am J Biol Anthropol*, PMID 38441252).
3. **Lekeli veri tartışması ÇÖZÜLMEZ.** Etik ihlalle üretilmiş verinin kullanımı literatürde
   açıkça uyuşmazlık hâlindedir (Post 1991 PMID 2033631; Moe 1984 PMID 6392198; Yee 2019
   PMID 30224084; Farahani & Janhonen 2024 PMID 38842746). Pozisyonlar **taraflarıyla** sunulur
   ve **ifşa yükümlülüğü** uygulanır: kökeni her kullanımda yazılır. Uzlaşı **uydurulmaz**.
4. **Metafor disiplini.** Vakanın **belgelediği** ile **sembolize ettiği** ayrı paragraflarda
   yazılır (Tuskegee: Fairchild & Bayer 1999 PMID 10357678; Gamble 1997 PMID 9366634;
   Reverby 2001 PMID 11524509). Yaygın hatalar birincil kaynağa karşı denetlenir.

## Normatif soyağacı — doğrulanabilir uçlarla

Nürnberg Kodu (1947) → Helsinki (1964→, **revizyon belirtilir**) → Belmont (1979,
`health-policy`/GovInfo) → Oviedo CETS 164 ve MEDICRIME CETS 211 (`intl-treaty`; ⚠️ küratörlü
snapshot, `mcp_verified:false` + `snapshot_age_days` yazılır) → ulusal düzenlemeler.

> "Helsinki der ki…" cümlesi **hangi revizyon** olduğu yazılmadan kurulmaz.

## Sömürge boyutu

Sömürge tıbbî deneyleri anlatılırken postkolonyal kontrol sorusu uygulanır: *fail kim, nesne
kim?* Yerli aktörler yalnız kurban olarak mı görünüyor (`kuresel-cerceve.md` §5)?

## Getirim planı

openalex + pubmed-epmc (`Historical Article` + Bioethics MeSH) · paper-search (monograflar) ·
`intl-treaty` (norm metinleri) · `health-policy` (ABD federal kaydı, komisyon raporları) ·
`uk-legal` (Hansard) · openathens → annas-reader · Türkiye kolu.

## Finalize kontrol listesi

`ethics-of-atrocity.md` §6'daki sekiz maddelik liste **çıktı öncesi** işletilir.

## Çıktı

G0 manifestosu · kurbanlar adlandırıldı mı beyanı · lekeli veri kullanıldıysa köken ifşası ·
norm atıflarında sürüm.
