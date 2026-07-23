---
name: publication-bias
description: Use specifically for publication bias assessment (funnel, Egger, trim-and-fill); requires completed meta-analysis with k >= 10 Triggers include: publication bias, funnel plot, small-study effects, Egger test.
version: 1.1
last_updated: 2026-03-30
domain: statistics
tokens: ~1500
triggers:
  - publication bias
  - funnel plot
  - small-study effects
  - Egger test
requires_packages: [meta]
reference_files: []
pipeline_position: [3, 5]
---

# Skill: Assess Publication Bias

## When to use

Use this skill when:
- Meta-analysis includes ≥10 studies
- Need to assess potential publication bias
- Preparing manuscript with publication bias assessment

## Prerequisites

- Meta-analysis with k ≥ 10 studies
- Effect estimates and standard errors available

## Step-by-step procedure

1. **Visual assessment - Funnel plot:**
   ```r
   library(meta)
   # Create funnel plot with contour lines
   funnel(ma, 
          contour = c(0.9, 0.95, 0.99),
          studlab = TRUE)
   ```

2. **Statistical tests:**
   ```r
   # For binary outcomes: Peters' test
   if(outcome_type == "binary") {
     peters_test <- metabias(ma, method = "peters")
     print(peters_test)
   }
   
   # For continuous outcomes: Egger's test
   egger_test <- metabias(ma, method = "egger")
   print(egger_test)
   ```

3. **Trim-and-fill analysis:**
   ```r
   # Estimate missing studies
   tf <- trimfill(ma)
   print(tf)
   
   # Visualize
   funnel(tf)
   forest(tf)
   ```

4. **Interpret results:**
   - **Funnel plot asymmetry:** Visual inspection
   - **Statistical tests:** p < 0.10 suggests potential bias
   - **Trim-and-fill:** Number of missing studies estimated
   - **Consider other causes:** Heterogeneity, quality, true effect

5. **Report findings:**
   - Describe funnel plot (symmetric/asymmetric)
   - Report statistical test results (p-values)
   - Report trim-and-fill results (if performed)
   - Discuss potential causes of asymmetry
   - Acknowledge limitations of methods

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "k=14 studija; ima li asimetrije u funnel plotu za primarni ishod?"  
**Output:** "Egger/Peters rezultati `[VERIFIED]` iz izračuna; klinička interpretacija `[INFERRED]`; za k<10 ne forsirati test `[EXTRACTED]` iz skill granica."

## Verification

- [ ] Funnel plot created (if k ≥ 10)
- [ ] Statistical test performed (Egger's or Peters')
- [ ] Trim-and-fill analysis performed (if asymmetry detected)
- [ ] Results interpreted in context
- [ ] Other causes of asymmetry considered
- [ ] Findings reported in manuscript

## Important Notes

- **k < 10:** Funnel plot and tests have low power, interpret cautiously
- **Asymmetry ≠ Publication bias:** Consider heterogeneity, quality, true effect
- **Multiple methods:** Use visual + statistical + trim-and-fill for comprehensive assessment

## Learning integration

- **task_type:** analysis
- **log_fields:** methods_used, k_studies, tests_performed
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related rules

- `.cursor/rules/statistics.mdc` (when migrated)
- `30_system/behavior_rules/02_statistics.md` (Publication Bias Assessment)

## Learning integration

This skill logs:
- Common patterns in publication bias assessment
- Which methods are most informative
- User preferences for reporting

Improves by:
- Learning interpretation patterns
- Adapting to different outcome types
- Suggesting appropriate methods

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
