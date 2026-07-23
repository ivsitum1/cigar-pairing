> **⚠️ MIGRATED** -> `.cursor/rules/agentic-workflow-guardrails.mdc` (2026-05-08)

# Agentic Workflow Controls

## Purpose

This document describes protocols for controlling agentic workflows, including task decomposition, checkpoint system, rollback protocols, and progress tracking. These protocols ensure reliability and control over complex tasks.

---

## Self-Assessment Protocol

**Threshold and dimensions:** See `00_core_principles.md` (minimum **9/10** before delivery; dimensions listed there).

**Loop:** Generate → critique → rate 1–10 → if &lt; 9, improve → repeat up to 3 iterations (or use Python `mandatory_self_assess()` in `40_operations/python/quality_validation/`).

**Checkpoints:** Use the **Checkpoint System** and **Progress Tracking Template** sections below in this file for explicit verification blocks on complex tasks.

---

## Task Decomposition Protocol

### Approach: Break Complex Tasks into Verified Steps

**IMPORTANT - Break complex tasks into verifiable steps:**

```yaml
DECOMPOSITION_TEMPLATE:
  step_1_understand:
    action: "Parse and clarify requirements"
    output: "Clear statement of what needs to be done"
    verification: "User confirms understanding"
  
  step_2_plan:
    action: "Design approach and identify risks"
    output: "Numbered list of sub-tasks"
    verification: "Each sub-task is independently testable"
  
  step_3_execute:
    action: "Implement one sub-task at a time"
    output: "Working code for each sub-task"
    verification: "Sub-task passes its specific test"
  
  step_4_integrate:
    action: "Combine sub-tasks"
    output: "Complete solution"
    verification: "End-to-end test passes"
  
  step_5_document:
    action: "Document solution and decisions"
    output: "README, comments, changelog"
    verification: "Another developer can understand"
```

### Example: Task Decomposition

```markdown
## Task: Implement Meta-Analysis with Forest Plot

### Step 1: Understand
- [x] User wants meta-analysis with forest plot
- [x] Data is in Excel file
- [x] Need to display both random and common effects

### Step 2: Plan
1. Load data from Excel
2. Prepare data for meta-analysis
3. Perform meta-analysis (random + common effects)
4. Generate forest plot
5. Export results

### Step 3: Execute
- [x] Step 1: Loading data
- [x] Step 2: Data preparation
- [ ] Step 3: Meta-analysis (in progress)
- [ ] Step 4: Forest plot
- [ ] Step 5: Export

### Step 4: Integrate
- [ ] End-to-end test

### Step 5: Document
- [ ] README
- [ ] Code comments
```

---

## Checkpoint System

### Checkpoint Triggers

**Mandatory checkpoints:**
- Before deleting any file
- Before modifying >3 files
- Before running destructive commands
- After completing each major sub-task
- When confidence falls below 70%

**Checkpoint format:**
```markdown
## CHECKPOINT: [Name]

**Progress:**
- Completed: [list]
- In progress: [current task]
- Remaining: [list]

**Current State:**
- Modified files: [list]
- Tests pass: [yes/no/partial]

**Decision Point:**
- Options: [A, B, C]
- Recommended: [X]
- Rationale: [why]

**Continue?** [Awaiting confirmation]
```

### Checkpoint Example

```markdown
## CHECKPOINT: Before Deleting Test Files

**Progress:**
- Completed: 
  - Created new project structure
  - Migrated data
- In progress: Cleaning old test files
- Remaining: 
  - Final verification
  - Documentation

**Current State:**
- Modified files: 
  - `data/new_structure.xlsx`
  - `40_operations/scripts/migration.R`
- Tests pass: yes

**Decision Point:**
- Option A: Delete all test files at once
- Option B: Delete individually with verification
- Option C: Archive instead of deleting
- Recommended: Option C (archiving)
- Rationale: Safer, can revert if needed

**Continue?** Please confirm option.
```

---

## Rollback Protocol

### Before Any Change

**1. Verify git status:**
```bash
git status
# Should be clean (commit or stash pending changes)
```

**2. Create checkpoint:**
```bash
git add -A
git commit -m "CHECKPOINT: before [task]"
```

**3. Document rollback command:**
```markdown
# Rollback command:
git reset --hard HEAD~1
```

### If Changes Fail

**1. STOP immediately - do not attempt to fix broken state**

**2. Report what was attempted and what failed**

**3. Execute rollback:**
```bash
git reset --hard [checkpoint]
```

