# Weekly memory maintenance: prune, health report, learning-loop proposals.
# Non-blocking: prune/report/learning failures are warned, script exits 0.
# Schedule via Task Scheduler (weekly). Dry-run: -DryRun
#
# Learning loop defaults to propose (no file edits). For guarded skill apply:
#   -LearningMode apply
# Rules auto-apply is never enabled here; use self_eval_learning_loop.py manually.

param(
    [int]$Days = 30,
    [int]$SelfEvalMaxLines = 20000,
    [int]$LearningWindowDays = 7,
    [int]$LearningMaxCandidates = 3,
    [ValidateSet("propose", "apply")]
    [string]$LearningMode = "propose",
    [switch]$DryRun
)

$ErrorActionPreference = "Continue"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $Root

Write-Host "memory_weekly_maintenance: days=$Days self_eval_max=$SelfEvalMaxLines dry_run=$DryRun"
Write-Host "  learning: mode=$LearningMode window_days=$LearningWindowDays max_candidates=$LearningMaxCandidates"

if ($DryRun) {
    python 40_operations/scripts/memory_admin.py prune --days $Days --self-eval-max-lines $SelfEvalMaxLines --dry-run
} else {
    python 40_operations/scripts/memory_admin.py prune --days $Days --self-eval-max-lines $SelfEvalMaxLines
}
if ($LASTEXITCODE -ne 0) { Write-Warning "memory_admin prune exited $LASTEXITCODE" }

python 40_operations/scripts/memory_self_eval_report.py
if ($LASTEXITCODE -ne 0) { Write-Warning "memory_self_eval_report exited $LASTEXITCODE" }
Write-Host "Report: 40_operations/logs/self_eval_report.md"

$learningArgs = @(
    "40_operations/scripts/self_eval_learning_loop.py",
    "--mode", $LearningMode,
    "--window-days", $LearningWindowDays,
    "--max-candidates", $LearningMaxCandidates,
    "--json"
)
if ($DryRun) { $learningArgs += "--dry-run" }

Write-Host "Learning loop: python $($learningArgs -join ' ')"
python @learningArgs
if ($LASTEXITCODE -ne 0) {
    Write-Warning "self_eval_learning_loop exited $LASTEXITCODE"
} else {
    Write-Host "Learning proposals: .agent/task/learning_run_*.json, 30_system/docs/LEARNING_UPDATES.md"
}

exit 0
