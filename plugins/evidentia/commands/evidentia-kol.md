---
description: KOL (Key Opinion Leader) haritalama koşumu. Bir terapötik alan/molekül için OpenAlex→Semantic Scholar→EuropePMC yazar taraması, ABD PI doğrulaması (NPI), Türk akademisyen katmanı (YÖK Akademik) ile ortak-yazar ağı + etki sıralaması üretir. medical-research §8 KOL Haritası protokolü.
argument-hint: <terapötik alan / molekül / endikasyon>
---

# /evidentia-kol — KOL Haritası

Alan/molekül: **$ARGUMENTS**

`medical-research` **§8 KOL Haritası** protokolünü (v8.2) yürüt.

## Kademe

1. **Yayın tabanı (OpenAlex REST).** Alan/molekül için en üretken/etkili yazarlar; kurum,
   atıf, son-yazarlık sinyalleri. (`extended-api.md` OpenAlex; kanonik `kol_graph` artefaktı.)
2. **Semantic Scholar Graph.** Yazar disambiguasyonu + atıf/h-index + ortak-yazar kenarları.
3. **EuropePMC.** Yazar-bağlı yayın doğrulama (native `search`); klinik-çalışma yazarlığı.
4. **ABD PI doğrulama (NPI).** ABD klinisyen-KOL'ler için `npi_search`/`npi_lookup`/`npi_validate`
   — uzmanlık + lokasyon teyidi (sahip olmak ruhsat/aktiflik **garanti etmez** — not düş).
5. **Türk akademisyen katmanı (YÖK Akademik).** TR KOL'ler için `yok-akademik` — **YÖK Tez'den
   FARKLI**: h-index, ortak-yazar ağı, yayın, danışmanlık tezleri, kurum. (Tier-O Worker.)

## Çıktı

- **Sıralı KOL listesi** (etki: yayın hacmi + atıf + son-yazarlık + klinik-çalışma rolü).
- **Ortak-yazar ağı** (kümeler/merkeziyet) — kanonik `kol_graph`'ten.
- **Coğrafi katman** — global + ABD (NPI-doğrulu) + TR (YÖK Akademik).
- Her KOL için provenans (hangi kaynak hangi sinyali verdi).

## Disiplin

- **Kimlik çapraz-doğrulama:** OpenAlex/S2 yazar-ID disambiguasyonu olmadan tek-isim eşleşmesi
  sunulMAZ (eş-isim riski).
- **Native-first:** EPMC/YÖK Akademik native; OpenAlex/S2 REST. Tek-sefer (`kol_graph` paylaşılır).
- **Kapsam sınırı:** KOL kimliklendirme yapısal akademik kaynaklardan (OpenAlex/S2/EPMC/NPI/YÖK) yapılır;
  OSINT/web rekabet sinyali v1.4.0'da kaldırıldı (kapsam dışı → `pharmaintel`). Erişilebilirlik/etki
  bağlamı **klinik** KOL-sıralamasının temeli değildir.
- **Gizlilik:** kişi tanımlama için görsel/sorgu disiplinine uy; uydurma profil/iletişim **yok**.
