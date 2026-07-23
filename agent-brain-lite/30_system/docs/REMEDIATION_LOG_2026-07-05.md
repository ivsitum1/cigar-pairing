# Brain Remediation Log — 2026-07-05

Durable trace of the comprehensive audit + fixes applied to the agent-rules
brain. Companion to the commit history; survives the git history rewrite.

## Pre-purge history backup

Full `git bundle --all` snapshot of the repository **including all bloated
history**, taken immediately before the history rewrite:

- **Location:** `C:\Users\Ivan\Documents\agent-rules-prepurge-backup.bundle`
- **Machine:** original workstation (local disk, outside the repo)
- **Size:** ~2.0 GB · 12 refs (all local + remote-tracking branches)
- **Recover:** `git clone agent-rules-prepurge-backup.bundle recovered-repo`

This is the "saved trace" of everything that existed before the purge. Keep it
until you have confirmed the rewritten remote clones and works end-to-end, then
it can be deleted to reclaim disk.

## What was audited

Full workspace check: 5,906 files, 4,079 markdown, 397 Python. Test suite
healthy (282 tests, 0 failures). Memory engine confirmed real and active
(88 MB SQLite, 13k observations + FTS, self-eval telemetry).

## What was fixed (commits 41037804 → f9dce03e and the purge)

| # | Problem | Resolution |
|---|---------|------------|
| P1 | `.git` 2.6 GB / tree 5.8 GB — not portable; PDFs/blobs in history | Backup bundle above + history purge (blobs >10 MB stripped); pre-commit 10 MB guard prevents recurrence |
| P2 | ~79% of live graph links broken | Fixed 3 generator path bugs (off-by-one folder index, stale orphan pruning, absolute-as-relative PDF index). 79%→11%. Added `check_md_links.py` + pytest gate (baseline 790) + pre-commit hook |
| P3 | Autonomy loop dormant, no staleness alerting | `brain_freshness.py` SLO monitor + `run_weekly_maintenance.ps1` + Task Scheduler installer |
| P4 | Unbounded logs (self_eval.jsonl 121k lines) + 88 MB DB | `memory_maintenance.py` — gzip-archives overflow, trims table, VACUUM (non-destructive). Ran once |
| P5 | Suspected CLAUDE.md/claude.md case collision | Verified non-issue — no case-collision pairs tracked; Linux-clone safe |
| P6 | Top-level redirect-stub folders | Intentional compatibility bridges — left as-is |

## Learning loop — made automatic + committing (2026-07-05 follow-up)

The sophisticated `self_eval_learning_loop.py` already distils memory/eval
signal into concrete skill/rule edits with an eval-before/after gate (keeps a
change only if the skill eval improves, auto-reverts regressions; high-risk
rules never auto-apply). It was **not scheduled** and its last run was
2026-06-11, so learning had effectively stopped.

Closed the loop:
- `run_weekly_learning.ps1` runs the loop in eval-gated `apply` mode and
  commits **only** the learned artifacts (`30_system/SKILLS/`, `.cursor/rules/`,
  `LEARNING_UPDATES.*`, `CHANGELOG_AUTO.jsonl`). Raw memory (`.agent/memory`)
  is never staged — it stays uncommitted by design.
- Wired into `run_weekly_maintenance.ps1`, so the existing weekly scheduled
  task now runs learning too. Verified end-to-end: no-ops cleanly when signal
  is quiet, no false commits.

### Known limiter (next lever for learning *quality*)

The loop is currently quiet because self-eval scores sit ~0.9 (>0.8 trigger)
and `memory.db` observations are mostly raw hook dumps with
`lifecycle="unknown"` and a hardcoded 0.8 confidence — so little actionable
signal surfaces. Root cause is upstream at the capture-hook layer (events reach
ingest unstructured), **not** the composer. Fixing the hook to emit structured
lifecycle + meaningful payload would make the accumulated memory genuinely
mineable. Deferred as a focused change to avoid destabilising a tested
subsystem.

## Capture-hook BOM fix — memory stops being garbage (2026-07-05)

Root cause of the "unknown:" raw-dump memory: `.cursor/hooks/memory_lifecycle.py`
`_read_stdin_json()` did not strip a leading UTF-8 BOM (U+FEFF). Windows/
PowerShell piping prepends one, and `str.strip()` does not remove it (U+FEFF is
not whitespace), so `json.loads` failed on **every** hook event and each was
stored as an opaque `{"raw_input": ...}` blob with `lifecycle="unknown"` and a
hardcoded 0.8 confidence. Fixed by stripping the BOM before parsing; regression
test in `test_hook_bom.py`. New events now capture structured lifecycle +
payload, so the memory becomes mineable and the learning loop gets real signal.
(Existing 13k pre-fix rows stay noise; they age out via `memory_maintenance.py`.)

## Cross-machine learning exchange — monthly reconciliation (2026-07-05)

Each machine's `memory.db` is local/uncommitted. To reconcile what different
brains learn, `memory_sync.py` exports a small git-tracked **learning digest**
(curated observations, opaque dumps filtered out) under
`20_knowledge/learning_exchange/<machine-id>/`, and imports peers' digests into
the local store (dedupe by id, tagged `federated:<machine>`). The
`AgentRules-MonthlyLearningSync` task runs `run_monthly_learning_sync.ps1`
monthly: `git pull` → reconcile → commit + push. Learned skills/rules already
reconcile through normal git; this covers the memory layer. Roundtrip test in
`test_memory_sync.py`. Setup per machine:
`install_monthly_learning_sync_task.ps1` (optionally set `AGENT_MACHINE_ID`).

## New tooling added (all under 40_operations/scripts/)

- `check_md_links.py` — broken internal-link report + regression gate
- `memory_maintenance.py` — bounded-growth log rotation + DB VACUUM
- `brain_freshness.py` — autonomy freshness SLO monitor
- `run_weekly_maintenance.ps1` + `install_weekly_maintenance_task.ps1`
- `run_weekly_learning.ps1` — automatic eval-gated learning + artifact commit

## Not transferred by git (copy manually to continue elsewhere)

These are gitignored by design and stay local:

- `.agent/memory/memory.db` (~82 MB) — the brain's learned memory
- `.agent/memory/*.jsonl`, `.agent/memory/archive/` — telemetry
- `.env`, `.env.local` — secrets/config

To continue on another machine with full continuity, copy the files above out of
band (USB/cloud), not via git.
