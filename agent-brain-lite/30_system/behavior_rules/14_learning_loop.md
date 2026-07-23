# Learning Loop and Adaptive Behavior

## Purpose

This document describes the learning loop protocol that enables AI agents to adapt and learn from past interactions, mistakes, and feedback. The learning loop allows the agent to improve its performance over time by tracking patterns, learning from errors, and adapting behavior based on outcomes.

---

## Learning Loop Architecture

### Core Components

```yaml
LEARNING_LOOP_COMPONENTS:
  observation:
    description: "Track all interactions, decisions, and outcomes"
    storage: "learning_log.json"
  
  analysis:
    description: "Identify patterns, errors, and improvement opportunities"
    frequency: "After each session, weekly summary"
  
  adaptation:
    description: "Update behavior rules and strategies based on learnings"
    mechanism: "Rule updates, strategy refinement"
  
  evaluation:
    description: "Measure improvement and validate adaptations"
    metrics: "Error rate, user satisfaction, task completion"
```

### Learning Loop Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    LEARNING LOOP CYCLE                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  STEP 1: OBSERVE                                             │
│  ────────────────────────────────────────────────────────   │
│  • Track all interactions and decisions                     │
│  • Record outcomes (success/failure)                         │
│  • Capture user feedback (explicit/implicit)                │
│  • Log errors and their resolutions                         │
│              ↓                                               │
│  STEP 2: ANALYZE                                             │
│  ────────────────────────────────────────────────────────   │
│  • Identify recurring error patterns                        │
│  • Detect successful strategies                             │
│  • Find user preferences and patterns                       │
│  • Calculate performance metrics                            │
│              ↓                                               │
│  STEP 3: ADAPT                                               │
│  ────────────────────────────────────────────────────────   │
│  • Update behavior rules based on learnings                │
│  • Refine strategies for common tasks                       │
│  • Adjust confidence thresholds                             │
│  • Create new heuristics for edge cases                     │
│              ↓                                               │
│  STEP 4: EVALUATE                                            │
│  ────────────────────────────────────────────────────────   │
│  • Measure improvement in metrics                           │
│  • Validate adaptations don't break existing functionality  │
│  • A/B test new strategies when appropriate                 │
│  • Document learnings for future reference                  │
│              ↓                                               │
│  STEP 5: ITERATE                                             │
│  ────────────────────────────────────────────────────────   │
│  • Continue observing with new adaptations                  │
│  • Refine further based on new data                        │
│  • Maintain learning log for long-term patterns             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## LEARNING_BLOCK Format (for LLM Output)

When an agent completes a task, it may output a structured block for ingestion into the learning log. Use `30_system/behavior_rules/tools/ingest_learning_block.py` to parse and log:

```
## LEARNING_BLOCK
{"task_type": "setup", "task_description": "...", "approach": "...", "status": "success|partial|failure", "learnings": {"what_worked": [], "what_failed": [], "insights": []}}
## END_LEARNING_BLOCK
```

**Required fields:** `task_type`, `task_description`, `approach`, `status`

**Optional:** `learnings`, `files_modified`, `error_occurred`, `error_type`, `user_feedback`, `self_assessment_score`

**Ingestion:** `python 30_system/behavior_rules/tools/ingest_learning_block.py < output.txt`

---

### Trajectory JSONL (complex / benchmark runs)

For multi-tool runs that feed trajectory RL and benchmarks, append events to `90_archive/artifacts/<run_id>/trajectory.jsonl` per `30_system/docs/TRAJECTORY_EMIT_PROTOCOL.md`. Hooks in `.cursor/hooks/trajectory_lifecycle.py` capture `tool_selected` on `postToolUse` when not disabled (`TRAJECTORY_RL_DISABLED=1`). Agents should add `expected_tool` on golden benchmark cases.

---

### LEARNING_BLOCK for drug_discovery (Pipeline 7A/7B)

When `task_type` is `"drug_discovery"` or `"discovery"` and the run used the Discovery Engine (Pipeline 7A or 7B), include these **optional** fields so the Learning Loop can analyse discovery-specific patterns:

