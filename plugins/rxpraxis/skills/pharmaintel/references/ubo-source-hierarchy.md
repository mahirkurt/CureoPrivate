# ubo-source-hierarchy.md

**Ultimate Beneficial Ownership (UBO) Source Hierarchy Reference (v5.0.0)**

> **Purpose:** Defines the court-defensibility-ordered source priority hierarchy for UBO, corporate structure, sanctions, and litigation-related claims. Required reading for any `claim_type ∈ {beneficial_ownership, sanctions_hit, litigation_exhibit, corporate_structure}` invocation of the Forensic Provenance Layer.
>
> **Architectural context:** Reference document for `provenance-engine.md` §3.2 (L1 source resolution) + `sub-protocol-bd-dd.md` § target assessment + `sub-protocol-provenance.md` direct capture orchestration. Cross-referenced by validator gate G56/G-PROV-06 (UBO claims require P0 or P1 source + triangulation partner).

---

## §1. Priority Framework

### 1.1 Triangulation rules

| Scenario | Primer source | Triangulation partner | Citeable? |
|---|---|---|---|
| P0 found | P0 | P1 recommended | YES |
| P0 unavailable, P1 found | P1 | P2 mandatory | YES |
| P0+P1 unavailable | P2 | P2 (second distinct source) | CONDITIONAL (declare gap) |
| Only P3 | — | — | **NO** — P3 never citeable alone |

**Rationale:** Court-defensibility degrades sharply between P0 (statutory authority) and P3 (commercial aggregator). A claim backed only by Crunchbase investor listings cannot withstand TİTCK commission scrutiny or OFAC compliance review.

### 1.2 Tier definitions (cross-reference `evidence-object-schema.md` §3.3)

| Priority | Class | Authority basis | Defensibility |
|---|---|---|---|
| **P0** | Primary authority (statutory) | Government-maintained public registries | HIGH — court-admissible |
| **P1** | Authorized aggregator | Corporate data aggregators with registered licensing | HIGH — corroborative |
| **P2** | Investigative | Investigative journalism + leaked documents | MEDIUM — context-dependent |
| **P3** | Commercial / niche | Commercial intelligence services + web scrapes | LOW — context only |

---

## §2. P0 — Primary Authority Registries

### 2.1 Companies House UK

**Scope:** UK Ltd + Plc + LLP (including 99%+ of UK-domiciled biopharma SPVs + publicly-listed issuers like Oxford Nanopore, Bicycle Therapeutics, Autolus Therapeutics holding structure).

**Base URL:** `https://api.company-information.service.gov.uk`
**Auth:** Basic auth, API key as username + empty password
**Rate limit:** 600 req / 5 min
**Cost:** Free (email registration)

**Key endpoints:**
```
/company/{company_number}                                     # Company profile
/company/{company_number}/persons-with-significant-control    # PSC register
/company/{company_number}/officers                             # Directors + secretaries
/company/{company_number}/filing-history                       # Filing timeline
/company/{company_number}/charges                              # Security interests
/search/companies?q={name}                                     # Name search
```

**PSC register semantics:**
UK PSC (Persons with Significant Control) regime (Small Business, Enterprise and Employment Act 2015) requires disclosure of:
- Individuals holding ≥25% shares OR voting rights
- Individuals holding right to appoint/remove majority of directors
- Individuals exercising significant influence/control

PSC entries encoded via `nature_of_control` codes:
- `"ownership-of-shares-25-to-50-percent"`
- `"ownership-of-shares-50-to-75-percent"`
- `"ownership-of-shares-75-to-100-percent"`
- `"voting-rights-25-to-50-percent"` (and equivalent bands)
- `"right-to-appoint-and-remove-directors"`
- `"significant-influence-or-control"`

**Corporate PSC (legal entities):** When PSC is itself a legal entity (common in fund structures), recursive drill-down required via the corporate PSC's registration number + jurisdiction. This is where **investor chain walking** occurs.

**Forensic-grade caveat:** Companies House PSC data is **self-declared** by the filing company. Known false-filing cases (Jesus Christ as PSC of multiple shell companies, 2021 exposé) exist. PSC register is authoritative but not infallible — triangulate with OpenOwnership BODS + filing history.

