# SkillLens four-layer taxonomy (agent-rules)

**Version:** 1.0 | **Last updated:** 2026-06-08  
**Source:** SkillLens (arXiv:2605.08386) via Relation-Conditioned notebook gate  
**Map:** [RELATION_CONDITIONED_MAP.md](RELATION_CONDITIONED_MAP.md)

---

## Layers

| Layer | SkillLens | Purpose | Load when |
|-------|-----------|---------|-----------|
| **Policy** | Policy | Non-negotiable behaviour, safety, orchestration kernel | Always (Tier 0 rules) |
| **Strategy** | Strategy | Pipeline choice, subagent routing, stage order | Task classified; before heavy skills |
| **Procedure** | Procedure | Step workflows with progressive disclosure | After verifier ACCEPT/DECOMPOSE |
| **Primitive** | Primitive | MCP tools and scripts with stable schemas | On demand per procedure step |

---

## Artifact mapping

| Layer | Examples in this repo |
|-------|----------------------|
| Policy | `.cursor/rules/core-principles.mdc`, `00_orchestrator_agent.mdc`, `verification.mdc` |
| Strategy | `22_pipeline_and_refinement.md`, `skills-auto-detect.mdc` pipeline table, `skill-dag-router` |
| Procedure | `30_system/SKILLS/SKILL_*.md`, `skill_decompose.py` subunits |
| Primitive | `.cursor/mcp.json` tools, `40_operations/scripts/*.py` |

---

## Registry field

Optional per skill in `registry.json`:

```json
"granularity": "policy|strategy|procedure|primitive"
```

Validator: `40_operations/scripts/skill_registry.py validate` warns if value is invalid.

**Defaults by domain (when omitted):**

| domain | default granularity |
|--------|---------------------|
| engineering (grill-me, write-prd, ralph-loop) | procedure |
| statistics, writing, methodology, clinical | procedure |
| tools (notebooklm-research-gate, document-conversion) | procedure |
| MCP-only stubs | primitive |

Orchestrator skills (`grill-me`, `write-prd`, `skill-dag-router`) may be tagged `strategy` where they select pipelines rather than execute steps.

---

## Dual registry (SkillLens)

| Registry | File | Contents |
|----------|------|----------|
| Agent | `30_system/SKILLS/registry.json` | Skills, triggers, `depends_on`, optional `granularity` |
| Verifier | `30_system/docs/verifier_registry.json` | Thresholds, `force_action`, `rewrite_on_gap`, relation boosts |

Evolution: `evolve_dual_registry.py` | Validate: `verifier_registry_validate.py`

---

```bash
python 40_operations/scripts/skill_verifier.py --prompt "..." --dag --json
```

Actions: **ACCEPT** (full skill), **DECOMPOSE** (subunits via `skill_decompose`), **SKIP** (do not inject).

---

## Related

- [RELATION_CONDITIONED_MAP.md](RELATION_CONDITIONED_MAP.md)
- [SKILLDAG_MAP.md](SKILLDAG_MAP.md)
- [[Relation-conditioned harness]]
