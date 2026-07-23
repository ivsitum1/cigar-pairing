# External Integration Failure Handling

## Purpose

Defines behavior when external MCPs (PubMed, filesystem, ClinicalTrials, Crossref)
fail due to timeout, rate limit, 404, or service unavailability.

## Affected Pipelines

- `24_discovery_pipeline.md` (Pipeline 7A)
- `26_discovery_superpipeline.md` (Pipeline 7B)
- `25_capability_registry.md` (capability availability)

## Retry Logic

On any external MCP failure:

1. Wait 5 seconds; retry (attempt 2)
2. Wait 15 seconds; retry (attempt 3)
3. After 3 failures: trigger the appropriate fallback below

Never retry more than 3 times without logging.

## Fallback Strategy by Stage

| Stage | Service | Fallback |
|-------|---------|----------|
| RETRIEVE | PubMed | Proceed with cached results if available; flag as "PubMed unavailable — results may be incomplete" |
| RETRIEVE | ClinicalTrials | Skip ongoing trials; note in output: "ClinicalTrials search not performed — service unavailable" |
| DISCOVER | Any | Proceed with evidence retrieved so far; flag each missing source |
| PLAN | Filesystem | Use in-memory context only; warn that no files were saved |

## Hard Stop Conditions

These failures require stopping the pipeline and reporting to the user:

- PubMed fails during RETRIEVE stage with 0 results retrieved
- Filesystem MCP fails when writing final output (data loss risk)
- All databases fail simultaneously (network issue likely — not a pipeline error)

## Failure Logging (Mandatory)

Every external failure must be logged to `learning_log.json` with:

```json
{
  "timestamp": "ISO-8601",
  "service": "PubMed | ClinicalTrials | filesystem | ...",
  "stage": "RETRIEVE | DISCOVER | PLAN | ...",
  "query": "the query that failed",
  "error": "timeout | rate_limit | 404 | connection_refused",
  "attempts": 3,
  "fallback_applied": "description of what was done instead"
}
```

## Rate Limit Handling

- PubMed: max 3 requests/second without API key; 10/second with key
- If rate-limited: wait 60 seconds before resuming; add API key if not already configured
- Never flood a rate-limited service; back off immediately

---

**Version:** 1.0  
**Last updated:** 2026-04-10

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
