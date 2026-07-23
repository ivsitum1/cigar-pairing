> **⚠️ MIGRATED** -> `.cursor/rules/visualization.mdc` (2026-05-08)

# Visualization Standards

## Purpose

This document establishes standards for creating publication-quality figures for meta-analysis results. All figures should be clear, informative and meet journal requirements.

---

## Forest Plots

### Required Elements

- [ ] Individual study estimates (squares/boxes)
- [ ] Confidence intervals (horizontal lines)
- [ ] Pooled estimate (diamond)
- [ ] Study labels (author, year)
- [ ] Sample sizes for each group
- [ ] Effect estimates with 95% CI
- [ ] Weights (as percentages)
- [ ] Reference line (null effect)
- [ ] "Favors" labels
- [ ] Heterogeneity statistics
- [ ] Test for overall effect

### Color Scheme

**Standard Colors:**
- Individual studies: `#1B998B` (Teal) or `#2E86AB` (Blue)
- Pooled estimate: `#A23B72` (Purple/Magenta)
- Reference line: Black
- Text: Black

**Color-blind friendly:** Test with color-blind simulators, ensure grayscale printing works.

**Implementation:**
```r
forest(ma,
       col.square = "#1B998B",
       col.square.lines = "#1B998B",
       col.diamond = "#A23B72",
       col.diamond.lines = "#A23B72")
```

## Colorblind Accessibility (Mandatory)

All figures must pass colorblind simulation before submission.

Check in R:

```r
library(colorblindr)
colorblindr::cvd_grid(your_plot)
```

