# Digital Touchpoints

Reference loaded for every brief — digital touchpoints are baseline for almost all brands today. Covers web atmosphere, social media template kit, presentation deck system, app interface (when applicable), email atmosphere beyond signature.

## Why digital touchpoints differ

Digital touchpoints are:
- **Most frequently encountered**: customers encounter the website 10x more than the business card
- **Most measurable**: analytics provide direct feedback on resonance
- **Most adaptable**: easier to iterate than physical touchpoints
- **Most fractured by device**: same touchpoint experienced differently across desktop / tablet / mobile
- **Subject to platform constraints**: social platforms dictate format; brand adapts to platform

This makes digital touchpoint design both lower-stakes (per change) and higher-cumulative-stakes (most encounters).

## Web Atmosphere

The website is the brand's most-visited environment. Specifications must cover:

### Architectural design
- Information architecture (page hierarchy, navigation structure)
- Page archetypes (home, about, product/service, contact, others)
- Conversion path mapping (entry → consideration → conversion)
- Mobile-first or desktop-first design philosophy

### Visual atmospheric design
- Color application (primary palette use vs accent vs supporting)
- Typography system (display, body, micro)
- Whitespace generosity (sparse vs dense)
- Image treatment (full-bleed photography, contained imagery, abstract patterns, illustration)
- Motion language (transitions, hover states, scroll effects, micro-interactions)
- Loading + intermediate states (skeleton screens, progressive disclosure)

### Content discipline
- Voice + tone consistency (drawn from brand-platform voice principles)
- Headline + body copy hierarchy
- CTA language consistency
- Brand voice in error messages, form labels, empty states (often-overlooked atmospheric moments)

### Technical specifications
- Performance targets (Largest Contentful Paint < 2.5s, etc.)
- Accessibility standard (WCAG 2.1 AA minimum, AAA where appropriate)
- Cross-browser support (current + last major version)
- Cross-device responsiveness (mobile, tablet, desktop, ultrawide)
- SEO + AI-discoverability (structured data, semantic HTML)

### Component library
The web touchpoint produces (or consumes) a component library:
- Buttons, form fields, navigation, cards, modals, tooltips
- Each component specified visually + behaviorally
- Each component's brand atmosphere contribution noted
- Component library aligned with brand-visual's design system if existing

## Social Media Template Kit

Brands appear on social platforms in formats dictated by the platforms:

| Platform | Standard formats |
|---|---|
| Instagram | Square (1:1), portrait (4:5), Reels (9:16), Stories (9:16) |
| LinkedIn | Square (1:1), landscape (1.91:1), document (multi-page) |
| Twitter / X | Landscape (16:9), square (1:1) |
| TikTok | Vertical (9:16) |
| YouTube | Landscape (16:9) for video, 1:1 for shorts |
| Pinterest | Vertical (2:3, 1:2.1) |

For each platform the brand actively uses, the template kit includes:

### Per-platform templates
- Quote / text-only posts
- Photo + caption posts
- Carousel / multi-frame posts
- Story / vertical posts
- Cover images / banners
- Profile image conventions

### Template specifications
- Dimensions (exact pixel)
- Safe zones (mobile crop, platform UI overlap)
- Typography hierarchy
- Color application
- Logo placement + size
- Caption / handle treatment
- File format (PNG, JPEG, MP4) + compression specifications

### Editable systems
- Editor tool specified (Figma, Canva, Adobe Express)
- Master template files with editable text + image areas
- Variable swap rules (which elements can vary, which are fixed)
- Approval workflow (who can publish without review)

### Cadence + rhythm
- Posting frequency targets
- Content type distribution
- Voice consistency in captions
- Hashtag strategy
- Link-out strategy

## Presentation Deck System

Presentation slides are touchpoints. A brand that designs a careful identity then uses default PowerPoint templates is publicly demonstrating that it stopped investing.

### Deck system specifications

**Master templates** (multiple deck variants):
- External pitch / sales deck
- Internal team meeting deck
- All-hands / company-wide deck
- Investor pitch deck (if applicable)
- Conference / keynote deck

Each variant has different formality + density requirements.

### Slide architecture (per template)
- Title slide
- Section divider
- Content slide variations (single statement, bullets, two-column, image-led, data-led)
- Quote slide
- Statistic / data slide
- Team / about slide
- Contact / next-steps slide
- Closing slide

