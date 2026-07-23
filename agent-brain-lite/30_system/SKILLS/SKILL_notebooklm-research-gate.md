---
name: notebooklm-research-gate
description: Gate implementation on NotebookLM-grounded Q&A with explicit VERIFIED/INFERRED/UNVERIFIED labels and source provenance. Use before acting on NotebookLM or YouTube-synthesized harness/skill claims. NOT full systematic review (meta-analysis) or quick PubMed lookup alone (research-lookup).
version: 1.3
last_updated: 2026-07-04
domain: tools
tokens: ~650
triggers:
  - notebooklm research gate
  - notebooklm verify claims
  - ground notebooklm synthesis
  - notebooklm before implement
  - verify notebook sources
  - NotebookLM research gate
requires_packages: []
reference_files:
  - docs/NOTEBOOKLM_CONSUMER_INTEGRATION.md
  - 30_system/docs/reference/notebooklm_rag_anatomy_grill_prompts.md
  - 30_system/docs/reference/notebooklm_skilldag_grill_prompts.md
  - 30_system/docs/LIFEHARNESS_4_LAYER.md
  - 30_system/docs/RAG_ANATOMY_MAP.md
  - 30_system/docs/SKILLDAG_MAP.md
  - 30_system/docs/notebooklm_rag_anatomy_external_verification.json
  - 30_system/docs/notebooklm_skilldag_external_verification.json
  - 30_system/docs/reference/notebooklm_relation_conditioned_grill_prompts.md
  - 30_system/docs/reference/notebooklm_harness_skilltree_grill_prompts.md
  - 30_system/docs/reference/notebooklm_harness_v2_grill_prompts.md
  - 30_system/docs/notebooklm_harness_v2_external_verification.json
  - 30_system/docs/RELATION_CONDITIONED_MAP.md
  - 30_system/docs/notebooklm_relation_conditioned_external_verification.json
  - 30_system/docs/notebooklm_harness_skilltree_external_verification.json
  - 30_system/docs/reference/notebooklm_batch_2026-06_grill_prompts.md
  - 30_system/docs/reference/notebooklm_batch_2026-06_questions.json
  - .agent/task/NOTEBOOKLM_BATCH_2026-06_FIRST_RUN.md
  - 30_system/docs/reference/notebooklm_user_notebook_91614142_grill_prompts.md
  - 30_system/docs/notebooklm_user_notebook_91614142_external_verification.json
  - 30_system/docs/reference/self_evolving_arxiv_registry.json
  - 30_system/docs/SELF_EVOLVING_AGENTS_LANDSCAPE.md
  - 20_knowledge/wiki/sources/notebooklm/self_evolving_2026_arxiv_bundle.md
  - reference/scientific_thinking/pubmed/search_syntax.md
pipeline_position:
  - grill-me
  - write-prd
conflicts_with:
  - meta-analysis
  - literature-synthesis
disambiguation: Gate NotebookLM answers before implementation; for PubMed-only quick lookup use research-lookup; for formal SR use meta-analysis.
---

# Skill: NotebookLM Research Gate

## When to use

- User or agent wants to **implement** something based on NotebookLM chat or YouTube notebook sources
- Harness, skill, or RAG ideas originate from *The Geometry of Intelligence* or similar notebooks
- Need GO/NO-GO with explicit claim statuses before PRD or code changes

## When NOT to use

- Simple NotebookLM Q&A with no implementation intent (use MCP `ask_question` directly)
- Clinical or statistical claims requiring formal SR (use meta-analysis / literature-synthesis)

## Procedure

1. **Auth and notebook**
   - MCP: `get_health` → `setup_auth` if needed → `select_notebook` or `add_notebook`
   - CLI fallback: `python 40_operations/scripts/notebooklm_consumer_extract.py check-auth` (profile default: `~/.notebooklm/profiles/default/storage_state.json`)
   - If API auth expired: `python 40_operations/scripts/notebooklm_grill_playwright.py` per `30_system/docs/reference/notebooklm_rag_anatomy_grill_prompts.md`

2. **Scoped query**
   - `ask_question` with focused question; reuse `session_id` for follow-ups
   - Prefer `source_format: footnotes` when available

3. **Claim extraction**
   - Split answer into atomic claims
   - Tag each: `VERIFIED` | `INFERRED` | `UNVERIFIED`
   - `VERIFIED`: backed by cited source you can open or reproduce locally
   - `INFERRED`: reasonable synthesis, not directly quoted
   - `UNVERIFIED`: benchmark numbers, repo URLs, or mechanisms not yet checked

4. **Cross-check (mandatory for GO)**
   - Critical claims → `research-lookup` or PubMed MCP
   - Block GO if implementation depends solely on UNVERIFIED benchmark gains

5. **AI Semantic Gate**
   - Classify usable content: CORE / BACKGROUND / REJECTED per `.cursor/docs/AI_SEMANTIC_GATE.md`
   - NotebookLM prose is never CORE without external verification

6. **Gate report**
   - Run: `python 40_operations/scripts/notebooklm_bridge.py gate-report --input <export.json>`
   - Or write equivalent markdown with GO/NO-GO and blockers

7. **Handoff**
   - GO → proceed to `write-prd` with `verification_protocol` populated
   - NO-GO → list verification steps; do not edit rules/skills/code on UNVERIFIED claims alone

## Verification checklist

- [ ] Every implementation-driving claim has a status label
- [ ] At least one external check for non-trivial technical claims
- [ ] Export archived under `outputs/notebooklm/`
- [ ] Wiki log updated if concepts promoted to `20_knowledge/wiki/`

## Related

- `SKILL_research-lookup.md`, `SKILL_model-native-skill-transform.md`
- [[NotebookLM research gate]]

## Semantic graph (auto)

- [[NotebookLM research gate]]
- [[Skill registry]]
- [[skills-auto-detect]]
- [SKILLS INDEX](../docs/indexes/SKILLS_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[NotebookLM research gate]]
- [[SKILL_research-lookup]]
- [[SKILL_model-native-skill-transform]]
- [[Research lookup skill]]
- [[LifeHarness four-layer model]]
