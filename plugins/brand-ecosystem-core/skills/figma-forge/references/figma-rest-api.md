# Figma REST API Reference (Channel 2)

Channel 2 uses the Figma REST API directly via authenticated HTTP requests. This is the primary path for **Variables API operations** on Enterprise tenants. For non-Enterprise plans, route to Channel 3 (plugin).

## Authentication

All Figma REST calls use the user's Personal Access Token (PAT):

```
GET /v1/files/:file_key
Host: api.figma.com
X-Figma-Token: <PAT>
```

The skill prompts the user for their PAT when entering Channel 2 mode. **The PAT is held only in the current session memory; never logged, never persisted, never written to disk.** When the skill's task is complete, the PAT reference is dropped.

## Endpoint inventory used by figma-forge

### File read

```
GET https://api.figma.com/v1/files/:file_key
GET https://api.figma.com/v1/files/:file_key/nodes?ids=<id1>,<id2>
GET https://api.figma.com/v1/files/:file_key/styles
GET https://api.figma.com/v1/files/:file_key/components
GET https://api.figma.com/v1/files/:file_key/component_sets
```

### Variables (read — any plan)

```
GET https://api.figma.com/v1/files/:file_key/variables/local
GET https://api.figma.com/v1/files/:file_key/variables/published
```

Response shape (abridged):

```json
{
  "status": 200,
  "meta": {
    "variableCollections": {
      "VariableCollectionId:1:1": {
        "id": "VariableCollectionId:1:1",
        "name": "Primitives",
        "modes": [{"modeId": "1:0", "name": "Default"}],
        "defaultModeId": "1:0",
        "remote": false,
        "hiddenFromPublishing": false,
        "variableIds": ["VariableID:1:1", "VariableID:1:2"]
      }
    },
    "variables": {
      "VariableID:1:1": {
        "id": "VariableID:1:1",
        "name": "color/blue/500",
        "resolvedType": "COLOR",
        "valuesByMode": {"1:0": {"r": 0.0, "g": 0.4, "b": 0.8, "a": 1.0}},
        "remote": false,
        "scopes": ["ALL_FILLS"]
      }
    }
  }
}
```

### Variables (write — Enterprise only)

```
POST https://api.figma.com/v1/files/:file_key/variables
```

Body shape (batch operations):

```json
{
  "variableCollections": [
    {"action": "CREATE", "id": "<temp_id>", "name": "Primitives", "initialModeId": "<temp_mode_id>"}
  ],
  "variableModes": [
    {"action": "CREATE", "id": "<temp_mode_id>", "name": "Default",
     "variableCollectionId": "<temp_id>"}
  ],
  "variables": [
    {"action": "CREATE", "id": "<temp_var_id>", "name": "color/blue/500",
     "variableCollectionId": "<temp_id>", "resolvedType": "COLOR",
     "scopes": ["ALL_FILLS"]}
  ],
  "variableModeValues": [
    {"variableId": "<temp_var_id>", "modeId": "<temp_mode_id>",
     "value": {"r": 0.0, "g": 0.4, "b": 0.8, "a": 1.0}}
  ]
}
```

Key rules:

- **Batch all operations in one POST.** Figma resolves cross-references between temp IDs within a single batch but not across batches.
- **Temp IDs** can be any string (e.g., `tmp_collection_primitives`); they are mapped to real Figma IDs in the response.
- **Aliased variables** use `{"type": "VARIABLE_ALIAS", "id": "<target_var_id>"}` as the value.
- **Modes** beyond the default must be created explicitly via the `variableModes` array.
- **Color values** are 0–1 floats for r/g/b/a, not 0–255.

### Library publish

```
POST https://api.figma.com/v1/files/:file_key/library_publish
```

Body:

```json
{
  "description": "<release notes>"
}
```

Requires the file to have at least one publishable asset (component, style, or variable). Library publish is asynchronous; the response includes a job ID that can be polled.

### Team library

```
GET https://api.figma.com/v1/teams/:team_id/styles?page_size=1000
GET https://api.figma.com/v1/teams/:team_id/components?page_size=1000
GET https://api.figma.com/v1/teams/:team_id/component_sets?page_size=1000
```

Used by `PUBLISH_AUDIT` to verify that a file's published assets reach the team library.

### Comments (optional for audit)

```
GET https://api.figma.com/v1/files/:file_key/comments
POST https://api.figma.com/v1/files/:file_key/comments
```

Audit mode can leave automated comments on nodes that fail gate checks. Skill default: don't comment; report only.

---

## Rate limits

Figma's REST API has the following published limits:

- **30 requests per minute per token** (general read)
- **100 variable batches per file per day** (variables write)
- 429 response → exponential backoff starting at 2s; the skill caps at 32s before failing the run.

The skill's REST client (`scripts/figma_rest_client.py`, if generated) implements:

- Token bucket pacing at 25 req/min (margin for safety)
- Exponential backoff: 2s → 4s → 8s → 16s → 32s → fail
- Idempotency: each variable batch carries a deterministic `client_request_id` derived from input hash, so retries don't double-write

---

## Error handling

| Error | Action |
|---|---|
| 400 (bad request) | Halt; log full request + response; surface to user |
| 401 (unauthorized) | PAT invalid or expired; prompt user for new PAT |
| 403 (forbidden) | User lacks permission on target file; explain + abort |
| 404 (not found) | file_key wrong; abort with user-readable error |
| 429 (rate limited) | Backoff per schedule above |
| 5xx | Retry once after 5s; if still failing, abort |

Plan-specific errors:

| Error message contains | Likely cause | Action |
|---|---|---|
| `requires enterprise` | Variables write attempted on non-Enterprise plan | Fall through to Channel 3 plugin |
| `not eligible to be published` | File has no publishable assets | Build assets first |
| `Variable collection not found` | Wrong collection ID or temp ID resolution failure | Audit batch contents |

---

## Security posture

- PAT is treated as a secret. Not logged in run reports, not echoed in tool calls.
- PAT scope: figma-forge requests "file_content:read" + "file_content:write" + "library_assets:read". User can revoke at any time via Figma Settings.
- Skill output never contains the PAT. If the user copies a run report to share, they can do so safely.
- For audit mode (read-only), figma-forge prompts for a read-only PAT if the user has one provisioned.

---

End of reference. For the Plugin fallback (Channel 3), see `figma-plugin-fallback.md`.
