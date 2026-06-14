# Trademark, Domain, Social Handle Securing — Checklist

Reference for the legal + digital foundation that must be in place before external launch. Operationalizes Geyrhalter's Step 5 securing protocol.

## The mandate

Before external launch:
- Trademarks filed in primary jurisdictions
- Domains registered (primary + defensive)
- Social handles secured across major platforms

Brands that skip this step face high-impact preventable failures: trademark conflicts surfacing post-launch, opportunistic domain squatters, social handle hijacking, brand identity collisions.

## Trademark Filings

### What a trademark protects

A registered trademark gives the owner exclusive rights to use a mark in connection with specific goods/services in specific jurisdictions. It prevents others from using the same or confusingly similar marks in the same classes in the same jurisdictions.

### Pre-filing diligence

Before filing:

- **Trademark availability search** (USPTO TESS, EUIPO eSearch+, WIPO Madrid Monitor, national office databases for primary markets)
- **Common-law use search** (Google + industry-specific search; does anyone use this mark already without registration?)
- **Domain availability check** (parallel; see domain section)
- **Social handle availability** (parallel; see social section)
- **Linguistic / cultural check** (does the mark have unintended meaning in primary market languages?)

A name that fails any of these is high-risk; remediate before filing.

### Filing strategy

**Jurisdictions** (order by priority):

1. **Home jurisdiction**: where the entity is incorporated
2. **Primary operating markets**: jurisdictions where the brand has substantial customer presence
3. **Strategic future markets**: jurisdictions the brand expects to enter within 3-5 years
4. **Madrid Protocol filing**: for multi-jurisdictional coverage with single application (cost-efficient)

**Common jurisdiction recommendations**:
- US: USPTO
- EU: EUIPO (covers all EU member states)
- UK: UKIPO (post-Brexit)
- China: CNIPA (often filed defensively even without operations)
- Switzerland, Norway, Iceland: national offices (non-EU EFTA)
- Türkiye: TÜRKPATENT
- Japan: JPO
- Canada: CIPO
- Australia: IP Australia

**Classes** (Nice Classification, 45 classes):

Identify operating classes — what goods/services does the brand actually offer? Plus adjacent classes the brand may expand into.

Common class examples:
- Class 9: software, electronic devices
- Class 25: clothing, footwear
- Class 35: business management, advertising, retail
- Class 36: financial services
- Class 41: education, entertainment
- Class 42: scientific + technological services, including SaaS
- Class 43: hospitality, food, beverage service

Filing in too few classes leaves coverage gaps; filing in too many classes is wasteful + may invite "intent to use" challenges in jurisdictions where use evidence is required.

### Filing timing

- **3-6 months before external launch**: file primary jurisdiction applications
- **Pre-launch but post-internal-saturation**: file additional jurisdictions
- **Post-launch ongoing**: file in newly entered markets, file new classes as offerings expand

USPTO applications can take 8-12 months to register; EUIPO typically 4-6 months; Madrid Protocol can extend longer. Filing early reduces the gap between launch (when mark begins public use) and registration.

### Trademark monitoring

After filing:

- **Watch service** monitors new applications for similar marks
- **Annual review** of trademark portfolio (renewals due, opportunities to expand)
- **Enforcement protocol** when infringement detected (cease & desist process, escalation path)
- **Renewal calendar** (most jurisdictions require renewal at 10-year intervals; some sooner)

### Trademark documentation for launch plan

The launch plan includes:
- Filings completed (jurisdiction + class + date filed + status)
- Filings pending (planned filings + timing)
- Watch service in place (vendor + scope)
- Renewal calendar
- Conflict resolution protocol

## Domain Registration

### Primary domain decision

- **TLD priority order**: .com (global default) > .co (alternative when .com unavailable) > country code TLD (.uk, .de, .com.tr) > industry-specific (.studio, .design, .technology, .law)
- **Length**: shorter better; 6-12 characters ideal
- **Pronounceability**: must work spoken
- **Memorability**: must be retrievable without checking
- **Spelling resilience**: minimize common misspelling risks

### Defensive registrations

Beyond the primary domain:

**Variants**:
- Plural / singular if applicable
- Hyphenated version (and without hyphens)
- Common misspellings (especially of distinctive coined words)

**Geographic TLDs** for primary markets:
- .co.uk for UK
- .de for Germany
- .com.tr for Türkiye
- .ch for Switzerland
- Country code TLD for each market with substantial operations

**Adjacent TLDs**:
- .net (as backup)
- .org (if relevant to brand context)
- .[industry] (.studio, .design, .technology, etc.)

**Sub-brand defensive**:
- Domains for known future sub-brands or product lines

### Domain administration

