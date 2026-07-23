# Tools Directory

**Location:** `30_system/behavior_rules/tools/`  
**Purpose:** All tools and utilities for the agent rules system

---

## Structure

```
tools/
├── writing/                    # Writing tools (moved from .ai/)
│   ├── writing_workflow.R      # Complete writing workflow
│   ├── writing_workflow.py
│   ├── writing_auto_revise.R  # Auto-revision engine
│   ├── writing_auto_revise.py
│   ├── writing_feedback.R     # Real-time feedback
│   ├── writing_feedback.py
│   ├── writing_realtime_check.R # Real-time checking
│   └── writing_realtime_check.py
├── agents/                     # Agent tools (moved from .ai/)
│   ├── agent_auto_detection.R # Agent auto-detection
│   ├── agent_auto_detection.py
│   └── agent_activation_middleware.R # Agent activation
├── project_check_page.py     # Detailed project check page + optional Slack
├── check_ai_plagiarism.py     # AI plagiarism checker
├── check_ai_score_fast.R      # Fast AI score check (moved from .ai/)
├── check_ai_score_fast.py
├── ai_detection_advanced.py   # Advanced AI detection (moved from .ai/)
├── learning_loop.py           # Learning loop system
├── learning_integration.py    # Learning integration module
├── ingest_learning_block.py   # Ingest LEARNING_BLOCK from LLM output into learning_log.json
├── assistant_learning.py      # Assistant learning
├── track_versions.py          # Version tracking
└── [other tools]
```

---

## Writing Tools

### Usage

**R:**
```r
source("30_system/behavior_rules/tools/writing/writing_workflow.R")
result <- write_with_ai_check(
  initial_text = "Your text here",
  target_ai_score = 0.20,
  max_iterations = 5
)
```

**Python:**
```python
from behavior_rules.tools.writing.writing_workflow import write_with_ai_check

result = write_with_ai_check(
    initial_text="Your text here",
    target_ai_score=0.20,
    max_iterations=5
)
```

---

## Agent Tools

### Usage

**R:**
```r
source("30_system/behavior_rules/tools/agents/agent_activation_middleware.R")
result <- activate_agent_for_prompt("analiziraj podatke", context_files = c("data.csv"))
```

**Python:**
```python
from behavior_rules.tools.agents.agent_auto_detection import detect_agent_from_prompt

result = detect_agent_from_prompt("analiziraj podatke", context_files=["data.csv"])
```

---

## AI Detection Tools

### Usage

**R:**
```r
source("30_system/behavior_rules/tools/check_ai_score_fast.R")
score <- check_ai_score_fast(text, fast_mode = TRUE)
```

**Python:**
```python
from behavior_rules.tools.check_ai_score_fast import check_ai_score_fast

score = check_ai_score_fast(text, fast_mode=True)
```

---

## Learning Loop

### ingest_learning_block.py

Parses `## LEARNING_BLOCK` ... `## END_LEARNING_BLOCK` from text and appends to learning_log.json.

**Usage:**
```bash
python 30_system/behavior_rules/tools/ingest_learning_block.py < output.txt
python 30_system/behavior_rules/tools/ingest_learning_block.py path/to/output.txt
```

See `30_system/behavior_rules/14_learning_loop.md` for LEARNING_BLOCK format.

---

## Project check page (Slack tool)

### project_check_page.py

Generates a **detailed check page** per project (`30_system/docs/PROJECT_CHECK.md` or `PROJECT_CHECK.md`) and can post a short summary to **Slack** via Incoming Webhook.

**Check page includes:** roadmap agreed, R only for stats/simulation/modeling/power in `40_operations/R/`, Python for writing/tooling, paths and validation presence, folder structure, git status. Some rows are auto-filled from discovery; others are checkboxes for you to update.

**Usage:**
```bash
# Generate check page only (from project root)
python 30_system/behavior_rules/tools/project_check_page.py

# Custom project root and name
python 30_system/behavior_rules/tools/project_check_page.py --project-root /path/to/project --name "My Study"

# Generate and notify Slack (requires SLACK_WEBHOOK_URL)
set SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
python 30_system/behavior_rules/tools/project_check_page.py --slack
```

**Slack setup:** Create an Incoming Webhook in your Slack workspace (App → Incoming Webhooks → Add to Slack). Set `SLACK_WEBHOOK_URL` in your environment; the script sends one message per run when `--slack` is used.

---

## Migration Notes

**Tools moved from `.ai/` to `30_system/behavior_rules/tools/` on 2026-01-27:**
- Writing tools → `tools/writing/`
- Agent tools → `tools/agents/`
- AI detection tools → `tools/`

All paths have been updated. If you encounter issues, check that you're using the new paths.

---

## Related Documentation

- `30_system/behavior_rules/README.md` - Main behavior rules overview
- `.cursor/rules/README.md` - Cursor rules overview
- `30_system/SKILLS/` - Procedural instructions

---

**Version:** 1.0  
**Last Updated:** 2026-01-27

## Related Hubs

- [Folder index hub](../../docs/FOLDER_INDEX.md)
- [All notes index](../../docs/ALL_NOTES_INDEX.md)
- [Graph connectivity map](../../docs/GRAPH_CONNECTIVITY_MAP.md)
