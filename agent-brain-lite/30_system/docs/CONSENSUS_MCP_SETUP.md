# Consensus MCP setup (Cursor)

Peer-reviewed literature search for **research-lookup** and writing pipelines. OAuth only; no REST API key in this repo.

## Enable

1. Confirm `.cursor/mcp.json` contains:

   ```json
   "consensus": {
     "url": "https://mcp.consensus.app/mcp",
     "description": "Peer-reviewed literature search (OAuth in Cursor)"
   }
   ```

2. **Cursor Settings → MCP** → enable `consensus` → sign in via OAuth when prompted.

3. In a new chat, ask a focused evidence question with skill `research-lookup` or explicit “use Consensus MCP”.

## What to do next (after OAuth)

1. **Smoke test in chat:**  
   `Using research-lookup: What does current evidence say about [one focused clinical/scientific question]? Use Consensus MCP first, then PubMed for PMIDs.`

2. **Manuscript / pipeline work:** When drafting Introduction or Discussion, ask for cited evidence the same way; tag claims `[EXTRACTED]` vs `[INFERRED]`.

3. **Do not confuse** with literature-synthesis **evidence agreement table** (internal “consensus meter”) — that skill is separate.

4. **If Consensus returns nothing:** Agent should say evidence is sparse and cross-check PubMed only — never invent DOIs (see eval `case_consensus_empty_no_fabrication`).

## Verify (manual)

- MCP server shows connected (green) in Cursor.
- A test query returns paper metadata or an explicit empty result.
- If empty: agent must state sparse evidence and **must not** invent DOI/PMID.

## Troubleshooting

| Issue | Action |
|-------|--------|
| OAuth loop | Disable/re-enable server; sign out of Consensus in browser and retry |
| 404 on URL | Use exact path `/mcp` on `https://mcp.consensus.app/mcp` |
| Rate limit | Retry later; fall back to PubMed MCP only |
| CI/headless | Not supported in this setup (IDE OAuth only) |

## Related

- Wiki: `20_knowledge/wiki/concepts/Consensus MCP.md`
- Skill: `30_system/SKILLS/SKILL_research-lookup.md`

## Semantic graph (auto)

- [[Consensus MCP]]
- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
