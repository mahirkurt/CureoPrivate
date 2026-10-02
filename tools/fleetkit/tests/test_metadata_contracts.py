#!/usr/bin/env python3
"""claude.ai sync metadata sınırları; gerçek repo yerine geçici fixture kullanır."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml

FLEETKIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLEETKIT))

import check_marketplace  # noqa: E402


class MetadataContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.repo = Path(self._tmp.name)
        self.root = self.repo / "plugins" / "example"
        self.manifest_path = self.root / ".claude-plugin" / "plugin.json"
        self.manifest_path.parent.mkdir(parents=True)
        self.skill_path = self.root / "skills" / "example" / "SKILL.md"
        self.skill_path.parent.mkdir(parents=True)
        self.manifest = {"name": "example", "version": "1.0.0", "description": "Açıklama"}
        self.entry = {
            **self.manifest,
            "displayName": "Example",
            "source": "./plugins/example",
            "author": {"name": "Author"},
            "category": "research",
            "keywords": ["example"],
            "strict": False,
        }
        patcher = mock.patch.object(check_marketplace, "REPO", self.repo)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.write_manifest()
        self.write_skill("Açıklama")

    def write_manifest(self) -> None:
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def write_skill(self, description: str) -> None:
        frontmatter = yaml.safe_dump(
            {"name": "example", "description": description}, allow_unicode=True
        )
        self.skill_path.write_text(f"---\n{frontmatter}---\n\n# Example\n", encoding="utf-8")

    def catalog_issues(self) -> list[str]:
        return check_marketplace.check_catalog({"plugins": [self.entry]})

    def plugin_issues(self) -> list[str]:
        return check_marketplace.check_plugin(self.root)

    def test_plugin_description_character_boundary(self) -> None:
        for length in (500, 501):
            with self.subTest(length=length):
                self.manifest["description"] = "ş" * length
                self.write_manifest()
                issues = self.plugin_issues()
                if length == 500:
                    self.assertEqual([], issues)
                else:
                    self.assertTrue(any("500 karakter" in issue and "(501)" in issue for issue in issues))

    def test_catalog_description_character_boundary(self) -> None:
        for length in (500, 501):
            with self.subTest(length=length):
                self.entry["description"] = self.manifest["description"] = "İ" * length
                self.write_manifest()
                issues = self.catalog_issues()
                if length == 500:
                    self.assertEqual([], issues)
                else:
                    self.assertTrue(any("katalog: description" in issue and "(501)" in issue for issue in issues))

    def test_catalog_and_plugin_descriptions_must_match(self) -> None:
        self.assertEqual([], self.catalog_issues())
        self.entry["description"] = "Farklı açıklama"
        self.assertTrue(any("katalog description ≠ plugin.json" in issue for issue in self.catalog_issues()))

    def test_plugin_schema_key_is_rejected_for_claude_ai_sync(self) -> None:
        self.manifest["$schema"] = "https://example.invalid/plugin.schema.json"
        self.write_manifest()
        self.assertTrue(any("Claude.ai sync" in issue and "$schema" in issue for issue in self.plugin_issues()))

    def test_skill_description_character_boundary(self) -> None:
        for length in (1024, 1025):
            with self.subTest(length=length):
                self.write_skill("ğ" * length)
                issues = self.plugin_issues()
                if length == 1024:
                    self.assertEqual([], issues)
                else:
                    self.assertTrue(any("1024 karakter" in issue and "(1025)" in issue for issue in issues))

    def test_folded_and_literal_description_boundaries(self) -> None:
        for style, separator in ((">-", " "), ("|-", "\n")):
            for length in (1024, 1025):
                with self.subTest(style=style, length=length):
                    first, second = "a" * 512, "b" * (length - 513)
                    self.skill_path.write_text(
                        f"---\nname: example\ndescription: {style}\n  {first}\n  {second}\n---\n",
                        encoding="utf-8",
                    )
                    parsed = check_marketplace.frontmatter(self.skill_path)["description"]
                    self.assertEqual(first + separator + second, parsed)
                    self.assertEqual(length, len(parsed))
                    issues = self.plugin_issues()
                    if length == 1024:
                        self.assertEqual([], issues)
                    else:
                        self.assertTrue(any("(1025)" in issue for issue in issues))

    def test_description_whitespace_cannot_hide_limit_violation(self) -> None:
        first, second = "a" * 512, "b" * 511
        for scalar in (f">-\n  {first}  {second}", f"|-\n  {first}\n\n  {second}"):
            with self.subTest(style=scalar[:2]):
                self.skill_path.write_text(
                    f"---\nname: example\ndescription: {scalar}\n---\n", encoding="utf-8"
                )
                parsed = check_marketplace.frontmatter(self.skill_path)["description"]
                self.assertEqual(1025, len(parsed))
                self.assertEqual(1024, len(" ".join(parsed.split())))
                self.assertTrue(any("(1025)" in issue for issue in self.plugin_issues()))

    def test_non_string_description_is_rejected(self) -> None:
        self.write_skill("Açıklama")
        self.manifest["description"] = self.entry["description"] = 123
        self.write_manifest()
        self.assertTrue(any("description boş olmayan metin" in issue for issue in self.plugin_issues()))
        self.assertTrue(any("description boş olmayan metin" in issue for issue in self.catalog_issues()))


if __name__ == "__main__":
    unittest.main()