### 2.2 BRIS — Business Registers Interconnection System (EU-wide)

**Scope:** All EU member state company registers cross-linked via e-Justice portal.

**Access:** `https://e-justice.europa.eu/content_business_registers_in_member_states-106-en.do`

**Rate limit:** Manual (web portal, no formal API). Per-member-state register limits apply.

**Key limitation:** BRIS provides **discovery + cross-linking**, not bulk download. Each member state register must be queried separately via its national portal.

**Member state coverage:**
- All 27 EU member states
- Basic data: company name + registration number + status + address
- Full UBO data: **requires** direct query to national PSC-equivalent register (see §2.3-2.6)

### 2.3 Handelsregister Deutschland (Germany)

**Scope:** German AG, GmbH, KG, OHG (AstraZeneca Munich, BioNTech Mainz, CureVac Tübingen, Evotec Hamburg, Qiagen Hilden, Merck KGaA Darmstadt all filed here).

**Portal:** `https://www.handelsregister.de`
**API option:** `https://www.unternehmensregister.de/ureg/` + third-party wrapper `register-api.de`
**Cost:** Free tier (register-api.de ~€0.50-2.00/query for bulk extracts)

**UBO register:** `Transparenzregister` (Transparency Register) — mandatory since 2017 per Geldwäschegesetz (GwG) §19-21 for German legal entities.
- Access: `https://www.transparenzregister.de`
- Beneficial owner disclosure required at ≥25% ownership
- Full public access (post-2022 ECJ ruling C-37/20 restricted access for non-legitimate-interest parties; legitimate interest must be demonstrated)

**Forensic-grade note:** German UBO register access gate (post-C-37/20) requires registered account + demonstrated legitimate interest (research, journalism, regulatory defense, compliance). pharmaintel legitimate interest = commercial intelligence for regulatory defense under BaFin/EU money-laundering prevention framework.

### 2.4 KBO-BCE Belgium

**Scope:** Belgian BV (SRL), NV (SA), Comm.V (SCS), CVBA, CommVA — UCB Brussels, Galapagos Mechelen, Argenx Ghent.

**Portal:** `https://kbopub.economie.fgov.be`
**API:** REST, no auth required, reasonable rate limits
**UBO register:** `UBO-register` separate — access via `https://finances.belgium.be/en/E-services/Ubo-register`

**Cost:** Free public access

### 2.5 KvK Netherlands

**Scope:** Dutch BV, NV — Merck & Co Dutch subsidiaries, Galapagos Hoofddorp + Leiden, Janssen Beerse cross-border, Mediq Utrecht.

**Portal:** `https://www.kvk.nl`
**API:** REST; paid per-query (~€2.30/transaction)
**UBO register:** Integrated into KvK — access restricted post-2022 to legitimate interest parties only

**Cost:** Paid per-query — highest-cost P0 in EU. Budget consideration for high-volume BD due diligence.

### 2.6 MERSİS + Ticaret Sicili Gazetesi (Türkiye)

**Scope:** Turkish AŞ (joint-stock), Ltd. Şti. (limited liability), Komandit Şti., Kollektif Şti.

**MERSİS (Merkezi Sicil Kayıt Sistemi):**
- Portal: `https://mersis.ticaret.gov.tr`
- **No public API** — web-only manual scraping (ToS: non-commercial research allowed with rate limit)
- Returns: company registration + address + status + capital

**Ticaret Sicili Gazetesi (Commercial Registry Gazette):**
- Portal: `https://www.ticaretsicil.gov.tr`
- **Primary Turkish UBO source** for forensic purposes
- PDF archive of all Turkish company registrations + amendments (2008+)
- Notary-validated — each announcement has official publication number
- Cost: Free access; subscription for bulk downloads

**Resmi Gazete (Official Gazette):**
- Portal: `https://www.resmigazete.gov.tr`
- Publishes: mergers, demergers, share transfers, liquidation, capital changes for publicly-relevant companies
- PDF archive searchable; API not public

