# Claude Science → The Machine — Adoption Map

**Version:** 1.0 | **Last Updated:** 2026-07-03
**Status:** Concept mapping + 2 quick wins implemented; remaining proposals routed through weekly-digest governance.

## Context

Anthropic launched **Claude Science** on 2026-06-30 — an AI workbench for researchers, positioned as "Claude Code for science." It is a single coordinating agent over 60+ curated skills/connectors, a dedicated reviewer agent for QA, auditable artifacts, session forking, and compute abstraction (HPC/Modal). This document maps those concepts to The Machine (`THE_MACHINE.md`) and records what to adopt.

**Verification note:** feature descriptions are `[EXTRACTED]` from the public launch post (anthropic.com/news/claude-science-ai-workbench) and press coverage on 2026-07-03. Treat product-capability claims as vendor-stated, not independently benchmarked.

## Concept → component map

| Claude Science concept | The Machine today | Verdict |
|---|---|---|
| Generalist coordinating agent | Orchestrator (`00_orchestrator_agent.mdc`) — classify + delegate to subagents | ✅ Already have |
| 60+ curated skills/connectors | `registry.json` (71 skills, tiered, DAG-routed) | ✅ Already have |
| Reviewer agent (bad citations, untraceable numbers, figure↔code mismatch, self-correct) | Verifier (collect-only until 2026-09-01), `author_claims_check.py`, `verification.mdc` (adversarial/statistical) | ⚠️ Partial → **Quick win 1** |
| Auditable artifacts (code + env + methodology + message history) | `trajectory.jsonl`, logs, `LEARNING_BLOCK` — process telemetry, not per-deliverable bundles | ⚠️ Partial → **Quick win 2** |
| Scientific DB connectors (UniProt, PDB, ClinVar, ChEMBL, GEO) | MCP: `pubmed`, `consensus`, `books_rag`, `pdf` | ➡️ Gap — see proposals |
| Session forking (compare approaches, keep context) | git worktrees, Cursor Tasks, fan-out (`AGENT_AUTONOMY_AND_PARALLEL.md`) | ✅ Equivalent (documented below) |
| Compute abstraction (SSH/HPC/Modal, job submission) | Local GPU (books_rag, RTX 4060); no cluster | ➡️ N/A for single-user; revisit if scale grows |
| NVIDIA BioNeMo (Evo 2, Boltz-2, OpenFold3) | — | ➡️ Out of scope (Ivan's domain = clinical/biostat, not structural bio) |
| AI for Science credits ($30k, apply by 2026-07-15) | — | ℹ️ **Action for Ivan** — eligibility decision, not a code change |

## Quick wins implemented (this change)

### QW1 — Reviewer-agent QA stage → `.cursor/rules/reviewer-agent.mdc`
Final-stage deliverable QA distinct from `verification.mdc` (which is adversarial/statistical). Four checks lifted from the Claude Science reviewer: citation existence + support, number traceability, figure↔code consistency, self-correct loop. Wraps existing `author_claims_check.py`; invoked as `@review-stage` or as last orchestrator pipeline stage.

### QW2 — Artifact audit bundle → `30_system/SKILLS/SKILL_artifact-audit-bundle.md`
Per-deliverable reproducibility bundle (exact code + env freeze + plain-language methodology + session ref) under the existing `90_archive/artifacts/<run_id>/` convention. Registered in `registry.json` (`artifact-audit-bundle`).

## Session forking — existing equivalence (no new work)

Claude Science "session forking" = compare analytical approaches without losing the original. The Machine already covers this: **git worktrees** (`using-git-worktrees`) for isolated code branches, **Cursor Tasks / fan-out** for parallel independent tracks with fan-in (`AGENT_AUTONOMY_AND_PARALLEL.md`). No adoption needed; documented here so it is not re-proposed.

## Proposals routed to governance (NOT implemented here)

These are candidate improvements; they enter the normal pipeline (weekly digest → `digest_proposal_ledger.jsonl` → human GO):

1. **Scientific DB MCP connectors** — several are already available as deferred MCP servers (ClinicalTrials.gov, bioRxiv/medRxiv, ICD-10-CM/PCS, PMC full-text). Proposal: register the clinically relevant ones (ClinicalTrials, ICD-10, PMC) in `.cursor/mcp.json` with prescreen entries. *Value: high for clinical work; Effort: low.*
2. **Reviewer agent as scheduled gate** — once the Verifier exits collect-only (2026-09-01), fold QW1 checks into the Verifier learning loop. *Value: medium; Effort: medium; blocked until 2026-09-01.*
3. **Artifact bundle auto-emit hook** — a `stop`/`sessionEnd` hook that auto-generates QW2 bundles for flagged deliverables. *Value: medium; Effort: medium; defer until QW2 skill is used manually a few times.*

## Related

- [THE_MACHINE.md](THE_MACHINE.md)
- [LIFEHARNESS_4_LAYER.md](LIFEHARNESS_4_LAYER.md)
- [MACHINE_PRIMARY_SECONDARY.md](MACHINE_PRIMARY_SECONDARY.md)
- `.cursor/rules/reviewer-agent.mdc`
- `30_system/SKILLS/SKILL_artifact-audit-bundle.md`

## Semantic graph (auto)

- [[THE_MACHINE]]
- [[Orchestrator - agent roles]]
- [[Skill registry]]
- [FOLDER INDEX](FOLDER_INDEX.md)
- [GRAPH CONNECTIVITY MAP](GRAPH_CONNECTIVITY_MAP.md)
