# Self-evolving agents — landscape (2025–2026)

Canonical arXiv registry: `reference/self_evolving_arxiv_registry.json`  
Scan CLI: `python 40_operations/scripts/arxiv_self_evolving_scan.py`

## Maturity ladder (survey 2508.07407)

| Layer | What evolves | Our repo |
|-------|----------------|----------|
| Text-mutable artifacts | skills, rules, wiki, prompts | **Current default** — registry, SKILL_gap, error_memory |
| Harness co-evolution | routing, hooks, dispatch | **Human-gated only** — wargame + PRD; no auto orchestrator rewrite |
| Weight / adapter evolution | model parameters | Out of scope (frozen Cursor models) |

## Key papers → implementation map

### EvoSC (2602.01966) — contrastive + consolidation

- Contrastive reflection on success vs failure trajectories
- Consolidate into compact rules (not model weights)
- **Repo:** `contrastive_reflection.py`, `CONTRASTIVE_REFLECTION.md`

### MOSS (2605.22794) — source-level harness rewrite

- Failure batch → plan → implement → trial workers → user consent apply
- **Repo:** partial — `error_log`, `skill_gap_optimize_gate`, ATDP hooks; **not** auto container swap

### OPD-Evolver (2606.17628) — on-policy distillation for evolver

- Fast loop: read/use/write/maintain memory; slow loop: distill into policy
- **Repo:** `DISTILLATION_TRACE_PROTOCOL.md` (on-policy traces for md-system student)

### Metis (2606.24151) — text vs code memory

- Text: broad applicability; code tools: efficiency when pattern repeats
- **Repo:** wiki + `40_operations/scripts` as code-as-skill; crystallize after N repeats `[TO_CONFIRM threshold]`

### SEA (2607.00871) — anytime-valid certificates

- Self-modification only through auditable gates; frozen base + steering adapter
- **Repo:** `skill_auditor.py` (score ≥70), `skill_gap_optimize_gate.py` (composite 72), trust tiers

### SkillCoach (2607.01874) — process rubrics

Four dimensions (separate from outcome verifier):

1. Skill selection
2. Skill following
3. Skill composition
4. Skill-grounded reflection

- **Repo:** `skill_process_rubric.py` on `trajectory.jsonl`

### HASE (2607.03935) — harness-aware co-evolution

- Single agent edits harness components and task solutions in RL loop
- **Repo:** P2 research — document only; do not enable autonomous harness edits

### Agentic RL systems (2607.01120) — three pillars

1. Trajectory data protocol (step granularity) → **ATDP-lite**
2. Data proxy (governed learning substrate) → **PHI scrub in atdp.py**
3. Evolution control plane (when to update weights vs harness) → **skill_gap_optimize_gate + human gate**

## Operational commands

```bash
python 40_operations/scripts/arxiv_self_evolving_scan.py
python 40_operations/scripts/skill_process_rubric.py --trace 90_archive/artifacts/<run_id>/trajectory.jsonl --json
python 40_operations/scripts/contrastive_reflection.py --auto-latest --write-wiki --json
python 40_operations/scripts/skill_trust_audit.py --json
```

## NotebookLM bundle

Upload to notebook *The AI Frontier news*:

`20_knowledge/wiki/sources/notebooklm/self_evolving_2026_arxiv_bundle.md`

## Related wiki

- [[Self-evolving agents 2026 arXiv synthesis]]
- [[Skill trust tiers]]
- [[Contrastive reflection patterns]]
- [[Wargame blueprint protocol]]