| Field | Type | Description |
|-------|------|--------------|
| `pipeline_variant` | string | `"7A"` (MVP, 5 phases) or `"7B"` (full super-pipeline) |
| `hypothesis_pivots` | number | Count of times the system rejected a hypothesis and re-ideated (Evidence Consistency Check fail → pivot) |
| `evidence_consistency_scores` | object or array | Per-hypothesis or final support ratio / consistency score; e.g. `{"support_ratio": 0.32, "threshold": 0.25}` |
| `council_score` | number | Agent Council score (e.g. /100) if Pipeline 7B ran through Protocol + Red Team + Council |
| `red_team_flaws` | object | Counts or summary: `{"critical": 2, "major": 4}` (optional) |

Example (Pipeline 7B):

```
## LEARNING_BLOCK
{"task_type": "drug_discovery", "task_description": "Novel therapeutic strategy for T1D honeymoon phase", "approach": "Discovery Super-pipeline (26_discovery_superpipeline.md)", "status": "success", "pipeline_variant": "7B", "hypothesis_pivots": 1, "evidence_consistency_scores": {"first_hypothesis_support": 0.20, "after_pivot_support": 0.45}, "council_score": 70, "red_team_flaws": {"critical": 3, "major": 4}, "learnings": {"what_worked": ["PubMed + semantic gate", "pivot on evidence check"], "what_failed": [], "insights": ["Bcl-2 hypothesis under-supported; pivot to AAV PD-L1 + IL-2"]}}
## END_LEARNING_BLOCK
```

Analysis tools (e.g. `learning_loop.py analyze`) can filter on `task_type == "drug_discovery"` to compute metrics such as average pivots per run, council score distribution, and recurring failure patterns. See `30_system/behavior_rules/24_discovery_pipeline.md` (Learning Loop hook) and `30_system/behavior_rules/26_discovery_superpipeline.md` (Step 45).

---

## Observation Protocol

### Distillation skeletons (hybrid capture)

After substantive sessions, enrich recent auto skeleton traces in `.agent/distillation/raw/` (`skeleton: true`, `enrichment_status: pending`) with `context` + `reasoning`, then re-capture or promote per `30_system/docs/DISTILLATION_TRACE_PROTOCOL.md`. Hook: `.cursor/hooks/distillation_lifecycle.py` on `sessionEnd`/`stop`.

### What to Track

**MANDATORY - Track these events:**

```yaml
TRACKED_EVENTS:
  task_execution:
    - Task type and description
    - Approach taken
    - Time to completion
    - Success/failure status
    - Error messages (if any)
  
  user_feedback:
    - Explicit corrections
    - Implicit signals (rejections, re-requests)
    - User preferences expressed
    - Satisfaction indicators
  
  error_occurrences:
    - Error type (syntax/runtime/logic/design)
    - Error message
    - Context (file, function, line)
    - Resolution approach
    - Success of resolution
  
  performance_metrics:
    - Code quality scores
    - Self-assessment ratings
    - Verification pass rates
    - User approval rates
```

### Data Structure

```json
{
  "session_id": "timestamp-uuid",
  "timestamp": "2024-12-31T12:00:00Z",
  "task": {
    "type": "code_generation|analysis|debugging|refactoring",
    "description": "Brief task description",
    "complexity": "low|medium|high"
  },
  "execution": {
    "approach": "Description of approach taken",
    "files_modified": ["file1.R", "file2.md"],
    "time_seconds": 45,
    "iterations": 3
  },
  "outcome": {
    "status": "success|partial|failure",
    "user_feedback": "positive|neutral|negative|none",
    "error_occurred": true,
    "error_type": "LEVEL_1|LEVEL_2|LEVEL_3|LEVEL_4",
    "self_assessment_score": 8.5
  },
  "learnings": {
    "what_worked": ["strategy1", "strategy2"],
    "what_failed": ["approach1"],
    "insights": ["insight1", "insight2"]
  }
}
```

---

## Analysis Protocol

### Pattern Detection

**Identify these patterns:**

1. **Recurring Errors**
   - Same error type appearing multiple times
   - Common failure points
   - Error-prone task types

2. **Successful Strategies**
   - Approaches that consistently work
   - High-performing patterns
   - User-preferred methods

3. **User Preferences**
   - Preferred code style
   - Communication style preferences
   - Common request patterns

