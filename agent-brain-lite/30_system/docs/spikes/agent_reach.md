# Spike: Agent-Reach external research

**Repo:** https://github.com/Panniantong/Agent-Reach  
**Machine US:** US-25 (v2), **US-34** (v3 W28 scope A)  
**W27 verdict:** approved_spike  
**Notebook bridge:** STORM / loop-of-loops research expansion

## Coverage matrix (US-34)

| Source type | Agent-Reach | Brain today | Gap |
|-------------|-------------|-------------|-----|
| PubMed / papers | partial | PubMed MCP, research-lookup | Low for clinical SR |
| PDF full text | partial | pdf MCP twin + evidence | Low |
| Textbooks | no | books_rag fused search | Low |
| Wiki / concepts | no | wiki-query, context pack | Low |
| Twitter / Reddit | yes | **none** | High — policy + MCP gate |
| YouTube | yes | NotebookLM (gated) | Medium — UNVERIFIED claims |
| GitHub repos | yes | plugin-github, digest sensors | Low |

## Take for agent-rules

| Pattern | Adopt | Notes |
|---------|-------|-------|
| Unified social/web/GitHub search for agents | **Spike only** | Matrix above |
| New MCP server install | **BLOCKED** | MCP governance — human approval required |
| Search orchestration in Python script | **Maybe** | Public GitHub API only if license OK |

## Existing coverage

- PubMed MCP, pdf MCP, books_rag, notebooklm bridge, W28 github_ai_watch sensor

## Next step

Human gate before Twitter/Reddit path: approve Runlayer MCP or thin Python wrapper with institutional policy check.

## Reject

- Unaudited scraping bypassing institutional policy
