# Changelog — brand-touchpoint

All notable changes to this skill are documented in this file. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to Semantic Versioning ([SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)).

## [1.1.0] — 2026-05-29

### Changed
- Upstream schema_ref now resolves to brand-visual-ecosystem handoff schema (F-M-003)
- Created `luxury-touchpoint-extension.md` and `corporate-touchpoint-extension.md` reference files (F-C-003)
- Bibliography expanded from 40 to 61+ lines (F-M-007)

### Fixed
- Manifest file renamed from `manifest.smp.yaml` to `skill-manifest.yaml` to align with SMP v1.0 ecosystem convention (F-C-001 audit finding)
- Manifest schema migrated to SMP v1.0 §§4-6 — `smp_version` replaced by `manifest_version`, `classification` block added, `entry_point` declared, `protocol_reference` added (F-M-001)

### Added
- `predecessors` block declaring required and recommended upstream skills (F-m-006)
- `verification` block with trigger test prompts and composition test specs
- `CHANGELOG.md` (this file) (F-m-003)

## [1.0.0] — 2026-05-21

### Added
- Initial release of Touchpoint Application Specification Protocol
- Production-grade SKILL.md (description validated < 1024 chars)
- Reference files with canonical source citations
- Quality gate system with blocking semantics
- Bilingual TR/EN support
