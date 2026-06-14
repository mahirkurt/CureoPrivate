# Supply-Chain Attestation (v1.0.0)

> Status: v1.0.0 GA · stable public API · SLSA v1.0 provenance shape

`figma-forge` v1.0.0 ships cryptographic supply-chain provenance for
design-system library bundles. Three artifacts every release should
attach to GitHub Releases / S3 / your artifact server:

1. `manifest.json` — schema-v1.0 SHA-256 inventory (file count, total
   size, per-file hash)
2. `provenance.json` — [SLSA v1.0](https://slsa.dev/spec/v1.0/provenance)
   provenance attestation declaring builder identity, source repo +
   commit, invocation command
3. `signature.sigstore` — Sigstore keyless signing bundle (or
   sha256-only fallback when Sigstore unavailable)

## Why this matters

A design system library is a **trust boundary**. Consumers (apps,
microsites, internal tooling) build their UI on top of it. If an
attacker substitutes a malicious bundle for the legitimate one, every
downstream consumer is compromised. Supply-chain attestation lets
consumers verify cryptographically that the bundle they downloaded:

- Was produced by the legitimate builder (e.g. the `main` branch
  workflow of the official repo)
- Matches a specific source commit
- Has not been modified since publication

## End-to-end signing workflow

```bash
# 1. Build the bundle (assumes you already have a Figma library bundle)
# 2. Sign it (CI-friendly, OIDC-keyless)
python3 scripts/sign.py \
    --library-dir . \
    --output-dir signed-release/ \
    --identity "https://github.com/myorg/figma-library/.github/workflows/release.yml@refs/tags/v1.0.0" \
    --source-repository "https://github.com/myorg/figma-library" \
    --source-commit "$GITHUB_SHA" \
    --builder-id "https://github.com/myorg/figma-library/.github/workflows/release.yml@refs/tags/v1.0.0" \
    --sign-mode sigstore-keyless

# Outputs:
#   signed-release/manifest.json
#   signed-release/provenance.json
#   signed-release/signature.sigstore
```

## End-to-end verification workflow

```bash
# Consumer downloads all three files + bundle
# Then runs:
python3 scripts/verify.py \
    --manifest manifest.json \
    --provenance provenance.json \
    --signature signature.sigstore \
    --library-dir . \
    --expected-identity 'https://github.com/myorg/figma-library/.github/workflows/release.yml@refs/tags/v1.0.0'

# Exit 0 → safe to consume
# Exit 1 → verification failure, refuse to consume
```

## Three-layer verification

| Layer | Check                                                  | When checked |
|-------|--------------------------------------------------------|--------------|
| 1     | Manifest SHA-256 matches `subject[0].digest.sha256` in provenance | always |
| 2     | Every file in the bundle re-hashes to the manifest's recorded SHA-256 | when `--library-dir` provided |
| 3     | Sigstore signature verifies against the expected OIDC identity | when `--signature` provided + sigstore installed |

A failure in any layer fails the overall verification.

## SLSA v1.0 provenance shape

The `provenance.json` produced by `sign_manifest` follows the SLSA
v1.0 attestation shape:

```jsonc
{
  "_type": "https://in-toto.io/Statement/v1",
  "predicateType": "https://slsa.dev/provenance/v1",
  "subject": [
    {
      "name": "bundle-manifest.json",
      "digest": { "sha256": "73a3df74e40632b0…" }
    }
  ],
  "predicate": {
    "buildDefinition": {
      "buildType": "https://figma-forge.io/build-type/figma-library@v1",
      "externalParameters": {
        "command": "python3 scripts/sign.py --library-dir . ..."
      },
      "internalParameters": {
        "PYTHON_VERSION": "3.12",
        "GITHUB_REPOSITORY": "myorg/figma-library",
        "GITHUB_WORKFLOW": "release"
      },
      "resolvedDependencies": [
        {
          "uri": "git+https://github.com/myorg/figma-library@a1b2c3…",
          "digest": { "gitCommit": "a1b2c3d4e5f6…" }
        }
      ]
    },
    "runDetails": {
      "builder": {
        "id": "https://github.com/myorg/figma-library/.github/workflows/release.yml@refs/tags/v1.0.0"
      },
      "metadata": {
        "invocationId": "",
        "startedOn": "2026-05-27T05:08:28.907501Z",
        "finishedOn": "2026-05-27T05:08:28.907501Z"
      }
    }
  }
}
```

This is the canonical shape consumed by `sigstore-verifier`,
`in-toto`, `slsa-verifier`, and any other SLSA-compliant tooling.

## Sigstore keyless flow

Sigstore keyless signing eliminates long-lived private keys. The
workflow:

1. Builder requests an OIDC identity token from the issuer
   (GitHub Actions, Google Cloud, etc.)
2. Sigstore Fulcio issues a short-lived (10-minute) X.509 certificate
   binding the identity to a freshly-generated keypair
3. Builder signs the artifact with the private half
4. Signature + certificate + transparency log entry → bundle
5. Sigstore Rekor logs the signing event to a public transparency log
6. Verifier checks: certificate signed by Fulcio root, identity
   matches expected, Rekor log entry exists, certificate covers the
   signing time

Private keys never leave the builder's process. The X.509 cert
expires in 10 minutes. The transparency log is public and append-only.

## sha256-only fallback

When Sigstore is unavailable (air-gapped builds, classified
environments, sandboxes without internet), `sign_manifest(...,
sign_mode="sha256-only")` produces a signature shape with:

```json
{
  "kind": "sha256-only",
  "manifest_hash": "73a3df74e40632b0…",
  "provenance_hash": "fa646833e11448a8…",
  "signer_identity": "release-bot@example.com",
  "signed_at": "2026-05-27T05:08:28.907501Z"
}
```

The verifier cross-checks the recorded hashes against fresh
recomputations. Identity is **declared**, not cryptographically
proven — this mode trusts the source channel (e.g., signed git
commit) to anchor the identity. Suitable as a transitional mode
or for fully air-gapped environments where you trust the build
host transitively.

## CI integration

A reference GitHub Actions workflow template is shipped at:

```
templates/.github/workflows/release.yml
```

Copy to your design-system repository, adjust the identity
expression, and tagging a release (`git tag v1.0.0 && git push
--tags`) triggers the workflow.

Key permission requirement:

```yaml
permissions:
  contents: read
  id-token: write   # MANDATORY for Sigstore keyless flow
```

`id-token: write` is what allows the workflow to request the OIDC
token Sigstore needs.

## Verification at scale — Roche RDS example

For Roche's 5 RDS libraries (Foundations, Components, Patterns,
Icons, Data Visualization), each release would emit its own signed
bundle. A consumer pipeline can verify all five in one batch:

```bash
for lib in foundations components patterns icons data-viz; do
  python3 scripts/verify.py \
    --manifest "rds-$lib/manifest.json" \
    --provenance "rds-$lib/provenance.json" \
    --signature "rds-$lib/signature.sigstore" \
    --library-dir "rds-$lib/" \
    --expected-identity 'https://github.com/Roche/rds/.github/workflows/release.yml@refs/tags/4.24' \
    || exit 1
done
echo "✓ All 5 RDS libraries verified"
```

Any drift (modified file, regenerated bundle outside CI, identity
substitution) fails the verifier. This is the **gate** that closes
the supply-chain trust loop end-to-end.