**Turkish UBO discipline:**
1. **Primary:** Ticaret Sicili Gazetesi PDF (notary-validated official record)
2. **Secondary:** MERSİS (current state)
3. **Tertiary:** Resmi Gazete (material change announcements for TMK-listed companies)
4. **Triangulation partner:** OpenCorporates TR jurisdiction (if coverage available — historically sparse)

**Forensic-grade Türkiye caveat:** Turkish UBO regime under MASAK (Mali Suçları Araştırma Kurulu) AML framework requires 25%+ beneficial owner disclosure but **public access limited**. Most UBO data accessible only via:
- Notarized request to Ticaret Sicili Müdürlüğü (public companies) 
- Subpoena/mahkeme kararı (closely-held)

For pharmaintel commercial intelligence context, Ticaret Sicili Gazetesi + MERSİS + Resmi Gazete triangulation is the accessible ceiling.

### 2.7 Other notable P0 registries

| Jurisdiction | Registry | Portal | API | Cost |
|---|---|---|---|---|
| **France** | INPI Registre National des Entreprises (RNE) | `data.inpi.fr` | REST | Free |
| **Spain** | Registro Mercantil | `www.rmc.es` | Web | Paid per-query |
| **Italy** | Registro Imprese | `www.registroimprese.it` | Paid API | Paid tier |
| **Switzerland** | Zefix + Cantonal registers | `www.zefix.ch` | REST | Free |
| **Ireland** | CRO | `www.cro.ie` | Web | Paid per-document |
| **Sweden** | Bolagsverket | `www.bolagsverket.se` | REST | Free + paid tier |
| **Denmark** | CVR + Virksomhedsregister | `cvrapi.dk` | REST | Free |
| **Finland** | PRH | `www.prh.fi` | REST | Free |
| **Luxembourg** | RCS + RCSL | `www.rcsl.lu` | Paid portal | Paid per-document |
| **Japan** | Houmusho Registration Portal | `www1.touki.or.jp` | Manual | Paid (¥300-500/document) |
| **USA** | Per-state Secretary of State | Varies (50 states) | Varies | Varies |
| **Delaware** | DE Division of Corporations | `icis.corp.delaware.gov` | Paid portal | Paid per-document ($20-50) |
| **Russia** | EGRUL (Единый государственный реестр юридических лиц) | `egrul.nalog.ru` | Web | Free |
| **China** | 国家企业信用信息公示系统 (NECIPS) | `www.gsxt.gov.cn` | Web (sanctions check risk) | Free |
| **Hong Kong** | Companies Registry ICRIS | `www.icris.cr.gov.hk` | Paid portal | Paid per-document (HK$22) |
| **Singapore** | ACRA BizFile+ | `www.bizfile.gov.sg` | Paid portal | Paid per-document (S$5.50) |
| **Canada** | SEDAR+ / Corporations Canada | `beta.canadacompanies.ic.gc.ca` | Web | Mostly free |
| **Australia** | ASIC Connect | `connectonline.asic.gov.au` | Paid portal | Paid per-document (A$9-40) |
| **Brazil** | Receita Federal CNPJ | `www.receita.economia.gov.br` | REST (ReceitaWS wrapper) | Free |

### 2.8 SEC EDGAR (US public issuers)

**Scope:** ALL SEC-registered US public issuers (10-K, 10-Q, 8-K, 20-F, S-1, proxy statements, 13D/13G beneficial ownership filings).

**Base URL:** `https://www.sec.gov/cgi-bin/browser`
**API:** `https://data.sec.gov/submissions/CIK{cik}.json`
**Rate limit:** 10 req/sec (SEC Fair Access Rule compliance)
**Cost:** Free

**UBO-relevant filings:**
- **Schedule 13D** — >5% beneficial ownership, active intent
- **Schedule 13G** — >5% passive institutional ownership
- **Form 4** — insider transactions
- **DEF 14A** — proxy statement beneficial ownership table
- **10-K Item 12** — security ownership of management and principal shareholders

Cross-reference: `api-integrations.md` §SEC EDGAR for fetch patterns.

---

## §3. P1 — Authorized Aggregators

### 3.1 OpenCorporates

