# Zulüm Tarihini Yazmanın Etiği

**ETHICA modunda yüklenmesi ZORUNLUDUR.**

---

## 0. Neden ayrı bir dosya

Tıbbî zulüm tarihi (insan deneyleri, öjeni, sömürge tıbbı, zorla kısırlaştırma) yalnız bir konu
değil, **kendi yazım normları olan** bir alandır. Bu normlar alanın kendi literatüründe
kodlanmıştır ve burada uydurulmaz.

---

## 1. Kurban-merkezli anlatı — olumlu norm

1990'lar sonrası Nazi tıbbı çalışmalarının kabul gören çerçevesi **fail-merkezli anlatıdan
kurban-merkezli anlatıya** geçiştir: zorla araştırmaya tabi tutulan bireylerin sistematik olarak
**kimliklendirilmesi ve adlandırılması** (Weindling et al. 2016, *Endeavour*, PMID 26749461,
DOI 10.1016/j.endeavour.2015.10.005).

**Bu bir yazım talimatıdır:**
- Bilinen kurban adları **anılır**; anonim toplu ifadeye ("denekler") indirgenmez.
- Fail hekimin adı, eseri ve kariyeri anlatının **merkezi** yapılmaz; failin bilimsel "başarısı"
  övgüyle aktarılmaz.
- Sayı verildiğinde kaynağı ve kapsamı yazılır; yuvarlanmış "binlerce" ifadesi tek başına kalmaz.

---

## 2. İnsan kalıntıları — adlandırılmış protokol

Holokost kökenli insan kalıntıları ve bunlardan türetilmiş materyaller için **kodlanmış,
aktarılabilir bir protokol** vardır: **Viyana Protokolü**. Protokol, benzeşim yoluyla başka
bağlamlara (ör. Afrikalı-Amerikalı biyoarkeolojik koleksiyonlar) genişletilmektedir
(Hildebrandt 2025, *Am J Biol Anthropol*, PMID 38441252, DOI 10.1002/ajpa.24918).

**Kural:** insan kalıntısı, preparat veya bunlardan üretilmiş görüntü söz konusuysa protokol
**adıyla** anılır ve uygulanır; doğaçlama ilke üretilmez.

---

## 3. "Lekeli veri" — ÇÖZÜLMEMİŞ tartışma

Etik ihlalle üretilmiş verinin (Nazi deneyleri, Birim 731, Pernkopf atlası) kullanılıp
kullanılamayacağı literatürde **açıkça uyuşmazlık hâlindedir** — tam kullanmama tezinden,
ifşa koşuluyla koşullu kullanıma kadar:

- Post 1991, *J Med Ethics* (PMID 2033631) — "The echo of Nuremberg: Nazi data and ethics"
- Moe 1984, *Hastings Cent Rep* (PMID 6392198)
- Yee et al. 2019, *Surgery* (PMID 30224084) — Pernkopf atlası
- Farahani & Janhonen 2024, *Med Health Care Philos* (PMID 38842746)

> **Bu plugin tartışmayı ÇÖZMEZ.** Çözmek, var olmayan bir etik uzlaşıyı uydurmak olurdu.
> Yapılacak: pozisyonları taraflarıyla sunmak + **ifşa yükümlülüğünü uygulamak** — verinin
> kökeni her kullanımda açıkça belirtilir.

---

## 4. Metafor disiplini — Tuskegee örneği

Tuskegee'nin tarihyazımı **kendisi bir metodoloji nesnesi** hâline gelmiştir: belgelenmiş
çalışma ile "metafor olarak Tuskegee" ayrı şeylerdir ve metaforik kullanım hem tarihi hem de
bugünkü güven araştırmasını çarpıtır.

- Fairchild & Bayer 1999, *Science* (PMID 10357678) — "Uses and abuses of Tuskegee"
- Gamble 1997, *Am J Public Health* (PMID 9366634) — "Under the shadow of Tuskegee"
- Reverby 2001, *Postgrad Med J* (PMID 11524509)

**Kural:** kaydın **belgelediği** ile vakanın **sembolize ettiği** ayrı paragraflarda yazılır.
Yaygın hatalar (ör. deneklere kasten bulaştırıldığı iddiası) tekrarlanmadan önce birincil
kaynağa karşı denetlenir.

---

## 5. Normatif soyağacı — doğrulanabilir uçlar

ETHICA modunda normların tarihi anlatılırken zincir **doğrulanabilir belgelere** bağlanır:

| Norm | Doğrulama yolu |
|---|---|
| Nürnberg Kodu (1947) | Duruşma kaydı; birincil metin |
| Helsinki Bildirgesi (1964→) | Sürüm sürüm; hangi revizyonun konuşulduğu **belirtilir** |
| Belmont Raporu (1979) | ABD federal kaydı → `health-policy` (GovInfo) |
| Oviedo Sözleşmesi (CETS 164) | `intl-treaty:coe_treaty_signatories` — ⚠️ küratörlü snapshot, `mcp_verified:false`, `snapshot_age_days` yazılır |
| MEDICRIME (CETS 211) | aynı |
| Ulusal düzenlemeler | `health-policy` (ABD/JP/AU…), `mevzuat`/`tbmm` (TR) |

**Sert kural:** "Helsinki Bildirgesi der ki…" cümlesi **hangi revizyon** olduğu yazılmadan
kurulmaz; metin 1964'ten bu yana defalarca değişmiştir.

---

## 6. Yazım kontrol listesi (ETHICA çıktısı finalize edilmeden önce)

- [ ] Kurbanlar adlandırılabildiği yerde adlandırıldı mı; anonim yığına indirgenmedi mi?
- [ ] Failin "bilimsel katkısı" övgüyle aktarılmadı mı?
- [ ] İnsan kalıntısı/preparat varsa Viyana Protokolü anıldı mı?
- [ ] Lekeli veri kullanıldıysa kökeni ifşa edildi ve tartışma **çözülmemiş** olarak sunuldu mu?
- [ ] Belge ↔ metafor ayrımı yapıldı mı?
- [ ] Norm atıflarında **sürüm/revizyon** belirtildi mi?
- [ ] Kimliklenmiş bir topluluk etkileniyorsa bu, gövdede açıkça yazıldı mı?
- [ ] Sansasyonel dil (grafik ayrıntının gereksiz teşhiri) elendi mi?
