
## Overview
This document provides detailed reference material for ML/MLOps practices. 
For Cursor-activated rules, see `.cursor/rules/50_ml_mlops_standards.mdc`.

**Scope:** Deployment, monitoring, feature stores, and MLOps maturity. For model validation methodology,
interpretability, leakage prevention, and when classical statistics beats ML, see **`30_system/behavior_rules/12_machine_learning.md`**.

## 1. MLOps Maturity Levels (Google Framework)

### Level 0: Manual Process
- Manual experimentation
- Manual model training
- No pipeline automation
- **Typical in**: Early research, prototyping

### Level 1: ML Pipeline Automation
- Automated training pipeline
- Continuous training (CT)
- Model registry
- **Typical in**: Mature ML teams

### Level 2: CI/CD Pipeline Automation
- Automated testing
- Continuous integration
- Continuous deployment
- A/B testing infrastructure
- **Typical in**: Production ML systems

## 2. Feature Store Architecture

### Components
```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                 Feature Store                    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚  Offline Store  â”‚      Online Store             â”‚
â”‚  (Training)     â”‚      (Serving)                â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚ - Historical    â”‚ - Low latency (<10ms)         â”‚
â”‚ - Batch compute â”‚ - Real-time features          â”‚
â”‚ - Point-in-time â”‚ - Caching layer               â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Key Principles
1. **Training-serving consistency**: Same feature computation
2. **Point-in-time correctness**: No future leakage
3. **Feature versioning**: Track transformations
4. **Documentation**: Feature descriptions, owners

### Tools Comparison
| Feature Store | Open Source | Managed | Best For |
|---------------|-------------|---------|----------|
| Feast | Yes | No | Kubernetes environments |
| Tecton | No | Yes | Enterprise, real-time |
| Databricks | No | Yes | Spark-native workflows |
| SageMaker | No | Yes | AWS ecosystems |

## 3. FDA Good Machine Learning Practice (GMLP)

### 10 Guiding Principles (2021)

1. **Multi-disciplinary expertise** throughout product lifecycle
2. **Good software engineering** and security practices

---

**Version:** 1.0  
**Last updated:** 2026-04-10

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
