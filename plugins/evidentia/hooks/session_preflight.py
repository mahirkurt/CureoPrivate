#!/usr/bin/env python3
"""evidentia SessionStart preflight — credential-free integration check.

evidentia's six gated self-host connectors resolve their Bearer keys from the process env
(Doppler-injected via `doppler run -- claude`). If a key is absent, that connector silently
401s at call time. This hook surfaces the gap ONCE at session start with the exact fix — and
stays SILENT when every key is present (the normal `doppler run` case), so it adds no noise to
non-evidentia sessions.

Emits SessionStart additionalContext only when ≥1 gated key is missing. Fail-open on any error.
"""
import json
import os
import sys

# Gated connector → env var (see docs/EVIDENTIA-KURULUM-VE-KEYLER.md).
GATED = {
    "openathens": "OPENATHENS_MCP_API_KEY",
    "anamnesis": "ANAMNESIS_MCP_API_KEY",
    "openfda": "OPENFDA_MCP_API_KEY",
    "evidentia-kb": "EVIDENTIA_KB_MCP_API_KEY",
    "annas-reader": "ANNAS_MCP_API_KEY",
    "yok-akademik": "YOK_AKADEMIK_MCP_API_KEY",
}


def main():
    try:
        sys.stdin.read()  # drain stdin (SessionStart payload), unused
    except Exception:
        pass

    missing = [f"{c} (${v})" for c, v in GATED.items() if not os.environ.get(v)]
    if not missing:
        sys.exit(0)  # all present → silent

    ctx = (
        "[evidentia preflight] Gated self-host connector key(ler)i süreç ortamında YOK: "
        + ", ".join(missing)
        + ". Bu connector'lar çağrı anında 401 döner (openathens=tam-metin Tier 3, "
        "anamnesis=RAG/GraphRAG substratı önemlidir). Çözüm: oturumu `doppler run -p cureohub "
        "-c dev_personal -- claude` ile başlat → tüm ${VAR}'lar otomatik enjekte olur, ek "
        "credential girmeye gerek yok. (Keyless connector'lar — pipeworx gateway'leri, drugddx, "
        "titck-cache — etkilenmez.)"
    )
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": ctx}
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
