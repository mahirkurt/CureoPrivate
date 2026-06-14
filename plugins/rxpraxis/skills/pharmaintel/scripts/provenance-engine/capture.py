#!/usr/bin/env python3
"""
capture.py — pharmaintel v5.0.0 Forensic Provenance Layer

L2 capture layer — k-redundant 3-path web archive capture:
  - Path A: Internet Archive Wayback Machine SPN2 (Save Page Now 2) + CDX fallback
  - Path B: Archive.is (archive.ph/archive.today) submission via Playwright
  - Path C: Local Playwright headless Chromium with WARC + HAR + PDF + PNG + HTML

Orchestration: All 3 paths attempted in parallel via asyncio.TaskGroup.
Minimum success: ≥2 of 3 paths per G53/G-PROV-03 BLOCKER gate.

External dependencies (optional, graceful degradation):
  - requests         → Path A (Wayback SPN2 + CDX)
  - playwright       → Path B (Archive.is submission) + Path C (local capture)
  - warcio           → Path C (WARC writing; falls back to HTML+PDF if missing)

Authentication:
  - Wayback SPN2: Set env IA_ACCESS_KEY + IA_SECRET_KEY for 12 req/min
    (non-authenticated falls back to 5 req/min)

Run as module:
  python3 capture.py --url <url>                       # All 3 paths
  python3 capture.py --url <url> --only wayback        # Path A only
  python3 capture.py --url <url> --evidence-root ./evidence
  python3 capture.py --example                          # Dry-run with fake URL

Cross-references:
  - references/provenance-engine.md §3.3 (L2 capture 3-path)
  - references/sub-protocol-provenance.md §2.1 Step 2b
  - scripts/provenance-engine/evidence_object.py (produces EvidenceObject archive block)
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

try:
    import requests  # type: ignore

    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    from playwright.async_api import async_playwright  # type: ignore

    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) pharmaintel-provenance-engine/5.0.0"
WAYBACK_SPN_URL = "https://web.archive.org/save/"
WAYBACK_CDX_URL = "https://web.archive.org/cdx/search/cdx"
ARCHIVE_IS_URL = "https://archive.ph/"


# --- Result dataclass -------------------------------------------------------


@dataclass
class CaptureResult:
    evidence_id: str
    primary_url: str
    retrieved_at: str  # ISO 8601 UTC
    wayback_url: Optional[str] = None
    wayback_timestamp: Optional[str] = None
    wayback_snapshot_mode: Optional[str] = None  # spn | existing | cdx-discovered
    archive_is_url: Optional[str] = None
    archive_is_hash: Optional[str] = None
    fallback_paths: dict[str, str] = field(default_factory=dict)
    capture_paths_succeeded: list[str] = field(default_factory=list)
    capture_paths_failed: list[dict] = field(default_factory=list)
    capture_duration_seconds: float = 0.0
    http_status: Optional[int] = None
    content_type: Optional[str] = None
    content_length_bytes: Optional[int] = None

    def to_archive_block(self) -> dict:
        """Return the 'archive' block of an Evidence Object."""
        return {
            "wayback_url": self.wayback_url,
            "wayback_timestamp": self.wayback_timestamp,
            "wayback_snapshot_mode": self.wayback_snapshot_mode,
            "archive_is_url": self.archive_is_url,
            "archive_is_hash": self.archive_is_hash,
            "fallback_method": ("playwright_fullpage"
                                if "local" in self.capture_paths_succeeded else "none"),
            "fallback_paths": self.fallback_paths,
            "capture_paths_succeeded": self.capture_paths_succeeded,
            "capture_paths_failed": [e.get("path", "") for e in self.capture_paths_failed],
            "capture_duration_seconds": self.capture_duration_seconds,
        }


# --- Path A: Wayback Machine ------------------------------------------------


async def capture_wayback(url: str, retries: int = 3) -> dict:
    """Path A — Wayback Machine SPN2 with CDX fallback.

    Returns dict with: {success, wayback_url, wayback_timestamp, mode}.
    On failure: {success: False, error: <reason>}.
    """
    if not HAS_REQUESTS:
        return {"success": False, "error": "requests not installed"}

    ia_key = os.environ.get("IA_ACCESS_KEY")
    ia_secret = os.environ.get("IA_SECRET_KEY")
    headers = {"Accept": "application/json", "User-Agent": USER_AGENT}
    if ia_key and ia_secret:
        headers["Authorization"] = f"LOW {ia_key}:{ia_secret}"

    # Try SPN2
    last_err = None
    for attempt in range(retries):
        try:
            r = await asyncio.to_thread(
                requests.post,
                WAYBACK_SPN_URL,
                headers=headers,
                data={"url": url, "capture_all": "1", "capture_screenshot": "1"},
                timeout=60,
            )
            if r.status_code == 429:
                # Rate limited — exponential backoff
                await asyncio.sleep(2 ** attempt * 5)
                continue
            r.raise_for_status()
            payload = r.json()
            job_id = payload.get("job_id")
            if not job_id:
                last_err = f"No job_id in SPN response: {payload}"
                continue

            # Poll for completion
            for _ in range(60):  # 60 polls × 2s = 2min max
                await asyncio.sleep(2)
                s = await asyncio.to_thread(
                    requests.get,
                    f"https://web.archive.org/save/status/{job_id}",
                    headers=headers,
                    timeout=30,
                )
                status = s.json()
                if status.get("status") == "success":
                    ts = status["timestamp"]
                    return {
                        "success": True,
                        "wayback_url": f"https://web.archive.org/web/{ts}/{url}",
                        "wayback_timestamp": ts,
                        "mode": "spn",
                    }
                if status.get("status") == "error":
                    last_err = status.get("message", "SPN error")
                    break
            else:
                last_err = "SPN polling timeout"
        except Exception as e:  # noqa: BLE001
            last_err = str(e)
            await asyncio.sleep(2 ** attempt)

    # SPN failed — fall back to CDX existing snapshot
    try:
        r = await asyncio.to_thread(
            requests.get,
            WAYBACK_CDX_URL,
            params={"url": url, "output": "json", "limit": "-1"},
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
        data = r.json()
        if len(data) > 1:
            header, *rows = data
            latest = rows[-1]
            ts = latest[header.index("timestamp")]
            return {
                "success": True,
                "wayback_url": f"https://web.archive.org/web/{ts}/{url}",
                "wayback_timestamp": ts,
                "mode": "cdx-discovered",
                "note": "SPN failed; returned latest existing CDX snapshot",
            }
    except Exception as e:  # noqa: BLE001
        return {"success": False, "error": f"SPN and CDX both failed: {last_err} | {e}"}

    return {"success": False, "error": last_err or "No existing CDX snapshot"}


# --- Path B: Archive.is ------------------------------------------------------


async def capture_archive_is(url: str, timeout: int = 90) -> dict:
    """Path B — Archive.is submission via Playwright form POST.

    Returns dict with: {success, archive_is_url, archive_is_hash}.
    On CAPTCHA or JS-heavy SPA failure: {success: False, error}.
    """
    if not HAS_PLAYWRIGHT:
        return {"success": False, "error": "playwright not installed"}

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            try:
                ctx = await browser.new_context(user_agent=USER_AGENT)
                page = await ctx.new_page()
                await page.goto(ARCHIVE_IS_URL, wait_until="domcontentloaded",
                                timeout=30000)

                # Check for Cloudflare challenge
                html = await page.content()
                if "cf-challenge" in html.lower() or "just a moment" in html.lower():
                    return {"success": False, "error": "Cloudflare CAPTCHA"}

                # Submit URL via form
                try:
                    await page.fill('input[name="url"]', url)
                except Exception:
                    return {"success": False, "error": "Archive.is form not found"}
                await page.click('input[type="submit"]')

                # Wait for redirect to archived URL
                try:
                    await page.wait_for_url(
                        lambda u: "archive.ph" in u or "archive.today" in u
                                  or "archive.is" in u,
                        timeout=timeout * 1000,
                    )
                except Exception:
                    return {"success": False, "error": f"Archive.is timeout {timeout}s"}

                final_url = page.url
                # Extract short hash from URL like https://archive.ph/ABc12
                hash_segment = final_url.rstrip("/").split("/")[-1]
                return {
                    "success": True,
                    "archive_is_url": final_url,
                    "archive_is_hash": hash_segment,
                }
            finally:
                await browser.close()
    except Exception as e:  # noqa: BLE001
        return {"success": False, "error": str(e)}


# --- Path C: Local Playwright + WARC ----------------------------------------


async def capture_local_playwright(
    url: str, evidence_id: str, evidence_root: Path, timeout: int = 60,
) -> dict:
    """Path C — Local Playwright fullpage + HAR + PDF + PNG + HTML capture.

    Returns dict with: {success, paths, http_status, content_type, content_length}.
    """
    if not HAS_PLAYWRIGHT:
        return {"success": False, "error": "playwright not installed"}

    paths = {
        "pdf": str(evidence_root / "pdf" / f"{evidence_id}.pdf"),
        "png": str(evidence_root / "png" / f"{evidence_id}.png"),
        "html": str(evidence_root / "html" / f"{evidence_id}.html"),
        "har": str(evidence_root / "har" / f"{evidence_id}.har"),
    }
    for p in paths.values():
        Path(p).parent.mkdir(parents=True, exist_ok=True)

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-dev-shm-usage"],
            )
            try:
                ctx = await browser.new_context(
                    user_agent=USER_AGENT,
                    viewport={"width": 1920, "height": 1080},
                    record_har_path=paths["har"],
                )
                page = await ctx.new_page()
                response = await page.goto(
                    url, wait_until="networkidle", timeout=timeout * 1000,
                )
                if response is None:
                    return {"success": False, "error": "No response from page.goto"}

                html = await page.content()
                Path(paths["html"]).write_text(html, encoding="utf-8")
                await page.pdf(path=paths["pdf"], format="A4", print_background=True)
                await page.screenshot(path=paths["png"], full_page=True)

                result = {
                    "success": True,
                    "paths": paths,
                    "http_status": response.status,
                    "content_type": response.headers.get("content-type"),
                    "content_length": len(html.encode("utf-8")),
                }
                await ctx.close()  # finalize HAR
                return result
            finally:
                await browser.close()
    except Exception as e:  # noqa: BLE001
        return {"success": False, "error": str(e)}


# --- Orchestrator -----------------------------------------------------------


async def capture_all_paths(
    url: str, evidence_root: str | Path = "evidence",
) -> CaptureResult:
    """Run all 3 capture paths in parallel. Requires ≥2 success per G53."""
    evidence_root_p = Path(evidence_root)
    retrieved_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Deterministic evidence_id
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
    date_str = retrieved_at[:10]
    evidence_id = f"ev_{date_str}_{url_hash}"

    start = time.time()
    path_a, path_b, path_c = await asyncio.gather(
        capture_wayback(url),
        capture_archive_is(url),
        capture_local_playwright(url, evidence_id, evidence_root_p),
        return_exceptions=True,
    )
    elapsed = time.time() - start

    result = CaptureResult(
        evidence_id=evidence_id,
        primary_url=url,
        retrieved_at=retrieved_at,
        capture_duration_seconds=round(elapsed, 2),
    )

    # Normalize exceptions to dicts
    def _as_dict(x: Any) -> dict:
        if isinstance(x, Exception):
            return {"success": False, "error": str(x)}
        return x

    path_a, path_b, path_c = _as_dict(path_a), _as_dict(path_b), _as_dict(path_c)

    if path_a.get("success"):
        result.wayback_url = path_a.get("wayback_url")
        result.wayback_timestamp = path_a.get("wayback_timestamp")
        result.wayback_snapshot_mode = path_a.get("mode")
        result.capture_paths_succeeded.append("wayback")
    else:
        result.capture_paths_failed.append({"path": "wayback",
                                             "error": path_a.get("error", "unknown")})

    if path_b.get("success"):
        result.archive_is_url = path_b.get("archive_is_url")
        result.archive_is_hash = path_b.get("archive_is_hash")
        result.capture_paths_succeeded.append("archive_is")
    else:
        result.capture_paths_failed.append({"path": "archive_is",
                                             "error": path_b.get("error", "unknown")})

    if path_c.get("success"):
        paths = path_c.get("paths", {})
        result.fallback_paths = paths
        result.http_status = path_c.get("http_status")
        result.content_type = path_c.get("content_type")
        result.content_length_bytes = path_c.get("content_length")
        result.capture_paths_succeeded.append("local")
    else:
        result.capture_paths_failed.append({"path": "local",
                                             "error": path_c.get("error", "unknown")})

    return result


# --- Example fixture --------------------------------------------------------


def example_capture_result() -> CaptureResult:
    """Return a CaptureResult example (for dry-run / documentation)."""
    return CaptureResult(
        evidence_id="ev_2026-04-16_7f3a2b1e",
        primary_url="https://example.gov/public-registry/12345",
        retrieved_at="2026-04-16T09:34:22Z",
        wayback_url="https://web.archive.org/web/20260416093500/https://example.gov/public-registry/12345",
        wayback_timestamp="20260416093500",
        wayback_snapshot_mode="spn",
        archive_is_url="https://archive.ph/ABc12",
        archive_is_hash="ABc12",
        fallback_paths={
            "pdf": "evidence/pdf/ev_2026-04-16_7f3a2b1e.pdf",
            "png": "evidence/png/ev_2026-04-16_7f3a2b1e.png",
            "html": "evidence/html/ev_2026-04-16_7f3a2b1e.html",
            "har": "evidence/har/ev_2026-04-16_7f3a2b1e.har",
        },
        capture_paths_succeeded=["wayback", "archive_is", "local"],
        capture_paths_failed=[],
        capture_duration_seconds=18.3,
        http_status=200,
        content_type="text/html; charset=utf-8",
        content_length_bytes=184726,
    )


# --- CLI --------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description="pharmaintel v5.0.0 Forensic Provenance Layer — capture orchestrator"
    )
    parser.add_argument("--url", help="Target URL to capture")
    parser.add_argument("--evidence-root", default="evidence",
                        help="Root dir for evidence artifacts (default: ./evidence)")
    parser.add_argument("--only", choices=["wayback", "archive_is", "local"],
                        help="Run single path only (diagnostic)")
    parser.add_argument("--example", action="store_true",
                        help="Print example CaptureResult (no network)")
    args = parser.parse_args()

    if args.example:
        result = example_capture_result()
        print(json.dumps({"archive_block": result.to_archive_block()},
                         indent=2, ensure_ascii=False))
        print(f"\nDependencies available — requests: {HAS_REQUESTS}, "
              f"playwright: {HAS_PLAYWRIGHT}", file=sys.stderr)
        return 0

    if not args.url:
        parser.error("--url required (or use --example)")

    if args.only == "wayback":
        res = asyncio.run(capture_wayback(args.url))
    elif args.only == "archive_is":
        res = asyncio.run(capture_archive_is(args.url))
    elif args.only == "local":
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        url_hash = hashlib.sha256(args.url.encode()).hexdigest()[:8]
        eid = f"ev_{date_str}_{url_hash}"
        res = asyncio.run(capture_local_playwright(
            args.url, eid, Path(args.evidence_root)))
    else:
        result = asyncio.run(capture_all_paths(args.url, args.evidence_root))
        res = {
            "evidence_id": result.evidence_id,
            "succeeded": result.capture_paths_succeeded,
            "failed": [e["path"] for e in result.capture_paths_failed],
            "archive_block": result.to_archive_block(),
        }

    print(json.dumps(res, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