The recommended palette (#1B998B teal, #A23B72 purple, #FF6B35 orange) is safe for
deuteranopia and protanopia. Always add shapes (circle/triangle/square) as a second
encoding channel alongside colors — never rely on color alone to distinguish groups.

## Font Specifications

- **Standard manuscripts**: Arial or Helvetica (sans-serif)
- **Journals requiring serif fonts**: Times New Roman (check author guidelines)
- **Never use**: decorative fonts, Comic Sans, or script fonts
- **Minimum sizes**: 8pt axis labels · 10pt legend text · 12pt figure title
- Verify all text is ≥8pt after figure resizing to journal dimensions

### Font Sizes

- Base font: 11-12pt
- Study names: 10-12pt
- Numbers: 11-12pt
- Title: 12-14pt

### Layout Dimensions

- Width: 14-16 inches (or equivalent in cm)
- Height: ~0.5-1 inch per study (minimum 8 inches)
- Spacing: 1.2-1.5x default

**Implementation:**
```r
pdf("forest_plot.pdf", width = 14, height = 8, pointsize = 12)
forest(ma, spacing = 1.3, plotwidth = "8cm")
dev.off()
```

### Labels

**Left columns:**
- Study name
- Group 1: N, Mean, SD (continuous) or Events, Total (binary)
- Group 2: N, Mean, SD (continuous) or Events, Total (binary)

**Right columns:**
- Weight (%)
- Effect estimate
- 95% CI

**Implementation:**
```r
forest(ma,
       label.e = "TIVA Propofol",
       label.c = "Sevoflurane",
       leftlabs = c("Study", "N", "Mean", "SD", "N", "Mean", "SD"),
       rightlabs = c("Weight", "MD", "95% CI"),
       label.left = "Favors TIVA",
       label.right = "Favors Sevoflurane")
```

---

## Funnel Plots

### Required Elements

- [ ] Effect size on x-axis
- [ ] Standard error (or sample size) on y-axis
- [ ] Individual study points
- [ ] Contour lines for significance levels (0.90, 0.95, 0.99)
- [ ] Trim-and-fill results (if applicable)

### Standard Format

**Implementation:**
```r
funnel(ma,
       xlab = "Effect Size (MD or log RR)",
       ylab = "Standard Error",
       contour = c(0.9, 0.95, 0.99),
       col.contour = c("gray50", "gray75", "gray90"),
       studlab = TRUE)
```

### Trim-and-Fill Visualization

```r
tf <- trimfill(ma)
funnel(tf,
       legend = TRUE,
       xlab = "Effect Size",
       ylab = "Standard Error")
```

---

## Bubble Plots (Meta-Regression)

### Required Elements

- [ ] Covariate on x-axis
- [ ] Effect size on y-axis
- [ ] Bubble size proportional to weight
- [ ] Regression line
- [ ] Study labels (optional)

**Implementation:**
```r
bubble(ma_reg,
       xlab = "Year of Publication",
       ylab = "Effect Size",
       cex.bubble = 1.5,
       studlab = TRUE)
```

---

## Sensitivity Analysis Plots

### Leave-One-Out Forest Plot

- Show pooled estimate with each study removed
- Highlight original estimate
- Clear labeling

**Implementation:**
```r
loo <- metainf(ma, pooled = "random")
forest(loo,
       xlab = "Effect Size",
       col.diamond = "red")
```

### Influence Plot

- Standardized residuals vs. fitted values
- Identify outliers (|residual| > 2 or 3)
- Clearly marked thresholds

**Implementation:**
```r
inf <- influence(ma)
plot(inf,
     xlab = "Fitted Values",
     ylab = "Standardized Residuals")
abline(h = c(-2, 2), lty = 2, col = "red")
abline(h = c(-3, 3), lty = 2, col = "orange")
```

---

## Cumulative Meta-Analysis

### Format

- Studies ordered by year or sample size
- Cumulative effect estimate shown
- Confidence intervals updated with each study

---

## File Formats and Export

### Export Formats

**Primary:**
- PDF (vector, scalable, preferred)

**Alternative (if journal requires):**
- PNG (300+ DPI)
- TIFF (300+ DPI)
- EPS (for some journals)

**Implementation:**
```r
# PDF (preferred)
pdf("figure.pdf", width = 14, height = 8, pointsize = 12)
# ... plot code ...
dev.off()

# High resolution PNG
png("figure.png", width = 14*300, height = 8*300, res = 300, pointsize = 12)
# ... plot code ...
dev.off()
```

### Resolution Requirements

- Minimum: 300 DPI
- Preferred: 600 DPI for journals
- Vector formats (PDF, EPS) are resolution-independent

---

## Figure Captions

### Required Information

1. **Figure title**: Descriptive title
2. **What is shown**: Plot type and what it shows
3. **Study information**: Number of studies and participants
4. **Statistical details**: Effect estimates, heterogeneity, tests
5. **Interpretation**: Key findings

### Template

**Forest Plot:**
"Forest plot shows [outcome] comparing [treatment] vs. [control]. Each square represents effect estimate from individual study (n = [X] studies, [Y] participants), with size proportional to study weight. Horizontal lines indicate 95% confidence intervals. Diamond represents pooled estimate (random effects model) with its 95% confidence interval. Heterogeneity: I² = [X]%, τ² = [Y], Q = [Z] (p = [p]). Test for overall effect: z = [z], p = [p]."

**Funnel Plot:**
"Funnel plot assesses potential publication bias for [outcome]. Each point represents a study. Contour lines indicate regions of statistical significance (p = 0.90, 0.95, 0.99). Symmetry suggests absence of publication bias. Egger's test: p = [p]."

**Bubble Plot:**
"Bubble plot shows association between [covariate] and effect size. Bubble size is proportional to study weight. Regression line indicates estimated association (β = [coefficient], 95% CI: [CI], p = [p]). R² = [value], indicating that [X]% of heterogeneity is explained by this covariate."

---

## Quality Checklist

Before finalizing any figure:

- [ ] All required elements present
- [ ] Colors are color-blind friendly
- [ ] Text is readable (adequate font size)
- [ ] No overlapping labels
- [ ] Appropriate file format and resolution
- [ ] Figure caption complete
- [ ] Consistent with other figures in manuscript
- [ ] Meets journal requirements

---

## Consistency Standards

### Across All Figures

- **Color scheme**: Consistent use of colors for treatment groups
- **Font**: Same font family and sizes
- **Labels**: Consistent terminology
- **Format**: Same file format and resolution
- **Style**: Consistent aesthetics

### Naming Conventions

**File names:**
- `forest_[outcome].pdf`
- `funnel_[outcome].pdf`
- `metareg_[covariate]_[outcome].pdf`
- `sensitivity_[type]_[outcome].pdf`

---

## References

See `methodology_repository/06_forest_plot_standards.md` for detailed guidelines and examples.

---

## Additional Notes

### For General Figures (Not Meta-Analysis)

**Format:**
- JPG (publication-ready, ≥300 DPI) or PDF (preferred)
- Descriptive filenames that reflect content

**Example names:**
- `boxplot_age_by_group.jpg`
- `kaplan_meier_survival.jpg`
- `forest_primary_outcome.jpg`

**Complete labeling:**
- Axes, legends, annotations
- Clear titles and labels
- Adequate font size for readability

---

**Version:** 1.1  
**Last updated:** 2026-04-10

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
