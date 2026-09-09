import pytest

from indexer.client import AnamnesisError
from indexer.main import parse_collections, run


class FakeClient:
    def __init__(self, graphs, fail_upsert=()):
        self.graphs = graphs
        self.fail_upsert = set(fail_upsert)
        self.upserts = {}

    def graph_export(self, collection):
        if collection not in self.graphs:
            raise AnamnesisError(f"invalid collection '{collection}'")
        return self.graphs[collection]

    def upsert_communities(self, collection, communities):
        if collection in self.fail_upsert:
            raise AnamnesisError("write refused")
        self.upserts[collection] = communities
        return {"collection": collection, "upserted": len(communities), "replaced": 0}


def _triangles(prefix):
    nodes = [{"id": f"{prefix}::n{i}", "label": f"n{i}"} for i in range(6)]
    edges = [{"subject": f"{prefix}::n{a}", "object": f"{prefix}::n{b}", "weight": 3}
             for a, b in [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5)]]
    return {"nodes": nodes, "edges": edges}


def test_indexes_each_collection_and_reports_counts():
    c = FakeClient({"evidentia:lib:a": _triangles("evidentia:lib:a")})
    report = run(c, ["evidentia:lib:a"])
    assert report["ok"] == 1 and report["failed"] == 0
    assert len(c.upserts["evidentia:lib:a"]) == 2


def test_one_bad_collection_does_not_abort_the_others():
    # A nightly job that dies on the first unreadable collection silently stops maintaining
    # every collection after it.
    c = FakeClient({"evidentia:lib:b": _triangles("evidentia:lib:b")})
    report = run(c, ["evidentia:lib:missing", "evidentia:lib:b"])
    assert report["ok"] == 1 and report["failed"] == 1
    assert "evidentia:lib:b" in c.upserts
    assert report["errors"][0]["collection"] == "evidentia:lib:missing"


def test_an_empty_graph_is_skipped_rather_than_written_as_an_empty_partition():
    c = FakeClient({"evidentia:lib:empty": {"nodes": [], "edges": []}})
    report = run(c, ["evidentia:lib:empty"])
    assert report["skipped"] == 1
    assert "evidentia:lib:empty" not in c.upserts


def test_a_failed_write_is_reported_not_swallowed():
    c = FakeClient({"evidentia:lib:c": _triangles("evidentia:lib:c")}, fail_upsert=["evidentia:lib:c"])
    report = run(c, ["evidentia:lib:c"])
    assert report["failed"] == 1


@pytest.mark.parametrize("raw,expected", [
    ("a:lib:1, b:lib:2", ["a:lib:1", "b:lib:2"]),
    ("  ", []),
    ("a:lib:1,,a:lib:1", ["a:lib:1"]),
])
def test_parses_the_collection_list(raw, expected):
    assert parse_collections(raw) == expected
