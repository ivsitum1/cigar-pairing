# SKILLS Markdown Index

Canonical hub for linking `SKILL_*` notes into functional units for Obsidian graph navigation.

## Related Hubs

- [30_system index](30_system_INDEX.md)
- [Folder index hub](../FOLDER_INDEX.md)
- [All notes index](../ALL_NOTES_INDEX.md)
- [Graph connectivity map](../GRAPH_CONNECTIVITY_MAP.md)
## Functional Units

### Knowledge graph (Obsidian)

- [[SKILL_obsidian-wiki-agent]] - ingest, Obsidian sintaksa (playbook u `30_system/SKILLS/reference/OBSIDIAN_AGENT_PLAYBOOK.md`), Canvas/Bases, `index`/`log`, provjera grafa za `20_knowledge/wiki/`; LLM Wiki Mode u `30_system/claude.md`.

### Setup and Validation

- [[SKILL_setup-project]] - inicijalna struktura projekta; nastavlja na [[SKILL_validate-setup]].
- [[SKILL_validate-setup]] - provjera ispravnosti strukture; prije analize ili pisanja.
- [[SKILL_swiss-cheese]] - višeslojna validacija kritičnih rezultata; most prema checklistama i pisanju.
- [[SKILL_create-sop]] - pretvara slozene popravke u standardni postupak; koristi se nakon incidenta ili uspjesne stabilizacije.
- [[SKILL_document-conversion]] - konverzija docx/xlsx/txt/md artefakata; priprema input za ostale skillove.

### Statistical Analysis Pipeline

- [[SKILL_r-statistics]] - R implementacija, paketi, reproducibilni skripti; kodiranje + `reference/r_statistics_packages.md`; delegira na specijalizirane skillove ispod.
- [[SKILL_eda-flexplot]] - eksplorativna analiza i vizualna inspekcija; zatim [[SKILL_test-selection]] ili [[SKILL_meta-analysis]].
- [[SKILL_test-selection]] - odabir inferencijskog testa po dizajnu i distribuciji; ulaz u glavnu statisticku analizu.
- [[SKILL_meta-analysis]] - puni SR/MA workflow od protokola do pooled procjene; grana prema [[SKILL_forest-plot]], [[SKILL_publication-bias]] i [[SKILL_sensitivity-analysis]].
- [[SKILL_forest-plot]] - izrada pojedinacnog forest plota ili outputa iz MA pipelinea.
- [[SKILL_publication-bias]] - funnel/Egger/trim-and-fill procjena; nakon dovrsene meta-analize.
- [[SKILL_sensitivity-analysis]] - robustnost MA nalaza (LOO, influence, method checks); prije finalnog tumacenja.
- [[SKILL_bayesian-workflow]] - puni Bayes postupak (priors, fit, dijagnostika, reporting); alternativna analiticka grana.
- [[SKILL_target-trial-emulation]] - emulacija RCT-a iz opservacijskih podataka; causal-specijalizacija.
- [[SKILL_statsmodels-python]] - Python statsmodels (OLS, GLM, ARIMA) samo na eksplicitni zahtjev; inace R grana.

### Non-Academic Writing

- [[SKILL_nonacademic-writer]] - blog, newsletter, tutorial; outline + hook + izvori; NE rukopis/IMRaD/SR.
- Pariranje (Tier 3): [[SKILL_avoid-ai-formulations]], [[SKILL_ai-detection]] prema `registry.json` `tier3_pairing`.

### Reporting and Methodology Checklists

- [[SKILL_prisma-checklist]] - PRISMA 2020 audit za SR/MA rukopise; tipicno nakon [[SKILL_meta-analysis]].
- [[SKILL_consort-checklist]] - CONSORT compliance za RCT manuskripte; uz [[SKILL_rct-manuscript]].
- [[SKILL_strobe-checklist]] - STROBE compliance za opservacijske studije; uz cohort/observational writing skillove.
- [[SKILL_grade-assessment]] - procjena sigurnosti dokaza po ishodima; dodaje metodolosku tezinu diskusiji i zakljuccima.

### Skills audit 2026-05 (new + enriched)

Hub: [[Skills audit 2026-05]]

- [[SKILL_academic-paper-review]] - peer review jednog rada
- [[SKILL_document-review]] - fact-check PDF/DOCX/PPTX/XLSX
- [[SKILL_research-lookup]] - brzi cited lookup (MCP)
- [[SKILL_presentation-speech]] - TED/keynote skripte
- [[SKILL_powerpoint-accessibility]] - PPTX a11y
- [[SKILL_meeting-insights]] - transkript → akcije
- [[SKILL_latex-compile]] - LaTeX → PDF
- [[SKILL_investor-materials]] · [[SKILL_scenario-planning]] · [[SKILL_financial-trading]] · [[SKILL_drug-discovery-workbench]]
- Reference: [[Medical research writing references]] · [[Obsidian literature workflow references]]

### Manuscript Writing Unit

