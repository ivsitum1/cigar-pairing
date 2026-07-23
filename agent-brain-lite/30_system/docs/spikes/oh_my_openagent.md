# Spike: oh-my-openagent harness

**Repo:** https://github.com/code-yeongyu/oh-my-openagent  
**Machine US:** US-27 (v2), **US-31** (v3 W28 scope B)  
**W27 verdict:** approved_spike  
**Notebook bridge:** last-mile + loop-of-loops

## Take for agent-rules

| Pattern | Adopt | Notes |
|---------|-------|-------|
| Token-maxxing harness for large codebases | **Study** | Compare to LifeHarness L1-L4, mcp_prescreen |
| Replace Cursor orchestrator | **Reject** | Brain is Cursor-native |
| Failure log → deterministic harness patches | **Partial (v3)** | `harness_failure_analyze.py` + `harness_tdd.mdc` § omo pattern |
| Prescreen before blind retry | **Partial (v3)** | Documented in `LAST_MILE_INTEGRATION_CHECKLIST.md` |

## v3 implemented patterns (US-31)

1. `harness_failure_analyze.py --json` on trajectory → rule snippet suggestions (no auto-apply).
2. `harness_tdd.mdc`: prescreen inputs before retry loops.

## Next step

No omo install. Revisit if LifeHarness prescreen gaps appear in trajectory audits.
