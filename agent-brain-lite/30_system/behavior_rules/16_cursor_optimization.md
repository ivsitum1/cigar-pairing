# Cursor-Specific Optimizations

## Purpose

Optimize AI agent behavior specifically for Cursor IDE to maximize speed, accuracy, and efficiency. This document provides Cursor-specific best practices that all agents should follow.

---

## Cursor-Specific Features to Leverage

### 1. Composer Mode Optimization

**Batch Operations:**
- Group related edits together in a single Composer session
- Make all related changes across multiple files in one pass
- Use Composer's context awareness to reference open files and recent edits

**Best Practices:**
```
✅ GOOD: "Update all three analysis scripts to use the new data structure"
❌ BAD: "Update script1, then script2, then script3" (three separate requests)
```

### 2. Chat Mode Efficiency

**Precise Queries:**
- Use specific file paths and line numbers when referencing code
- Quote code blocks using code references (```startLine:endLine:filepath```)
- Build incrementally on previous responses rather than starting over

**Best Practices:**
```
✅ GOOD: "In ```45:50:40_operations/scripts/analysis.R```, change the t-test to Mann-Whitney U"
❌ BAD: "Change the test in the analysis script" (too vague)
```

### 3. Codebase Indexing

**Leverage Cursor's Index:**
- Reference indexed functions/classes using @-mentions
- Follow existing project patterns discovered by Cursor's index
- Use @-mentions for file references instead of full paths

**Best Practices:**
```
✅ GOOD: "Use the same pattern as @calculate_sample_size function"
❌ BAD: "Write a function similar to what's in utils.R" (requires manual lookup)
```

### 4. Token Efficiency

**Progressive Disclosure:**
- Start with high-level overview, add details only if needed
- Reference existing rules instead of repeating content
- Use concise responses that get to the point quickly

**Best Practices:**
```
✅ GOOD: "See ```12:25:30_system/behavior_rules/02_statistics.md``` for meta-analysis rules"
❌ BAD: [Repeats entire section from statistics.md]
```

---

## Response Speed Optimizations

### Quick Wins

1. **Use Code References**
   - Format: ```startLine:endLine:filepath```
   - Shows code in context without full file content
   - Faster for both agent and user

2. **Reference Existing Rules**
   - Instead of repeating content, reference rule files
   - Example: "Following ```45:60:30_system/behavior_rules/01_general_rules.md```"

3. **Batch File Operations**
   - Use Composer mode for multi-file changes
   - Group related edits together
   - Reduces total interaction time

4. **Use @-Mentions**
   - Reference files/functions using @filename or @functionname
   - Leverages Cursor's indexing for faster lookup

### Context Management

