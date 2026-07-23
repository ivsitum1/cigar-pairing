# Trust tier policy (skills + MCP)

Obsidian hub: [[Skill trust tiers]].

## Tiers

| Tier | Name | Agent may |
|------|------|-----------|
| 1 | metadata_only | List skill/MCP name and description only |
| 2 | instruction_access | Load SKILL.md or MCP docs into context |
| 3 | supervised_execution | Run tools only with explicit user approval per session |
| 4 | autonomous_execution | Run within workspace sandbox without per-call approval |

## Defaults

- **New community or agent-generated skills:** tier **3** (`registry.json` → `trust_tier_policy.default_new_skill`).
- **New MCP servers:** tier **3** (`mcp_trust_registry.json` → `default_new_server`).
- **Curated brain skills:** assigned by `skill_trust_bootstrap.py`; re-run after registry changes.

## Registry locations

- Skills: `30_system/SKILLS/registry.json` → `trust_tier` per skill, `trust_tier_policy` block.
- MCP: `30_system/docs/mcp_trust_registry.json`.

## Audit

```bash
python 40_operations/scripts/skill_trust_audit.py --json
python 40_operations/scripts/skill_auditor.py --skill-id <id>
python 40_operations/scripts/skill_auditor.py --scan-all
```

## ClawHavoc mitigation

- Never promote tier 3→4 without `skill_auditor.py` pass and human review.
- Block skills with auditor score below 30.
- See `.cursor/rules/skill-trust-tiers.mdc` for agent behavior.

## Promotion certificate (SEA-inspired, arXiv:2607.00871)

Tier 3 → 4 requires all of:

1. `skill_auditor.py --skill-id <id>` → score ≥ 70, no critical findings
2. Optional: `skill_process_rubric.py` on a golden trajectory → process_score ≥ 60
3. Human approval recorded (chat or commit message)

Treat promotion as an **auditable certificate**, not implicit trust from usage alone.

## Landscape

Full paper map: `30_system/docs/SELF_EVOLVING_AGENTS_LANDSCAPE.md`