**Scope:** 200+ jurisdictions with ~200M+ companies. Most comprehensive global aggregator.

**Base URL:** `https://api.opencorporates.com/v0.4`
**Auth:** API token
**Rate limit:** Free tier 200 req/month; Paid $99/mo unlimited; Enterprise $2K+/mo bulk
**UBO coverage:** UK PSC + selected EU + some Latin American; **Türkiye coverage sparse**

**Key endpoints:**
```
/companies/search?q={name}&jurisdiction_code={iso}
/companies/{jurisdiction}/{number}
/officers/search?q={name}
```

**Triangulation role:** Use OpenCorporates as **triangulation partner** when P0 national register is primer source. Cross-validates:
- Company existence + current status
- Registration number normalization
- Cross-jurisdictional subsidiary linkage

**Forensic-grade note:** OpenCorporates data is **derived** from national registers. Latency 1-14 days typical between national register update and OpenCorporates sync. For time-sensitive TİTCK defense where 2023 state is critical, **direct P0 query preferred over OpenCorporates**.

### 3.2 OpenOwnership Register + BODS

**Scope:** UK PSC + Slovakia + Denmark + Ukraine + selected other jurisdictions. Growing.

**Access:** `https://register.openownership.org`
**Bulk download:** `https://oo-register-v2.openownership.org/exports/statements.latest.jsonl.gz`
**Format:** BODS (Beneficial Ownership Data Standard) JSON Lines
**Cost:** Free

**Advantages:**
- Standardized schema across jurisdictions
- Bulk offline-queryable (entire register in single JSONL download)
- Structured beneficial ownership chain representation

**Use case:** Pre-indexing the entire OpenOwnership dump enables offline investor chain walking with zero API latency or rate limits. Ideal for comprehensive BD due diligence screening.

### 3.3 OCCRP Aleph (authorized sources subset)

**Scope:** Aggregates 3,500+ datasets including PEP lists, sanctions, court records, corporate registries.

**Portal:** `https://aleph.occrp.org`
**API:** REST (free account required)
**Coverage:** Strong for Eastern Europe + Russia + post-Soviet + offshore jurisdictions

**Duality:** Aleph hosts both **authorized public datasets** (treat as P1) AND **leaked/investigative corpus** (treat as P2 — see §4.1).

**P1 subset:** Sanctions lists (OFAC SDN + EU + UK HMT + CanSanctions + etc.), PEP databases (WorldCheck equivalent open data), authorized corporate registry mirrors.

---

## §4. P2 — Investigative Sources

### 4.1 OCCRP Aleph leaks corpus

Accessible leaked document corpus:
- **Panama Papers (2016)** — Mossack Fonseca (~11.5M documents)
- **Paradise Papers (2017)** — Appleby + Asiaciti Trust
- **Pandora Papers (2021)** — 14 offshore service providers
- **FinCEN Files (2020)** — SAR leaks
- **Luanda Leaks (2020)**, **Cyprus Confidential (2023)**, **Pandora Files** continuations

**Forensic use:** Leaked documents are **admissible evidence in many jurisdictions** depending on acquisition provenance (cf. Daily Mirror v. Daily Mail 2001 + subsequent UK/US evidence rulings). Use as **corroborating source** when P0 is unavailable or as red-flag trigger.

**Ethical red-line:** pharmaintel never **republishes** leaked documents — only references their public OCCRP Aleph indexing. Quoting leaked personal data triggers G58/G-PROV-08 PII redaction mandate.

### 4.2 ICIJ Offshore Leaks Database

**Access:** `https://offshoreleaks.icij.org`
**Coverage:** Consolidated ICIJ leak corpus with entity + officer + address cross-linking
**No API:** Web portal only; manual scraping permissible per ICIJ public policy for non-commercial research

### 4.3 Regional investigative outlets

| Region | Outlet | Focus |
|---|---|---|
| **Global** | Organized Crime and Corruption Reporting Project (OCCRP) | Cross-border investigative |
| **US** | ProPublica, ICIJ | Federal-level investigations |
| **EU** | European Investigative Collaborations (EIC) | EU policy + corruption |
| **UK** | Bureau of Investigative Journalism | UK + global finance |
| **Türkiye** | Medyascope + T24 + Bianet + investigative segments of Sözcü/Cumhuriyet | Turkish political economy |

