# Automation Index

This is the central map of automated loops and processing entrypoints in the workspace.

## Graph Hubs

- [[README]]
- [[30_system/docs/GRAPH_CONNECTIVITY_MAP]]
- [[30_system/docs/bridges/non_markdown_bridges]]
- [[code_graph_hub]] — Python/XML wikilink clusters ([[Code graph bridges]])
- [[40_operations/scripts/README]]
- [[.cursor/docs/INDEX]]

## Active Loop Entry Points

### Hook and Memory Lifecycle

- `.cursor/hooks.json`
- `.cursor/hooks/memory_lifecycle.py`
- `memory_engine/memory_hook.py`
- `.agent/memory/raw_events.jsonl`
- `.agent/memory/self_eval.jsonl`
- `40_operations/scripts/memory_admin.py` (prune raw/DB, cap self_eval)
- `40_operations/scripts/memory_self_eval_report.py` (health report → `40_operations/logs/self_eval_report.md`)
- `40_operations/scripts/memory_weekly_maintenance.ps1` (weekly: prune + report + learning loop; non-blocking)
  - Steps: `memory_admin prune` → `memory_self_eval_report.py` → `self_eval_learning_loop.py --mode propose` (default)
  - Schedule: Windows Task Scheduler, weekly (e.g. Sunday 03:00), action:
    `powershell -NoProfile -File "<workspace>/40_operations/scripts/memory_weekly_maintenance.ps1"`
  - Dry-run: `powershell -File 40_operations/scripts/memory_weekly_maintenance.ps1 -DryRun`
  - Learning only: `-LearningWindowDays 7 -LearningMaxCandidates 3` (defaults); guarded skill apply:
    `-LearningMode apply` (rules still require manual `--allow-rule-apply` on the Python CLI)

### Machine weekly digest (brain repo)

- `40_operations/scripts/machine_weekly_digest.py` (arXiv weekly + **self-evolving arXiv** + GitHub AI + RSS + upgrade proposals)
- `40_operations/scripts/github_ai_watch.py`, `ai_news_feed.py`, `arxiv_self_evolving_scan.py`
- Config: `30_system/config/github_ai_watch.json`, `30_system/config/ai_news_feeds.json`
- Output: `.agent/task/machine_digest_YYYY-WW.md`
- Skill: `30_system/SKILLS/SKILL_machine-weekly-digest.md`
- Schedule: `40_operations/scripts/install_machine_weekly_task.ps1` → `AgentRules-MachineWeeklyDigest` (Sunday 08:00 default)
- Dry-run: `python 40_operations/scripts/machine_weekly_digest.py --dry-run --skip-sensors`
- Doc: `30_system/docs/THE_MACHINE.md`
- GitHub token: copy `.env.local.example` → `.env.local` with `GITHUB_TOKEN` (gitignored)
- Dreaming after digest: `run_machine_weekly_digest.ps1` runs `dreaming_daemon.py` on success
- Digest learning: `python 40_operations/scripts/self_eval_learning_loop.py --ingest-machine-digest 2026-W27`

### Changelog Automation

**Brain repo (agent-rules root):**

- `40_operations/scripts/post-commit-hook.sh`
- `40_operations/scripts/post-commit-hook.ps1`
- `40_operations/scripts/changelog_auto.py`
- `30_system/docs/CHANGELOG_AUTO.md`
- `30_system/docs/CHANGELOG_AUTO.jsonl`

**Study project (workspace with `01_input/`, git at project root):**

- `40_operations/scripts/project_init.py` (seeds `05_version_control/changelog.md`, installs hook)
- `40_operations/scripts/project_changelog_auto.py`
- `40_operations/scripts/project-post-commit-hook.sh`
- `05_version_control/CHANGELOG_AUTO.md` + `.jsonl` (at project root, not inside agent-rules)
- `.cursor/rules/project-changelog.mdc`

### Context Synchronization Loop

- `40_operations/scripts/context_sync.py`
- `40_operations/scripts/memory_trim.py`
- `.agent/MEMORY.md`
- `30_system/04_documentation/context/log.md`

