---
name: test-selection
description: Selects statistically appropriate tests based on design, distribution, sample size, and robustness needs, with explicit primary vs sensitivity choices. Use when users ask which test to use or how to justify test selection.
version: 1.2
last_updated: 2026-05-16
domain: statistics
tokens: ~1500
triggers:
  - which test
  - test selection
  - Welch
  - comparison of groups
  - statistical test choice
  - power analysis
  - sample size
  - multiple comparison
  - assumption check
requires_packages: []
reference_files:
  - reference/kdense/test_selection_guide.md
  - reference/kdense/assumptions_and_diagnostics.md
  - reference/kdense/effect_sizes_and_power.md
  - reference/kdense/reporting_standards.md
  - reference/kdense/results_reporting_snippets.md
pipeline_position: [1]
---

# Skill: Select Appropriate Statistical Test

## When to use

Use this skill when:
- Need to choose statistical test for comparison
- Uncertain which test to use
- Want to follow modern best practices
- Need to justify test choice

## Prerequisites

- Data prepared
- Know design (independent groups, paired, multiple groups)
- Understand outcome type (continuous, binary, time-to-event)

## Honesty and grounding checkpoints

- Mark recommendations with claim tags where appropriate (`[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, `[BLANK]`).
- Do not claim assumption checks passed without explicit evidence (normality, variance, outliers, sample size constraints).
- If key diagnostics are missing, return `[BLANK]` for final test choice and request required checks.
- Keep primary test and sensitivity test explicitly separated.

## Pipeline position (with EDA)

After `eda-flexplot` (or equivalent EDA), use this skill before inferential analysis. Do not run pooling or manuscript Results in the same turn unless the user explicitly requests it.

Load `reference/kdense/test_selection_guide.md` when choosing among several plausible tests; load `assumptions_and_diagnostics.md` before locking the primary test.

## Step-by-step procedure

0. **Power and sample size (when N not fixed):**
   - If required N is unknown, run or request a priori power analysis; mark target N as `[BLANK]` until protocol or data confirm it.
   - Document primary outcome and minimally important effect size before viewing results.

1. **Identify design:**
   - Independent groups (between-subjects)?
   - Paired/matched/repeated measures (within-subjects)?
   - Multiple groups (> 2)?

2. **For two independent groups, continuous outcome:**
   - **PRIMARY:** Welch's t-test (default, robust to unequal variances). When Levene test indicates unequal variances (p < 0.05), always recommend Welch and state that nejednake varijance (or "varijance") justify Welch over Student's t-test.
   - **If small sample (n < 20) or non-normal (e.g. Shapiro-Wilk p < 0.05):** Use Mann-Whitney U (Wilcoxon rank-sum) or permutation test; mention "neparametrijski", "nonparametric", or "asimetrična distribucija" and refer to Shapiro-Wilk / normalnost.
   - **If outliers present:** Yuen-Welch trimmed mean test (20% trimming)
   - **SECONDARY (sensitivity only):** Mann-Whitney U test

3. **For paired groups, continuous outcome:**
   - **PRIMARY:** Paired t-test (upareni t-test) when differences are normal (Shapiro-Wilk p > 0.05). Explicitly state "paired" or "upareni" and "paired t-test" or "upareni t-test". Do not recommend independent-samples test or Wilcoxon when distribution of differences is normal.

4. **For multiple groups (> 2), continuous outcome:**
   - **PRIMARY:** One-way ANOVA (or Welch ANOVA if heteroscedastic). Always recommend post-hoc (e.g. Tukey HSD or Bonferroni) when comparing groups. Do not recommend only t-test (više od 2 grupe); do not recommend Kruskal-Wallis when distribution is normal (SW p > 0.1).

5. **Multiple comparisons:**
   - If more than one primary comparison (or many secondary tests), pre-specify correction (Bonferroni, Holm, or FDR) before viewing results.
   - Label exploratory comparisons explicitly.

6. **Assumption checks (R or Python):**
   - **R:** normality (Shapiro-Wilk or Q-Q), variance (Levene), design-appropriate diagnostics per `reference/kdense/assumptions_and_diagnostics.md`.
   - **Python (tabular data):** optional `python 40_operations/python/statistics/assumption_checks.py` on CSV/parquet; do not replace R workflow unless user requests Python.

7. **Report both primary and secondary:**
   - Always report effect size and 95% CI with p-values (never p alone).
   - Always report primary test (Welch/Permutation/Robust)
   - Add secondary (non-parametric) as sensitivity analysis
   - Clearly label sensitivity analyses
   - **Manuscript Results:** Vancouver (or journal style) by default; APA only if user requests it (`reference/kdense/reporting_standards.md`, `results_reporting_snippets.md`).

## Decision tree

```
Two independent groups, continuous outcome?
├─ Normal + Equal variances? → Standard t-test (rare)
├─ Normal + Unequal variances? → PRIMARY: Welch's t-test
├─ Small sample OR Non-normal? → PRIMARY: Permutation Welch
├─ Outliers? → PRIMARY: Yuen-Welch trimmed mean
└─ ALWAYS: Add SECONDARY sensitivity (Mann-Whitney U)
```

## Verification

- [ ] Design correctly identified
- [ ] Primary test selected (Welch/Permutation/Robust)
- [ ] Secondary test selected for sensitivity (if applicable)
- [ ] Test choice justified
- [ ] Both primary and secondary results will be reported

## Examples

**Input:** "Dvije nezavisne grupe, kontinuirani ishod, Shapiro-Wilk p=0.01."  
**Output:** "Primarni test: Mann-Whitney/permutation `[INFERRED]` iz nenormalnosti; Welch kao dodatna osjetljivost `[ASSUMPTION]` ako varijance nisu ekstremno asimetrične."

## Related rules

- `.cursor/rules/statistics-test-selection.mdc`
- `30_system/behavior_rules/02_statistics.md`

## Learning integration

- **task_type:** analysis
- **log_fields:** test_selected, design, justification
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)

## Skill reference graph (auto)

- [[results_reporting_snippets]]
- [[test_selection_guide]]
- [[assumptions_and_diagnostics]]
- [[effect_sizes_and_power]]
- [[reporting_standards]]
- [[REFERENCE_INDEX]]
- [[Statistics skill stack]]
