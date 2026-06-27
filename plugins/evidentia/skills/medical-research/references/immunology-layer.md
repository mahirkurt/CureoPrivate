# Immunology & Inflammation Layer (0.5.F)

**Loaded:** when axis 0.5.F fires. **Adım 1 package:** §1.L.
**Recreated v8.2.0 (UP-003).**

**Triggers (full):** RA/romatoid artrit, PsA/psoriatik artrit, AS/aksiyel spondiloartrit, SLE/lupus,
IBD, Crohn, ülseratif kolit, psoriasis/sedef, atopik dermatit, astım, KOAH-overlap, ürtiker, anti-TNF,
IL-17, IL-23, IL-4/13, IL-5, IL-6, JAK, TYK2, BTK, biyolojik, biyobenzer, ACR20/50/70, PASI, EASI,
DAS28, SDAI, Mayo, CDAI, treat-to-target.

---

## 1. Guidelines (Tier 1)
ACR (RA, SLE, gout), EULAR (RA, SpA, SLE — including treat-to-target), AAD (psoriasis), GINA
(asthma), ECCO (IBD), AAAAI/EAACI (atopic). Cite recommendation + strength.

## 2. Mechanism & class
anti-TNF, IL-17(A/F), IL-23(p19), IL-4Rα, IL-5, IL-6R, JAK1/2/3, TYK2 — ChEMBL native
(`get_mechanism`) + class-safety context (JAK boxed-warning: MACE/VTE/malignancy per ORAL
Surveillance). Biosimilar landscape via TİTCK `find_biosimilar_group`.

## 3. Endpoint appraisal
- **Composite/threshold endpoints:** ACR20/50/70, PASI75/90/100, EASI, DAS28-remission, Mayo
  endoscopic, clinical/endoscopic remission — define each; high placebo response is common.
- Long-term safety (registry/RWE Tier 4): infection, malignancy, MACE/VTE for JAK.
- Treat-to-target framing where guidelines specify.

## 4. Output → §1.L / §3 / §9
Feeds §3 Mechanism, §9 guideline placement, §4 label/safety (JAK class warnings). TR biosimilar +
SUT access in §5. `specialty_payload`: endpoint set + class-safety note.
