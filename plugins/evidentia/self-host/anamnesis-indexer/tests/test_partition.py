"""Leiden partitioning is the one thing this package computes itself, so it is the one thing
that must be pinned. Everything else is transport."""

from indexer.partition import partition_graph

# Two tight triangles joined by a single weak edge — the textbook two-community graph.
TRIANGLES_NODES = [{"id": f"c::n{i}", "label": f"n{i}"} for i in range(6)]
TRIANGLES_EDGES = [
    {"subject": "c::n0", "object": "c::n1", "weight": 3},
    {"subject": "c::n1", "object": "c::n2", "weight": 3},
    {"subject": "c::n0", "object": "c::n2", "weight": 3},
    {"subject": "c::n3", "object": "c::n4", "weight": 3},
    {"subject": "c::n4", "object": "c::n5", "weight": 3},
    {"subject": "c::n3", "object": "c::n5", "weight": 3},
    {"subject": "c::n2", "object": "c::n3", "weight": 1},
]


def _level(parts, level):
    return [p for p in parts if p["level"] == level]


def test_splits_two_weakly_joined_triangles():
    parts = partition_graph(TRIANGLES_NODES, TRIANGLES_EDGES)
    level0 = _level(parts, 0)
    assert len(level0) == 2
    members = sorted(sorted(p["members"]) for p in level0)
    assert members == [["c::n0", "c::n1", "c::n2"], ["c::n3", "c::n4", "c::n5"]]


def test_members_are_original_node_ids_not_graph_indices():
    parts = partition_graph(TRIANGLES_NODES, TRIANGLES_EDGES)
    every = {m for p in parts for m in p["members"]}
    assert every <= {n["id"] for n in TRIANGLES_NODES}
    assert all(isinstance(m, str) and m.startswith("c::") for m in every)


def test_counts_only_intra_community_edges():
    parts = _level(partition_graph(TRIANGLES_NODES, TRIANGLES_EDGES), 0)
    # The joining edge belongs to neither community.
    assert sorted(p["edge_count"] for p in parts) == [3, 3]


def test_is_deterministic_for_a_fixed_seed():
    a = partition_graph(TRIANGLES_NODES, TRIANGLES_EDGES, seed=7)
    b = partition_graph(TRIANGLES_NODES, TRIANGLES_EDGES, seed=7)
    assert [sorted(p["members"]) for p in a] == [sorted(p["members"]) for p in b]


def test_empty_graph_yields_no_communities():
    assert partition_graph([], []) == []
    # Nodes with no edges cannot be clustered; they must not vanish silently either.
    solo = partition_graph([{"id": "c::x", "label": "x"}], [])
    assert {m for p in solo for m in p["members"]} == {"c::x"}


def test_ignores_edges_pointing_at_unknown_nodes():
    # graph_export is consistent, but a truncated or racing export must not crash the indexer.
    parts = partition_graph(
        TRIANGLES_NODES, TRIANGLES_EDGES + [{"subject": "c::ghost", "object": "c::n0", "weight": 1}]
    )
    assert {m for p in parts for m in p["members"]} <= {n["id"] for n in TRIANGLES_NODES}


def test_builds_a_coarser_second_level_when_one_exists():
    # Four tight cliques, paired: 0-1 and 2-3. Level 0 should find 4, level 1 should merge pairs.
    nodes, edges = [], []
    for c in range(4):
        for i in range(4):
            nodes.append({"id": f"c::g{c}n{i}", "label": f"g{c}n{i}"})
        for i in range(4):
            for j in range(i + 1, 4):
                edges.append({"subject": f"c::g{c}n{i}", "object": f"c::g{c}n{j}", "weight": 10})
    edges.append({"subject": "c::g0n0", "object": "c::g1n0", "weight": 4})
    edges.append({"subject": "c::g2n0", "object": "c::g3n0", "weight": 4})

    parts = partition_graph(nodes, edges)
    assert len(_level(parts, 0)) == 4
    level1 = _level(parts, 1)
    assert 0 < len(level1) < 4
    # A coarse community must be a union of fine ones — never a re-slicing of them.
    fine = [set(p["members"]) for p in _level(parts, 0)]
    for coarse in (set(p["members"]) for p in level1):
        covered = [f for f in fine if f <= coarse]
        assert sum(len(f) for f in covered) == len(coarse)
