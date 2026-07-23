# Classification Hints – Full Reference

**Purpose:** Complete keyword and context mapping for orchestrator task classification. Used when inline hints in 00_orchestrator_agent.mdc are insufficient.

---

## Context / Files

| Match | Task Type |
|-------|-----------|
| `.R`, `.Rmd`, `**/analysis/**`, `**/statistics/**` | STATISTICS |
| `**/manuscript/**`, `**/writing/**`, `**/*paper*`, `**/article*`, `**/*.docx` | WRITING |
| `**/20_knowledge/wiki/**`, `**/*.canvas`, vault-centric markdown | WRITING or CODE_IMPL (pair with SKILL_obsidian-wiki-agent via Special Triggers) |
| Protocol/design docs | METHODOLOGY |
| Code under review | CODE_QA |

---

## Keywords (en)

| Task Type | Keywords |
|-----------|----------|
| STATISTICS | analysis, model, regression, test, p-value, CI, ANOVA, Bayes, EDA |
| WRITING | write, draft, manuscript, section, abstract, discussion |
| CODE_QA | check code, review, code quality |
| OUTPUT_CTRL | output gate, output check, kontrola outputa, provjeri output, final gate, zero tolerance, @OUTPUT_CTRL, @output-gate, isporuči, deliver before submit |
| METHODOLOGY | design, protocol, methodology, sample size, randomization, PICO |
| CLINICAL | patient, therapy, ICU, clinical scenario, anestezija, bedside, ECMO sedation, CDSS |
| PROMPT_ENG | prompt, CRAFT, RAG |
| RULES_MAINT | rules, audit, skill discovery, SkillsMP, find skill, nedostaje skill |
| LEGAL | contract review, NDA, MSA, DPA, ugovor, redline, indemnification, governing law |
| DISCOVERY_DRUG | discovery, drug discovery, novel therapeutic strategy, research directions, gap identification, MedDiscovery, full discovery |

---

## Special Triggers (+ Skill / Action)

