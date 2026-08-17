---
name: lex-bill
description: Mod 8 TBMM_KANUN_TEKLIFI — en üst düzey reform (TBMM kanun teklifi). Dayanak Anayasa Md.88 + TBMM İçtüzüğü Md.74-91 (5210 yalnız referans; "5210-uyumlu" DENMEZ). Genel gerekçe (10 alt-başlık) + 6-bölüm teklif metni + madde gerekçeleri + komisyon havalesi. evidentia ÇİFT-zorunlu tam §1-20. Argüman = kanun teklifinin konusu.
argument-hint: <teklif konusu — örn. "1219 SK tabiplik reformu kanun teklifi">
---

# /lex-bill — Mod 8 TBMM_KANUN_TEKLIFI (kanun teklifi)

Talep: **$ARGUMENTS**

`cureolex` flagship skill'ini **Mod 8 TBMM_KANUN_TEKLIFI** olarak çalıştır. Template: [[`templates/tbmm-kanun-teklifi.md`](../skills/cureolex/templates/tbmm-kanun-teklifi.md)](../skills/cureolex/templates/tbmm-kanun-teklifi.md).

## Yürütme

1. **Scope Guard (§6).**
2. **Tam-filo (G0).** `legal-distiller` ile Mod 8 server-listesi. Load-bearing: **tbmm** (yasama tarihçesi, 0.2.1) + mevzuat + resmi-gazete + Yarg + yok-akademik + karşılaştırmalı. Distiller TBMM araçlarını **çağırır**: `tbmm_search_kanun_teklifi` → `tbmm_get_kanun_teklifi(sira_no)` (önerge+imza); gerekçe gövdesi `get_mevzuat_gerekce`; komisyon search/get + `tbmm_list_komisyon_havale`; tutanak search/get (SPA `related_acik_erisim` kütüphane zabıtıdır, canlı Genel Kurul değildir); sponsor `tbmm_get_milletvekili`; OA `tbmm_list_acik_erisim_collections` + `tbmm_search_acik_erisim`.
3. **evidentia ÇİFT-zorunlu:** tam §1-20 rapor (klinik konu varsa). G7↔M-G8 çift-limit birleştirme.
4. **Dayanak notu:** Anayasa Md.88 + İçtüzük Md.74-91; **5210 Md.1/3 kapsam-dışı** açıkça belirt.
5. **TBMM 10-adım:** teklif imzaları (`sira_no` onerge + `tbmm_get_milletvekili`) → ihtiyacı netleştir → Tabaka tespiti → genel gerekçe (10 alt-başlık; locator TBMM, gövde mevzuat; **Md.90/5:** `treaty_status`/`treaty_reservations` + `coe_treaty_signatories` 164/211 + `intl_treaty_info`; andlaşma↔kanun → md. 90/5 cümlesi) → 6-bölüm teklif metni → madde gerekçeleri → İçtüzük Md.81 görüşme-usulü notu (tutanak; DSpace ≠ canlı Genel Kurul) → komisyon havalesi (esas = Sağlık/Aile/Çalışma ve Sosyal İşler; havale deep-link query'siz) → ekler → kalite kapıları.
6. **Kapılar tümü + G8.** `evidence_ledger`, no-fabrication.
7. **sci-audit'e delege et.**
8. **Kapsam manifestosu + confidence_label** ile bitir.