**Use:** Named investigation cited as primary source + archived via provenance-engine L2 capture.

---

## §5. P3 — Commercial / Niche Sources

### 5.1 LittleSis

**Scope:** US-focused "power mapping" — connections between individuals, corporations, government.

**Portal:** `https://littlesis.org`
**API:** REST (free, rate-limited)
**Coverage:** Strong for US biotech board/director overlap mapping; weak for operational UBO

**Caveat:** Crowdsourced + volunteer-curated. Data quality varies. **Never citeable alone** — always pair with P0/P1 verification.

### 5.2 Crunchbase

**Scope:** Private company funding rounds + investor chain + executive team.

**Portal:** `https://www.crunchbase.com`
**API:** REST, Startup tier $29/mo, Pro tier $49/mo, Enterprise $229+/mo
**Coverage:** Strong for biotech VC-backed private companies; moderate for post-IPO tracking

**Forensic limitation:** Crunchbase is self-reported + journalist-compiled. **Investor listings** are indicative but not legally binding beneficial ownership proofs. Use for **funding round context + investor identification**, then P0 verify at each investor entity.

### 5.3 Rusprofile + similar regional

**Rusprofile** (`rusprofile.ru`) — wraps EGRUL + EGRIP + court records for Russian legal entities. Web-only; ToS scrape-tolerant for non-commercial.

**Equivalent regional scrape wrappers:**
- **SAIC wrappers** for China (Qichacha, Tianyancha) — Mandarin, partial UBO
- **Turkish equivalents:** Findeks, TurkStat commercial scrapes (limited UBO)
- **Korean DART** equivalent wrappers for KRX-listed Korean companies

---

## §6. Specialized Datasets — Sanctions + PEP

### 6.1 OFAC SDN (Specially Designated Nationals)

**Scope:** US Treasury OFAC consolidated sanctions list.

**Access:** 
- Full list: `https://www.treasury.gov/ofac/downloads/sdn.xml`
- Search: `https://sanctionssearch.ofac.treas.gov`
- API wrapper: `https://ofac.treasury.gov/consolidated-sanctions-list`

**Update frequency:** Daily
**Fuzzy matching:** Required — sanctioned individuals often have name variants; implement phonetic + edit-distance matching

### 6.2 EU Consolidated Financial Sanctions List (CFSL)

**Access:** `https://data.europa.eu/data/datasets/consolidated-list-of-persons-groups-and-entities-subject-to-eu-financial-sanctions`
**Format:** XML, daily updates

### 6.3 UK HMT / OFSI Consolidated List

**Access:** `https://www.gov.uk/government/publications/financial-sanctions-consolidated-list-of-targets`
**Format:** CSV + XML

### 6.4 UN Consolidated Sanctions List

**Access:** `https://www.un.org/securitycouncil/sanctions/un-sc-consolidated-list`

### 6.5 Türkiye Sanctions (MASAK)

**Access:** MASAK published lists via `https://masak.hmb.gov.tr`

**Forensic-grade sanctions discipline:** In BD due diligence (sub-protocol-bd-dd.md), **all 4+ primary lists** must be screened for UBO chain members. Single-list hit = BLOCKER flag regardless of geographic concentration of pharmaintel operation.

---

## §7. Investor Chain Walk Discipline

### 7.1 Recursive drill-down pattern

UBO investigation rarely terminates at direct shareholder — investor chains through SPVs, GP/LP structures, trusts, foundations:

```
Target: "Hypothetical Biotech Co., Shanghai"
  ↓ Direct shareholders (SAIC/Qichacha)
  ├─ Shanghai Tianyi Investment LLP (60%)
  │   ↓ Beneficial owner (OpenCorporates + SAIC)
  │   └─ Parent LP: Cayman Islands Exempted Company (CIMA registry)
  │       ↓ General Partner
  │       └─ BVI Management Co. (BVI FSC registry)
  │           ↓ Ultimate individual
  │           └─ Mainland Chinese national X
  │               ↓ Sanctions screen
  │               └─ OFAC + EU + UK HMT clear / hit
  │
  ├─ State-owned biopharmaceutical group (25%)
  │   ↓ SASAC registry
  │   └─ PRC state entity (ultimate)
  │
  └─ Founder holdings (15%)
      ↓ Direct
      └─ Individual Y (sanctions screen)
```

