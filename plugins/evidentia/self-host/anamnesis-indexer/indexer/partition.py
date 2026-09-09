"""Leiden community detection over an anamnesis collection graph.

WHY THIS RUNS HERE AND NOT IN THE WORKER (anamnesis BUILD-BRIEF §5): community detection is batch
graph work, not request-scoped work, and §5 refused to ship a weak in-Worker approximation of it.
So the Worker stores and serves a partition; this package computes one with the real algorithm.

No language model is involved at any point. Leiden is pure graph mathematics, so there is nothing
here to approximate and nothing to be dishonest about. Community *summaries* are a separate matter
and stay with the orchestrator (Claude) via the Worker's `community_summarize` tool — the same
Claude-in-the-loop doctrine that governs entity extraction.
"""
from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import igraph as ig
import leidenalg

DEFAULT_SEED = 42


def _build(nodes: list[dict[str, Any]], edges: Iterable[dict[str, Any]]) -> tuple[ig.Graph, list[str]]:
    """Build an undirected weighted graph. Edges naming unknown nodes are dropped, not fatal:
    `graph_export` is consistent, but a truncated or racing export must not stop the nightly run."""
    ids = [str(n["id"]) for n in nodes]
    index = {nid: i for i, nid in enumerate(ids)}
    pairs: list[tuple[int, int]] = []
    weights: list[float] = []
    for e in edges:
        s, o = index.get(str(e.get("subject"))), index.get(str(e.get("object")))
        if s is None or o is None or s == o:
            continue
        pairs.append((s, o))
        weights.append(float(e.get("weight") or 1))
    g = ig.Graph(n=len(ids), edges=pairs, directed=False)
    if weights:
        g.es["weight"] = weights
    return g, ids


def _communities(graph: ig.Graph, seed: int) -> list[list[int]]:
    if graph.vcount() == 0:
        return []
    if graph.ecount() == 0:
        # No edges: every vertex is its own community. Emitting them keeps the partition a
        # complete cover of the graph — a node must never disappear just because it is isolated.
        return [[v] for v in range(graph.vcount())]
    weights = graph.es["weight"] if "weight" in graph.es.attributes() else None
    part = leidenalg.find_partition(
        graph, leidenalg.ModularityVertexPartition, weights=weights, seed=seed
    )
    return [list(c) for c in part]


def _intra_edges(graph: ig.Graph, members: set[int]) -> int:
    return sum(1 for e in graph.es if e.source in members and e.target in members)


def partition_graph(
    nodes: list[dict[str, Any]], edges: list[dict[str, Any]], seed: int = DEFAULT_SEED
) -> list[dict[str, Any]]:
    """Return a hierarchical partition as `upsert_communities` payload entries.

    Level 0 is the Leiden partition of the graph. Level 1 is the Leiden partition of the
    *aggregated* graph (one vertex per level-0 community), so a coarse community is always a
    UNION of fine ones rather than an independent re-slicing — which is what makes the two levels
    a hierarchy instead of two unrelated answers. Level 1 is emitted only when it actually merges
    something; an unchanged partition would just be level 0 restated.
    """
    graph, ids = _build(nodes, edges)
    fine = _communities(graph, seed)
    if not fine:
        return []

    out: list[dict[str, Any]] = [
        {
            "level": 0,
            "members": [ids[v] for v in sorted(community)],
            "edge_count": _intra_edges(graph, set(community)),
        }
        for community in fine
    ]

    if len(fine) < 3 or graph.ecount() == 0:
        return out

    # Aggregate: one vertex per level-0 community, edge weights summed across the boundary.
    of_community = {v: ci for ci, community in enumerate(fine) for v in community}
    boundary: dict[tuple[int, int], float] = {}
    for e in graph.es:
        a, b = of_community[e.source], of_community[e.target]
        if a == b:
            continue
        key = (min(a, b), max(a, b))
        boundary[key] = boundary.get(key, 0.0) + float(e["weight"] if "weight" in e.attributes() else 1)
    if not boundary:
        return out

    coarse_graph = ig.Graph(n=len(fine), edges=list(boundary.keys()), directed=False)
    coarse_graph.es["weight"] = list(boundary.values())
    coarse = _communities(coarse_graph, seed)
    if len(coarse) >= len(fine):
        return out  # nothing merged; a second level would only restate the first

    for group in coarse:
        members = sorted(ids[v] for ci in group for v in fine[ci])
        if len(group) < 2:
            continue  # a coarse community identical to a fine one adds no information
        out.append(
            {
                "level": 1,
                "members": members,
                "edge_count": _intra_edges(graph, {v for ci in group for v in fine[ci]}),
            }
        )
    return out