4. **Performance Trends**
   - Improvement or degradation over time
   - Task-specific performance
   - Time-to-resolution trends

### Analysis Frequency

```yaml
ANALYSIS_SCHEDULE:
  immediate:
    - After each error occurrence
    - After user correction
    - After task failure
  
  session_end:
    - Summarize session learnings
    - Identify immediate improvements
  
  weekly:
    - Aggregate patterns
    - Calculate performance metrics
    - Generate adaptation recommendations
  
  monthly:
    - Long-term trend analysis
    - Major rule updates
    - Strategy refinement
```

---

## Adaptation Protocol

### Rule Updates

**When to update rules:**

1. **Error Pattern Detected**
   - If same error occurs 3+ times → Add preventive rule
   - If error resolution works consistently → Document as best practice

2. **User Preference Identified**
   - If user consistently requests specific style → Update style guide
   - If user prefers certain approaches → Prioritize those approaches

3. **Performance Improvement Opportunity**
   - If strategy A works better than B → Update default strategy
   - If certain checks reduce errors → Make them mandatory

### Adaptation Process

```yaml
ADAPTATION_PROCESS:
  step_1_identify:
    action: "Identify specific rule or behavior to adapt"
    criteria: "Based on analysis findings"
  
  step_2_propose:
    action: "Propose specific adaptation"
    format: "Clear before/after comparison"
  
  step_3_test:
    action: "Test adaptation in controlled manner"
    duration: "Minimum 5-10 interactions"
  
  step_4_evaluate:
    action: "Measure impact of adaptation"
    metrics: "Error rate, user satisfaction, performance"
  
  step_5_commit:
    action: "Permanently adopt if successful"
    documentation: "Update relevant rule file"
```

### Adaptation Examples

**Example 1: Error Prevention Rule**

```markdown
## Learning: Namespace Conflicts in R

**Pattern Detected:**
- Error "object 'filter' not found" occurred 5 times
- Always when using dplyr without explicit namespace

**Adaptation:**
- Add mandatory check: "Always use explicit namespacing for dplyr functions"
- Update rule: 01_general_rules.md, Section "Namespace Conflicts"
- Add to pre-execution checklist

**Impact:**
- Error rate for namespace issues: 5 → 0
- Code quality improved
```

**Example 2: User Preference Learning**

```markdown
## Learning: User Prefers Detailed Explanations

**Pattern Detected:**
- User consistently requests "explain more" or "add details"
- Never requests "make it shorter"
- High satisfaction when explanations are comprehensive

**Adaptation:**
- Set default verbosity to HIGH for this user
- Update: 01_general_rules.md, Section "Verbosity Control"
- Prioritize educational explanations

**Impact:**
- User satisfaction increased
- Fewer clarification requests
```

---

## Evaluation Protocol

### Metrics to Track

```yaml
EVALUATION_METRICS:
  error_rate:
    calculation: "Errors per 100 tasks"
    target: "< 5%"
    tracking: "Weekly trend"
  
  resolution_success:
    calculation: "Successful resolutions / Total errors"
    target: "> 90%"
    tracking: "Per error type"
  
  user_satisfaction:
    calculation: "Positive feedback / Total feedback"
    target: "> 80%"
    tracking: "Weekly average"
  
  task_completion:
    calculation: "Completed tasks / Total tasks"
    target: "> 95%"
    tracking: "Per task type"
  
  self_assessment_accuracy:
    calculation: "Correlation with actual outcomes"
    target: "> 0.7"
    tracking: "Monthly analysis"
```

### Evaluation Checklist

Before committing an adaptation:

- [ ] Adaptation tested for minimum 5 interactions
- [ ] Error rate improved or maintained
- [ ] No new errors introduced
- [ ] User satisfaction maintained or improved
- [ ] Performance metrics stable or improved
- [ ] Documentation updated
- [ ] Rollback plan available if needed

---

## Implementation

### Learning Log Structure

**File:** `30_system/behavior_rules/tools/learning_log.json`

