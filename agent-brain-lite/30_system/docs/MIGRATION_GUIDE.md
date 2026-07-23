# Migration Guide: 30_system/behavior_rules/ → .cursor/rules/

**Version:** 1.0  
**Date:** 2026-01-27

---

## Overview

This guide explains the migration from the `30_system/behavior_rules/` folder structure to Cursor's native `.cursor/rules/` directory with `.mdc` files, and the addition of Skills for procedural instructions.

---

## What Changed?

### New Structure

1. **`.cursor/rules/`** - Cursor-native rules (`.mdc` files)
   - Automatically activated based on file patterns
   - More efficient context management
   - Better integration with Cursor IDE

2. **`30_system/SKILLS/`** - Procedural "how-to" instructions
   - Invoked with `@skill-name`
   - Dynamic context discovery
   - Better for step-by-step workflows

3. **`30_system/behavior_rules/`** - Retained for backward compatibility
   - Original rules remain available
   - Detailed reference documentation
   - Gradual migration path

---

## Rules vs Skills

### Rules (`.mdc` files in `.cursor/rules/`)

**Use for:**
- Declarative guidelines
- Always-on principles
- Domain-specific standards
- Reporting checklists

**Examples:**
- `core-principles.mdc` - Always active
- `statistics-test-selection.mdc` - Activates for `.R` files
- `reporting-prisma.mdc` - Activates for systematic reviews

### Skills (`SKILL_*.md` files in `30_system/SKILLS/`)

**Use for:**
- Procedural "how-to" instructions
- Step-by-step workflows
- Dynamic context discovery
- Task-specific guidance

**Examples:**
- `SKILL_setup-project.md` - Invoke with `@setup-project`
- `SKILL_meta-analysis.md` - Invoke with `@meta-analysis`

---

## Migration Status

### ✅ Completed

**Core Rules:**
- `core-principles.mdc` ← `00_core_principles.md`
- `context-optimization.mdc` (source `17_context_optimization.md` removed; use .mdc)

**New Critical Rules:**
- `statistics-test-selection.mdc` - Modern test selection framework
- `writing-avoid-ai.mdc` - AI formulation avoidance

**Reporting Guidelines:**
- `reporting-strobe.mdc` - STROBE Statement
- `reporting-consort.mdc` - CONSORT 2010
- `reporting-prisma.mdc` - PRISMA 2020
- `reporting-tripod-ai.mdc` - TRIPOD+AI
- `reporting-stard.mdc` - STARD 2015
- `reporting-care.mdc` - CARE Statement

**Skills:**
- `SKILL_setup-project.md`
- `SKILL_meta-analysis.md`

### 🔄 In Progress

- Migration of remaining domain rules
- Additional Skills creation
- Learning loop integration

### 📋 Planned

- Remaining reporting guidelines (SPIRIT, SQUIRE, CHEERS)
- Additional statistical rules (Network Meta-Analysis, IPD, etc.)
- More Skills for common workflows

---

## How to Use

### For New Projects

1. **Rules activate automatically** based on file patterns
2. **Invoke Skills** when needed: `@setup-project`, `@meta-analysis`, etc.
3. **Reference 30_system/behavior_rules/** for detailed documentation

### For Existing Projects

1. **No changes required** - backward compatible
2. **Gradually adopt** new `.cursor/rules/` structure
3. **Use Skills** for new workflows

---

## File Pattern Mapping

| Pattern | Activates Rules |
|---------|----------------|
| `**/*.R`, `**/*.Rmd` | Statistics rules |
| `**/manuscript/**` | Writing rules |
| `**/rct*.md` | CONSORT rules |
| `**/systematic*.md` | PRISMA rules |
| `**/cohort*.md` | STROBE rules |
| `**/*model*.md` | TRIPOD+AI rules |

---

## Learning Loop Integration

All tools now include learning loop with positive reinforcement:

- **Setup tools** - Learn from successful setups
- **Statistical tools** - Learn from test selections
- **Writing tools** - Learn from AI detection scores
- **Skills** - Learn from usage patterns

See `30_system/behavior_rules/14_learning_loop.md` for details.

---

## Key Improvements

1. **Modern Test Selection:**
   - Welch/Permutation as PRIMARY
   - Non-parametric as SECONDARY (sensitivity only)
   - Clear hierarchy and rationale

2. **Comprehensive Reporting Guidelines:**
   - All major guidelines (STROBE, CONSORT, PRISMA, TRIPOD+AI, etc.)
   - Auto-detection based on study type
   - Complete checklists

3. **AI Writing Avoidance:**
   - Specific formulations to avoid
   - Natural writing strategies
   - Integration with AI checkers

4. **Learning Integration:**
   - All tools learn and improve
   - Positive reinforcement mechanism
   - Automatic adaptation

---

## Backward Compatibility

- `30_system/behavior_rules/` folder retained
- All original rules still available
- Gradual migration path
- No breaking changes

---

## Questions?

- See `.cursor/rules/README.md` for rules overview
- See `30_system/behavior_rules/README.md` for original structure
- **Migration status & validation:** [WORKFLOW_CURSOR_MIGRATION.md](WORKFLOW_CURSOR_MIGRATION.md) (includes hygiene checklist)
- Check individual rule files for specific guidance

---

**Last Updated:** 2026-06-28

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[README]]
- [[SKILL_setup-project]]
- [[SKILL_prisma-checklist]]
- [[SKILL_ai-detection]]
- [[00_core_principles]]
