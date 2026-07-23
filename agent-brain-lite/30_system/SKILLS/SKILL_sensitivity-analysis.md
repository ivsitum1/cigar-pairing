---
name: sensitivity-analysis
description: Use for meta-analysis sensitivity analyses (leave-one-out, influence, method comparison); NOT for general statistical sensitivity analysis outside meta-analysis Triggers include: sensitivity analysis, robustness checks, leave-one-out, influence analysis.
version: 1.1
last_updated: 2026-03-30
domain: statistics
tokens: ~1750
triggers:
  - sensitivity analysis
  - robustness checks
  - leave-one-out
  - influence analysis
requires_packages: [meta, metafor]
reference_files: []
pipeline_position: [3]
---

# Skill: Conduct Sensitivity Analyses

## When to use

Use this skill when:
- Need to assess robustness of meta-analysis results
- Checking influence of individual studies
- Evaluating impact of methodological choices

## Prerequisites

- Primary meta-analysis completed
- Data available for all studies

## Step-by-step procedure

1. **Leave-one-out analysis:**
   ```r
   library(meta)
   # Remove each study one at a time
   leave_one_out <- metainf(ma, pooled = "random")
   print(leave_one_out)
   
   # Visualize
   forest(leave_one_out)
   ```

2. **Influence analysis:**
   ```r
   library(metafor)
   # Calculate influence measures
   inf <- influence(ma)
   
   # Identify outliers (|residual| > 3)
   outliers <- which(abs(inf$resid) > 3)
   
   # Create influence plot
   plot(inf)
   ```

3. **Method comparison:**
   ```r
   # Compare different tau² estimators
   ma_REML <- update(ma, method.tau = "REML")
   ma_DL <- update(ma, method.tau = "DL")
   ma_HS <- update(ma, method.tau = "HS")
   
   # Compare results
   summary(ma_REML)
   summary(ma_DL)
   summary(ma_HS)
   ```

4. **Outlier removal (if identified):**
   ```r
   # Primary analysis (all studies)
   ma_all <- ma
   
   # Sensitivity analysis (without outliers)
   ma_no_outliers <- update(ma, subset = !(1:ma$k %in% outliers))
   
   # Compare results
   summary(ma_all)
   summary(ma_no_outliers)
   ```

5. **Risk of bias restriction:**
   ```r
   # If risk of bias data available
   # Restrict to low risk of bias studies
   ma_low_rob <- update(ma, subset = rob == "low")
   ```

6. **Subgroup sensitivity:**
   ```r
   # If subgroup analysis performed
   # Test robustness of subgroup findings
   # (Repeat subgroup analysis with different methods)
   ```

7. **Report all sensitivity analyses:**
   - Create table comparing primary vs sensitivity results
   - Document any substantial differences
   - Discuss implications for robustness

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Leave-one-out za primarni pooled effect u meta-analizi."  
**Output:** "LOO rezultati `[VERIFIED]` iz ponovnog fita; utjecaj studije `[INFERRED]`; bez pokrenutog modela `[BLANK]`."

## Verification

- [ ] Leave-one-out analysis performed
- [ ] Influence analysis performed
- [ ] Method comparison done (if applicable)
- [ ] Outlier removal tested (if outliers found)
- [ ] Risk of bias restriction tested (if data available)
- [ ] All sensitivity results documented
- [ ] Differences discussed in manuscript

## Learning integration

- **task_type:** analysis
- **log_fields:** methods_used, robustness_findings
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related rules

- `.cursor/rules/statistics.mdc` (when migrated)
- `30_system/behavior_rules/02_statistics.md` (Sensitivity Analysis Requirements)

## Learning integration

This skill logs:
- Which sensitivity analyses are most useful
- Common patterns in sensitivity results
- User preferences for reporting

Improves by:
- Learning which analyses detect problems
- Adapting to different study types
- Suggesting relevant analyses based on data

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
