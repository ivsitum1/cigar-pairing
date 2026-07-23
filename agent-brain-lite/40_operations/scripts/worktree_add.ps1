# worktree_add.ps1 - Create git worktree with symlinks for .env
# Usage: .\worktree_add.ps1 -Branch <branch> -Path <dir>
# Example: .\worktree_add.ps1 -Branch feature/xyz -Path ..\agent-rules-feature-xyz

param(
    [Parameter(Mandatory = $true)]
    [string]$Branch,
    [Parameter(Mandatory = $true)]
    [string]$Path
)

$ErrorActionPreference = "Stop"
$MainRepo = git rev-parse --show-toplevel 2>$null
if (-not $MainRepo) { Write-Error "Not in a git repository" }

$PathResolved = [System.IO.Path]::GetFullPath((Join-Path $MainRepo $Path))

Write-Host "Creating worktree: branch=$Branch path=$PathResolved" -ForegroundColor Cyan
git worktree add -b $Branch $PathResolved
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

# Symlink .env if it exists in main repo
$MainEnv = Join-Path $MainRepo ".env"
if (Test-Path $MainEnv) {
    $WorktreeEnv = Join-Path $PathResolved ".env"
    if (-not (Test-Path $WorktreeEnv)) {
        New-Item -ItemType SymbolicLink -Path $WorktreeEnv -Target $MainEnv -Force | Out-Null
        Write-Host "Symlinked .env -> main repo" -ForegroundColor Green
    }
}

# Create .env.local for DB isolation (optional - if project uses DB)
$EnvLocal = Join-Path $PathResolved ".env.local"
$SafeBranch = $Branch -replace '[\/\\]', '_'
if (-not (Test-Path $EnvLocal)) {
    Set-Content -Path $EnvLocal -Value "DB_NAME=project_test_$SafeBranch" -Encoding UTF8
    Write-Host "Created .env.local with DB_NAME=project_test_$SafeBranch" -ForegroundColor Green
}

Write-Host ""
Write-Host "Next: cd `"$PathResolved`" then open in Cursor" -ForegroundColor Yellow
