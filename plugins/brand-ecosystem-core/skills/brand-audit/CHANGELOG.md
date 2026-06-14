# Changelog — brand-audit

All notable changes to this skill are documented in this file. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and adheres to Semantic Versioning ([SemVer 2.0.0](https://semver.org/spec/v2.0.0.html)).

## [1.1.0] — 2026-05-29

### Changed
- Input types corrected to SMP v1.0 compliant taxonomy: `file_collection` with `mime_types` array replacing invalid `files` and `pdf|markdown` union (F-M-004)
- G6 (Audit coverage ≥ 80%) elevated to blocking gate (F-m-005)
- Bibliography expanded from 38 to 56+ lines (F-M-007)

### Fixed
- Manifest file renamed from `manifest.smp.yaml` to `skill-manifest.yaml` to align with SMP v1.0 ecosystem convention (F-C-001 audit finding)
- Manifest schema migrated to SMP v1.0 §§4-6 — `smp_version` replaced by `manifest_version`, `classification` block added, `entry_point` declared, `protocol_reference` added (F-M-001)

### Added
- `predecessors` block declaring required and recommended upstream skills (F-m-006)
- `verification` block with trigger test prompts and composition test specs
- `CHANGELOG.md` (this file) (F-m-003)

## [1.0.0] — 2026-05-21

### Added
- Initial release of Diagnostic Brand Audit Protocol
- Production-grade SKILL.md (description validated < 1024 chars)
- Reference files with canonical source citations
- Quality gate system with blocking semantics
- Bilingual TR/EN support