### Visual specifications
- Color palette use across slides
- Typography hierarchy
- Image treatment
- Chart + graph styling (the most-undersigned element of most decks)
- Icon use (custom or licensed system)
- Animation philosophy (restraint preferred for professional decks)

### Authoring discipline
- Voice + tone consistency
- Slide density rules (one idea per slide ideal)
- Speaker notes vs visible text
- Updating + versioning protocol

### Distribution
- File format (PowerPoint, Keynote, Google Slides, PDF export)
- Web-presentable versions (cloud links)
- Print versions (handout format with notes)

## Email Atmosphere (Beyond Signature)

Email marketing and customer service emails are touchpoints. Discipline:

### Marketing email templates
- Layout (single-column for mobile, multi-column where appropriate)
- Color application (typically restrained vs brand spectrum)
- Typography (web-safe with fallback or system fonts)
- Image use (alt text mandatory)
- CTA treatment
- Footer (legal, unsubscribe, social, address)

### Transactional email design
- Order confirmation
- Shipping notification
- Account changes
- Receipt / invoice
- Password reset
- Welcome series

Transactional emails are high-trust, high-engagement touchpoints. They deserve the same atmospheric care as marketing emails. Many brands neglect them.

### Customer service email guidance
- Voice consistency (drawn from brand voice principles)
- Response templates (high-frequency questions)
- Escalation language
- Resolution / sign-off conventions

## Mobile App (When Applicable)

For brands with native apps:

- App icon (per platform spec — iOS 1024×1024, adaptive icon for Android)
- Splash screen / launch experience
- Onboarding flow
- Navigation paradigm
- Component library (mobile-specific, often distinct from web)
- Notification design (push + in-app)
- Empty states
- Error states
- Loading states

Mobile app atmosphere often diverges from web atmosphere in subtle ways. Specifications must define both the unified brand and the platform-appropriate adaptations.

## Web Component Considerations: Atmosphere vs UI Convention

Tension exists between brand atmospheric expression and UI convention. Users expect certain interactions (login forms work a certain way, navigation appears in certain places). Diverging from convention for atmospheric expression risks usability.

The discipline: **break convention sparingly and only where atmospheric payoff justifies usability cost.**

Generally:
- Functional UI components follow convention (forms, buttons, navigation)
- Atmospheric components express brand (imagery, typography, color, motion)
- Convention-breaking permitted in editorial / brand-statement contexts
- Convention-breaking discouraged in transactional / functional contexts

## Accessibility + Atmosphere

Accessibility is not in tension with brand atmosphere — it is a constraint that good atmosphere respects:

- Color contrast meets WCAG AA minimum (or AAA for body text)
- Typography legible across viewport sizes
- Interactive elements have visible focus states
- Motion respects user preference (prefers-reduced-motion)
- Alt text on imagery
- Semantic HTML structure
- Keyboard navigation works

A brand whose atmospheric design excludes users with disabilities is not "premium" — it is incomplete.

## Bilingual digital touchpoints

For multilingual brands:

- Language switcher: visible, accessible, intuitive
- Typography testing: bilingual rendering at common breakpoints
- Translation governance: who translates, who approves, how updates propagate
- Right-to-left language support if Arabic/Hebrew in market
- Diacritic handling: TR specific characters (ç, ş, ı, İ, ğ, ü, ö) tested

## Anti-patterns

| Anti-pattern | Symptom | Remedy |
|---|---|---|
| Website as marketing surface only | Site optimized for conversion, neglected as brand touchpoint | Design brand atmosphere alongside conversion |
| Default presentation templates | Carefully designed identity, generic PowerPoint | Build deck system as first-class touchpoint |
| Social platform abdication | "We just post stuff" — no template kit | Build template kit; consistency compounds |
| Transactional email neglect | Marketing emails branded, receipts use raw HTML | Transactional emails deserve atmospheric care |
| Mobile-as-afterthought | Desktop designed first, mobile retrofitted | Mobile-first or genuinely responsive design |
| Accessibility/atmosphere conflict | Brand chose unreadable type contrast for atmospheric reasons | Atmosphere within accessibility constraints |
