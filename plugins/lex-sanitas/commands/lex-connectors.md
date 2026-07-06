---
description: Lex Sanitas tam-filo bağlantı durumu — wire edilmiş 14 hukuk/regülasyon MCP + companion (Yargı/Open Law/Ansvar) + evidentia/sci-audit zorunlu delegasyonun canlı erişilebilirliğini raporlar. Hangi araçlar hazır, hangileri anahtar/bağlantı bekliyor gösterir. Argüman gerekmez.
argument-hint: (argüman gerekmez)
allowed-tools: Read, Bash, Task
---

# /lex-connectors — Tam-Filo Bağlantı Durumu

Lex Sanitas'ın **tam-filo ilkesi** (wire'lı tüm araçlar her sorguda çalışır) için hangi connector'ların hazır olduğunu raporla.

## Yürütme

1. **Wire'lı fleet'i oku.** [`.mcp.json`](../.mcp.json) — 14 server + rol notları.
2. **SessionStart preflight çıktısını oku** (varsa): `${CLAUDE_PLUGIN_ROOT}/hooks/scripts/session_start.py` hangi Bearer anahtarlarının env'de olduğunu işaretler.
3. **Canlı erişilebilirliği raporla** — üç kategori:
   - **TR primer/idari:** mevzuat · mevzuat-bilgisi (ikincil) · resmi-gazete · saglikbakanligi · titck · tbmm · detsis
   - **Karşılaştırmalı/uluslararası:** health-policy (18 araç — **semantic_search** doğal-dil çok-dilli keşif US/JP/AU/CN + 8 ülke fetch + legal_distill) · german-law · ich-guidelines · intl-treaty · eudamed · oecd
   - **Doktrin + companion:** yok-akademik · Yargı (`mcp__Yarg__*`) · Open Law (`mcp__Open_Law__*`) · Ansvar (`mcp__Ansvar__*`)
   - **Büyük-veri substratı:** anamnesis (`mcp__anamnesis__*`) — RAG/GraphRAG evidence_index (kaynak değil, bağlam-ekonomisi Tier 2)
   - **Delegasyon:** evidentia (klinik kanıt) · sci-audit (atıf-adli + dil)
4. **Her satır için durum:** `hazır (anahtar var)` / `anahtar bekliyor: <ENV_VAR>` / `companion — claude.ai connector olarak ekle` / `plugin kurulu değil (graceful degrade)`.
5. **Kapı etkisini göster:** companion/delegasyon satırlarında eksikliğin maliyetini açıkça yaz — `Yargı bağlı değil ⇒ G5 en fazla CONDITIONAL (içtihat doğrulanamaz)` · `Open Law bağlı değil ⇒ G6 CONDITIONAL (CELEX doğrulama degrade)` · `Ansvar bağlı değil ⇒ Mod 7'de CH/FR/IT/NL/SE/DK/FI/AT/PL satırları manual_required` · `evidentia kurulu değil ⇒ klinik iddialar unverified` · `sci-audit kurulu değil ⇒ çıktı-QA manuel`.
6. **Özet:** kaç server tam-filoya hazır, hangileri kullanıcı aksiyonu bekliyor (Doppler `cureohub/dev_personal` Bearer inject veya claude.ai connector ekleme) ve bu eksikliklerin hangi kapıları CONDITIONAL'a düşürdüğü.

> Not: Bir server anahtar/bağlantı beklese bile plugin **graceful degrade** eder — o katman kapsam manifestosunda `skipped: anahtar yok` olarak beyan edilir, çıktı durmaz, asla uydurma yapılmaz. **Ters yüzü:** kurulu/bağlı bir katman (companion dahil) tetiklenmiş bağlamda ATLANAMAZ — bu G0 ihlalidir (`shared/composition-contract.md`).

## Anahtar env-var haritası

| Server | Env-var (Doppler → Bearer) |
|---|---|
| mevzuat | `MEVZUAT_MCP_API_KEY` |
| resmi-gazete | `RESMI_GAZETE_MCP_API_KEY` |
| tbmm | `TBMM_MCP_API_KEY` |
| saglikbakanligi | `SAGLIK_BAKANLIGI_MCP_API_KEY` |
| detsis | `DETSIS_MCP_API_KEY` |
| health-policy | `LEX_SANITAS_MCP_API_KEY` |
| german-law | `GERMAN_LAW_MCP_API_KEY` |
| ich-guidelines | `ICH_MCP_API_KEY` |
| intl-treaty | `INTL_TREATY_MCP_API_KEY` |
| eudamed | `EUDAMED_MCP_MCP_API_KEY` |
| oecd | `OECD_MCP_API_KEY` |
| yok-akademik | `YOK_AKADEMIK_MCP_API_KEY` |
| anamnesis (büyük-veri substratı) | `ANAMNESIS_MCP_API_KEY` |
| titck · mevzuat-bilgisi | (public — anahtar yok) |

> anamnesis bir *kaynak* değil, bağlam-ekonomisi Tier 2 RAG substratıdır (büyük tam-metin ingest→bounded query). Anahtarı yoksa büyük belge işleme bounded-chunk fallback'e degrade eder (`references/16` §C) — plugin yine çalışır.
