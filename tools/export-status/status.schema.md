# status.json — Schema v1

The single read contract between the Marketing 4.0 skills (motor) and the
cockpit (display). The cockpit only reads this file; it never writes back.

| Field | Type | Rule |
|---|---|---|
| schemaVersion | int | must be 1 |
| client.slug | string | non-empty, lowercase slug |
| client.name | string | display name |
| generatedAt | string | ISO 8601 UTC (`...Z`) |
| stages.atrair / converter / nutrir / medir | object | all four required |
| stages.<s>.deliverables | array | items mirrored from the stage's artifact file |
| stages.<s>.count | int | must equal len(deliverables) |
| stages.atrair.firstPublishedAt | string \| null | ISO 8601 UTC or null |
| stages.converter.firstPublishedAt | string \| null | ISO 8601 UTC or null |
| stages.nutrir.firstSentAt | string \| null | ISO 8601 UTC or null |

Timestamps must be ISO 8601 UTC. Artifact files: `artifacts/atrair/posts.json`,
`artifacts/converter/blueprints.json`, `artifacts/nutrir/emails.json`,
`artifacts/medir/campaigns.json` — each shaped `{"items": [...]}`.

## Example

```json
{
  "schemaVersion": 1,
  "client": {"slug": "coesa", "name": "COESA"},
  "generatedAt": "2026-08-20T10:00:00Z",
  "stages": {
    "atrair": {"deliverables": [], "count": 0, "firstPublishedAt": null},
    "converter": {"deliverables": [], "count": 0, "firstPublishedAt": null},
    "nutrir": {"deliverables": [], "count": 0, "firstSentAt": null},
    "medir": {"deliverables": [], "count": 0}
  }
}
```
