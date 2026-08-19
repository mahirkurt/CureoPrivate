#!/usr/bin/env python3
"""`programmatic_source_healthcheck.yaml` SÖZLEŞMESİNİN koşucusu.

O dosya kendi başlığında "bir koşucu DEĞİL, bir SÖZLEŞMEDİR" der — ve gerçekten
hiçbir uygulayıcısı yoktu. Sonuç: sözleşme her ucun nasıl yoklanacağını,
beklenen durum kodunu ve düşerse uygulanacak degrade davranışını tarif ediyor
ama HİÇBİRİ ölçülmüyordu. Ölü bir uç (2026-08-06 denetiminde bulunan 404
gibi) fark edilmeden aylarca durabiliyor; skill onu canlı sanıp
`mcp_verified` etiketini yanlış hesaplıyor.

Bu koşucu sözleşmeyi OLDUĞU GİBİ uygular: her ucun kendi `method` +
`expected_status` beyanını kullanır — kendi ölçütünü uydurmaz. Bir uç
beyanının dışına çıkarsa bulgu üretir; beyanına uyuyorsa (401 dâhil, çünkü
kapılı MCP uçları 401'i BEKLENEN olarak bildirir) temizdir.

`on_failure: degrade_and_label` sözleşmesi gereği bu koşucunun bulgusu
cureolex ÇIKTISINI durdurmaz — bakım sinyalidir. Bu yüzden varsayılan çıkış
kodu 0'dır; CI'da sertleştirmek için `--strict`.
"""
import ssl
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urljoin

import yaml

ROOT = Path(__file__).resolve().parents[2]
SPEC = (ROOT / "plugins" / "cureolex" / "skills" / "cureolex"
        / "programmatic_source_healthcheck.yaml")


def target_url(ep):
    """`base_url` + `health_path` — sözleşmenin YOKLAMA hedefi.

    `health_path` yok sayılırsa REST kökleri (api.fda.gov/, clinicaltrials.gov/
    api/v2/) ve /mcp altına mount edilmiş sunucular kaynaksız kök yolda 404
    döner; sağlıklı uç ÖLÜ raporlanır. `urljoin` hem '/mcp' (baştan eğik)
    hem 'studies?pageSize=1' (göreli) biçimini doğru birleştirir.
    """
    base = ep.get("base_url") or ep.get("url")
    hp = ep.get("health_path")
    return urljoin(base, hp) if hp else base


def probe(ep, defaults):
    url = target_url(ep)
    method = ep.get("method", "GET").upper()
    expect = ep.get("expected_status") or [200]
    timeout = ep.get("timeout_seconds", defaults.get("timeout_seconds", 15))
    ua = defaults.get("user_agent", "cureolex-healthcheck/1.0")
    # Sözleşme POST diyen uçlar MCP'dir; boş gövde yerine geçerli bir JSON-RPC
    # zarfı gider — aksi hâlde sağlıklı sunucu 400 döner ve sahte bulgu olur.
    data = None
    headers = {"User-Agent": ua}
    if method == "POST":
        data = (b'{"jsonrpc":"2.0","id":1,"method":"initialize","params":'
                b'{"protocolVersion":"2025-06-18","capabilities":{},'
                b'"clientInfo":{"name":"healthcheck","version":"1"}}}')
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json, text/event-stream"

    ctx = ssl.create_default_context()
    for attempt in range(1 + defaults.get("retries", 1)):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                code = r.status
                break
        except urllib.error.HTTPError as e:
            code = e.code
            # 5xx GEÇİCİDİR — yeniden denenmezse dalgalanan upstream (ölçüldü:
            # clinicaltrials.gov aynı dakika içinde 200 ve 500 döndürdü) kalıcı
            # bir sözleşme ihlali gibi raporlanır. 4xx kalıcıdır, denenmez.
            if code >= 500 and attempt < defaults.get("retries", 1):
                continue
            break
        except Exception as e:
            code, err = None, type(e).__name__
            if attempt == defaults.get("retries", 1):
                return ep["id"], None, err
    else:
        return ep["id"], None, "retries_exhausted"
    return ep["id"], code, None


def main(strict=False):
    spec = yaml.safe_load(SPEC.read_text(encoding="utf-8"))
    defaults, eps = spec.get("defaults", {}), spec["endpoints"]
    by_id = {e["id"]: e for e in eps}

    with ThreadPoolExecutor(max_workers=8) as ex:
        rows = list(ex.map(lambda e: probe(e, defaults), eps))

    bad = []
    print(f"KAYNAK UCU SAĞLIK KOŞUMU — sözleşme v{spec.get('healthcheck_version')}, "
          f"{len(eps)} uç\n")
    for eid, code, err in sorted(rows):
        ep = by_id[eid]
        expect = ep.get("expected_status") or [200]
        ok = code in expect
        mark = "✓" if ok else "✗"
        got = err or code
        print(f"  {mark}  {eid:26} {ep.get('method','GET'):5} "
              f"beklenen {str(expect):16} alınan {got}")
        if not ok:
            bad.append((eid, got, expect, ep.get("fallback", "")))
    print()
    if bad:
        print(f"SÖZLEŞME DIŞI UÇ: {len(bad)}")
        for eid, got, expect, fb in bad:
            print(f"  · {eid}: {got} ∉ {expect}")
            if fb:
                print(f"    degrade sözleşmesi: {fb[:110]}")
        # Varsayılan 0 — sözleşmenin kendi `on_failure: degrade_and_label`
        # kuralı çıktıyı durdurmamayı emreder. --strict CI içindir.
        return 1 if strict else 0
    print(f"TÜM UÇLAR SÖZLEŞMEYE UYGUN — {len(eps)} uç")
    return 0


if __name__ == "__main__":
    sys.exit(main(strict="--strict" in sys.argv))
