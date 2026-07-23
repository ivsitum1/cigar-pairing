# Spike: Crabbox sandboxes vs git worktrees

**Source:** OKF notebook (`okf-knowledge`)  
**Related:** `REFERENCE_Mind_Map_AI_Agents_Harness_2026.md` (git worktrees)

## Comparison

| Dimension | Crabbox (notebook) | Git worktrees (repo) | Cursor Cloud Agents |
|-----------|-------------------|----------------------|---------------------|
| Isolation | Cloud sandbox per agent | Local branch worktree | Remote VM |
| Code execution | Yes (claimed) | Local only | Yes |
| Merge back | Manual / PR | git merge | PR / diff |
| Brain repo fit | Spike external | **Already documented** | Optional future |

## Take for agent-rules

- **P2 docs only** (OKF-3): no Crabbox install without governance review
- Parallel fan-out: prefer Task tool + disjoint outputs per `AGENT_AUTONOMY_AND_PARALLEL.md`

## Reject

- Replacing worktrees with paid sandbox for default brain maintenance