**Each hop produces a separate Evidence Object** cross-linked via `cross_refs.triangulation_partner_ids`. Rendered as a **provenance tree diagram** in §Appendix B.

### 7.2 Common obfuscation patterns

| Pattern | Typical jurisdiction | pharmaintel response |
|---|---|---|
| **SCSp (société en commandite spéciale)** | Luxembourg | Query LBR (Luxembourg Business Register) for GP; GP is typically UK/Cayman | 
| **LP + GP structure** | Cayman / BVI / Delaware | Query GP registry (BVI FSC or DE Division of Corporations); GP officers often indirect proxy |
| **Foundation/Stiftung** | Liechtenstein / Panama / Anguilla | Nominee directors common; requires P2 investigative sources typically |
| **Trust** | Jersey / Guernsey / IOM / BVI | Trust beneficiaries rarely in public register; requires discovery in litigation or leaked corpus |
| **Nominee shareholder** | Global | Indicated when shareholder is registered as "director services" firm; requires look-through demand or P2 investigative |
| **Bearer shares** | Panama (pre-2015 prohibition), some Caribbean | Functionally untraceable via public registries; rely on P2 leaks |
| **Strawman / proxy director** | Global | Same address + same DOB for multiple companies = red flag; LittleSis-style power mapping helpful |

### 7.3 Recursion termination rule

Walk terminates when one of:
- **Ultimate individual identified** (natural person with ≥25% economic ownership after flow-through)
- **Sovereign / state entity reached** (e.g., China SASAC, Saudi PIF, Norwegian GPFG)
- **Publicly-traded parent reached** (with SEC/EDGAR 13D/13G disclosure)
- **Hard obfuscation point** (trust/foundation with unpublished beneficiary) → declare gap in §Appendix B

**Maximum recursion depth:** 7 hops (empirical saturation; beyond 7 hops typically = deliberate obfuscation layer requiring P2 leak corroboration or legal discovery).

---

## §8. Turkish UBO Practice — Special Considerations

### 8.1 Türk sermaye piyasası vs kapalı şirketler

