"""figma-forge supply-chain attestation — v1.0.0.

Cryptographic supply-chain provenance for design system library
bundles, built on three layers:

1. **Bundle manifest** — schema-v1.0 SHA-256 inventory (already
   implemented in v0.3.0-rc.1 ``bundle_manifest.py``; re-exported
   here under the v1.0 public API name ``build_bundle_manifest``).

2. **SLSA v1.0 provenance attestation** — declares the *builder*
   identity, the *materials* (source repo + commit), the *invocation*
   (which command was run, with what parameters), and the *artifacts*
   produced. Follows the SLSA v1.0 provenance shape so that any
   SLSA-aware consumer (in-toto, sigstore-verifier, etc.) can verify.

3. **Sigstore keyless signing** — signs the (manifest + provenance)
   bundle with a short-lived OIDC-identity certificate from the
   Sigstore public good instance. No long-lived private key required.
   Suitable for GitHub Actions workflows (uses the OIDC token issued
   to the workflow). Falls back to SHA-256-only verification when
   ``sigstore`` is not installed.

Public API (re-exported via :mod:`figma_forge`):

    build_bundle_manifest(library_dir) -> BundleManifest
    sign_manifest(manifest, *, identity, ...) -> SignedManifest
    verify_manifest(signed, *, identity, ...) -> VerificationResult
    ProvenanceAttestation
    BundleManifest

The module is **import-safe without sigstore** — calling
``sign_manifest`` without sigstore installed raises a clear
``RuntimeError`` directing the user to install it; everything else
works on stdlib alone.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

# Try to import the bundle-manifest builder.
# bundle_manifest.py is the v0.3.0-rc.1 module; here we just re-shape
# its output and add a name alias for the v1.0 API contract.
from bundle_manifest import build_manifest as _build_inventory


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------

@dataclass
class BundleManifest:
    """Lightweight wrapper over a schema-v1.0 bundle manifest dict.

    Stores the raw manifest payload plus convenience accessors. Stable
    in v1.x — all fields documented here are guaranteed to exist on
    the underlying dict.
    """

    payload: dict[str, Any]

    @property
    def bundle_name(self) -> str:
        return str(self.payload.get("bundle_name", ""))

    @property
    def bundle_version(self) -> str:
        return str(self.payload.get("bundle_version", ""))

    @property
    def file_count(self) -> int:
        return int(self.payload.get("file_count", 0))

    @property
    def total_size_bytes(self) -> int:
        return int(self.payload.get("total_size_bytes", 0))

    def manifest_hash(self) -> str:
        """Canonical SHA-256 of the manifest's **content-only** payload.

        Computed over a deterministically-encoded JSON form
        (sort_keys, no whitespace) of the payload with **non-deterministic
        fields stripped**:

        - ``generated_at`` — changes on every invocation
        - ``generator`` — may legitimately differ across builds

        The remaining fields (``bundle_name``, ``bundle_version``,
        ``file_count``, ``total_size_bytes``, ``files[]``, etc.) form
        the *content identity* of the bundle: two manifests with
        identical content_only payloads describe identical bundles
        regardless of when or by whom they were built.

        This determinism is required by SLSA provenance: the manifest
        hash anchored in ``subject[0].digest.sha256`` must be
        reproducible by a verifier who re-runs the manifest builder.
        """
        canonical = {
            k: v for k, v in self.payload.items()
            if k not in {"generated_at", "generator"}
        }
        encoded = json.dumps(
            canonical, sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.payload, indent=indent, ensure_ascii=False) + "\n"


@dataclass
class ProvenanceAttestation:
    """SLSA v1.0 provenance shape.

    See https://slsa.dev/spec/v1.0/provenance for the canonical
    schema. We emit a subset suitable for design-system library
    bundles — full SLSA Build Level 3 requires a hardened build
    platform, which is the integrator's responsibility.
    """

    bundle_manifest_hash: str
    builder_id: str
    invocation_command: str
    invocation_environment: dict[str, str] = field(default_factory=dict)
    source_repository: str = ""
    source_commit: str = ""
    build_started_at: str = ""
    build_finished_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Emit the SLSA v1.0 provenance JSON shape."""
        return {
            "_type": "https://in-toto.io/Statement/v1",
            "predicateType": "https://slsa.dev/provenance/v1",
            "subject": [
                {
                    "name": "bundle-manifest.json",
                    "digest": {"sha256": self.bundle_manifest_hash},
                }
            ],
            "predicate": {
                "buildDefinition": {
                    "buildType":
                        "https://figma-forge.io/build-type/figma-library@v1",
                    "externalParameters": {
                        "command": self.invocation_command,
                    },
                    "internalParameters": dict(self.invocation_environment),
                    "resolvedDependencies": [
                        {
                            "uri": f"git+{self.source_repository}"
                                   f"@{self.source_commit}"
                            if self.source_commit else self.source_repository,
                            "digest": (
                                {"gitCommit": self.source_commit}
                                if self.source_commit else {}
                            ),
                        }
                    ] if self.source_repository else [],
                },
                "runDetails": {
                    "builder": {"id": self.builder_id},
                    "metadata": {
                        "invocationId": "",
                        "startedOn": self.build_started_at,
                        "finishedOn": self.build_finished_at,
                    },
                },
            },
        }

    def to_json(self, *, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False) + "\n"