### Health and Composite Checks

- `40_operations/scripts/run_all_checks.sh`
- `40_operations/scripts/run_all_checks.ps1`
- `40_operations/scripts/obsidian_connectivity_check.py`
- `40_operations/scripts/generate_non_md_index.py`
- `40_operations/scripts/validate_non_md_index.py`
- `40_operations/scripts/brain_status.py`
- `40_operations/scripts/brain_health.py`
- `40_operations/scripts/brain_audit.py`
- `40_operations/scripts/workspace_inventory_audit.py` (git ls-files + compileall smoke + registry vs SKILL files)
- `40_operations/scripts/run_brain_qa.ps1` (brain_health + skill_registry validate + inventory + brain_audit + pytest)
- `40_operations/scripts/refresh_workspace_reconstruction.py` (sync `workspace_reconstruction.json` from registry)
- `40_operations/scripts/skill_eval_coverage.py` (list registry ids missing `evals/<id>.json`)
- `30_system/docs/CURSOR_RULES_SETUP.md` (avoid duplicate user-global rules)
- `30_system/docs/BRAIN_HEALTH_CRITERIA.md` (PASS definition for brain_health)
- `.pre-commit-config.yaml` (optional local hooks: brain_health, skill_registry, inventory)
- `40_operations/scripts/cursor_paths.py` (resolve `.cursor/scripts` vs legacy `.cursor/40_operations/scripts`)

### Verifier learning loop (SkillLens usage → eval)

- **Automatic:** `.cursor/hooks/relation_conditioned_lifecycle.py` + `verifier_learning_lifecycle.py` (sessionEnd/stop)
- `40_operations/python/brain_assist/verifier_learning_cycle.py`
- `40_operations/scripts/verifier_learning_cycle.py`
- `40_operations/python/brain_assist/verifier_usage_ledger.py`
- `40_operations/scripts/verifier_learning_bridge.py`
- `40_operations/scripts/rcml_export_live.py`
- `40_operations/scripts/verifier_ml_train.py` / `verifier_ml_predict.py`
- `.agent/memory/verifier_usage_ledger.jsonl` (gitignored)
- `30_system/docs/VERIFIER_LEARNING_LOOP.md`
- Phase 4 reminder: `.agent/task/REMINDER_VERIFIER_NEURAL_PHASE4_2026-07-08.md` → [VERIFIER_NEURAL_TRAINING_DEFERRED.md](VERIFIER_NEURAL_TRAINING_DEFERRED.md)

### Output Controller gate (deliverable zero-tolerance)

- **Automatic:** `.cursor/hooks/output_gate_lifecycle.py` (sessionStart, postToolUse Write/StrReplace, sessionEnd/stop)
- `40_operations/python/brain_assist/output_gate_session.py`
- `40_operations/python/brain_assist/output_controller_gate.py`
- `40_operations/scripts/output_controller_gate.py`
- `40_operations/scripts/output_gate_queue.py` (manual queue / flush)
- `.agent/output_gate/last_report.json` (session report; gitignored)
- Opt-out: `OUTPUT_GATE_HOOK_DISABLED=1`
- Skill: `SKILL_output-controller` | Rule: `output-controller-agent.mdc`

### Learning and Evaluation Loop

- `40_operations/scripts/self_eval_learning_loop.py`
- `40_operations/scripts/run_autoresearch.py`
- `40_operations/scripts/skill_eval_runner.py`
- `40_operations/scripts/skill_gap_ingest.py` (eval regression ingest + wiki log; see `30_system/docs/SKILL_GAP_PIPELINE.md`)
- `40_operations/scripts/skill_gap_optimize_gate.py` (composite score + cutoff for optimization loop arming)
- `40_operations/scripts/trajectory_emit.py` (append trajectory JSONL events; see `30_system/docs/TRAJECTORY_EMIT_PROTOCOL.md`)
- `40_operations/scripts/trajectory_rl_bridge.py` (scan benchmark trajectory failures → learning loop)
- `40_operations/scripts/run_agent_benchmark.py` (trajectory + RAG + reliability manifest runner)

