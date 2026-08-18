#!/usr/bin/env python3
"""fleet_probe cache kimliği ve yerel dosya güvenliği regresyonları."""
from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
import tempfile
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock

FLEETKIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(FLEETKIT))

import fleet_probe  # noqa: E402


class FleetProbeCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.base = Path(self._tmp.name)
        self.plugin = self.base / "plugin"
        self.plugin.mkdir()
        self.cache_home = self.base / "cache-home"
        self.cache_home.mkdir(mode=0o700)
        self.lock = {
            "plugin": "cache-test",
            "servers": [
                {
                    "name": "alpha",
                    "url": "https://alpha.invalid/mcp",
                    "auth_env": "ALPHA_TOKEN",
                },
                {
                    "name": "public",
                    "url": "https://public.invalid/mcp",
                    "auth_env": None,
                },
            ],
        }
        self._write_lock(self.lock)
        self.calls: list[dict] = []
        self._env_patch = mock.patch.dict(
            os.environ,
            {"XDG_CACHE_HOME": str(self.cache_home)},
            clear=False,
        )
        self._env_patch.start()
        self._probe_patch = mock.patch.object(
            fleet_probe,
            "probe_fleet",
            side_effect=self._fake_probe,
        )
        self._probe_patch.start()

    def tearDown(self) -> None:
        self._probe_patch.stop()
        self._env_patch.stop()
        self._tmp.cleanup()

    @property
    def cache_root(self) -> Path:
        return self.cache_home / "cureonics-fleet"

    @property
    def cache_path(self) -> Path:
        return self.cache_root / "cache-test.json"

    @property
    def salt_path(self) -> Path:
        name = getattr(fleet_probe, "CACHE_SALT_NAME", ".credential-salt")
        return self.cache_root / name

    def _write_lock(self, lock: dict) -> None:
        (self.plugin / "fleet.lock.json").write_text(json.dumps(lock), encoding="utf-8")

    def _fake_probe(self, lock: dict, env: dict) -> dict:
        self.calls.append(env)
        secret = env.get("ALPHA_TOKEN") or ""
        return {
            "alpha": {
                "name": "alpha",
                "status": "ok",
                "http": 200,
                "detail": f"upstream-echo:{secret}",
            }
        }

    def _probe(self, env: dict) -> dict:
        return fleet_probe.cached_probe(self.plugin, env)

    def test_same_credential_hits_cache_and_uses_supplied_env(self) -> None:
        env = {"ALPHA_TOKEN": "same-credential"}
        self._probe(env)
        cached = self._probe(env)

        self.assertEqual(1, len(self.calls))
        self.assertIs(self.calls[0], env)
        self.assertEqual("ok", cached["alpha"]["status"])

    def test_credential_rotation_misses_cache(self) -> None:
        self._probe({"ALPHA_TOKEN": "credential-one"})
        self._probe({"ALPHA_TOKEN": "credential-two"})
        self.assertEqual(2, len(self.calls))

    def test_missing_present_transitions_both_miss(self) -> None:
        self._probe({})
        self._probe({})
        self.assertEqual(1, len(self.calls), "aynı eksik-anahtar durumu cache hit olmalı")

        self._probe({"ALPHA_TOKEN": "now-present"})
        self.assertEqual(2, len(self.calls), "missing → present cache miss olmalı")

        self._probe({})
        self.assertEqual(3, len(self.calls), "present → missing cache miss olmalı")

    def test_roster_request_fields_invalidate_but_order_does_not(self) -> None:
        env = {"ALPHA_TOKEN": "stable"}
        self._probe(env)

        reordered = {**self.lock, "servers": list(reversed(self.lock["servers"]))}
        self._write_lock(reordered)
        self._probe(env)
        self.assertEqual(1, len(self.calls), "salt sunucu sırası kimliği değiştirmemeli")

        variants = [
            ("name", "alpha-renamed"),
            ("url", "https://alpha-new.invalid/mcp"),
            ("auth_env", "ALPHA_TOKEN_NEW"),
            ("headers", {"X-Auth-Mode": "suite"}),
            ("auth_type", "ApiKey"),
            ("header_type", "X-Api-Key"),
        ]
        current = reordered
        for field, value in variants:
            servers = [dict(server) for server in current["servers"]]
            target = next(server for server in servers if server["name"].startswith("alpha"))
            target[field] = value
            current = {**current, "servers": servers}
            self._write_lock(current)
            self._probe({**env, "ALPHA_TOKEN_NEW": "stable"})

        self.assertEqual(1 + len(variants), len(self.calls))

    def test_cache_bytes_contain_only_allowed_identity_metadata(self) -> None:
        secret = "ZXQ9-never-store-7KLM2-secret-5VBN8"
        self._probe({"ALPHA_TOKEN": secret})

        raw = self.cache_path.read_bytes()
        payload = json.loads(raw)
        self.assertNotIn(secret.encode(), raw)
        self.assertNotIn(secret[:8].encode(), raw)
        self.assertNotIn(secret[-8:].encode(), raw)
        self.assertEqual(
            {
                "schema_version",
                "roster",
                "auth_presence",
                "credential_fingerprint",
                "ts",
                "results",
            },
            set(payload),
        )
        self.assertEqual([True, False], sorted(payload["auth_presence"], reverse=True))
        self.assertRegex(payload["credential_fingerprint"], r"^[0-9a-f]{64}$")
        self.assertNotEqual(
            hashlib.sha256(secret.encode()).hexdigest(),
            payload["credential_fingerprint"],
        )
        self.assertNotIn(secret, json.dumps(payload["results"]))

    def test_new_cache_root_salt_and_cache_are_private(self) -> None:
        self._probe({"ALPHA_TOKEN": "private-modes"})

        self.assertEqual(0o700, stat.S_IMODE(self.cache_root.stat().st_mode))
        self.assertEqual(0o600, stat.S_IMODE(self.salt_path.stat().st_mode))
        self.assertEqual(0o600, stat.S_IMODE(self.cache_path.stat().st_mode))
        self.assertEqual(32, self.salt_path.stat().st_size)

    def test_shared_cache_root_is_refused_without_chmod(self) -> None:
        self.cache_root.mkdir(mode=0o755)
        os.chmod(self.cache_root, 0o755)

        self._probe({"ALPHA_TOKEN": "one"})
        self._probe({"ALPHA_TOKEN": "one"})

        self.assertEqual(2, len(self.calls))
        self.assertEqual(0o755, stat.S_IMODE(self.cache_root.stat().st_mode))
        self.assertFalse(self.cache_path.exists())
        self.assertFalse(self.salt_path.exists())

    def test_symlink_salt_is_refused_fail_open(self) -> None:
        self.cache_root.mkdir(mode=0o700)
        target = self.base / "salt-target"
        target.write_bytes(b"x" * 32)
        os.chmod(target, 0o600)
        self.salt_path.symlink_to(target)

        self._probe({"ALPHA_TOKEN": "one"})
        self._probe({"ALPHA_TOKEN": "one"})

        self.assertEqual(2, len(self.calls))
        self.assertEqual(b"x" * 32, target.read_bytes())
        self.assertFalse(self.cache_path.exists())

    def test_symlink_cache_is_never_read_or_replaced(self) -> None:
        self.cache_root.mkdir(mode=0o700)
        target = self.base / "cache-target"
        target.write_text('{"sentinel": true}', encoding="utf-8")
        os.chmod(target, 0o600)
        self.cache_path.symlink_to(target)

        self._probe({"ALPHA_TOKEN": "one"})
        self._probe({"ALPHA_TOKEN": "one"})

        self.assertEqual(2, len(self.calls))
        self.assertEqual('{"sentinel": true}', target.read_text(encoding="utf-8"))
        self.assertTrue(self.cache_path.is_symlink())

    def test_corrupt_and_legacy_cache_are_invalidated(self) -> None:
        self._probe({"ALPHA_TOKEN": "one"})
        self.calls.clear()

        self.cache_path.write_text("{broken", encoding="utf-8")
        os.chmod(self.cache_path, 0o600)
        self._probe({"ALPHA_TOKEN": "one"})
        self.assertEqual(1, len(self.calls))

        self.calls.clear()
        legacy = {
            "ts": time.time(),
            "roster": fleet_probe.roster_fingerprint(self.lock),
            "results": {"alpha": {"status": "ok"}},
        }
        self.cache_path.write_text(json.dumps(legacy), encoding="utf-8")
        os.chmod(self.cache_path, 0o600)
        self._probe({"ALPHA_TOKEN": "one"})
        self.assertEqual(1, len(self.calls))

    def test_oversize_cache_is_rejected_before_json_parse(self) -> None:
        self.cache_root.mkdir(mode=0o700)
        limit = getattr(fleet_probe, "CACHE_MAX_BYTES", 1024 * 1024)
        self.cache_path.write_bytes(b"{" + b"x" * limit)
        os.chmod(self.cache_path, 0o600)

        parse_called = False
        original_loads = fleet_probe.json.loads

        def recording_loads(raw):
            nonlocal parse_called
            parse_called = True
            return original_loads(raw)

        with mock.patch.object(fleet_probe.json, "loads", side_effect=recording_loads):
            self.assertIsNone(
                fleet_probe.read_cache(
                    self.cache_path,
                    roster=fleet_probe.roster_fingerprint(self.lock),
                )
            )
        self.assertFalse(parse_called)

    def test_salt_rotation_invalidates_cache(self) -> None:
        env = {"ALPHA_TOKEN": "same-credential"}
        self._probe(env)
        self._probe(env)
        self.assertEqual(1, len(self.calls))

        self.assertTrue(self.salt_path.is_file(), "ilk yazım kalıcı salt üretmeli")
        self.salt_path.unlink()
        self.salt_path.write_bytes(os.urandom(32))
        os.chmod(self.salt_path, 0o600)
        self._probe(env)

        self.assertEqual(2, len(self.calls))

    def test_atomic_unique_temp_replace_and_concurrent_writers(self) -> None:
        roster = fleet_probe.roster_fingerprint(self.lock)
        original_replace = os.replace
        replacements: list[tuple[Path, Path]] = []

        def recording_replace(src, dst):
            replacements.append((Path(src), Path(dst)))
            return original_replace(src, dst)

        with mock.patch.object(fleet_probe.os, "replace", side_effect=recording_replace):
            fleet_probe.write_cache(
                self.cache_path,
                {"alpha": {"status": "ok", "writer": "single"}},
                roster,
            )

        self.assertEqual(1, len(replacements))
        self.assertNotEqual(replacements[0][0], replacements[0][1])
        self.assertEqual(self.cache_path, replacements[0][1])

        def write_one(index: int) -> None:
            fleet_probe.write_cache(
                self.cache_path,
                {"alpha": {"status": "ok", "writer": index}},
                roster,
            )

        with ThreadPoolExecutor(max_workers=8) as pool:
            list(pool.map(write_one, range(32)))

        payload = json.loads(self.cache_path.read_text(encoding="utf-8"))
        self.assertIn(payload["results"]["alpha"]["writer"], range(32))
        leftovers = [
            path
            for path in self.cache_root.iterdir()
            if path not in {self.cache_path, self.salt_path}
        ]
        self.assertEqual([], leftovers)


if __name__ == "__main__":
    unittest.main()
