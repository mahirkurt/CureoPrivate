import json

import httpx
import pytest

from indexer.client import AnamnesisClient, AnamnesisError


def _frame(payload, sse=False):
    body = json.dumps({"jsonrpc": "2.0", "id": 1,
                       "result": {"content": [{"type": "text", "text": json.dumps(payload)}]}})
    if sse:
        return httpx.Response(200, headers={"content-type": "text/event-stream"},
                              text=f"event: message\ndata: {body}\n\n")
    return httpx.Response(200, headers={"content-type": "application/json"}, text=body)


def _client(handler):
    return AnamnesisClient("https://w.example", "k" * 64,
                           transport=httpx.MockTransport(handler))


def test_parses_a_plain_json_frame():
    c = _client(lambda r: _frame({"collection": "evidentia:lib:c", "nodes": [], "edges": []}))
    assert c.graph_export("evidentia:lib:c")["collection"] == "evidentia:lib:c"


def test_parses_an_sse_frame():
    # The worker answers either way depending on Accept negotiation; both must work.
    c = _client(lambda r: _frame({"collection": "evidentia:lib:c", "nodes": [], "edges": []}, sse=True))
    assert c.graph_export("evidentia:lib:c")["nodes"] == []


def test_raises_on_a_tool_error_instead_of_returning_junk():
    def handler(_):
        body = json.dumps({"jsonrpc": "2.0", "id": 1,
                           "result": {"isError": True,
                                      "content": [{"type": "text", "text": "invalid collection 'x'"}]}})
        return httpx.Response(200, headers={"content-type": "application/json"}, text=body)
    with pytest.raises(AnamnesisError, match="invalid collection"):
        _client(handler).graph_export("x")


def test_sends_bearer_and_the_expected_tool_call():
    seen = {}

    def handler(request: httpx.Request):
        seen["auth"] = request.headers.get("authorization")
        seen["body"] = json.loads(request.content)
        return _frame({"collection": "evidentia:lib:c", "upserted": 2, "replaced": 0})

    r = _client(handler).upsert_communities(
        "evidentia:lib:c", [{"level": 0, "members": ["a"], "edge_count": 0}])
    assert seen["auth"] == "Bearer " + "k" * 64
    assert seen["body"]["params"]["name"] == "upsert_communities"
    assert seen["body"]["params"]["arguments"]["collection"] == "evidentia:lib:c"
    assert r["upserted"] == 2