```json
{
  "metadata": {
    "version": "1.0",
    "last_updated": "2024-12-31T12:00:00Z",
    "total_sessions": 150,
    "total_tasks": 1250
  },
  "sessions": [
    {
      "session_id": "2024-12-31-001",
      "timestamp": "2024-12-31T12:00:00Z",
      "tasks": [...],
      "summary": {
        "total_tasks": 8,
        "successful": 7,
        "failed": 1,
        "errors": 2,
        "user_feedback": "positive"
      }
    }
  ],
  "patterns": {
    "recurring_errors": [
      {
        "error_type": "LEVEL_2",
        "error_message": "object 'filter' not found",
        "frequency": 5,
        "last_occurrence": "2024-12-30",
        "resolution": "Use dplyr::filter() explicitly",
        "prevention_rule": "Added to namespace rules"
      }
    ],
    "successful_strategies": [
      {
        "strategy": "Explicit namespacing for dplyr",
        "success_rate": 1.0,
        "usage_count": 50,
        "recommended": true
      }
    ],
    "user_preferences": [
      {
        "preference": "High verbosity",
        "confidence": 0.95,
        "evidence_count": 20,
        "applied": true
      }
    ]
  },
  "adaptations": [
    {
      "date": "2024-12-30",
      "type": "rule_update",
      "description": "Added mandatory explicit namespacing",
      "impact": {
        "error_reduction": 0.8,
        "user_satisfaction": "maintained"
      }
    }
  ]
}
```

### Learning Loop Script

**File:** `30_system/behavior_rules/tools/learning_loop.py`

The learning loop script provides:
- Automatic logging of interactions
- Pattern analysis
- Adaptation recommendations
- Performance tracking

**Usage:**
```bash
# Log a task execution
python learning_loop.py log --task "code_generation" --status "success"

# Analyze patterns
python learning_loop.py analyze --period "weekly"

# Get adaptation recommendations
python learning_loop.py recommend

# Generate performance report
python learning_loop.py report --period "monthly"
```

---

## Integration with Existing Rules

### Connection Points

1. **Self-Assessment Loop (01_general_rules.md)**
   - Learning loop uses self-assessment scores as input
   - Adaptations can improve self-assessment accuracy

2. **Error Handling (01_general_rules.md)**
   - All errors are logged to learning loop
   - Error patterns inform adaptation

3. **Verification Protocol (05_verification.md)**
   - Verification failures are tracked
   - Successful verification strategies are learned

4. **Agentic Workflow (13_agentic_workflow.md)**
   - Task decomposition patterns are learned
   - Successful workflows are documented

---

## Best Practices

### Learning Loop Guidelines

1. **Privacy and Security**
   - Never log sensitive data (PHI, credentials)
   - Anonymize user-specific information
   - Store logs securely

2. **Data Quality**
   - Ensure accurate logging
   - Validate data before analysis
   - Handle missing data appropriately

3. **Adaptation Safety**
   - Test adaptations before permanent adoption
   - Maintain rollback capability
   - Document all changes

4. **Continuous Improvement**
   - Regular analysis (weekly minimum)
   - Act on clear patterns (not single occurrences)
   - Balance adaptation with stability

5. **Transparency**
   - Document all adaptations
   - Explain reasoning for changes
   - Track impact of adaptations

---

## Limitations and Considerations

### What the Learning Loop Cannot Do

- **Cannot learn from future events** - Only learns from past interactions
- **Cannot guarantee improvement** - Adaptations may not always work
- **Requires sufficient data** - Needs multiple interactions to identify patterns
- **May overfit** - Could adapt too much to specific user patterns

### Mitigation Strategies

1. **Minimum Sample Size**
   - Require at least 3-5 occurrences before adapting
   - Use statistical significance for pattern detection

2. **Validation**
   - Test adaptations before permanent adoption
   - Monitor for unintended consequences

3. **Diversity**
   - Learn from diverse task types
   - Avoid over-adapting to edge cases

4. **Human Oversight**
   - Review major adaptations
   - Allow human override of automatic adaptations

---

## Version

**Version:** 1.0  
**Last updated:** 2024-12-31  
**Status:** Active  
**Integration:** Works with all existing behavior rules

## Related Hubs

- [Folder index hub](../docs/FOLDER_INDEX.md)
- [All notes index](../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../docs/GRAPH_CONNECTIVITY_MAP.md)
