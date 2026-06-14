"""G13 — DTCG alias path resolution & normalization strategy.

When the publish_audit G13 gate reports unresolved aliases in a merged
DTCG document, this strategy:

1. Loads the merged DTCG JSON
2. Builds the full path index (every leaf token's fully-qualified path)
3. For each unresolved alias, searches the index for paths **ending in**
   the alias target string
4. Unique match → propose a path-rewrite (e.g. ``{tbk.9}`` → ``{color.tbk.9}``)
5. Multiple matches → mark as ambiguous, skip
6. Zero matches → flag for human review

Empirically derived from the Düstur build experience where ~%38.5 of
tokens required path-prefix rewriting on first merge attempt.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Sequence

from ..base import (
    Channel,
    GateFailure,
    RemediationAction,
    RemediationContext,
    RemediationStrategy,
    UnsupportedChannelError,
    register_strategy,
)

_ALIAS_RE = re.compile(r"^\{([^}]+)\}$")


@register_strategy(gate_id=13)
class AliasResolutionStrategy(RemediationStrategy):
    """Normalize DTCG alias paths to their fully-qualified form."""

    title = "DTCG alias path normalizer"
    output_channels = ("pr",)

    def plan(
        self, failure: GateFailure, ctx: RemediationContext
    ) -> Sequence[RemediationAction]:
        # Find the merged DTCG file referenced in the failure samples
        # (publish_audit attaches the source path in details.merged_dtcg)
        merged_path_rel = failure.details.get("merged_dtcg", "tokens/dustur.tokens.json")
        merged_full = ctx.library_dir / merged_path_rel

        if not merged_full.exists():
            # Cannot remediate without the source file
            return []

        tokens = ctx.read_json(merged_path_rel)
        path_index = _collect_paths(tokens)

        # Collect unresolved aliases via tree walk (don't rely only on samples)
        unresolved = list(_find_unresolved_aliases(tokens, path_index))
        if not unresolved:
            return []

        # Build the rewrite map
        rewrites: dict[str, str] = {}      # old alias → new alias
        ambiguous: list[str] = []
        unknown: list[str] = []

        for _, old_alias in unresolved:
            candidates = [p for p in path_index if p.endswith("." + old_alias) or p == old_alias]
            # Filter out exact matches (already resolved upstream)
            candidates = [c for c in candidates if c != old_alias]
            if len(candidates) == 1:
                rewrites["{" + old_alias + "}"] = "{" + candidates[0] + "}"
            elif len(candidates) > 1:
                ambiguous.append(old_alias)
            else:
                unknown.append(old_alias)

        if not rewrites:
            return []

        # Apply rewrites to a copy of the document
        original_json = json.dumps(tokens, indent=2, ensure_ascii=False) + "\n"
        rewritten = _apply_rewrites_to_tree(tokens, rewrites)
        rewritten_json = json.dumps(rewritten, indent=2, ensure_ascii=False) + "\n"

        rationale_lines = [
            f"Normalize {len(rewrites)} DTCG alias path(s) to their fully-qualified form.",
            "",
            "Source: G13 gate failure (figma-forge publish_audit).",
            "Rationale: alias targets must resolve against the merged DTCG path index,",
            "otherwise the Figma Variables payload falls back to literal hex values,",
            "breaking the primitive→semantic indirection chain.",
        ]
        if ambiguous:
            rationale_lines.append("")
            rationale_lines.append(f"⚠️  {len(ambiguous)} ambiguous alias(es) skipped:")
            for a in ambiguous[:10]:
                rationale_lines.append(f"  - {a}")
        if unknown:
            rationale_lines.append("")
            rationale_lines.append(f"⚠️  {len(unknown)} unmatchable alias(es) (human review):")
            for u in unknown[:10]:
                rationale_lines.append(f"  - {u}")

        action = RemediationAction(
            strategy_id=13,
            action_type="patch_file",
            target_path=merged_path_rel,
            rationale="\n".join(rationale_lines),
            old_content=original_json,
            new_content=rewritten_json,
            confidence="high" if not ambiguous else "medium",
        )

        return [action]

    def render(self, action: RemediationAction, channel: Channel) -> str:
        if channel not in self.output_channels:
            raise UnsupportedChannelError(
                f"G13 strategy does not support channel {channel!r} "
                f"(available: {self.output_channels})"
            )
        return _render_unified_diff(
            target=action.target_path,
            old=action.old_content or "",
            new=action.new_content or "",
            rationale=action.rationale,
        )


# ---------------------------------------------------------------------------
# Helpers — kept module-private so strategy is self-contained
# ---------------------------------------------------------------------------

def _collect_paths(tree, prefix: str = "") -> set[str]:
    """Walk DTCG tree; return the set of fully-qualified paths of all leaf
    tokens. A leaf is any dict containing a ``$value`` key."""
    out: set[str] = set()
    if isinstance(tree, dict):
        if "$value" in tree:
            out.add(prefix)
        else:
            for k, v in tree.items():
                if k.startswith("$"):
                    continue
                p = f"{prefix}.{k}" if prefix else k
                out.update(_collect_paths(v, p))
    return out


def _find_unresolved_aliases(tree, path_index: set[str], prefix: str = "") -> list[tuple[str, str]]:
    """Yield ``(token_path, alias_target)`` for every alias whose target
    is missing from ``path_index``."""
    out: list[tuple[str, str]] = []
    if isinstance(tree, dict):
        if "$value" in tree and isinstance(tree["$value"], str):
            m = _ALIAS_RE.match(tree["$value"])
            if m and m.group(1) not in path_index:
                out.append((prefix, m.group(1)))
        else:
            for k, v in tree.items():
                if k.startswith("$"):
                    continue
                p = f"{prefix}.{k}" if prefix else k
                out.extend(_find_unresolved_aliases(v, path_index, p))
    return out


def _apply_rewrites_to_tree(tree, rewrites: dict[str, str]):
    """Return a deep-copy of ``tree`` with every alias literal replaced
    via the ``rewrites`` map (string → string)."""
    if isinstance(tree, dict):
        new = {}
        for k, v in tree.items():
            if k == "$value" and isinstance(v, str) and v in rewrites:
                new[k] = rewrites[v]
            else:
                new[k] = _apply_rewrites_to_tree(v, rewrites)
        return new
    if isinstance(tree, list):
        return [_apply_rewrites_to_tree(x, rewrites) for x in tree]
    return tree


def _render_unified_diff(*, target: str, old: str, new: str, rationale: str) -> str:
    """Format a unified diff with a leading rationale comment block."""
    import difflib

    diff_lines = list(
        difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile=f"a/{target}",
            tofile=f"b/{target}",
            n=3,
        )
    )
    rationale_block = "\n".join(f"# {line}" for line in rationale.splitlines())
    return f"{rationale_block}\n{''.join(diff_lines)}"
