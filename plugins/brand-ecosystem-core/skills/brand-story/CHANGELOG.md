# Changelog — brand-story

All notable changes to this skill are documented in this file. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to Semantic Versioning ([SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)).

## [1.1.0] — 2026-05-29

### Changed
- Replaced non-standard `trigger_signals_inherited_from` with explicit `trigger_signals` lists for all opt-in modules (F-M-005)
- Created `luxury-narrative-restraint.md`, `b2b-narrative-stakeholders.md`, `purpose-narrative-stance.md` reference files (F-C-002)
- Bibliography expanded from 45 to 65+ lines with per-chapter source attributions (F-M-007)
- G9 (Bilingual rationale) elevated to blocking gate

### Fixed
- Manifest file renamed from `manifest.smp.yaml` to `skill-manifest.yaml` to align with SMP v1.0 ecosystem convention (F-C-001 audit finding)
- Manifest schema migrated to SMP v1.0 §§4-6 — `smp_version` replaced by `manifest_version`, `classification` block added, `entry_point` declared, `protocol_reference` added (F-M-001)

### Added
- `predecessors` block declaring required and recommended upstream skills (F-m-006)
- `verification` block with trigger test prompts and composition test specs
- `CHANGELOG.md` (this file) (F-m-003)

## [1.0.0] — 2026-05-21

### Added
- Initial release of Customer-Centric Brand Narrative Protocol
- Production-grade SKILL.md (description validated < 1024 chars)
- Reference files with canonical source citations
- Quality gate system with blocking semantics
- Bilingual TR/EN support
