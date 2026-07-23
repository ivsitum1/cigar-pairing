---
name: arxiv-skill-scout
description: Monthly arXiv scan for agent/stat/CS methods to propose new procedural skills. Use for arxiv monthly, arxiv digest, scan arxiv for skills. NOT PubMed clinical lookup (research-lookup) or SkillsMP marketplace (skill-discovery).
version: 1.0
last_updated: 2026-06-01
domain: meta
tokens: ~650
triggers:
  - arxiv monthly
  - arxiv digest
  - scan arxiv for skills
  - arxiv skill scout
  - monthly arxiv scan
requires_packages:
  - arxiv>=2.1.0
reference_files:
  - ../../30_system/config/arxiv_monthly_scan.json
conflicts_with:
  - research-lookup
  - skill-discovery
disambiguation: Use for monthly preprint scouting to propose agent/stat/CS skills. For clinical evidence use research-lookup (Consensus MCP + PubMed). For SkillsMP/GitHub skill import use skill-discovery. Never auto-create skills without user approval.
pipeline_position: []
---

# Skill: arXiv skill scout

## When to use

- User asks for monthly arXiv digest or skill ideas from stat/CS/math preprints
- Scheduled monthly run (Task Scheduler) produced `.agent/task/arxiv_digest_YYYY-MM.md`
- Before `create-skill` when the source is a methods preprint, not SkillsMP

## When NOT to use

- Clinical or biomedical evidence questions → `research-lookup`
- Hunting existing agent skills on SkillsMP → `skill-discovery`
- Systematic review / meta-analysis → `meta-analysis`

## Step-by-step procedure

1. **Run CLI** (repo root):

   ```bash
   py -3 40_operations/scripts/arxiv_monthly_scan.py
   ```

   Optional: `--month YYYY-MM`, `--dry-run` (query only), `--json`.

2. **Read outputs:**
   - `.agent/task/arxiv_scan_YYYY-MM.json`
   - `.agent/task/arxiv_digest_YYYY-MM.md`

3. **Present digest** to user: top papers + **Proposed skills** section (1–3 candidates).

4. **Human gate (mandatory):** Ask approve/reject per `proposed_skill_id`. Do **not** write `SKILL_*.md` or edit `registry.json` until user approves.

5. **On approve:** Hand off to `SKILL_create-skill.md` — procedural workflow only; label source as non-peer-reviewed arXiv preprint.

6. **Optional log:**

   ```bash
   python 40_operations/scripts/skill_gap_ingest.py wiki-log --detail "arxiv scout YYYY-MM approved <id>"
   ```

## Safety

- Preprints are **not** peer-reviewed; do not use for clinical dosing or treatment claims.
- No PHI in queries or digests.
- Proposals must describe **repeatable procedures**, not one-off trivia.

## Verification

- [ ] Digest states non-peer-reviewed status
- [ ] No registry change without explicit user approval
- [ ] Disambiguated from Consensus.app and internal literature-synthesis "consensus meter"

## Related

- `SKILL_skill-discovery.md`, `SKILL_create-skill.md`
- Config: `30_system/config/arxiv_monthly_scan.json`

## Related Hubs

- [[Skill gap pipeline]]
- [[arxiv skill scout]]
