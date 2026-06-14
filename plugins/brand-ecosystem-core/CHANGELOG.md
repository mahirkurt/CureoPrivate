# Changelog — brand-ecosystem-core

## 1.0.0
- Initial release. Bundles ten Brand Ecosystem skills under one plugin:
  brand-audit, brand-platform, brand-story, brand-touchpoint, brand-launch,
  brand-maker-ecosystem, brand-visual-ecosystem, brand-maker, brand-visual,
  figma-forge.
- The seven brand-* skills carry skill-manifest.yaml files migrated to
  canonical SMP list-form by `smp migrate`; brand-maker (2.0.1), brand-visual
  (1.3.0) and figma-forge (0.2.1) ship their existing canonical manifests.
- Adds `/brand-ecosystem-core:pipeline` (audit → platform → story → naming →
  visual identity → touchpoints → launch), with handoff to the brand-voice
  plugin for the voice layer.
- `mcp.optional.json` documents Figma / GoDaddy / Exa as opt-in enhancers; no
  connector is required.
- Full ecosystem composition graph (these ten + the three brand-voice skills):
  13 nodes, 180/180 edges version_ok, 0 dangling.
