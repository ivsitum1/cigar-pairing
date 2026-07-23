# Monthly cross-machine learning reconciliation.
#
# Pulls peers' git-tracked learning digests, merges them into the local
# memory.db, exports this machine's fresh digest, and pushes it back — so every
# brain periodically absorbs what the others learned. Raw memory and secrets
# never leave the machine; only the curated digest under
# 20_knowledge/learning_exchange/<machine>/ is committed.
#
# Invoked by the AgentRules-MonthlyLearningSync task, or by hand.

$ErrorActionPreference = "Continue"
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$Scripts = Join-Path $RepoRoot "40_operations\scripts"
$LogDir = Join-Path $RepoRoot "40_operations\logs"
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$Log = Join-Path $LogDir ("learning_sync_{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))
$env:PYTHONPATH = "$Scripts;$(Join-Path $RepoRoot '40_operations\python')"
Set-Location $RepoRoot

function Note($m) { "$m" | Tee-Object -FilePath $Log -Append }

Note "=== monthly learning sync @ $(Get-Date -Format o) ==="

# 1. Get peers' latest digests (and any committed skill/rule learning).
Note "--- git pull ---"
git pull --no-edit 2>&1 | Tee-Object -FilePath $Log -Append

# 2. Merge peer digests into local (uncommitted) memory, then export ours.
Note "--- reconcile (import peers + export local) ---"
& python "$Scripts\memory_sync.py" --reconcile 2>&1 | Tee-Object -FilePath $Log -Append

# 3. Publish this machine's digest only.
$staged = git status --porcelain -- "20_knowledge/learning_exchange"
if ($staged) {
    git add -- "20_knowledge/learning_exchange"
    $mid = & python -c "import sys; sys.path.insert(0,r'$Scripts'); import memory_sync; print(memory_sync.machine_id())"
    git commit -m "learn(sync): publish $mid learning digest ($(Get-Date -Format yyyy-MM-dd))

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>" 2>&1 | Tee-Object -FilePath $Log -Append
    git push 2>&1 | Tee-Object -FilePath $Log -Append
    Note "Published digest and pushed."
} else {
    Note "No digest change to publish this cycle."
}

Write-Host "Monthly learning sync complete. Log: $Log"
