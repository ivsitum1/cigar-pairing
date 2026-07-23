---
name: literature-synthesis
description: Use for narrative synthesis, analysis grid, consensus meter, gap identification (no mandatory quantitative pooling). For full systematic review or meta-analysis workflow use meta-analysis; for PRISMA check use prisma-checklist; for manuscript structure use manuscript-structure. Triggers include: literature review, lit review, synthesis, analysis grid, consensus meter, gap identification.
version: 1.3
last_updated: 2026-05-18
domain: writing
tokens: ~1350
triggers:
  - literature review
  - lit review
  - synthesis
  - analysis grid
  - consensus meter
  - gap identification
  - research gap
  - critical review
requires_packages: []
reference_files:
  - reference/literature_synthesis_templates.md
  - reference/scientific_thinking/literature_review_phases.md
  - reference/scientific_thinking/database_strategies.md
  - reference/scientific_thinking/pubmed/search_syntax.md
  - reference/medical_research/INDEX.md
  - reference/medical_research/claim-strength-calibrator/hard-rules.md
  - reference/medical_research/reference-integrity-checker/hard-rules.md
  - reference/obsidian_literature/CLAIM-EXTRACTION.md
  - reference/obsidian_literature/RESEARCH-GAPS.md
pipeline_position: [4, 6]
---

# Skill: Literature Review Synthesis

## When to use

Use this skill when:
- Synthesizing findings across multiple research papers into a coherent narrative
- Building an analysis grid to extract and compare study characteristics
- Assessing degree of consensus on a research question (consensus meter)
- Identifying research gaps to justify a new study
- Constructing boolean search strings for database searches
- User asks "write a literature review", "identify research gaps", "synthesize the literature", "build an analysis grid"

## Prerequisites

- Research question or topic defined
- Access to relevant papers (full text or abstracts)
- Optional: `reference/literature_synthesis_templates.md` for grid and consensus meter templates

## Step-by-step procedure

### 1. Boolean search string construction

**Reproducible search log:** for each database, save query text, date, and result count before screening (see `reference/scientific_thinking/literature_review_phases.md`; full SR/MA remains `meta-analysis`). Prefer PubMed MCP over raw HTTP unless implementing custom E-utilities.

Construct a structured search string for systematic literature retrieval:

- Identify **core topic terms** (population, intervention/exposure, outcome)
- Connect synonyms within each concept using **OR**
- Connect different concepts using **AND**
- Apply truncation (*) and phrase markers ("") where appropriate
- Specify target databases (PubMed, Scopus, Web of Science, CINAHL, etc.)

Example: `("mechanical ventilation" OR "invasive ventilation") AND ("weaning" OR "liberation") AND ("outcome*" OR "mortality")`

Document the search strategy: database, date, filters, number of results.

### 2. Analysis Grid extraction

For each included study, extract into a structured grid:

| Study (Author, Year) | Aim | Design/Method | Sample | Key Findings | Limitations | Gap Identified |
|-|-|-|-|-|-|-|

- Populate one row per study
- Use consistent terminology across rows
- Note methodological quality observations in the Limitations column
- Load `reference/literature_synthesis_templates.md` for the full template when executing this step

### 3. Consensus Meter assessment

Quantify the degree of agreement across studies on specific research questions:

- For each RQ or sub-question, tally: **studies supporting** vs. **studies contradicting** vs. **inconclusive/mixed**
- Express as a ratio or percentage (e.g., "7/10 studies support X" = 70% consensus)
- Visual indicator: High consensus (>80%) | Moderate (50-80%) | Low/Divided (<50%)
- Where consensus is low or divided, this signals a gap worth investigating

### 4. Thematic synthesis

Organize the grid findings into coherent themes:

- Group studies by **thematic similarity** (shared outcomes, populations, or methods)
- Identify **contradictions** between studies and possible explanations (methodological differences, population differences, measurement variation)
- Note **methodological trends** (shift from cross-sectional to longitudinal, increasing use of specific tools)
- Identify **temporal patterns** (how findings have evolved over time)

### 4b. Claim strength and evidence gate (before gaps or writing handoff)

When promoting claims from paper notes to synthesis or manuscript:

1. Load `reference/medical_research/claim-strength-calibrator/hard-rules.md` and `reference/obsidian_literature/CLAIM-EXTRACTION.md`.
2. Label each claim: speculative | observed | supported | strong; tie to Evidence Record ID.
3. **Do not** promote abstract-only or weak sources into Research Gaps or main narrative.
4. For citation checks, load `reference/medical_research/reference-integrity-checker/` when verifying DOI/PMID.

### 5. Gap statement formulation

From the analysis grid and consensus meter, articulate what remains unknown:

- Synthesize where the literature **converges** and where it **diverges**
- Identify specific populations, settings, outcomes, or methods that are **under-studied**
- Frame each gap as a potential research question
- Prioritize gaps by: clinical relevance, feasibility, and novelty

### 6. Critical narrative writing