### Brain assist (TF-IDF routing; no rule fine-tuning)

- `30_system/docs/DEEP_LEARNING_POLICY.md`
- `40_operations/python/brain_assist/` (`skill_rerank`, `similar_errors`)
- `40_operations/scripts/skill_rerank.py`
- `40_operations/scripts/similar_errors.py`
- `40_operations/scripts/validate_experiment_artifacts.py`
- `40_operations/scripts/generate_experiment_report.py`
- `30_system/docs/LEARNING_UPDATES.md`
- `30_system/docs/SKILL_GAP_PIPELINE.md`
- `90_archive/artifacts/`

### Reference library PDF extract and OCR

- `40_operations/scripts/bootstrap_paddleocr_vendor.py` (extract `PaddleOCR-main.zip` to vendor)
- `40_operations/scripts/install_paddle_ocr.py` ([PaddlePaddle](https://github.com/PaddlePaddle/Paddle) 3.3 wheels + paddleocr + paddlex[ocr]; see [PADDLEPADDLE.md](PADDLEPADDLE.md))
- `40_operations/scripts/extract_pdf_library_to_md.py` (`--ocr auto|paddle|off`, `--prune-stale`, `--resume`, `--report`)
- `40_operations/scripts/extract_pdf_ocr.ps1` (`.venv-ocr` wrapper)
- `40_operations/scripts/run_pdf_paddle_migration.ps1` (domain batches, archive, ingest)
- `40_operations/scripts/audit_books_md_extraction.py` (inventory JSON)
- `40_operations/python/pdf_extraction/` (PP-StructureV3 wrapper)
- `30_system/docs/REFERENCE_LIBRARY_AGENT_ACCESS.md`
- Skill: `30_system/SKILLS/SKILL_paddle-ocr.md`

### Periodic Knowledge Refresh Loop

- `40_operations/scripts/monthly_knowledge_refresh.py`
- `30_system/docs/MONTHLY_KNOWLEDGE_REFRESH.md`
- `30_system/docs/knowledge_refresh/YYYY-MM.md`

### Monthly arXiv skill scout

- `40_operations/scripts/arxiv_monthly_scan.py`
- `30_system/config/arxiv_monthly_scan.json`
- `30_system/docs/MONTHLY_ARXIV_SKILL_SCOUT.md`
- `30_system/SKILLS/SKILL_arxiv-skill-scout.md`
- Outputs: `.agent/task/arxiv_scan_YYYY-MM.json`, `.agent/task/arxiv_digest_YYYY-MM.md`, `self_evolving_arxiv_scan_YYYY-MM.json`
- Schedule: `40_operations/scripts/install_arxiv_scheduled_task.ps1` → task `AgentRules-ArXivSkillScout` (monthly, 1st 09:00)

### Consensus MCP (on-demand, IDE)

- `.cursor/mcp.json` server `consensus` → `https://mcp.consensus.app/mcp`
- `30_system/docs/CONSENSUS_MCP_SETUP.md`
- `20_knowledge/wiki/concepts/Consensus MCP.md`
- Used by `SKILL_research-lookup.md` (OAuth in Cursor; not scheduled)

## Legacy but Connected Surface

Canonical automation scripts (active):

- `40_operations/scripts/run_pipeline.py`
- `40_operations/scripts/brain_health.py`
- `40_operations/scripts/run_all_checks.sh`
- `40_operations/scripts/run_all_checks.ps1`
- `40_operations/scripts/pre-commit-hook.sh`
- `40_operations/scripts/pre-commit-hook.ps1`

Hostname-suffixed sync conflict copies are ignored via `.gitignore` and `cleanup_machine_variants.py` (not active paths).

## Processing Ownership Rule

- Runtime behavior is controlled by executable scripts and hook configs.
- Bridge documents provide graph connectivity and auditability.
- Generated artifacts are linked, not manually edited.