- [[SKILL_manuscript-structure]] - IMRaD strukturna provjera prije stilskih dorada.
- [[SKILL_avoid-ai-formulations]] - humanizacija i stilne zamjene; prije ili nakon [[SKILL_ai-detection]].
- [[SKILL_ai-detection]] - provjera i smanjenje AI-signala na postojecom tekstu.
- [[SKILL_literature-synthesis]] - narativna sinteza, analysis grid i gap identifikacija bez obaveznog poolinga.
- [[SKILL_rct-manuscript]] - pisanje/strukturiranje RCT rada; validira se kroz [[SKILL_consort-checklist]].
- [[SKILL_observational-studies]] - pisanje case-control/cross-sectional rada; validira se kroz [[SKILL_strobe-checklist]].
- [[SKILL_retrospective-cohort]] - pisanje retrospektivne kohortne studije; metodoloski izlaz kroz [[SKILL_strobe-checklist]].
- [[SKILL_prospective-cohort]] - pisanje prospektivne kohortne studije; metodoloski izlaz kroz [[SKILL_strobe-checklist]].
- [[SKILL_case-report-series]] - pisanje case report/series manuskripta po CARE logici.

### Figure and Visualization Unit

- [[SKILL_figure-pipeline]] - orkestracija svih publikacijskih figura u jednom prolazu.
- [[SKILL_forest-plot]] - kljucna MA figura; koristi se samostalno ili unutar figure pipelinea.
- [[SKILL_publication-bias]] - funnel i povezane bias figure za MA sekciju rezultata.

### Engineering Product Loop

- [[SKILL_agentic-react-os]] - TAOR, planning checkpointovi, CoT/ToT i limiti iteracija; operativni most prema proširenom vodiču `AGENTIC_REACT_OS.md` i `CLI_VS_MCP_AGENT_NATIVE.md` u `.cursor/docs/`.
- [[SKILL_grill-me]] - strukturirano razjasnjavanje zahtjeva prije implementacije.
- [[SKILL_write-prd]] - izrada software PRD specifikacije s pass kriterijima.
- [[SKILL_prd-to-issues]] - razlaganje PRD-a na vertikalne sliceove i taskove.
- [[SKILL_ralph-loop]] - iterativna izvedba po PRD-u uz TDD i progress logging.

### Scholarly Research Loop

- [[SKILL_research-grill-me]] - uskladivanje istrazivackog scopea i dizajna prije specifikacije.
- [[SKILL_write-research-spec]] - izrada `research-spec.json` za manuskript/analiticki rad.
- [[SKILL_research-spec-to-milestones]] - razlaganje research-speca u milestonee i redoslijed izvedbe.
- [[SKILL_scholarly-iteration-loop]] - iterativna izvedba istraživackih milestonea uz validacijske kontrole.

### Excluded from this index (deprecated staging)

External `SKILL.md` under `90_archive/imports/` are **not** brain skills. Use registry entries in `30_system/SKILLS/` only. See [[Archived skills staging]].

### Skill Governance and Expansion

- [[SKILL_create-skill]] - meta-skill za kreiranje novih skillova, eval suite i optimizacijske petlje.
- [[SKILL_skill-discovery]] - pretraga lokalnog registryja i SkillsMP prije importa.
- [[SKILL_obsidian-wiki-agent]] - wiki ingest, graph health, semantic linking (vidi [[Wiki semantic graph linking]]).

### Clinical and Legal

- [[SKILL_clinical-cdss]] - bedside ICU/anestezija; subagent CDSS, ne pharma dokumenti.
- [[SKILL_legal-contract-review]] - pregled ugovora HR/EU (playbook [[contract_review_playbook_hr_eu]]); nije pravni savjet.

### Reference playbooks (stats / methods)

K-Dense i statsmodels reference datoteke povezuju se na skillove preko [[REFERENCE_INDEX]] i [[Statistics skill stack]].

#### Statsmodels (Python) — [[SKILL_statsmodels-python]]

- [[linear_models]] - OLS, robust SE
- [[glm]] - GLM obitelj
- [[discrete_choice]] - logit/probit
- [[time_series]] - ARIMA
- [[stats_diagnostics]] - dijagnostika reziduala
- Hub: `30_system/SKILLS/reference/kdense/statsmodels/INDEX.md`

#### K-Dense (R / opći)

- [[test_selection_guide]] · [[assumptions_and_diagnostics]] · [[effect_sizes_and_power]] · [[reporting_standards]] · [[bayesian_statistics]]
- R kodiranje: [[r_statistics_coding]] · [[r_statistics_packages]] — skill [[SKILL_r-statistics]]

## Pipeline Bridges

- EDA to inference (R): [[SKILL_eda-flexplot]] -> [[SKILL_test-selection]] -> [[SKILL_r-statistics]] (ili [[SKILL_meta-analysis]] / [[SKILL_bayesian-workflow]])
- Analysis to manuscript: [[SKILL_eda-flexplot]] -> [[SKILL_meta-analysis]] -> [[SKILL_swiss-cheese]] -> [[SKILL_manuscript-structure]]
- Blog / newsletter: [[SKILL_nonacademic-writer]] -> opcionalno [[SKILL_avoid-ai-formulations]] ili [[SKILL_ai-detection]]
- Meta-analysis full flow: [[SKILL_meta-analysis]] -> [[SKILL_forest-plot]] -> [[SKILL_publication-bias]] -> [[SKILL_prisma-checklist]]
- Agentic OS (disciplina izvođenja): [[SKILL_agentic-react-os]] uz prošireni vodič `.cursor/docs/AGENTIC_REACT_OS.md`
- Engineering execution: [[SKILL_grill-me]] -> [[SKILL_write-prd]] -> [[SKILL_prd-to-issues]] -> [[SKILL_ralph-loop]]
- Scholarly execution: [[SKILL_research-grill-me]] -> [[SKILL_write-research-spec]] -> [[SKILL_research-spec-to-milestones]] -> [[SKILL_scholarly-iteration-loop]]
