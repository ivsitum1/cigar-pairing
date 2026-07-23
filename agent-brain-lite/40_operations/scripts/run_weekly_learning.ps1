# Weekly autonomous learning: distil accumulated memory/eval signal into
# committable skill & rule improvements, then commit ONLY those artifacts.
#
# The learned artifacts (skills, rules, learning ledger, changelog) are
# version-controlled; the raw memory that produced them (.agent/memory) stays
# uncommitted by design. The underlying loop (self_eval_learning_loop.py)
# applies a skill change only when its eval score improves and auto-reverts
# regressions, so automatic apply is quality-gated. High-risk rules are never
# auto-applied.
#
# Invoked by run_weekly_maintenance.ps1 (or the AgentRules-WeeklyMaintenance
# task); safe to run by hand. No-ops cleanly when there is nothing to learn.

$ErrorActionPreference = "Continue"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Scripts = Join-Path $RepoRoot "40_operations\scripts"
$LogDir = Join-Path $RepoRoot "40_operations\logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$Log = Join-Path $LogDir ("weekly_learning_{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))
$env:PYTHONPATH = "$Scripts;$(Join-Path $RepoRoot '40_operations\python')"

Set-Location $RepoRoot

# Only these tracked paths hold learned, committable artifacts. Memory
# (.agent/**) is deliberately excluded from staging.
$LearnPaths = @(
    "30_system/SKILLS",
    ".cursor/rules",
    "30_system/docs/LEARNING_UPDATES.jsonl",
    "30_system/docs/LEARNING_UPDATES.md",
    "30_system/docs/CHANGELOG_AUTO.jsonl"
)

"=== weekly learning @ $(Get-Date -Format o) ===" | Tee-Object -FilePath $Log -Append

# Apply mode: eval-gated skill changes are applied; rule edits stay proposals.
& python "$Scripts\self_eval_learning_loop.py" --mode apply --window-days 14 --json 2>&1 |
    Tee-Object -FilePath $Log -Append

# Stage only the learned-artifact paths that actually changed.
$staged = $false
foreach ($p in $LearnPaths) {
    $full = Join-Path $RepoRoot $p
    if (Test-Path $full) {
        $changes = git status --porcelain -- $p
        if ($changes) { git add -- $p; $staged = $true }
    }
}

if ($staged -and (git diff --cached --name-only)) {
    $stamp = Get-Date -Format "yyyy-MM-dd"
    git commit -m "learn(auto): weekly self-eval distillation into skills/rules ($stamp)

Applied eval-gated skill/rule improvements from accumulated memory signal.
Raw memory (.agent/memory) intentionally left uncommitted.

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" 2>&1 | Tee-Object -FilePath $Log -Append
    "Committed learned artifacts." | Tee-Object -FilePath $Log -Append
} else {
    "No committable learning this cycle (signal quiet or no eval improvement)." |
        Tee-Object -FilePath $Log -Append
}

Write-Host "Weekly learning complete. Log: $Log"
