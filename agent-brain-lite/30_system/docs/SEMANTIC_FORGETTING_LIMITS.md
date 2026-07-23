# Semantic forgetting limits (P2 — Beyond Intelligence)

**Status:** Documentation only. No runtime token-expansion fix is claimed.

## Claim

In long-context agents, **semantic forgetting** can be structural: information may be present in context or memory stores yet remain unusable for downstream reasoning. Adding tokens or context window alone does not guarantee reliable recall.

## Harness implications (agent-rules)

1. **Diagnose by operation** — use MemFail-style `failure_mode` tags (`summary`, `storage`, `retrieval`) rather than a single recall score.
2. **Episodic-first** — keep `trajectory.jsonl` and raw hook payloads as primary evidence; defer `.agent/MEMORY.md` consolidation to milestones ([TRAJECTORY_RL_POLICY.md](TRAJECTORY_RL_POLICY.md)).
3. **Mixture routing** — route queries to the substore that matches the failure mode ([MEMORY_MIXTURE_ROUTING.md](MEMORY_MIXTURE_ROUTING.md)).
4. **Do not** assert that larger prompts fix routing or verifier mistakes without measured eval improvement.

## References (external — not reproduced locally)

- MemFail: [arXiv:2605.26667](https://arxiv.org/abs/2605.26667)
- Notebook theme: Beyond Intelligence (`b8896972-fd70-40ca-9456-15c8ff41e72a`)

## Related

- [BEYOND_INTELLIGENCE_MAP.md](BEYOND_INTELLIGENCE_MAP.md) (BI-4)
- [notebooklm_beyond_intelligence_external_verification.json](notebooklm_beyond_intelligence_external_verification.json)
