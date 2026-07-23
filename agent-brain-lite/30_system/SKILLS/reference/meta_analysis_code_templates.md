# Meta-Analysis – Code Templates & Reference Data

**Used by:** `SKILL_meta-analysis.md`
**Source:** Extracted from skill to enable progressive loading. Load only when executing the corresponding step.

---

## Primary Meta-Analysis (Random Effects)

```r
library(meta)

ma <- metacont(
    n.e, mean.e, sd.e,
    n.c, mean.c, sd.c,
    data = data,
    method.tau = "REML"
)

# Common effects (sensitivity)
ma_common <- update(ma, comb.fixed = TRUE, comb.random = FALSE)
```

## Binary Outcome

```r
ma_bin <- metabin(
    event.e, n.e,
    event.c, n.c,
    data = data,
    sm = "OR",       # OR, RR, or RD
    method.tau = "REML"
)
```

## Heterogeneity Interpretation

| I-squared | Interpretation |
|---|---|
| 0-40% | Might not be important |
| 30-60% | Moderate heterogeneity |
| 50-90% | Substantial heterogeneity |
| 75-100% | Considerable heterogeneity |

Overlap in ranges is intentional (Cochrane Handbook). Always consider magnitude and direction of effects alongside I-squared.

## Prediction Interval

When I-squared > 50%, always compute and report prediction interval:

```r
ma_pred <- update(ma, prediction = TRUE)
print(ma_pred)
```

## Subgroup Analysis

```r
# Only if k >= 10 and pre-specified in protocol
ma_sub <- update(ma, subgroup = subgroup_var, tau.common = FALSE)
```

## Forest Plot (Quick)

```r
forest(ma,
       comb.fixed = TRUE,
       comb.random = TRUE,
       prediction = TRUE,
       print.tau2 = TRUE,
       print.I2 = TRUE)
```

## Publication Bias (Quick)

```r
# Funnel plot
funnel(ma, contour = c(0.9, 0.95, 0.99))

# Egger's test (continuous outcomes)
metabias(ma, method = "egger")

# Peters' test (binary outcomes)
metabias(ma, method = "peters")

# Trim-and-fill
tf <- trimfill(ma)
forest(tf)
```

## Reporting Checklist

- Pooled estimate with 95% CI
- Heterogeneity: I-squared, tau-squared, Q-statistic with p-value
- Prediction interval (if I-squared > 50%)
- Number of studies (k) and total participants (N)
- Model specification: random-effects, tau estimator (REML)
- Software and package versions

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)

## Parent skills (auto)

- [[SKILL_meta-analysis]]

## Related playbooks (auto)

- [[ai_detection_patterns]]
- [[ai_phrase_replacements]]
- [[bayesian_code_templates]]
- [[consort_checklist_items]]
- [[literature_synthesis_templates]]
- [[OBSIDIAN_AGENT_PLAYBOOK]]
- [[r_statistics_coding]]
- [[r_statistics_packages]]
