---
name: forest-plot
description: Use for creating a single forest plot; for full figure workflow use figure-pipeline instead Triggers include: forest plot, meta-analysis figure, study results visualization.
version: 1.1
last_updated: 2026-03-30
domain: statistics
tokens: ~1600
triggers:
  - forest plot
  - meta-analysis figure
  - study results visualization
requires_packages: [meta]
reference_files: []
pipeline_position: [3, 5]
---

# Skill: Create Forest Plot

## When to use

Use this skill when:
- Need to create forest plot for meta-analysis
- Visualizing study results and pooled estimate
- Preparing publication-ready figure

## Prerequisites

- Meta-analysis object (from `meta` or `metafor` package)
- Effect estimates and confidence intervals for each study
- Pooled estimate calculated

## Step-by-step procedure

1. **Prepare data:**
   - Ensure all studies have effect estimates and CIs
   - Check for missing data
   - Verify study labels are clear

2. **Create basic forest plot:**
   ```r
   library(meta)
   # Using meta package
   forest(ma, 
          xlim = c(-2, 2),  # Adjust based on effect size range
          xlab = "Effect Size (95% CI)",
          studlab = TRUE,
          comb.fixed = FALSE,  # Show random effects
          comb.random = TRUE)
   ```

3. **Add both random and common effects:**
   ```r
   forest(ma,
          comb.fixed = TRUE,   # Common effects
          comb.random = TRUE,  # Random effects
          print.tau2 = TRUE,
          print.I2 = TRUE,
          print.Q = TRUE)
   ```

4. **Add prediction interval (if I² > 50%):**
   ```r
   forest(ma,
          prediction = TRUE,  # Add prediction interval
          print.pred = TRUE)
   ```

5. **Customize appearance:**
   - Adjust x-axis limits based on data range
   - Set appropriate labels
   - Choose colors for different groups (if subgroup analysis)
   - Set font sizes for readability

6. **Export high resolution:**
   ```r
   # Save as high-resolution JPG
   jpeg("forest_plot.jpg", 
        width = 3000, 
        height = 4000, 
        res = 300, 
        units = "px")
   forest(ma)
   dev.off()
   ```

7. **Add figure caption:**
   - Include: effect measure, model used, heterogeneity statistics
   - Example: "Forest plot showing [outcome] for [intervention] vs [control]. Random effects model. I² = X%, τ² = X."

## Honesty and grounding checkpoints

- Tag outputs as `[EXTRACTED]`, `[VERIFIED]`, `[INFERRED]`, `[ASSUMPTION]`, or `[BLANK]`.
- Use `[VERIFIED]` only with evidence from code execution, user data, or authoritative documentation.
- If required inputs are missing, use `[BLANK]` and list what to supply next.
- Do not fabricate statistics, citations, guideline quotes, or tool outputs.

## Examples

**Input:** "Jedan forest plot iz meta-analize za primarni ishod."  
**Output:** "Pooled estimate i CI `[VERIFIED]` iz model outputa; oznake studija `[EXTRACTED]` iz dataseta; stil ako nije specificiran `[ASSUMPTION]`."

## Verification

- [ ] All studies included
- [ ] Effect estimates and CIs visible
- [ ] Pooled estimate shown (random and/or common effects)
- [ ] Prediction interval added (if applicable)
- [ ] Study labels clear and readable
- [ ] High resolution (≥300 DPI)
- [ ] Figure caption complete

## Learning integration

- **task_type:** analysis
- **log_fields:** plot_type, packages_used
- **post_step:** After completing procedure: output LEARNING_BLOCK (see `30_system/behavior_rules/14_learning_loop.md`) for ingestion.

## Related rules

- `.cursor/rules/visualization.mdc` (when migrated)
- `30_system/behavior_rules/04_visualization.md`
- `30_system/behavior_rules/02_statistics.md`

## Learning integration

This skill logs:
- Forest plot creation success
- Common customization requests
- Export format preferences
- User feedback on appearance

Improves by:
- Learning preferred styles
- Adapting to different effect sizes
- Suggesting improvements based on patterns

## Related Hubs

- [Skill registry](registry.json)
- [Skills index](../30_system/docs/indexes/SKILLS_INDEX.md)
- [Task optimization check](../30_system/docs/TASK_OPTIMIZATION_CHECK.md)
- [Workspace graph map](../30_system/docs/GRAPH_CONNECTIVITY_MAP.md)
- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