| Keywords | Action |
|----------|--------|
| validate, swiss cheese, verification, self-assessment, validate task | Load SKILL_swiss-cheese; delegate by context (STATISTICS/CODE_QA/CODE_IMPL) |
| output gate, output check, kontrola outputa, provjeri output, @OUTPUT_CTRL, @output-gate, zero tolerance, final gate, isporuči, deliver before submit | **OUTPUT_CTRL**; load **SKILL_output-controller**; run `output_controller_gate.py --gate` |
| critical analysis, end of analysis, preparation for publication, submission, revision | Load SKILL_swiss-cheese; **mandatory validation** |
| figure, visualization, forest plot, methods diagram, all figures, figures for study | STATISTICS or CODE_IMPL; load SKILL_figure-pipeline; see Pipeline 5 in `30_system/behavior_rules/23_figure_visualization_pipeline.md` |
| exploratory analysis, EDA, flexplot, explorativna analiza, visual EDA, explore variables | STATISTICS; load SKILL_eda-flexplot; then **pause** after presenting results/options until user picks analysis method |
| systematic review, sustavni pregled, meta-analysis, meta analiza, combine studies, pooled estimate | STATISTICS; load SKILL_meta-analysis (covers SR + MA workflow; for PRISMA checklist only use prisma-checklist) |
| case report, case series, prikaz slučaja, serija slučajeva, CARE, write case report | WRITING; load SKILL_case-report-series (structure + CARE; for checklist only use reporting-care.mdc) |
| retrospective cohort, retrospektivna kohortna studija, kohortna studija, write cohort study, pisanje kohortne studije | WRITING; load SKILL_retrospective-cohort (structure + STROBE cohort; for checklist only use strobe-checklist) |
| prospective cohort, prospektivna kohortna studija, write prospective cohort, longitudinal cohort | WRITING; load SKILL_prospective-cohort |
| observational study, opservacijska studija, case-control, cross-sectional, presječna studija, studija slučaj-kontrola | WRITING; load SKILL_observational-studies (case-control/cross-sectional structure; for cohort use prospective/retrospective-cohort) |
| RCT, write RCT, randomizirana kontrolirana studija, pisanje RCT-a, clinical trial manuscript | WRITING; load SKILL_rct-manuscript (structure + CONSORT); for checklist only use consort-checklist |
| Obsidian, vault, PKM, wiki ingest, wikilink, LLM Wiki Mode, second brain, graph connectivity, wiki lint, JSON Canvas, Obsidian Bases, OFM, callout, transclusion | WRITING or CODE_IMPL; load **SKILL_obsidian-wiki-agent** (`obsidian-wiki-agent` in registry); CODE_IMPL when running `obsidian_connectivity_check.py` / bulk rewrites |
| discovery, drug discovery, novel therapeutic strategy, research directions, gap identification, full discovery, MedDiscovery-style | DISCOVERY_DRUG; use Pipeline 7A (MVP) from `30_system/behavior_rules/24_discovery_pipeline.md` or Pipeline 7B (full) from `30_system/behavior_rules/26_discovery_superpipeline.md` + `25_capability_registry.md` depending on phrasing |
| Grill-me, grill me, shared understanding, interview before coding, design tree, clarify requirements | CODE_IMPL; load **SKILL_grill-me**; then write-prd when aligned (`30_system/docs/AGENTIC_ENGINEERING_WORKFLOW.md`) |
| Write PRD, product requirements, prd.json, passes flag | CODE_IMPL; load **SKILL_write-prd** |
| PRD to issues, vertical slice, tracer bullet, decompose PRD | CODE_IMPL; load **SKILL_prd-to-issues** after write-prd |
| Ralph ON, Ralph OFF, Ralph loop, PROMISE COMPLETE, Exploration Mode | CODE_IMPL; **auto-pipeline** via `skill_rerank --auto-pipeline --dag` (full chain through ralph-loop); load **SKILL_ralph-loop** when executing |
| new feature, nova funkcionalnost, implement PRD, agentic engineering (semantic) | CODE_IMPL; run `skill_rerank --auto-pipeline --dag`; load returned bundle in order |
| Agentic OS, Re-Act OS, TAOR, Tree of Thought, @agentic-os | CODE_IMPL; load **SKILL_agentic-react-os** |
| research grill-me, scholarly alignment, PICO interview, before research spec, manuscript scope | STATISTICS / WRITING / METHODOLOGY by stage; load **SKILL_research-grill-me** |
| research spec, research-spec.json, scholarly spec, write research spec | Same; load **SKILL_write-research-spec** (`30_system/docs/SCHOLARLY_WORKFLOW.md`) |
| research milestones, spec to milestones, tracer bullet research | Same; load **SKILL_research-spec-to-milestones** |
| LOOP ON, LOOP OFF, run loop, scholarly loop | Same; load **SKILL_scholarly-iteration-loop** when LOOP ON |
| blog, newsletter, Substack, LinkedIn article, non-academic writing, piši blog | WRITING; load **SKILL_nonacademic-writer** (not manuscript-structure or literature-synthesis) |
| R statistics, R analiza, napiši R kod, glmmTMB, survival analysis R, paketi za statistiku | STATISTICS; load **SKILL_r-statistics** (test choice only → test-selection) |
| statsmodels, Python regression, OLS Python, ARIMA Python | STATISTICS; load **SKILL_statsmodels-python** only when Python/statsmodels explicit |
| which test, test selection, Welch, assumption check | STATISTICS; load **SKILL_test-selection** |
| contract review, pregled ugovora, NDA, MSA, DPA, redline, ugovor o suradnji | RULES_MAINT or MIXED; load **SKILL_legal-contract-review** (not legal advice) |
| find skill, SkillsMP, external skill, skill nije integriran, pretraži skill, nedostaje skill | RULES_MAINT; load **SKILL_skill-discovery**; then create-skill if import needed |
| clinical scenario, bedside, ICU question, anestezija, ECMO sedation, klinički slučaj, CDSS (bedside) | CLINICAL; load **SKILL_clinical-cdss** (not pharma document CDS) |
| review this paper, peer review, critique paper, academic paper review, arXiv review | WRITING; load **SKILL_academic-paper-review** (not manuscript-structure for own draft) |
| document review, fact-check document, audit this PDF, proofread report | CODE_IMPL or WRITING; load **SKILL_document-review** |
| research lookup, current evidence, recent studies on, what does literature say now | STATISTICS or WRITING; load **SKILL_research-lookup** |
| speech writer, TED talk, keynote, public speaking, conference talk script | WRITING; load **SKILL_presentation-speech** |
| powerpoint accessibility, accessible presentation, PPTX audit, slide accessibility | CODE_IMPL or WRITING; load **SKILL_powerpoint-accessibility** |
| meeting insights, analyze transcript, meeting summary, action items from meeting | CODE_IMPL; load **SKILL_meeting-insights** |
| compile latex, compile paper, latex PDF, fix latex error | CODE_IMPL; load **SKILL_latex-compile** |
| pitch deck, investor memo, fundraising, accelerator application | WRITING or MIXED; load **SKILL_investor-materials** |
| what if, scenario analysis, scenario planning, threat model horizon | CODE_IMPL; load **SKILL_scenario-planning** |
| trading analysis, risk manager, portfolio risk, R-multiple, position sizing | MIXED; load **SKILL_financial-trading** |
| drug discovery, diffdock, pathml, molecular docking, discovery workbench | DISCOVERY_DRUG; load **SKILL_drug-discovery-workbench** (Pipeline 7B pointer) |

---

## Relation tags (Rcml prompt analogue — Relation-Conditioned slice)

When classifying tasks, attach an optional **relation tag** to steer retrieval (not model training):

| Relation tag | Use when | Routing hint |
|--------------|----------|--------------|
| `causality` | bug fix, regression, failure diagnosis | Graphify/LARGER expand callers; avoid text-similarity-only grep |
| `dependency` | refactor, move module, API seam | `larger_graph_expand.py` after lexical hit; Graphify path |
| `assumption_chain` | statistics, methods, SAP | methodology skill before analysis skill |
| `evidence_strength` | clinical claims, manuscript, review | research-lookup / swiss-cheese before strong wording |
| `procedure_reuse` | repeat workflow, skill routing | `skill_rerank --dag --rwr` then `skill_verifier.py` |

Orchestrator: after `skill_rerank --dag`, run `skill_verifier.py --dag` before loading Tier-3 SKILL bodies (ACCEPT/DECOMPOSE/SKIP).

---

**Reference:** `.cursor/rules/00_orchestrator_agent.mdc`

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)
