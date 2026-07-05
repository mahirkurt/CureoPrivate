# Governance mapping — sci-audit controls

The plugin's controls mapped to the frameworks that dominate the AI-integrity
regulatory surface. Use this to show a *defensible* audit process — which
matters when auditing text destined for regulated (medical / pharma / academic)
publication.

| sci-audit control | NIST AI RMF (GenAI Profile) | ISO/IEC 42001 | EU AI Act |
|---|---|---|---|
| Convention injection + no-fabrication invariant (Layer 0, SessionStart) | MEASURE 2.x (validity, reliability) | 8.3 operational control | Art. 13 transparency |
| Deterministic hooks / destructive + secret deny-list (Layer 1) | MANAGE 2.x (risk treatment) | 8.1 operational planning | Art. 15 robustness |
| Reference integrity + claim grounding (axes A, B) | MEASURE 2.3 (accuracy) | 9.1 monitoring | Art. 15 accuracy |
| Statistical-consistency checks (axis C) | MEASURE 2.3 | 9.1 | Art. 15 accuracy |
| Hallucination signals + semantic entropy (axis D) | MEASURE 2.x (confabulation) | 9.1 | Art. 15 robustness |
| Reporting-guideline conformance (axis E) | MEASURE 4.x (feedback) | 10.x improvement | Art. 17 quality mgmt |
| AI-use transparency scan (axis F) | GOVERN 1.x (accountability) | 7.5 documented info | Art. 50 disclosure |
| Adversarial subagents (citation-verifier, claim-refuter) | MANAGE 4.x | 8.1 | Art. 14 human oversight (assist) |
| Audit JSONL log (`/sci-audit:ai-log`) | GOVERN 1.x | 7.5 documented info | Art. 12 record-keeping |
| Turkish writing/orthography audit (axis G) | MEASURE 2.x | 8.3 | Art. 13 transparency |

Notes
- The audit ASSISTS a human reviewer; it does not replace sign-off for
  high-risk outputs (EU AI Act Art. 14 human oversight is only partially
  automatable).
- Record-keeping (Art. 12) is satisfied operationally by the audit JSONL log,
  provided runs are retained with their target/scores/gate outcome.
- This is an engineering-control map, not legal advice. Confirm applicability
  and enforcement dates with counsel for your jurisdiction and risk tier.
