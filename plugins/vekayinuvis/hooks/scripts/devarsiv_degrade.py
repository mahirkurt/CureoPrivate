#!/usr/bin/env python3
"""vekayinuvis PostToolUse/PostToolUseFailure degrade hook — devlet-arşivleri oturum-düşüşü
re-login runbook'u.

Bir `devarsiv_*` aracı `session_required` (canlı katalog oturumu yok) ya da `viewer_runtime_error`
(SatınAldıklarım viewer'ı Runtime Error 500 ≈ oturum süresi doldu) sinyali döndürdüğünde, model
BEKLEMEK yerine HP noVNC re-login akışını (K5 runbook'un kompakt 6-satır hâli) additionalContext
olarak alır — degrade-devam kuralı: yerel arşiv (list_archive/get_archive_page) + anamnesis +
akademik katman ÇALIŞMAYA DEVAM EDER, rapor akışı durmaz.

Hem `PostToolUse` hem (kurulu Claude Code sürümü tanıyorsa) `PostToolUseFailure` payload'ıyla
çalışacak şekilde alan-yokluğuna toleranslıdır (.get zinciri; tool_response/tool_result/
tool_error/error/message alanlarının hangisi gelirse gelsin taranır). Advisory only — asla
bloklamaz. Fail-open: hiçbir koşulda exception fırlatmaz, aksi hâlde sessiz "{}" döner.
"""
import json
import sys

TRIGGER_SIGNALS = ("session_required", "viewer_runtime_error")

RUNBOOK = (
    "[vekayinuvis] devlet-arşivleri oturumu düştü (session_required / viewer Runtime Error 500 "
    "≈ oturum süresi doldu → BEKLEME değil re-login gerekir):\n"
    "1. HP: sudo systemctl restart devarsiv-chrome\n"
    "2. noVNC: https://devarsiv-vnc.cureonics.com/vnc.html (Cloudflare Access, @cureonics.com OTP)\n"
    "3. Tarayıcıda reCAPTCHA çöz + T.C. Kimlik ile giriş (Doppler DEVLET_ARSIVLERI_*)\n"
    "4. devarsiv_session_status → alive:true doğrula\n"
    "5. Degrade-devam: katalog düşükken yerel arşiv (list_archive/get_archive_page) + anamnesis + "
    "akademik katman ÇALIŞMAYA DEVAM EDER — rapor akışını durdurma, \"katalog doğrulaması "
    "bekliyor\" şerhi düş."
)


def main():
    try:
        data = json.load(sys.stdin)

        tool = str(data.get("tool_name", "") or "")
        base = tool.split("__")[-1] if tool else ""
        if not base.startswith("devarsiv_"):
            print("{}")
            return

        haystack_parts = []
        for key in ("tool_response", "tool_result", "tool_error", "error", "message"):
            val = data.get(key)
            if val is None:
                continue
            if isinstance(val, str):
                haystack_parts.append(val)
            else:
                try:
                    haystack_parts.append(json.dumps(val, ensure_ascii=False))
                except Exception:
                    haystack_parts.append(str(val))
        haystack = " ".join(haystack_parts)

        if not any(sig in haystack for sig in TRIGGER_SIGNALS):
            print("{}")
            return

        event_name = data.get("hook_event_name") or "PostToolUse"
        print(json.dumps({
            "hookSpecificOutput": {"hookEventName": event_name, "additionalContext": RUNBOOK},
            "systemMessage": RUNBOOK,
        }))
    except Exception:
        print("{}")


if __name__ == "__main__":
    main()
