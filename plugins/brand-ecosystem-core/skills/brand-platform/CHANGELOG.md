# Changelog — brand-platform

All notable changes to this skill are documented in this file. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to Semantic Versioning ([SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)).

## [1.1.0] — 2026-05-29

### Changed
- Added `predecessors` block: recommended brand-audit
- Expanded opt-in module list (5 reserved slots: fintech, food-beverage, hospitality, regulated-professional, alcohol-tobacco)
- Added G7 (Persona depth covers 4Cs + Maslow tier) and G8 (Positioning statement clause completeness) blocking gates

### Fixed
- Manifest file renamed from `manifest.smp.yaml` to `skill-manifest.yaml` to align with SMP v1.0 ecosystem convention (F-C-001 audit finding)
- Manifest schema migrated to SMP v1.0 §§4-6 — `smp_version` replaced by `manifest_version`, `classification` block added, `entry_point` declared, `protocol_reference` added (F-M-001)

### Added
- `predecessors` block declaring required and recommended upstream skills (F-m-006)
- `verification` block with trigger test prompts and composition test specs
- `CHANGELOG.md` (this file) (F-m-003)

## [1.0.0] — 2026-05-21

### Added
- Initial release of Foundation Brand Platform Document Protocol
- Production-grade SKILL.md (description validated < 1024 chars)
- Reference files with canonical source citations
- Quality gate system with blocking semantics
- Bilingual TR/EN support