- **Registrar**: enterprise-grade registrar with domain locking, two-factor auth, transfer protection
- **DNS infrastructure**: reliable DNS provider (separate from registrar often preferred)
- **Email DNS**: SPF, DKIM, DMARC records configured
- **Domain monitoring**: alerts for unauthorized changes
- **Renewal calendar**: 5-10 year renewals preferred; auto-renew enabled with payment method monitored

### Domain documentation for launch plan

The launch plan includes:
- Primary domain (secured)
- Defensive registrations (list)
- TLD coverage map (by market)
- DNS configuration
- Email configuration
- Renewal calendar + auto-renew status
- Registrar account access protocol

## Social Handle Securing

### Platform priority

**Always claim** (default for all brands):
- Instagram
- LinkedIn (Company + Founder pages)
- X / Twitter
- Facebook (Business / Page)
- YouTube
- TikTok (claim even if not active; prevents squatting)

**Conditionally claim**:
- Threads, Bluesky, Mastodon (consumer brand reach, sector-dependent)
- Pinterest (visual / lifestyle brands)
- Reddit (community management presence)
- GitHub (technology brands)
- Behance, Dribbble (creative brands)
- Medium / Substack (content brands)
- Glassdoor (employer brand, claim employer page)
- App Store / Google Play developer accounts (app-publishing brands)

### Handle strategy

- **Consistency across platforms**: same handle ideal (@brand on every platform)
- **Variant fallback**: when primary unavailable, document fallback choices (@brand_ vs @brandHQ vs @brand_official)
- **Capitalization**: most platforms case-insensitive in handle but case-sensitive in display name; standardize display name capitalization
- **Brand mark**: profile photo uses brand mark (favicon-scale version) consistently
- **Bio**: short bio (varies by platform character limit) drawn from brand voice + tagline

### Verification

- **LinkedIn Company verification**: standard for businesses
- **X Verified Org**: paid verification, signals legitimacy
- **Meta Verified**: paid verification across Instagram + Facebook
- **TikTok / YouTube verification**: typically requires substantial follower base; pursue when relevant
- **Domain verification on platforms** that offer it (Pinterest, etc.)

### Social handle documentation for launch plan

The launch plan includes:
- Handle claimed per platform (with URL)
- Handle naming conventions / fallback rules
- Verification status per platform
- Profile setup status (photo, bio, link, complete)
- Account access protocol (multi-factor auth, recovery email)

## Combined Pre-Launch Checklist

```markdown
## Trademark Status
- [ ] Trademark search completed (USPTO + EUIPO + national offices + common law)
- [ ] Filing strategy documented (jurisdictions + classes)
- [ ] Primary jurisdiction application filed
- [ ] Secondary jurisdiction applications filed
- [ ] Madrid Protocol filing (if multi-jurisdictional)
- [ ] Trademark watch service engaged
- [ ] Renewal calendar established
- [ ] Conflict resolution protocol documented

## Domain Status
- [ ] Primary domain secured (.com preferred)
- [ ] Variant + misspelling defensive registrations complete
- [ ] Country-code TLDs secured for primary markets
- [ ] Industry-specific TLDs secured (if relevant)
- [ ] DNS infrastructure configured
- [ ] Email DNS records (SPF, DKIM, DMARC) configured
- [ ] Domain monitoring enabled
- [ ] Renewal calendar + auto-renew enabled
- [ ] Registrar account access documented (multi-factor, recovery)

## Social Handle Status
- [ ] Instagram secured + verified (when applicable)
- [ ] LinkedIn Company + Founder pages secured
- [ ] X / Twitter secured + verified (when applicable)
- [ ] Facebook Business / Page secured
- [ ] YouTube channel secured
- [ ] TikTok handle secured
- [ ] Threads / Bluesky / Mastodon (if relevant)
- [ ] Pinterest, Reddit, GitHub, Behance, Dribbble, etc. (per sector)
- [ ] Glassdoor employer page claimed
- [ ] App store developer accounts (if applicable)
- [ ] Profile setup complete across platforms
- [ ] Account access protocol documented
```

## Anti-patterns

| Anti-pattern | Symptom | Remedy |
|---|---|---|
| Launch-before-file | External launch begins before trademark filed | Mandatory: file ≥3 months pre-launch |
| Single-jurisdiction blindness | Filed in home jurisdiction only | Cover primary operating markets |
| Defensive domain neglect | Only primary domain secured; squatters claim variants | Secure variants + misspellings |
| Social handle gaps | Some major platforms not claimed | Secure all major platforms even if not active |
| Stale registrations | Renewals lapse, domains lost, trademarks abandoned | Calendar + auto-renew discipline |
| No monitoring | Infringement happens undetected | Watch service + social monitoring |
| Unclaimed verification | Verified status available but not pursued | Pursue verification on key platforms |
