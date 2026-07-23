# Visualization Standards for Medical Data Science

## Publication-Ready ggplot2 Theme

```r
# CUSTOM THEME FOR IVAN'S PUBLICATIONS

theme_ivan <- function(base_size = 12, base_family = "Arial") {
  theme_minimal(base_size = base_size, base_family = base_family) +
    theme(
      # Text
      plot.title = element_text(size = base_size + 2, face = "bold", hjust = 0),
      plot.subtitle = element_text(size = base_size, color = "gray40", hjust = 0),
      axis.title = element_text(size = base_size, face = "bold"),
      axis.text = element_text(size = base_size - 1),
      
      # Grid
      panel.grid.minor = element_blank(),
      panel.grid.major = element_line(color = "gray90", size = 0.3),
      
      # Legend
      legend.position = "bottom",
      legend.title = element_text(face = "bold"),
      legend.text = element_text(size = base_size - 1),
      
      # Facets
      strip.text = element_text(size = base_size, face = "bold"),
      strip.background = element_rect(fill = "gray95", color = NA),
      
      # Background
      plot.background = element_rect(fill = "white", color = NA),
      panel.background = element_rect(fill = "white", color = NA)
    )
}

# SET AS DEFAULT
theme_set(theme_ivan())
```

## Example Usage

```r
# BOXPLOT WITH JITTERED POINTS
ggplot(data_clean, aes(x = treatment_group, y = qor_day1, fill = treatment_group)) +
  geom_boxplot(alpha = 0.7) +
  geom_jitter(width = 0.2, alpha = 0.3) +
  scale_fill_manual(values = c("TIVA" = "#1f77b4", "Sevoflurane" = "#ff7f0e")) +
  labs(
    title = "QoR-40 Scores at 24 Hours Post-Surgery",
    subtitle = "PSIOS Trial (N = 200)",
    x = "Treatment Group",
    y = "QoR-40 Score",
    fill = "Group"
  ) +
  theme_ivan()
```

## Color Palettes

```r
# STANDARD COLOR PALETTES FOR CLINICAL RESEARCH

# Two-group comparison
colors_2group <- c("Control" = "#1f77b4", "Treatment" = "#ff7f0e")
colors_2group_alt <- c("TIVA" = "#2ca02c", "Sevoflurane" = "#d62728")

# Three-group comparison
colors_3group <- c("#1f77b4", "#ff7f0e", "#2ca02c")

# Sequential (for continuous outcomes)
colors_sequential <- c("#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", 
                       "#4292c6", "#2171b5", "#084594")

# Diverging (for change scores)
colors_diverging <- c("#d73027", "#f46d43", "#fdae61", "#fee090", 
                      "#e0f3f8", "#abd9e9", "#74add1", "#4575b4")
```

## Figure Types for Clinical Research

### 1. Forest Plot

```r
# Forest plot for meta-analysis or subgroup analysis
library(forestplot)

forest_data <- data.frame(
  Subgroup = c("Overall", "Male", "Female", "Age < 65", "Age >= 65"),
  OR = c(0.75, 0.72, 0.78, 0.70, 0.82),
  LowerCI = c(0.60, 0.52, 0.58, 0.48, 0.62),
  UpperCI = c(0.94, 0.99, 1.05, 1.02, 1.08)
)

ggplot(forest_data, aes(x = OR, y = Subgroup)) +
  geom_point(size = 3) +
  geom_errorbarh(aes(xmin = LowerCI, xmax = UpperCI), height = 0.2) +
  geom_vline(xintercept = 1, linetype = "dashed", color = "gray50") +
  scale_x_log10() +
  labs(
    title = "Subgroup Analysis: Treatment Effect",
    x = "Odds Ratio (95% CI)",
    y = ""
  ) +
  theme_ivan()
```

### 2. Kaplan-Meier Curves

```r
# Survival curves with risk table
library(survminer)

ggsurvplot(
  fit_km,
  data = data,
  pval = TRUE,
  conf.int = TRUE,
  risk.table = TRUE,
  risk.table.height = 0.25,
  palette = c("#1f77b4", "#ff7f0e"),
  legend.title = "Treatment",
  xlab = "Time (days)",
  ylab = "Survival probability",
  break.time.by = 30,
  ggtheme = theme_ivan()
)
```

### 3. Correlation Matrix

```r
# Correlation heatmap
library(corrplot)

cor_matrix <- cor(data_clean %>% select(age, bmi, qor_baseline, qor_day1), 
                  use = "complete.obs")

corrplot(cor_matrix, 
         method = "color",
         type = "upper",
         addCoef.col = "black",
         tl.col = "black",
         tl.srt = 45,
         diag = FALSE)
```

## Export Settings

```r
# STANDARD EXPORT SETTINGS FOR PUBLICATIONS

# PNG (for presentations)
ggsave("outputs/figures/figure1.png", 
       width = 10, height = 6, dpi = 300, bg = "white")

# PDF (for publications)
ggsave("outputs/figures/figure1.pdf", 
       width = 10, height = 6, device = cairo_pdf)

# TIFF (for journals requiring TIFF)
ggsave("outputs/figures/figure1.tiff", 
       width = 10, height = 6, dpi = 300, compression = "lzw")

# SVG (for web/editable)
ggsave("outputs/figures/figure1.svg", 
       width = 10, height = 6)
```

## Composite Figures with patchwork

```r
library(patchwork)

# Create individual plots
p1 <- ggplot(data, aes(x = age)) + 
  geom_histogram(bins = 30, fill = "#1f77b4") +
  labs(title = "A) Age Distribution")

p2 <- ggplot(data, aes(x = treatment_group, y = qor_day1)) + 
  geom_boxplot(fill = "#ff7f0e") +
  labs(title = "B) QoR-40 by Treatment")

p3 <- ggplot(data, aes(x = qor_baseline, y = qor_day1)) + 
  geom_point(alpha = 0.5) +
  geom_smooth(method = "lm") +
  labs(title = "C) Baseline vs Day 1")

# Combine
combined_plot <- (p1 | p2) / p3

ggsave("outputs/figures/figure_combined.png", 
       combined_plot, width = 12, height = 10, dpi = 300)
```

## Related Hubs

- [Folder index hub](../../../docs/FOLDER_INDEX.md)
- [All notes index](../../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../../docs/GRAPH_CONNECTIVITY_MAP.md)
