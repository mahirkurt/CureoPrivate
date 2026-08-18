#!/usr/bin/env python3
"""Platforma özgü marketplace hook sözleşmesi regresyon testleri."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

FLEETKIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLEETKIT))

import check_marketplace  # noqa: E402


class HookContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name) / "plugin"
        (self.root / "hooks" / "scripts").mkdir(parents=True)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def write_script(self, name: str, body: str) -> None:
        (self.root / "hooks" / "scripts" / name).write_text(body, encoding="utf-8")

    def write_hook_file(self, name: str, doc: dict) -> Path:
        path = self.root / "hooks" / name
        path.write_text(json.dumps(doc), encoding="utf-8")
        return path

    def validate(self, path: Path, platform: str) -> list[str]:
        validator = getattr(check_marketplace, "check_hook_contract", None)
        self.assertIsNotNone(
            validator,
            "check_hook_contract platforma özgü hook doğrulayıcısı henüz uygulanmadı",
        )
        return validator(self.root, path, platform)

    def claude_doc(self) -> dict:
        return {
            "hooks": {
                "SessionStart": [
                    {
                        "matcher": "startup|resume",
                        "hooks": [
                            {
                                "type": "command",
                                "command": (
                                    '/usr/bin/env python3 "${CLAUDE_PLUGIN_ROOT}/'
                                    'hooks/scripts/claude_session.py"'
                                ),
                                "timeout": 15,
                            }
                        ],
                    }
                ]
            }
        }

    def cursor_doc(self) -> dict:
        return {
            "version": 1,
            "hooks": {
                "sessionStart": [
                    {
                        "type": "command",
                        "command": (
                            '/usr/bin/env python3 "${CURSOR_PLUGIN_ROOT}/'
                            'hooks/scripts/cursor_session.py"'
                        ),
                        "timeout": 15,
                        "failClosed": False,
                    }
                ],
                "postToolUse": [
                    {
                        "type": "command",
                        "command": (
                            '/usr/bin/env python3 "${CURSOR_PLUGIN_ROOT}/'
                            'hooks/scripts/cursor_post.py"'
                        ),
                        "matcher": "Write",
                        "timeout": 30,
                        "failClosed": False,
                    }
                ],
            },
        }

    def test_claude_file_is_accepted_for_claude(self) -> None:
        self.write_script("claude_session.py", 'print(\'{"hookSpecificOutput": {}}\')\n')
        path = self.write_hook_file("hooks.json", self.claude_doc())
        self.assertEqual([], self.validate(path, "claude"))

    def test_claude_file_is_rejected_for_cursor(self) -> None:
        self.write_script("claude_session.py", 'print(\'{"hookSpecificOutput": {}}\')\n')
        path = self.write_hook_file("hooks.json", self.claude_doc())
        self.assertTrue(self.validate(path, "cursor"))

    def test_cursor_file_is_accepted_for_cursor(self) -> None:
        self.write_script("cursor_session.py", 'print(\'{"additional_context": "ok"}\')\n')
        self.write_script("cursor_post.py", 'print(\'{"additional_context": "ok"}\')\n')
        path = self.write_hook_file("hooks-cursor.json", self.cursor_doc())
        self.assertEqual([], self.validate(path, "cursor"))

    def test_cursor_workspace_open_event_is_accepted(self) -> None:
        self.write_script("cursor_session.py", 'print(\'{"additional_context": "ok"}\')\n')
        doc = self.cursor_doc()
        doc["hooks"] = {"workspaceOpen": doc["hooks"]["sessionStart"]}
        path = self.write_hook_file("hooks-cursor.json", doc)
        self.assertEqual([], self.validate(path, "cursor"))

    def test_cursor_rejects_non_camel_event(self) -> None:
        self.write_script("cursor_session.py", 'print(\'{"additional_context": "ok"}\')\n')
        doc = self.cursor_doc()
        doc["hooks"] = {"SessionStart": doc["hooks"]["sessionStart"]}
        path = self.write_hook_file("hooks-cursor.json", doc)
        issues = self.validate(path, "cursor")
        self.assertTrue(any("olay" in issue and "SessionStart" in issue for issue in issues))

    def test_cursor_rejects_traversing_command_path(self) -> None:
        self.write_script("cursor_session.py", 'print(\'{"additional_context": "ok"}\')\n')
        doc = self.cursor_doc()
        doc["hooks"] = {
            "sessionStart": [
                {
                    "type": "command",
                    "command": (
                        '/usr/bin/env python3 "${CURSOR_PLUGIN_ROOT}/'
                        'hooks/scripts/../cursor_session.py"'
                    ),
                    "timeout": 15,
                    "failClosed": False,
                }
            ]
        }
        path = self.write_hook_file("hooks-cursor.json", doc)
        self.assertTrue(any("`..`" in issue for issue in self.validate(path, "cursor")))

    def test_cursor_rejects_wrong_command_root(self) -> None:
        self.write_script("cursor_session.py", 'print(\'{"additional_context": "ok"}\')\n')
        doc = self.cursor_doc()
        doc["hooks"]["sessionStart"][0]["command"] = (
            '/usr/bin/env python3 "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/cursor_session.py"'
        )
        path = self.write_hook_file("hooks-cursor.json", doc)
        self.assertTrue(
            any("CURSOR_PLUGIN_ROOT" in issue for issue in self.validate(path, "cursor"))
        )

    def test_cursor_rejects_claude_output_wrapper(self) -> None:
        self.write_script(
            "cursor_session.py",
            'print(\'{"hookSpecificOutput": {"additionalContext": "wrong"}}\')\n',
        )
        self.write_script("cursor_post.py", 'print(\'{"additional_context": "ok"}\')\n')
        path = self.write_hook_file("hooks-cursor.json", self.cursor_doc())
        self.assertTrue(
            any("hookSpecificOutput" in issue for issue in self.validate(path, "cursor"))
        )


if __name__ == "__main__":
    unittest.main()