@dataclass
class SignedManifest:
    """Output of :func:`sign_manifest` — manifest + provenance + signature."""

    manifest: BundleManifest
    provenance: ProvenanceAttestation
    signature_bundle: bytes  # Sigstore signing bundle (JSON, encoded)
    signing_mode: Literal["sigstore-keyless", "sha256-only"]
    signer_identity: str
    signed_at: str

    def write_artifacts(self, output_dir: Path) -> dict[str, Path]:
        """Write the three artifacts to ``output_dir``.

        Returns a dict mapping logical name → file path. Always
        writes ``manifest.json`` and ``provenance.json``; writes
        ``signature.sigstore`` for both sigstore-keyless and
        sha256-only modes (the file extension is preserved to keep
        downstream tooling consistent regardless of signing mode).
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        out: dict[str, Path] = {}

        manifest_path = output_dir / "manifest.json"
        manifest_path.write_text(self.manifest.to_json(), encoding="utf-8")
        out["manifest"] = manifest_path

        provenance_path = output_dir / "provenance.json"
        provenance_path.write_text(self.provenance.to_json(), encoding="utf-8")
        out["provenance"] = provenance_path

        # Always emit the signature payload — sha256-only mode is still
        # a verifiable signature shape, just without Sigstore.
        sig_path = output_dir / "signature.sigstore"
        sig_path.write_bytes(self.signature_bundle)
        out["signature"] = sig_path
        return out


@dataclass
class VerificationResult:
    """Output of :func:`verify_manifest`."""

    is_valid: bool
    failed_checks: list[str] = field(default_factory=list)
    passed_checks: list[str] = field(default_factory=list)
    verified_identity: str = ""
    verification_timestamp: str = ""

    def __bool__(self) -> bool:
        return self.is_valid


# ---------------------------------------------------------------------------
# Build manifest (v1.0 API name; thin wrapper over v0.3.0 bundle_manifest)
# ---------------------------------------------------------------------------

def build_bundle_manifest(library_dir: Path) -> BundleManifest:
    """Build a schema-v1.0 bundle manifest for ``library_dir``.

    Stable v1.0 public API. Thin wrapper around the implementation
    in :func:`bundle_manifest.build_manifest`, exposed here under the
    canonical name so downstream users have a single import target.
    """
    raw_payload = _build_inventory(library_dir)
    return BundleManifest(payload=raw_payload)


# ---------------------------------------------------------------------------
# Sign manifest
# ---------------------------------------------------------------------------

def sign_manifest(
    manifest: BundleManifest,
    *,
    identity: str,
    source_repository: str = "",
    source_commit: str = "",
    builder_id: str = "figma-forge cli",
    invocation_command: str = "",
    invocation_environment: dict[str, str] | None = None,
    sign_mode: Literal["sigstore-keyless", "sha256-only", "auto"] = "auto",
) -> SignedManifest:
    """Sign a bundle manifest and produce a SLSA provenance attestation.

    Parameters
    ----------
    manifest:
        The :class:`BundleManifest` produced by
        :func:`build_bundle_manifest`.
    identity:
        The signer identity (email address for Sigstore keyless flow,
        or a free-form descriptor for sha256-only mode).
    source_repository, source_commit:
        Materials for the SLSA provenance ``resolvedDependencies``
        field. When provided, downstream verifiers can pin the build
        to a specific commit.
    builder_id:
        SLSA ``runDetails.builder.id``. Defaults to ``"figma-forge cli"``.
        In GitHub Actions, set to the workflow ref (e.g.
        ``"https://github.com/<org>/<repo>/.github/workflows/release.yml@refs/heads/main"``).
    invocation_command:
        The full command line that produced the bundle. Goes into
        SLSA ``externalParameters.command``.
    invocation_environment:
        Sanitized environment variables that influenced the build
        (e.g. ``{"PYTHON_VERSION": "3.12.3"}``). Goes into SLSA
        ``internalParameters``. Do **not** include secrets.
    sign_mode:
        ``"sigstore-keyless"`` — require Sigstore (raises if not
        installed). ``"sha256-only"`` — skip cryptographic signing
        and emit only the manifest + provenance (suitable for
        air-gapped builds). ``"auto"`` (default) — use Sigstore when
        available, fall back to sha256-only otherwise.

    Returns
    -------
    SignedManifest
        Contains the manifest, the SLSA provenance, and (in
        sigstore-keyless mode) the encoded Sigstore signing bundle.
    """
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    provenance = ProvenanceAttestation(
        bundle_manifest_hash=manifest.manifest_hash(),
        builder_id=builder_id,
        invocation_command=invocation_command,
        invocation_environment=dict(invocation_environment or {}),
        source_repository=source_repository,
        source_commit=source_commit,
        build_started_at=now,
        build_finished_at=now,
    )

    # Determine signing mode
    if sign_mode == "sigstore-keyless":
        effective_mode = "sigstore-keyless"
    elif sign_mode == "sha256-only":
        effective_mode = "sha256-only"
    else:  # auto
        effective_mode = "sigstore-keyless" if _sigstore_available() else "sha256-only"

    if effective_mode == "sigstore-keyless":
        if not _sigstore_available():
            raise RuntimeError(
                "sigstore-keyless signing requested but the 'sigstore' "
                "package is not installed. Run: pip install sigstore"
            )
        signature_bundle = _sigstore_sign_keyless(provenance.to_json())
    else:
        # Air-gapped fallback: signature bundle is the canonical
        # SHA-256 of the provenance payload, encoded as a trivial
        # JSON wrapper for symmetry with sigstore output.
        prov_hash = hashlib.sha256(provenance.to_json().encode("utf-8")).hexdigest()
        signature_bundle = json.dumps({
            "kind": "sha256-only",
            "manifest_hash": manifest.manifest_hash(),
            "provenance_hash": prov_hash,
            "signer_identity": identity,
            "signed_at": now,
        }, indent=2).encode("utf-8")

    return SignedManifest(
        manifest=manifest,
        provenance=provenance,
        signature_bundle=signature_bundle,
        signing_mode=effective_mode,
        signer_identity=identity,
        signed_at=now,
    )


# ---------------------------------------------------------------------------
# Verify manifest
# ---------------------------------------------------------------------------

def verify_manifest(
    *,
    manifest_path: Path,
    provenance_path: Path,
    signature_path: Path | None = None,
    expected_identity: str = "",
    expected_oidc_issuer: str = "",
    library_dir: Path | None = None,
) -> VerificationResult:
    """Verify a signed bundle manifest end-to-end.

    Three layers of validation, all of which must pass for the
    overall result to be ``is_valid=True``:

    1. **Manifest integrity** — re-hash the on-disk manifest and
       confirm it matches the SHA-256 declared in the provenance.
    2. **Bundle integrity** — when ``library_dir`` is provided, walk
       the bundle and recompute each file's SHA-256; confirm every
       file in the manifest is on disk and unmodified.
    3. **Signature** — when a signature file is present and
       ``sigstore`` is installed, verify the Sigstore bundle against
       the expected signer identity. When the signature file is
       ``sha256-only`` mode, verify the recorded hashes match.

    Returns a :class:`VerificationResult` with detailed pass/fail
    lists. Use ``bool(result)`` for a quick check.
    """
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    result = VerificationResult(
        is_valid=False, verification_timestamp=now,
        verified_identity=expected_identity,
    )

    # Layer 1 — Manifest integrity
    try:
        manifest_text = manifest_path.read_text(encoding="utf-8")
        manifest_dict = json.loads(manifest_text)
        provenance_dict = json.loads(provenance_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        result.failed_checks.append(f"manifest/provenance load: {e}")
        return result

    manifest = BundleManifest(payload=manifest_dict)
    expected_hash = manifest.manifest_hash()
    declared_hash = (
        provenance_dict.get("subject", [{}])[0]
        .get("digest", {}).get("sha256", "")
    )
    if expected_hash != declared_hash:
        result.failed_checks.append(
            f"manifest hash mismatch: re-computed {expected_hash[:12]}…, "
            f"provenance declared {declared_hash[:12]}…"
        )
    else:
        result.passed_checks.append("manifest integrity (SHA-256 matches)")

    # Layer 2 — Bundle integrity (per-file SHA-256)
    if library_dir is not None:
        bundle_failures = _verify_bundle_integrity(manifest_dict, library_dir)
        if bundle_failures:
            for f in bundle_failures:
                result.failed_checks.append(f"bundle integrity: {f}")
        else:
            result.passed_checks.append(
                f"bundle integrity ({manifest.file_count} files unmodified)"
            )

    # Layer 3 — Signature
    if signature_path is not None and signature_path.exists():
        sig_bytes = signature_path.read_bytes()
        try:
            sig_kind = json.loads(sig_bytes.decode("utf-8")).get("kind", "")
        except (json.JSONDecodeError, UnicodeDecodeError):
            sig_kind = "sigstore"  # binary Sigstore bundle — not JSON

        if sig_kind == "sha256-only":
            sig_obj = json.loads(sig_bytes.decode("utf-8"))
            if sig_obj.get("manifest_hash") != expected_hash:
                result.failed_checks.append(
                    "sha256-only signature: manifest hash mismatch"
                )
            else:
                result.passed_checks.append("sha256-only signature integrity")
            if expected_identity and sig_obj.get("signer_identity") != expected_identity:
                result.failed_checks.append(
                    f"sha256-only signature: identity mismatch "
                    f"(expected {expected_identity}, got "
                    f"{sig_obj.get('signer_identity')})"
                )
            else:
                if expected_identity:
                    result.passed_checks.append(
                        f"sha256-only signature: identity matches {expected_identity}"
                    )
        else:
            # Sigstore keyless verification
            if not _sigstore_available():
                result.failed_checks.append(
                    "sigstore-keyless signature present but sigstore "
                    "package not installed; cannot verify"
                )
            elif not expected_identity:
                result.failed_checks.append(
                    "sigstore-keyless verification requires expected_identity"
                )
            else:
                ok, err = _sigstore_verify_keyless(
                    sig_bytes, provenance_path.read_bytes(),
                    expected_identity=expected_identity,
                    expected_oidc_issuer=expected_oidc_issuer,
                )
                if ok:
                    result.passed_checks.append(
                        f"sigstore-keyless signature: verified for "
                        f"{expected_identity}"
                    )
                else:
                    result.failed_checks.append(
                        f"sigstore-keyless signature: {err}"
                    )
    else:
        result.passed_checks.append(
            "signature: not provided (manifest-only verification)"
        )

    result.is_valid = not result.failed_checks
    return result


# ---------------------------------------------------------------------------
# Helpers — Sigstore wrappers (graceful fallback when sigstore absent)
# ---------------------------------------------------------------------------

def _sigstore_available() -> bool:
    try:
        import sigstore  # noqa: F401
    except ImportError:
        return False
    return True


def _sigstore_sign_keyless(payload: str) -> bytes:
    """Sign ``payload`` with Sigstore keyless mode.

    Uses the ambient OIDC token (GitHub Actions workflow identity,
    or interactive flow). Returns the bundle JSON bytes.
    """
    from sigstore.sign import Signer  # type: ignore[import-not-found]
    from sigstore.oidc import detect_credential  # type: ignore[import-not-found]
    try:
        from sigstore.sign import SigningContext  # type: ignore[import-not-found]
    except ImportError:
        SigningContext = None  # type: ignore[assignment]

    cred = detect_credential()
    if cred is None:
        raise RuntimeError(
            "no OIDC credential detected; run in a GitHub Actions "
            "workflow with id-token: write, or set "
            "SIGSTORE_IDENTITY_TOKEN env var."
        )

    if SigningContext is not None:
        # sigstore-python 3.x+ flow
        ctx = SigningContext.production()
        with ctx.signer(cred) as signer:
            result = signer.sign_artifact(payload.encode("utf-8"))
        return result.to_json().encode("utf-8")
    else:
        # Legacy flow
        signer = Signer.production()
        result = signer.sign(payload.encode("utf-8"), cred)
        return result.to_bundle().to_json().encode("utf-8")


def _sigstore_verify_keyless(
    signature_bundle: bytes,
    artifact: bytes,
    *,
    expected_identity: str,
    expected_oidc_issuer: str,
) -> tuple[bool, str]:
    """Verify a Sigstore bundle. Returns ``(ok, error_message)``."""
    try:
        from sigstore.verify import Verifier  # type: ignore[import-not-found]
        from sigstore.verify.policy import Identity  # type: ignore[import-not-found]
        from sigstore.models import Bundle  # type: ignore[import-not-found]
    except ImportError as e:
        return False, f"sigstore imports failed: {e}"

    try:
        bundle = Bundle.from_json(signature_bundle.decode("utf-8"))
    except Exception as e:
        return False, f"signature bundle parse: {e}"

    verifier = Verifier.production()
    issuer = expected_oidc_issuer or "https://accounts.google.com"
    policy = Identity(identity=expected_identity, issuer=issuer)
    try:
        verifier.verify_artifact(input_=artifact, bundle=bundle, policy=policy)
        return True, ""
    except Exception as e:
        return False, str(e)


# ---------------------------------------------------------------------------
# Helpers — bundle integrity check
# ---------------------------------------------------------------------------

def _verify_bundle_integrity(
    manifest_payload: dict, library_dir: Path
) -> list[str]:
    """Re-hash every file in the manifest; return list of failures."""
    failures: list[str] = []
    files = manifest_payload.get("files", []) or []
    for entry in files:
        rel = entry.get("path")
        declared_hash = entry.get("sha256")
        if not isinstance(rel, str) or not isinstance(declared_hash, str):
            continue
        path = library_dir / rel
        if not path.exists():
            failures.append(f"missing file: {rel}")
            continue
        actual = _sha256_of(path)
        if actual != declared_hash:
            failures.append(
                f"hash mismatch: {rel} "
                f"(expected {declared_hash[:12]}…, got {actual[:12]}…)"
            )
    return failures


def _sha256_of(path: Path, *, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            block = fh.read(chunk_size)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Public re-exports
# ---------------------------------------------------------------------------

__all__ = [
    "BundleManifest",
    "ProvenanceAttestation",
    "SignedManifest",
    "VerificationResult",
    "build_bundle_manifest",
    "sign_manifest",
    "verify_manifest",
]