**Publicly-listed (BİST):** 
- Public Disclosure Platform (KAP) `https://www.kap.org.tr`
- Continuous disclosure: ≥5% + ≥10% + ≥25% + ≥50% + ≥66.67% şirket paylarının kontrolüne ilişkin bildirimler (II-23.1 Tebliği)
- Annual corporate governance statement with shareholder structure
- **Strong UBO transparency** for BİST-listed biotech (e.g., Abdi İbrahim'in borsa bağlantılı iştirakleri, Deva Holding, Bilim İlaç)

**Kapalı şirketler (private):**
- Ticaret Sicili Gazetesi yayın + MERSİS + notarized article of association
- **Beneficial ownership often obscured** via:
  - Family member cross-holdings (common in Turkish family-owned biotech)
  - Holding company layers (Koç Holding, Sabancı Holding, Doğan Holding patterns)
  - Cross-border SPVs (Lüksemburg, Hollanda conduit structures)

### 8.2 Türk yerli ilaç sanayii UBO landscape

Türk yerli ilaç sektörü beneficial ownership patterns (2026 cutoff):

| Sponsor | Ownership pattern | Public access |
|---|---|---|
| **Abdi İbrahim** | Kapalı AŞ; Bilgen ailesi kontrolünde + azınlık paylar | KAP + Ticaret Sicili |
| **Deva Holding** | BİST-listed (DEVA); public + anonim şirket paylar | KAP continuous disclosure |
| **Bilim İlaç** | Kapalı AŞ; Kurt ailesi kontrolünde | Ticaret Sicili + Resmi Gazete |
| **Sanovel** | Koç Holding iştiraki; Koç aile kontrolünde | KAP (Koç üzerinden) + Ticaret Sicili |
| **Pharmactive** | Kapalı AŞ | Ticaret Sicili |
| **Mustafa Nevzat** | Pfizer Türkiye acquisition 2011; Pfizer SA ABD nihai sahip | Pfizer 10-K + SEC EDGAR |
| **Eczacıbaşı İlaç** | Eczacıbaşı Holding BİST-listed; Eczacıbaşı ailesi | KAP + Borsa İstanbul |
| **Pharmactive** | Kapalı AŞ; bağımsız sermaye | Ticaret Sicili |
| **Em Pharma (Onko-Koçsel)** | Kapalı AŞ; bağımsız Türk biyoteknoloji | Ticaret Sicili |
| **Atabay İlaç** | Marmara + Boğaziçi + ITÜ Mobgam ortaklıkları + özel sermaye | Ticaret Sicili + akademik partnerships public |

### 8.3 Türk UBO forensic-grade P0 stratejisi

1. **Public (BİST-listed):** KAP continuous disclosure → snapshot via Wayback + local Playwright WARC
2. **Private (Kapalı):** Ticaret Sicili Gazetesi last filing → PDF snapshot + notary number extraction
3. **Notarized articles of association:** Request via mevcut çalışma veya noter yoluyla (sub-protocol-turkey.md context)
4. **Triangulation:** MERSİS current-state + Resmi Gazete material change announcements

---

## §9. Source Quality Decay Indicators

### 9.1 Red flags lowering source tier

| Red flag | Impact |
|---|---|
| Registered address = "formation agent" office (e.g., CSC, Intertrust) | Corporate PSC or nominee likely; drill-down required |
| Same director appears in >50 entities | Professional nominee director; not beneficial owner |
| PSC register "all shareholders are corporate" without natural person | Incomplete disclosure; triangulate with investigative |
| Company incorporated <30 days before target transaction | SPV just for deal; ultimate UBO elsewhere |
| Jurisdiction = well-known secrecy haven (BVI, Cayman, Seychelles, Marshall Islands, Belize) | Increased P2 corroboration required |
| Bearer shares historical flag | Functionally untraceable pre-abolition |
| Multiple jurisdiction hops through secrecy havens | Deliberate obfuscation; requires P2 investigative to complete |

### 9.2 Source freshness expectations

| Source | Acceptable lag |
|---|---|
| Companies House UK PSC | ≤30 days (statutory filing deadline) |
| Handelsregister DE Transparenzregister | ≤14 days |
| OpenCorporates | ≤14 days from national register |
| OpenOwnership BODS | Daily update |
| MERSİS Türkiye | ≤60 days (practical, not statutory) |
| Ticaret Sicili Gazetesi | 15-60 days per filing |
| OFAC SDN | Daily |
| SEC EDGAR | Minutes (live) |
| Commercial P3 (Crunchbase) | Weeks to months |

**Forensic-grade G57/G-PROV-07:** Evidence Object capture `retrieved_at` must be within 7 days of report cite date. For UBO claims where filing lag exceeds 7 days, explicit "acceptable P0 lag for <jurisdiction>" memo required in `compliance.lawful_basis_memorandum_ref`.

---

## §10. pharmaintel UBO Workflow Integration

### 10.1 Source resolution priority order

Implemented in `scripts/provenance-engine/ubo_resolver.py`:

```python
# Pseudocode — full in Aşama 10
SOURCE_PRIORITY = [
    # P0 — statutory
    ("companies_house_uk", query_companies_house_psc),
    ("handelsregister_de", query_handelsregister_transparenz),
    ("kbo_be", query_kbo_bce_ubo),
    ("kvk_nl", query_kvk_ubo),  # paid
    ("mersis_tr", query_mersis_web),
    ("ticaret_sicili_tr", query_ticaret_sicili_gazette),
    ("egrul_ru", query_egrul),
    ("sec_edgar", query_sec_edgar_13d),
    # P1 — authorized aggregators
    ("opencorporates", query_opencorporates),
    ("openownership_bods", query_openownership_bulk),
    ("occrp_aleph_authorized", query_aleph_authorized),
    # P2 — investigative
    ("occrp_aleph_leaks", query_aleph_leaks),
    ("icij_offshore_leaks", query_icij),
    # P3 — commercial (reference only, never primer)
    ("crunchbase", query_crunchbase_investors),
    ("littlesis", query_littlesis_power_map),
    ("rusprofile", query_rusprofile_ru),
]

def resolve_ubo(target_entity: Entity) -> List[EvidenceObject]:
    sources_tried = []
    for source_name, query_fn in SOURCE_PRIORITY:
        result = query_fn(target_entity)
        sources_tried.append((source_name, result))
        if result and source_name in P0_SOURCES:
            return complete_chain(target_entity, result, sources_tried)
    # No P0 — ensure P1 + P2 triangulation
    return construct_best_effort_chain(target_entity, sources_tried)
```

### 10.2 Triangulation enforcement at validator

G56/G-PROV-06 gate enforces:
- `source.authority_tier ∈ {"T0", "OSINT-T1", "OSINT-T2"}` for beneficial_ownership claims
- `cross_refs.triangulation_partner_ids` non-empty
- Partner evidence object resolves to distinct source (not same source captured twice)

Failure → BLOCKER in baseline mode (sanctions + regulatory require this baseline); additional BLOCKER in forensic-grade mode.

---

## §11. Versioning & Changelog

- **v5.0.0 (2026-04-16):** Initial release. Court-defensibility-ordered UBO source hierarchy reference covering: P0 statutory authority (Companies House UK + BRIS EU + Handelsregister DE with Transparenzregister post-C-37/20 gate + KBO BE + KvK NL paid-per-query + MERSİS TR + Ticaret Sicili Gazetesi notary-validated + Resmi Gazete + EGRUL RU + SEC EDGAR + 18 additional national registries covering FR/ES/IT/CH/IE/SE/DK/FI/LU/JP/USA-state/DE/HK/SG/CA/AU/BR); P1 authorized aggregators (OpenCorporates 200+ jurisdictions + OpenOwnership BODS JSONL bulk + OCCRP Aleph authorized subset); P2 investigative (Panama/Paradise/Pandora/FinCEN Files via Aleph + ICIJ Offshore Leaks + regional investigative journalism OCCRP/ProPublica/EIC/Bureau/Medyascope); P3 commercial niche (LittleSis US power map + Crunchbase VC data + Rusprofile regional). Triangulation rules (P0 + P1 corroboration; P0 unavailable requires P1 + P2 mandatory; P3 never citeable alone); sanctions + PEP screening surface (OFAC SDN daily + EU CFSL + UK HMT OFSI + UN + Türkiye MASAK); investor chain walk discipline with recursive drill-down pattern + common obfuscation patterns (SCSp Lux + LP/GP Cayman/BVI + Stiftung Liechtenstein + Trust Jersey/Guernsey + nominee shareholder + bearer shares + strawman proxy director) + recursion termination rule (≤7 hops empirical saturation); Turkish UBO practice (BİST KAP continuous disclosure II-23.1 vs kapalı Ticaret Sicili vs Resmi Gazete; Türk yerli ilaç UBO landscape Abdi İbrahim + Deva Holding BİST + Bilim İlaç + Sanovel Koç + Pfizer-Mustafa Nevzat 2011 + Eczacıbaşı + Atabay); source quality decay indicators (formation agent address + serial director + jurisdiction secrecy haven + bearer shares historical + recent SPV) + source freshness expectations with G57/G-PROV-07 7-day rule. Integration pseudocode for scripts/provenance-engine/ubo_resolver.py with P0→P1→P2→P3 priority order. Triangulation enforcement at validator G56/G-PROV-06 (BLOCKER baseline + forensic-grade). Cross-references: provenance-engine.md §3.2 (L1 source resolution), evidence-object-schema.md §3.3 (authority_tier enumeration), sub-protocol-bd-dd.md (BD due diligence invocation), sub-protocol-provenance.md (forensic capture orchestration), validate-report-discipline.py gate G56/G-PROV-06, api-integrations.md (fetch patterns for P0 registries).