**4. Verify rollback is successful**

**5. Re-analyze approach before retry**

### Rollback Verification

```yaml
ROLLBACK_VERIFICATION:
  - Run test suite to confirm working state
  - Check file integrity
  - Verify no orphaned changes
```

## Loop Detection

If the same subtask has been attempted 3 or more times without success:

1. STOP immediately — do not attempt again
2. Log: what was attempted each time, what error occurred
3. Diagnose root cause before any retry
4. Escalate to Level 3 (stop + report to user with full details)

Rationale: three identical failures indicate a structural problem, not a transient error.

## Timeout Rules

- **Single step timeout**: any task step running longer than 5 minutes without output
  → trigger a status check; log the step name and elapsed time
- **Hard timeout**: no response after 10 minutes → mark step as FAILED, trigger rollback
  to last checkpoint, report to user with step name and last known state
- **Never silently retry** a timed-out step without first logging the timeout event

---

## Progress Tracking Template

```markdown
## Task Progress Log

### Task: [Description]
### Started: [Timestamp]
### Status: [In Progress / Blocked / Completed]

---

#### Iteration 1
- **Action**: [What was attempted]
- **Result**: [Success/Failure + details]
- **Modified Files**: [List]
- **Next Step**: [What next]

#### Iteration 2
- **Action**: [What was attempted]
- **Result**: [Success/Failure + details]
- **Modified Files**: [List]
- **Next Step**: [What next]

---

### Summary
- **Total Iterations**: X
- **Final Status**: [Completed/Incomplete]
- **Remaining Issues**: [List if any]
- **Human Action Required**: [Yes/No + details]
```

---

## Task Status Management

### Status Categories

```yaml
STATUS_CATEGORIES:
  pending:
    description: "Task identified but not yet started"
    action: "Plan and add to queue"
  
  in_progress:
    description: "Active work on task"
    action: "Update progress log"
  
  blocked:
    description: "Task waiting on external input or dependency"
    action: "Identify blockage and escalate if needed"
  
  completed:
    description: "Task successfully completed and verified"
    action: "Document and archive"
  
  failed:
    description: "Task unsuccessful after maximum attempts"
    action: "Analyze cause and escalate"
```

### Status Transition Rules

```yaml
ALLOWED_TRANSITIONS:
  pending → in_progress: "When work starts"
  in_progress → blocked: "When blockage occurs"
  in_progress → completed: "When task is completed"
  in_progress → failed: "After maximum attempts"
  blocked → in_progress: "When blockage is resolved"
  blocked → failed: "If blockage cannot be resolved"
```

---

## Quality Gates

### Before Finalizing Task

```yaml
QUALITY_GATES:
  code_quality:
    - [ ] Code compiles without errors
    - [ ] No warnings (or justified)
    - [ ] Follows style guide
    - [ ] Documented with comments
  
  functionality:
    - [ ] All tests pass
    - [ ] Edge cases handled
    - [ ] Error handling implemented
  
  documentation:
    - [ ] README updated
    - [ ] Changelog updated
    - [ ] Code comments added
  
  verification:
    - [ ] Self-assessment score ≥ 9/10  (canonical per core-principles.mdc)
    - [ ] Code review passed (if needed)
    - [ ] User confirmed (for critical changes)
```

---

## Communication Protocol

### Status Updates

**When to give status update:**
- After each checkpoint
- When status changes (e.g. blocked → in_progress)
- When unexpected problem occurs
- On user request

**Status update format:**
```markdown
## Status Update: [Task Name]

**Current Status:** [in_progress/blocked/completed]

**Progress:**
- ✅ [Completed]
- 🔄 [In progress]
- ⏳ [Waiting]

**Blockages (if any):**
- [Description of blockage]
- [Action needed]

**Next Steps:**
1. [Step 1]
2. [Step 2]
```

---

**Version:** 1.0  
**Last updated:** 2024-12-31  
**Reference:** CURSOR_AGENT_INSTRUCTIONS (1).md, Section 12

## Semantic graph (auto)

- [[Behavior rules hub]]
- [[Orchestrator - agent roles]]
- [behavior rules INDEX](../docs/indexes/behavior_rules_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)
- [FOLDER INDEX](../docs/FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[SKILL_swiss-cheese]]
- [[SKILL_ralph-loop]]
- [[09_workflow_optimization]]
- [[SKILL_scholarly-iteration-loop]]
- [[SKILL_forest-plot]]
