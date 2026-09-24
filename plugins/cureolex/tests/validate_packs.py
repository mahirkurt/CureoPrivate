#!/usr/bin/env python3
"""cureolex yargı bölgesi paketi doğrulayıcısı — AĞ ERİŞİMİ YOK, deterministik.

`jurisdictions/<kod>/jurisdiction_pack.yaml` dosyalarını ve onlara bağlı sözleşmeleri
denetler. run_suites.py davranış ŞARTNAMELERİNİ denetler; bu dosya PAKET VERİSİNİ denetler.

  [P1] ŞEMA          her paket jurisdiction_pack.schema.json'dan geçer
  [P2] YAYIM KURALI  active ⇒ wire'lı S1 bağlayıcısı + uzman paneli (completed|grandfathered)
  [P3] FİLO          connectors[].server fleet.yaml'da sunucu ya da companion olarak VAR
  [P4] SAHİPLİK      references/ + templates/ altındaki her dosya TAM OLARAK BİR yerde:
                     bir paketin owned_files'ı ya da core_files.yaml — sahipsiz/çift = ihlal
  [P5] PARÇA AYNASI  paketin shards.S1 listesi fleet.yaml `shard` alanıyla aynı küme
  [P6] RUBRİK        legistic_rubric_families: K-1…K-21 her biri tek birincil aileye eşli;
                     paket ailelerinin anahtarları bilinen aileler; beyan edilen K-n o aileye ait
  [P7] KOD           paket kodu ISO deseninde; ayrılmış istisna (UK) paket kodu olamaz;
                     ORG: kodları ISO alanıyla çakışmaz; eski takma adlar çözülür
  [P8] MOD ADLARI    mode_aliases hedefleri kanonik mod; gate_params anahtarları G0–G11
  [P9] ALTIN VAKALAR paketin golden_cases dosyası var; `pack_check` blokları deterministik
                     koşulur (G11 statik ihlal sayısı · güven tavanı)
  [P10] SÖZLEŞME     connector_contract.reference_mappings'teki her araç filoda tools_used

`tavan_hesapla` ve `g11_ihlalleri` modül düzeyi fonksiyonlardır — run_suites ve hook'lar
aynı mantığı yeniden yazmadan içe aktarabilir.

Kullanım:
  python3 tests/validate_packs.py            # plugin kökünden ya da tests/ içinden
  python3 tests/validate_packs.py --quiet
Çıkış: 0 temiz · 1 ihlal.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
JUR = ROOT / "jurisdictions"
SCHEMA_DIR = JUR / "_schema"

# Kanonik modlar (yargı bölgesinden bağımsız adlar). Ulusal usul adları paketlerin
# mode_aliases alanından gelir (ör. TR: TBMM_KANUN_TEKLIFI → PARLIAMENTARY_BILL).
CANONICAL_MODES = {
    "DRAFT", "AMEND", "ANALYZE", "COMPLY", "OPINE", "RIA", "COMPARATIVE_LAW",
    "PARLIAMENTARY_BILL", "EX_POST_EVALUATION",
    "REGULATORY_MATURITY", "TRANSPOSITION", "RELIANCE_FRAMEWORK",
}
GATES = {f"G{i}" for i in range(12)}
ISO_RE = re.compile(r"^[A-Z]{2}(?:-[A-Z0-9]{1,3})?$")
ORG_RE = re.compile(r"^ORG:[A-Z][A-Z0-9-]{1,15}$")
ORDER = ["HIGH", "MODERATE", "LOW"]
PANEL_OK = {"completed", "grandfathered"}


def _yaml(p: Path):
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def load_packs():
    """{kod: (yol, paket)} — _schema dizini hariç her alt dizin bir pakettir."""
    packs = {}
    for p in sorted(JUR.glob("*/jurisdiction_pack.yaml")):
        doc = _yaml(p)
        code = (doc.get("jurisdiction") or {}).get("code", p.parent.name.upper())
        packs[code] = (p, doc)
    return packs


def load_fleet():
    fleet = _yaml(ROOT / "fleet.yaml")
    servers = {s["name"]: s for s in fleet["servers"]}
    companions = {c["name"] for c in fleet.get("companions", [])}
    return fleet, servers, companions


def mode_aliases(packs) -> dict:
    """Tüm paketlerin ulusal-ad → kanonik-mod eşlemesi (+ tarihsel kısa ad)."""
    out = {"EX_POST": "EX_POST_EVALUATION"}
    for _, (_, doc) in packs.items():
        out.update(doc.get("mode_aliases") or {})
    return out


def normalize_code(code: str, codes: dict) -> str:
    """3.x eski takma adlarını (WHO, UK) 4.0 kanonik koduna çevirir."""
    return (codes.get("legacy_aliases") or {}).get(code, code)


# ───────────────────────────── güven tavanı ─────────────────────────────
def s1_wired(pack) -> bool:
    return any(c.get("role") == "primary_legislation" and c.get("status") == "wired"
               for c in pack.get("connectors", []))


def tavan_hesapla(pack, mode=None, output_language=None, rules_doc=None):
    """Paketin yetenek bayraklarından güven TAVANINI hesapla.

    Döner: (tavan, [uygulanan kural kimlikleri]). Kurallar confidence_ceiling_rules.yaml'dan
    okunur — mantık burada, kurallar veri dosyasında yaşar. Tavan uygulanan kuralların EN
    DÜŞÜĞÜDÜR; hiçbiri uygulanmazsa HIGH.
    """
    rules_doc = rules_doc or _yaml(SCHEMA_DIR / "confidence_ceiling_rules.yaml")
    order = rules_doc.get("order", ORDER)
    caps = pack.get("capabilities", {})
    authentic = {l["code"] for l in pack.get("languages", []) if l.get("authentic")}
    applied = []
    for r in rules_doc["rules"]:
        w = r["when"]
        hit = False
        if "capability" in w:
            hit = bool(caps.get(w["capability"], {}).get("value")) == bool(w["value"])
        elif "pack_status" in w:
            hit = pack.get("status") == w["pack_status"]
        elif "s1_connector_wired" in w:
            hit = s1_wired(pack) == bool(w["s1_connector_wired"])
        elif "legistic_profile_verified" in w:
            hit = bool(pack.get("legistic_profile", {}).get("verified")) == bool(w["legistic_profile_verified"])
        if not hit:
            continue
        modes = r.get("applies_to_modes")
        if modes and mode and mode not in modes:
            continue
        if r.get("applies_when") == "output_language_not_authentic":
            # Dil verilmediyse ya da geçerli dillerden biriyse kural uygulanmaz.
            if not output_language or output_language in authentic:
                continue
        applied.append(r["id"])
    ceiling = "HIGH"
    for r in rules_doc["rules"]:
        if r["id"] in applied and order.index(r["ceiling"]) > order.index(ceiling):
            ceiling = r["ceiling"]
    return ceiling, applied


# ───────────────────────────── G11 statik denetimi ─────────────────────────────
def g11_ihlalleri(ledger: dict, packs: dict, codes: dict) -> list:
    """Kanıt defterinde YANLIŞ ROL ile kaydedilmiş yabancı kaynakları bul.

    Kural (G11): bir kanıt `binding` rolünü yalnız ev bölgesinin kendi normu için taşıyabilir.
    İstisna — ev bölgesi AB üyesiyse ve paket bunu gate_params.G11.eu_member ile beyan
    ediyorsa, EU kaynaklı norm binding olabilir. Başka her yabancı kaynak binding ise ihlaldir.
    Alt birim (DE-BY) üst birimin (DE) binding normu SAYILMAZ, tersi de.
    """
    home = normalize_code(ledger.get("home_jurisdiction") or "", codes)
    if not home:
        return []
    pack = (packs.get(home) or (None, {}))[1]
    eu_member = bool(((pack.get("gate_params") or {}).get("G11") or {}).get("eu_member"))
    out = []
    for e in ledger.get("entries", []):
        j = e.get("jurisdiction")
        if not j:
            continue
        j = normalize_code(j, codes)
        role = e.get("jurisdiction_role")
        if j == home or role != "binding":
            continue
        if j == "EU" and eu_member:
            continue
        out.append(f"{e.get('claim_id')}: {j} kaynağı {home} çıktısında 'binding' — "
                   f"doğru rol transposition_source / comparative_benchmark / treaty_obligation")
    return out


# ───────────────────────────── denetimler ─────────────────────────────
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="cureolex yargı bölgesi paketi doğrulayıcısı")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args(argv)

    try:
        import jsonschema
    except ImportError:
        jsonschema = None

    issues = []                    # (bağlam, mesaj)
    packs = load_packs()
    fleet, servers, companions = load_fleet()
    codes = _yaml(SCHEMA_DIR / "supranational_codes.yaml")
    rubric = _yaml(SCHEMA_DIR / "legistic_rubric_families.yaml")
    rules_doc = _yaml(SCHEMA_DIR / "confidence_ceiling_rules.yaml")
    contract = _yaml(SCHEMA_DIR / "connector_contract.yaml")
    core = _yaml(JUR / "core_files.yaml")
    schema = json.loads((SCHEMA_DIR / "jurisdiction_pack.schema.json").read_text(encoding="utf-8"))

    if not packs:
        issues.append(("PAKET", "jurisdictions/ altında hiç paket yok"))

    families = set(rubric.get("families", {}))
    r6b = rubric.get("r6b_mapping", {})
    aliases = mode_aliases(packs)
    rows = []

    # [P6a] Rubrik eşlemesi — K-1…K-21 tam ve tek birincil aileli.
    expected_k = {f"K-{i}" for i in range(1, 22)}
    if set(r6b) != expected_k:
        issues.append(("RUBRİK", f"r6b_mapping K-1…K-21 değil: eksik {sorted(expected_k - set(r6b))} "
                                 f"fazla {sorted(set(r6b) - expected_k)}"))
    for k, m in r6b.items():
        for fam in [m.get("family")] + list(m.get("secondary_families", [])):
            if fam not in families:
                issues.append(("RUBRİK", f"{k}: bilinmeyen aile '{fam}'"))

    # [P7a] Kod sözlüğü — ORG: ad alanı ISO'dan ayrık, eski takma adlar çözülür.
    for org in codes.get("organizations", {}):
        if not ORG_RE.match(org):
            issues.append(("KOD", f"örgüt kodu ORG: desenine uymuyor → {org}"))
    for old, new in (codes.get("legacy_aliases") or {}).items():
        if not (ISO_RE.match(new) or ORG_RE.match(new)):
            issues.append(("KOD", f"eski takma ad '{old}' geçersiz hedefe çözülüyor → {new}"))

    owned_all = {}
    for code, (path, pack) in packs.items():
        ctx = f"{path.parent.name}/"
        bad_before = len(issues)

        # [P1] Şema
        if jsonschema:
            v = jsonschema.Draft202012Validator(schema)
            for err in sorted(v.iter_errors(pack), key=lambda e: list(e.path)):
                loc = "/".join(str(p) for p in err.path) or "(kök)"
                issues.append((ctx, f"şema: {loc} — {err.message[:110]}"))

        # [P7b] Paket kodu
        reserved = codes.get("reserved_iso_exceptions", {})
        if code in reserved and reserved[code].get("canonical"):
            issues.append((ctx, f"paket kodu '{code}' ayrılmış istisna — kanonik kod "
                                f"{reserved[code]['canonical']} kullanılmalı"))
        if not (ISO_RE.match(code) or ORG_RE.match(code)):
            issues.append((ctx, f"paket kodu ISO/ORG deseninde değil → {code}"))
        if path.parent.name.upper() != code.replace("ORG:", "ORG-"):
            issues.append((ctx, f"dizin adı '{path.parent.name}' paket kodu '{code}' ile uyuşmuyor"))

        # [P2] Yayım kuralı
        panel = ((pack.get("publication") or {}).get("expert_panel") or {}).get("status")
        if pack.get("status") == "active":
            if not s1_wired(pack):
                issues.append((ctx, "active paket wire'lı S1 (primary_legislation) bağlayıcısı taşımıyor"))
            if panel not in PANEL_OK:
                issues.append((ctx, f"active paket uzman paneli '{panel}' — completed|grandfathered gerekir"))
        if not s1_wired(pack) and pack.get("status") != "draft":
            issues.append((ctx, "S1 bağlayıcısı yok — paket yalnız draft olabilir (CC-7)"))

        # [P3] Filo
        for c in pack.get("connectors", []):
            s = c.get("server")
            if s and s not in servers and s not in companions:
                issues.append((ctx, f"bağlayıcı '{s}' fleet.yaml'da ne sunucu ne companion"))
            if s in companions and c.get("status") == "wired":
                issues.append((ctx, f"'{s}' companion'dır — status wired olamaz"))
            if s in servers and c.get("status") == "companion":
                issues.append((ctx, f"'{s}' wire'lı sunucudur — status companion olamaz"))

        # [P5] Parça aynası (yalnız paket shards beyan ediyorsa)
        for shard, names in (pack.get("shards") or {}).items():
            fleet_set = {n for n, s in servers.items()
                         if shard in (s.get("shard") if isinstance(s.get("shard"), list) else [s.get("shard")])}
            if set(names) != fleet_set:
                issues.append((ctx, f"shards.{shard} fleet.yaml ile sapmış: paket-fazla "
                                    f"{sorted(set(names) - fleet_set)} filo-fazla {sorted(fleet_set - set(names))}"))

        # [P6b] Paket rubrik aileleri
        for fam, prm in (pack.get("legistic_profile", {}).get("families") or {}).items():
            if fam not in families:
                issues.append((ctx, f"legistic_profile: bilinmeyen aile '{fam}'"))
                continue
            for k in prm.get("checks", []) or []:
                m = r6b.get(k)
                if not m:
                    issues.append((ctx, f"{fam}: bilinmeyen kontrol {k}"))
                elif fam != m.get("family") and fam not in m.get("secondary_families", []):
                    issues.append((ctx, f"{fam}: {k} bu aileye eşli değil (r6b_mapping → {m.get('family')})"))
            if prm.get("anchor") == "UNVERIFIED" and pack.get("legistic_profile", {}).get("verified"):
                if not prm.get("coverage_gap"):
                    issues.append((ctx, f"{fam}: profil verified=true ama anchor UNVERIFIED "
                                        f"ve coverage_gap beyanı yok"))

        # [P8] Mod adları + kapı parametreleri
        for alias, target in (pack.get("mode_aliases") or {}).items():
            if target not in CANONICAL_MODES:
                issues.append((ctx, f"mode_aliases {alias} → '{target}' kanonik mod değil"))
            if alias in CANONICAL_MODES:
                issues.append((ctx, f"mode_aliases anahtarı '{alias}' zaten kanonik mod"))
        for g in (pack.get("gate_params") or {}):
            if g not in GATES:
                issues.append((ctx, f"gate_params: bilinmeyen kapı {g}"))

        # [P4] Sahiplik toplama
        for f in pack.get("owned_files", []) or []:
            if not (ROOT / f).is_file():
                issues.append((ctx, f"owned_files: dosya yok → {f}"))
            owned_all.setdefault(f, []).append(ctx)

        # [P9] Altın vakalar
        gc = pack.get("golden_cases")
        if pack.get("status") == "active" and not gc:
            issues.append((ctx, "active paket golden_cases taşımıyor"))
        if gc:
            gp = ROOT / gc
            if not gp.is_file():
                issues.append((ctx, f"golden_cases dosyası yok → {gc}"))
            else:
                gdoc = _yaml(gp)
                for case in gdoc.get("cases", []):
                    chk = case.get("pack_check")
                    if not chk:
                        continue
                    cid = case.get("id")
                    if "g11_violations" in chk:
                        led = case.get("ledger_fixture") or {}
                        got = g11_ihlalleri(led, packs, codes)
                        if len(got) != chk["g11_violations"]:
                            issues.append((ctx, f"{cid}: G11 ihlali beklenen {chk['g11_violations']}, "
                                                f"hesaplanan {len(got)} {got}"))
                    if "ceiling" in chk:
                        ceil, applied = tavan_hesapla(pack, chk.get("mode"), chk.get("output_language"), rules_doc)
                        if ceil != chk["ceiling"]:
                            issues.append((ctx, f"{cid}: tavan beklenen {chk['ceiling']}, hesaplanan {ceil} {applied}"))
                        if "rules" in chk and sorted(chk["rules"]) != sorted(applied):
                            issues.append((ctx, f"{cid}: uygulanan kurallar beklenen {chk['rules']}, hesaplanan {applied}"))

        ceil, applied = tavan_hesapla(pack, None, None, rules_doc)
        rows.append((ctx, code, pack.get("status"), panel, ceil, applied, len(issues) == bad_before))

    # [P4] Sahiplik — tam olarak bir kez
    core_files = set((core.get("files") or {}).keys())
    for f in core_files:
        if not (ROOT / f).is_file():
            issues.append(("SAHİPLİK", f"core_files.yaml: dosya yok → {f}"))
    for f, owners in owned_all.items():
        if len(owners) > 1:
            issues.append(("SAHİPLİK", f"{f} birden fazla pakette: {owners}"))
        if f in core_files:
            issues.append(("SAHİPLİK", f"{f} hem çekirdekte hem pakette ({owners})"))
    on_disk = {str(p.relative_to(ROOT)) for d in ("references", "templates")
               for p in (ROOT / "skills" / "cureolex" / d).glob("*.md")}
    for f in sorted(on_disk - core_files - set(owned_all)):
        issues.append(("SAHİPLİK", f"SAHİPSİZ dosya (ne çekirdekte ne pakette) → {f}"))

    # [P10] Bağlayıcı sözleşmesi ↔ filo araç listesi
    for code, mp in (contract.get("reference_mappings") or {}).items():
        srv = servers.get(mp.get("server"))
        if not srv:
            issues.append(("SÖZLEŞME", f"{code}: sunucu '{mp.get('server')}' filoda yok"))
            continue
        used = set(srv.get("tools_used", []))
        # conscious_excludes: [{server|servers, tools, reason}] — bilinçli dışlanan araç
        # tools_used'da olmaz ama sözleşme eşlemesinde anılabilir (ör. ChatGPT search/fetch).
        excl = set()
        for x in fleet.get("conscious_excludes") or []:
            if mp["server"] == x.get("server") or mp["server"] in (x.get("servers") or []):
                excl.update(x.get("tools", []))
        for cap, tools in mp.items():
            if cap == "server":
                continue
            for t in tools:
                if t not in used and t not in excl:
                    issues.append(("SÖZLEŞME", f"{code}.{cap}: '{t}' {mp['server']} tools_used'da yok"))

    if not a.quiet:
        for ctx, code, st, panel, ceil, applied, ok in rows:
            mark = "✓" if ok else "⚠"
            print(f"{mark} {ctx:5s} {code:4s} status={st:6s} panel={str(panel):14s} "
                  f"tavan(mod-bağımsız)={ceil:8s} {','.join(applied) or '-'}")
        by = {}
        for ctx, m in issues:
            by.setdefault(ctx, []).append(m)
        for ctx, ms in by.items():
            print(f"\n⚠ {ctx}")
            for m in ms:
                print(f"      · {m}")
        print(f"\n{'İHLAL VAR' if issues else 'PAKETLER TEMİZ'} — {len(packs)} paket · "
              f"{len(core_files)} çekirdek + {len(owned_all)} paket dosyası / {len(on_disk)} diskte"
              + ("" if jsonschema else "  (jsonschema yok → şema doğrulaması ATLANDI)"))
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