1. **Prioritize Open Files**
   - Focus on files currently open in editor
   - Reference recent edits explicitly
   - Use incremental builds (don't rewrite everything)

2. **Leverage Cursor's Memory**
   - Reference recent conversations
   - Build on previous context
   - Don't repeat information already provided

3. **Smart Context Selection**
   - Only include relevant context
   - Use code references for large files
   - Focus on what's needed for current task

---

## Accuracy Improvements

### Code Generation

1. **Check Existing Patterns**
   - Always check for similar code in codebase before creating new code
   - Use @-mentions to find existing implementations
   - Follow project-specific conventions

2. **Verify Imports**
   - Check existing imports in project
   - Match project's package management approach
   - Use same version conventions

3. **Test Immediately**
   - Generate testable code
   - Include validation checks
   - Make it easy to verify correctness

### Error Prevention

1. **Pattern Matching**
   - Check for similar code before writing
   - Verify function signatures match existing patterns
   - Ensure consistency with project style

2. **Type Safety**
   - Use type hints when available
   - Match existing type patterns
   - Leverage IDE type checking

3. **Incremental Changes**
   - Make small, testable changes
   - Build on working code
   - Avoid large rewrites

---

## Efficiency Best Practices

### For Agents

1. **Start with Overview**
   - Provide high-level plan before details
   - Let user guide depth of explanation
   - Use progressive disclosure

2. **Ask Clarifying Questions Early**
   - If request is ambiguous, ask immediately
   - Don't guess and potentially waste time
   - One clarifying question saves multiple iterations

3. **Use Templates**
   - For repetitive tasks, use templates
   - Reference existing templates in codebase
   - Customize templates for specific needs

4. **Reference Documentation**
   - Point to documentation instead of explaining
   - Use code references for examples
   - Link to relevant rule files

### For Users (Guidance to Provide)

1. **Be Specific**
   - Provide file paths and line numbers
   - Specify exact requirements
   - Include context about what you're trying to achieve

2. **Use @-Mentions**
   - Reference files using @filename
   - Reference functions using @functionname
   - Leverage Cursor's indexing

3. **Group Related Requests**
   - Combine related tasks in one request
   - Use Composer mode for multi-file changes
   - Provide all context upfront

4. **Provide Context**
   - Explain what you're trying to achieve
   - Reference related files/code
   - Include relevant constraints

---

## Cursor-Specific Response Format

### Code References (Preferred)

```startLine:endLine:filepath
// code content here
```

**Benefits:**
- Shows code in context
- Faster than full file content
- Easier to reference specific sections

### File References

- Use @filename for file references
- Use relative paths when @-mentions not available
- Reference open files explicitly

### Multi-File Operations

- Use Composer mode for related changes
- Group edits logically
- Reference relationships between files

---

## Performance Metrics to Track

### Speed Metrics

- **Time to first response**: Should be < 5 seconds for simple tasks
- **Iterations to completion**: Minimize back-and-forth
- **Token usage**: Efficient use of context window

### Accuracy Metrics

- **First-try success rate**: Code works on first attempt
- **Error rate**: Minimize syntax/runtime errors
- **Pattern compliance**: Matches existing codebase patterns

### Efficiency Metrics

- **Context efficiency**: Only include relevant context
- **Reference usage**: Use code references vs full content
- **Batch operations**: Group related changes

---

## Cursor Rules Generator Meta-Pattern

### Auto-Generation of Project-Specific Rules

**Purpose:** Automatically generate and maintain Cursor rules for medical data science projects.

**Structure:**
```
.cursor/rules/
├── cursor-rules.mdc          # Meta-rule for structure
├── self-improvement.mdc      # Auto-improvement
├── project-structure.mdc     # Auto-generated
├── tech-stack.mdc            # R packages + versions
├── swiss-cheese-defense.mdc  # Mandatory validation
└── domain/
    ├── clinical-trials.mdc   # RCT-specific rules
    ├── bayesian-analysis.mdc # Bayesian workflow
    ├── propensity-score.mdc  # PSM rules
    └── meta-analysis.mdc     # PRISMA workflow
```

**Generation prompts:**

**Project Structure:**
```
@cursor-rules.mdc Analyze all R scripts, .Rmd files, and /data directories.
Create rule documenting:
- Project structure (data/, 40_operations/scripts/, output/, 30_system/docs/)
- Naming conventions for variables and files
- Pipeline flow (raw → clean → analysis → output)
```

**Tech Stack:**
```
@cursor-rules.mdc @renv.lock (or @DESCRIPTION)
Analyze all packages and versions.
Create rule with:
- Versions of key packages (tidyverse, brms, rstanarm, survival, meta, metafor)
- Best practices for each version
- Known breaking changes
- Recommended alternatives for deprecated functions
```

**Domain-Specific Rules:**
```
@cursor-rules.mdc @40_operations/scripts/main_analysis.R
/Generate Cursor Rules
Analyze this RCT analysis script. Extract:
- ITT vs per-protocol handling
- Missing data strategies
- Multiplicity corrections
- CONSORT compliance checks
```

### Self-Improvement Rule Pattern

**Trigger for new rule:**
- Same pattern appears in 3+ scripts
- Repeated reviewer comments on coding
- New CONSORT/STROBE/PRISMA version

**Trigger for update:**
- New R package version with breaking changes
- Edge case found in analysis
- Better implementation found in literature

**Quality requirements:**
- Every rule must have concrete R example
- References to validated literature/documentation
- Self-assessment checkpoint before finalization

## Context Overload Detection and Response

### Detection Protocol

**If context exceeds 2000 tokens:**

1. **ALERT:** "⚠️ Context overload detected"
2. **PRIORITIZE:** Rank rules by relevance for current task
3. **SUSPEND:** Temporarily suspend low-priority rules
4. **REPORT:** List which rules are suspended

### Rule Priority Hierarchy

1. **SAFETY** (patient/data) - Never suspend
2. **ACCURACY** - Never suspend
3. **PROJECT-SPECIFIC** - Suspend if not active project
4. **STYLE/FORMAT** - Suspend on overload

### Context Budget Management

**Base context:** ~500 tokens (fixed)
- `00_core_principles.md` (~200 tokens)
- `.cursor/rules/context-optimization.mdc` (replaces former 17_context_optimization.md)
- `01_general_rules.md` (essential parts only, ~150 tokens)

**Active domain:** ~300-500 tokens
- Load based on task type (statistics, writing, ML, etc.)

**Total target:** <1500 tokens base

**Overload response:**
- Identify redundancies
- Merge overlapping rules
- Archive rarely-used rules
- Report: "Restructured rules: [changes]"

## Quick Commands System

### Available Commands

**`/plan`** → Generate plan for task
- Decomposes complex tasks into steps
- Identifies risks and success criteria
- Provides actionable roadmap

**`/check`** → Run self-assessment
- Evaluates current output quality
- Checks against quality gates
- Provides improvement suggestions

**`/agent`** → Show active agent
- Displays currently active agent role
- Shows agent capabilities
- Lists related agents

**`/rules`** → Show active rules
- Lists currently loaded rules
- Shows rule priorities
- Indicates suspended rules

**`/optimize`** → Suspend unnecessary rules
- Analyzes context usage
- Identifies low-priority rules
- Suspends rules to free context

### Usage Examples

```
User: /plan
Agent: [Generates structured plan with steps, risks, success criteria]

User: /check
Agent: [Runs self-assessment, provides score and improvement suggestions]

User: /agent
Agent: [Shows active agent: Statistical Analysis Expert, lists capabilities]

User: /rules
Agent: [Lists: 00_core_principles.md (active), 02_statistics.md (active), ...]

User: /optimize
Agent: [Suspends low-priority rules, reports freed context tokens]
```

## Integration with Other Rules

### Connection Points

1. **General Rules (01_general_rules.md)**
   - Cursor optimizations enhance general communication rules
   - Code references improve code citation format
   - @-mentions improve file referencing

2. **Agent Roles (15_agent_roles.md)**
   - All agents should follow Cursor optimizations
   - Agent-specific optimizations can be added
   - Multi-agent workflows benefit from efficient communication

3. **Workflow Optimization (09_workflow_optimization.md)**
   - Cursor optimizations enhance workflow efficiency
   - Composer mode enables better workflow execution
   - Context management improves workflow accuracy

4. **Context Optimization** (`.cursor/rules/context-optimization.mdc`)
   - Hierarchical loading system
   - Context budget allocation
   - Rule priority system

---

## Examples

### Example 1: Efficient Code Review

**Before (Inefficient):**
```
User: "Review this code"
[Agent pastes entire 500-line file]
[Agent provides review]
```

**After (Optimized):**
```
User: "Review ```120:150:40_operations/scripts/analysis.R```"
Agent: "Reviewing ```120:150:40_operations/scripts/analysis.R```:
- Line 125: Missing seed setting → Add set.seed(42)
- Line 135: Assumption check missing → Add shapiro.test()
See ```45:60:30_system/behavior_rules/agents/03_code_quality_assurance.md``` for full checklist"
```

### Example 2: Multi-File Update

**Before (Inefficient):**
```
User: "Update script1.R"
[Agent updates script1.R]
User: "Now update script2.R"
[Agent updates script2.R]
```

**After (Optimized):**
```
User: "Update all analysis scripts to use new data structure"
[Agent uses Composer mode to update script1.R, script2.R, script3.R in one pass]
```

### Example 3: Pattern Matching

**Before (Inefficient):**
```
User: "Write a function to calculate propensity scores"
[Agent writes function from scratch, may not match project style]
```

**After (Optimized):**
```
User: "Write a function to calculate propensity scores"
Agent: "Checking existing patterns... Found similar function in @utils.R.
Following that pattern, here's the function:
[Function matching project style]"
```

---

## Self-Assessment Checklist

Before responding:
- [ ] Used code references (```startLine:endLine:filepath```) instead of full code blocks?
- [ ] Referenced existing rules instead of repeating content?
- [ ] Used @-mentions for file/function references?
- [ ] Grouped related changes for Composer mode?
- [ ] Checked existing patterns before creating new code?
- [ ] Provided high-level overview before details?
- [ ] Minimized token usage while maintaining clarity?
- [ ] Leveraged Cursor's indexing and context?

---

## Version

**Version:** 1.0  
**Created:** 2025-01-07  
**Last updated:** 2025-01-07  
**Status:** Active

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
