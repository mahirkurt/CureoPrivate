"""Semantic entropy — consistency-based hallucination signal.

Implements the method of:
  Farquhar, S., Kossen, J., Kuhn, L. & Gal, Y. (2024).
  "Detecting hallucinations in large language models using semantic entropy."
  Nature 630(8017), 625-630.  https://doi.org/10.1038/s41586-024-07421-0

Idea: sample N answers to the same question, cluster them by *meaning*
(bidirectional NLI entailment), then compute entropy over the meaning-clusters.
High semantic entropy => the model is unsure of the *meaning* => elevated risk
of "confabulation" (the arbitrary, incorrect subset of hallucinations the paper
targets — NOT every hallucination type).

Honest cost note: the paper's follow-up (SEPs, arXiv 2406.15927) reports a
5-10x compute overhead because you must sample several generations. Use this
for high-stakes claims, not on every call.

This module is BACKEND-AGNOSTIC (stdlib only). Wire two callables:
  - generate(prompt, n) -> list[str]   (your LLM sampler, temperature > 0)
  - entails(a, b) -> bool              (your NLI model, "a entails b")
In the plugin, the natural wiring is a Claude subagent for both — but this file
imports nothing beyond the stdlib so it also runs in CI with any backend.
Defaults raise NotImplementedError with setup guidance.
"""
from __future__ import annotations
import math
from collections import Counter
from typing import Callable, List


def _no_generate(prompt: str, n: int) -> List[str]:
    raise NotImplementedError(
        "Configure a sampler returning n samples at temperature ~1.0. "
        "Pass it as `generate=`. In-plugin, drive it with a Claude subagent."
    )


def _no_entails(a: str, b: str) -> bool:
    raise NotImplementedError(
        "Configure an entailment judge returning True iff premise `a` entails "
        "hypothesis `b`. Pass it as `entails=`. In-plugin, use a Claude subagent."
    )


def cluster_by_meaning(answers: List[str], entails: Callable[[str, str], bool]) -> List[List[int]]:
    """Greedy bidirectional-entailment clustering of semantically equal answers."""
    clusters: List[List[int]] = []
    reps: List[str] = []
    for i, ans in enumerate(answers):
        placed = False
        for c, rep in enumerate(reps):
            if entails(rep, ans) and entails(ans, rep):
                clusters[c].append(i)
                placed = True
                break
        if not placed:
            clusters.append([i])
            reps.append(ans)
    return clusters


def semantic_entropy(
    prompt: str,
    n: int = 10,
    generate: Callable[[str, int], List[str]] = _no_generate,
    entails: Callable[[str, str], bool] = _no_entails,
) -> dict:
    """Return {'entropy': float, 'n_clusters': int, 'n_samples': int}.

    Entropy is in nats. ~0 => all samples mean the same thing (confident);
    higher => competing meanings (confabulation risk). Calibrate a threshold on
    YOUR golden set rather than using a fixed cutoff.
    """
    answers = generate(prompt, n)
    if not answers:
        return {"entropy": 0.0, "n_clusters": 0, "n_samples": 0}
    clusters = cluster_by_meaning(answers, entails)
    sizes = Counter(c for c, members in enumerate(clusters) for _ in members)
    total = sum(sizes.values())
    probs = [count / total for count in sizes.values()]
    ent = -sum(p * math.log(p) for p in probs if p > 0)
    return {"entropy": ent, "n_clusters": len(clusters), "n_samples": total}


def entropy_from_clusters(cluster_sizes: List[int]) -> dict:
    """Entropy (nats) over already-formed meaning-cluster sizes.

    This is the seam the `entropy-sampler` subagent uses: it does the sampling
    and meaning-clustering (it is the NLI judge), then feeds the cluster sizes
    here for the arithmetic. Stdin form: a JSON list of ints, e.g. [4,1,1].
    """
    sizes = [int(s) for s in cluster_sizes if int(s) > 0]
    total = sum(sizes)
    if total == 0:
        return {"entropy": 0.0, "n_clusters": 0, "n_samples": 0}
    probs = [s / total for s in sizes]
    ent = -sum(p * math.log(p) for p in probs if p > 0)
    return {"entropy": ent, "n_clusters": len(sizes), "n_samples": total}


if __name__ == "__main__":
    import json
    import sys

    data = sys.stdin.read().strip()
    if data:
        # Compute entropy from a JSON list of cluster sizes fed on stdin.
        print(json.dumps(entropy_from_clusters(json.loads(data))))
    else:
        # Smoke test of the clustering math with a trivial stub entailment.
        demo = ["Paris", "The capital is Paris", "Lyon", "Paris.", "It is Lyon"]
        same = lambda a, b: a.strip(". ").lower().replace("the capital is ", "").replace("it is ", "") \
            == b.strip(". ").lower().replace("the capital is ", "").replace("it is ", "")
        print(json.dumps(semantic_entropy("capital of France?", n=len(demo),
                                          generate=lambda p, k: demo, entails=same)))
