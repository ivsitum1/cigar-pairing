# Pre-commit hook for agent-rules repo (PowerShell)
# Install: copy this to .git/hooks/pre-commit and ensure Git runs it, or run manually before commit

$ErrorActionPreference = "Stop"

# 1. Validate Cursor rules frontmatter
if (Test-Path ".cursor/rules") {
    Get-ChildItem ".cursor/rules/*.mdc" -ErrorAction SilentlyContinue | ForEach-Object {
        $first = Get-Content $_.FullName -TotalCount 1
        if ($first -notmatch "^---") {
            Write-Error "Missing frontmatter: $($_.FullName)"
        }
    }
}

# 2. Check for common R mistakes (skip 40_operations/R/validation/rubrics/* and 40_operations/tests/* — rubrics/tests contain these patterns as detection targets or test strings)
$rFiles = git diff --cached --name-only | Where-Object { $_ -match "\.R$" }
foreach ($f in $rFiles) {
    if (-not (Test-Path $f)) { continue }
    if ($f -match "^40_operations/R/validation/rubrics/") { continue }
    if ($f -match "^40_operations/tests/") { continue }
    $content = Get-Content $f -Raw
    if ($content -match "subset\(" -and $content -notmatch "#.*subset\(") {
        Write-Host "Warning: $f uses subset() - prefer dplyr::filter()" -ForegroundColor Yellow
    }
    if ($content -match "setwd\(" -and $content -notmatch "#.*setwd\(") {
        Write-Error "$f uses setwd(). Use here::here() instead."
    }
    if ($content -match "\bT\b" -and $content -notmatch "TRUE") {
        Write-Host "Warning: $f may use T/F - use TRUE/FALSE" -ForegroundColor Yellow
    }
    if ($content -match "\bF\b" -and $content -notmatch "FALSE" -and $content -notmatch "Pr\(>F\)") {
        Write-Host "Warning: $f may use T/F - use TRUE/FALSE" -ForegroundColor Yellow
    }
}

# 3. Validate skill registry consistency
Write-Host "Validating skill registry..." -ForegroundColor Cyan
python "$PSScriptRoot\skill_registry.py" validate
if ($LASTEXITCODE -ne 0) {
    Write-Error "Skill registry validation failed"
}

# 4. Changelog runs in post-commit only (see 40_operations/scripts/post-commit-hook.ps1 / .sh)

# 5. Manuscript reminder
$staged = git diff --cached --name-only
if ($staged -match "manuscript|paper|draft") {
    Write-Host "Manuscript changed - consider running AI detection check" -ForegroundColor Cyan
}

Write-Host "Pre-commit checks passed" -ForegroundColor Green
