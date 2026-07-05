# MCP roster hygiene

Raw `codex mcp list` / `claude mcp list` can echo plaintext tokens embedded in
stdio server arguments. The `pre_tool_use_policy.py` hook denies the raw form.

When you need to inspect the configured MCP servers, use a **redacting** wrapper
that masks high-confidence secret patterns (`sk-…`, `xai-…`, `ghp_…`, JWTs,
etc.) before printing — the same pattern set the plugin's secret scanners use.
The plugin ships only remote HTTP servers (no stdio, no embedded tokens), so the
bundled roster is safe by construction; this guard protects any additional
stdio servers a user adds to their own config.

Never paste raw roster output, tokens, or `.env` contents into the conversation.