Draft the literature review section (1000-1200 words for a standard manuscript):

- Each study should be **evaluated**, not merely described — assess its contribution and limitations
- Use the **inverted triangle** structure: broad context first, narrowing to the specific gap (see `SKILL_manuscript-structure.md` for introduction guidance)
- Organize by **theme**, not chronologically (unless temporal evolution is the point)
- End with a clear **gap statement** that directly motivates the current study's research question
- Apply `SKILL_avoid-ai-formulations` principles: no AI-flagged phrases, varied sentence structure, natural academic voice

## Accuracy and guardrails (mandatory)

- **Synthesis only from provided studies.** Do not invent study details, effect sizes, or author names. Every claim in the synthesis must be traceable to the input (studies, grid, or user-supplied text).
- **When only the topic is given (no study list, no abstracts):** Do not generate a synthetic narrative or "konsenzus je" / "literatura pokazuje". Ask explicitly for specific studies, papers, or a reference list so that synthesis can be evidence-based.
- **Contradictory findings:** Describe inconsistency and heterogeneity; do not claim a single "winner" when studies conflict. Recommend further research and frame as mixed or insufficient evidence where appropriate.
- **Gaps:** Identify gaps from the actual comparison (what was not studied, or not studied in the target population/setting), not generic placeholders.

## Edge cases

- **Multi-language data:** Use AI transcription for non-English audio sources, then AI translation templates to prepare content for English manuscript writing. Always note the original language and translation method in the manuscript.
- **High similarity scores:** If plagiarism/similarity checks flag sections of the review, manually rewrite those sections. Synthesis should be original analytical prose, not paraphrased abstracts.
- **Large manuscripts:** When checking AI detection or similarity on reviews exceeding 1500 words, process in batches of 1500-10000 words to stay within tool limits.
- **Systematic reviews:** If the study itself is a systematic review, the entire manuscript IS the literature synthesis — skip a separate "literature review" section. The Introduction provides only the framing context, and Methods/Results contain the synthesis. To *conduct* a full systematic review or meta-analysis (protocol, search, pooling, PRISMA flow), use SKILL_meta-analysis; use this skill for narrative synthesis, analysis grid, and gap identification within or outside an SR.

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Napravi analysis grid i istraživačke praznine za literaturu o temi X."  
**Output:** "Grid i kategorije `[INFERRED]` iz pitanja; citati i godine `[EXTRACTED]` iz dostavljenih radova; bez liste studija `[BLANK]`."

## Verification

- [ ] Boolean search string documented with database, date, and result count
- [ ] Analysis grid complete with all included studies (one row per study)
- [ ] Consensus meter assessed for each primary research question
- [ ] Themes identified with contradictions and trends noted
- [ ] Gap statement clearly articulated and linked to the proposed study
- [ ] Narrative is critical and evaluative, not merely descriptive
- [ ] No AI-flagged phrases; natural academic prose
- [ ] Every claim traceable to provided studies (no fabrication); if only topic given, user was asked for specific studies/sources

## Learning integration

- **task_type:** writing
- **log_fields:** studies_reviewed, themes_identified, consensus_level, gaps_found
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related rules and references

- `SKILL_manuscript-structure.md` — IMRaD structure check, inverted triangle, CARS model
- `SKILL_avoid-ai-formulations.md` — Phrase-level revision for natural writing
- `SKILL_ai-detection.md` — Automated AI score checking
- `SKILL_prisma-checklist.md` — PRISMA 2020 for systematic reviews
- `.cursor/rules/writing-manuscript-structure.mdc` — Section-level writing rules
- `reference/literature_synthesis_templates.md` — Analysis grid and consensus meter templates

## Related Hubs

- [[Skills audit 2026-05]]
- [[Medical research writing references]]
- [[Obsidian literature workflow references]]
- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[hard-rules]]
- [[literature_synthesis_templates]]
- [[literature_review_phases]]
- [[database_strategies]]
- [[search_syntax]]
- [[INDEX]]
- [[hard-rules]]
- [[CLAIM-EXTRACTION]]
- [[RESEARCH-GAPS]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]


<!-- auto-learn:cand_traj_20260611_133322_001 -->
## Trajectory RL Guardrail (2026-06-11)
- Trigger reasons: trajectory:tool_correctness<0.7, trajectory:plan_quality<0.7, trace:90_archive/artifacts/bench_rl_demo/run_20260527_lit_bad_tool/trajectory.jsonl
- Trace reference: `90_archive/artifacts/bench_rl_demo/run_20260527_lit_bad_tool/trajectory.jsonl`
- Match the declared plan step to the correct MCP tool; do not substitute web fetch when PubMed is required.
- Before citing literature, call the PubMed MCP search tool (not generic web fetch) unless the user explicitly requests open-web-only search.
- On benchmark runs, set `expected_tool` on `tool_selected` trajectory events per `30_system/docs/TRAJECTORY_EMIT_PROTOCOL.md`.
- Rollback: remove this block if skill evals or trajectory benchmark regress.
