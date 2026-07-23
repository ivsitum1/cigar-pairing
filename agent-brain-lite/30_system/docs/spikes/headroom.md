# Spike: Headroom-style context compression

**Repo:** https://github.com/headroomlabs-ai/headroom  
**Machine US:** US-24 (v2), **US-32** (v3 rollout)  
**W27 verdict:** approved_implement  
**Notebook bridge:** OKF long-context skepticism

## v3 rollout (US-32)

| Step | Action |
|------|--------|
| Enable | Set `AGENT_CONTEXT_COMPRESS=1` in shell or Cursor env for one week trial |
| Hook | `.cursor/hooks/context_compress_lifecycle.py` (beforeSubmitPrompt) |
| Measure | Compare `compressed_chars` / `original_chars` in hook logs |
| Scope | Tool/MCP payloads >~8k tokens prose; **not** manuscript tables or clinical numbers |

Documented in `context-optimization.mdc` § Context compression rollout.

## Take for agent-rules

| Pattern | Adopt | Notes |
|---------|-------|-------|
| Compress tool/log output before LLM | **Yes (MVP)** | `brain_assist/context_compress.py` + opt-in hook `AGENT_CONTEXT_COMPRESS=1` |
| Full Headroom product integration | **No** | Separate service; spike only |
| Token accounting in hooks | **Partial** | `agent_message` reports char ratio |

## LifeHarness layer

- **L4 Trajectory Regulation:** reduce context noise before submit without dropping scoped memory injection.

## Acceptance

- `pytest 40_operations/tests/test_context_compress.py` passes
- Hook no-op when env unset

## Reject

- Auto-compress manuscript drafts (writing integrity)
- Lossy compression of clinical numbers tables
