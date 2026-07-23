# worktree_cleanup.ps1 - List and remove git worktrees
# Usage: .\worktree_cleanup.ps1              # list
#        .\worktree_cleanup.ps1 -Remove <path>  # remove one

param(
    [string]$Remove = ""
)

$ErrorActionPreference = "Stop"
$MainRepo = git rev-parse --show-toplevel 2>$null
if (-not $MainRepo) { Write-Error "Not in a git repository" }

if ($Remove) {
    $PathResolved = [System.IO.Path]::GetFullPath((Join-Path $MainRepo $Remove))
    Write-Host "Removing worktree: $PathResolved" -ForegroundColor Yellow
    git worktree remove $PathResolved --force
    Write-Host "Done. Prune: git worktree prune" -ForegroundColor Green
    exit 0
}

Write-Host "Worktrees:" -ForegroundColor Cyan
git worktree list
Write-Host ""
Write-Host "To remove: .\worktree_cleanup.ps1 -Remove <path>" -ForegroundColor Gray
