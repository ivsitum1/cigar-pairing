# Install @tobilu/qmd and index agent-rules collections (Windows).
# Uses node directly when npm's qmd.ps1 launcher fails (no Git Bash).

param(
    [switch]$SkipIndex,
    [switch]$RunEmbed,
    [string]$RepoRoot = ""
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

function Get-NodeExe {
    $candidates = @(
        "C:\Program Files\nodejs\node.exe",
        (Get-Command node -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source)
    )
    foreach ($p in $candidates) {
        if ($p -and (Test-Path $p)) { return $p }
    }
    return $null
}

function Get-QmdJs {
    Join-Path $env:APPDATA "npm\node_modules\@tobilu\qmd\dist\cli\qmd.js"
}

function Invoke-Qmd {
    param([string[]]$Args)
    $node = Get-NodeExe
    $qmdJs = Get-QmdJs
    if (-not $node) {
        Write-Host "Node.js not found. Install via: winget install OpenJS.NodeJS.LTS"
        exit 1
    }
    if (-not (Test-Path $qmdJs)) {
        Write-Host "Installing @tobilu/qmd..."
        $npm = "C:\Program Files\nodejs\npm.cmd"
        if (-not (Test-Path $npm)) { $npm = (Get-Command npm -ErrorAction SilentlyContinue).Source }
        & $npm install -g @tobilu/qmd
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        $qmdJs = Get-QmdJs
    }
    & $node $qmdJs @Args
    exit $LASTEXITCODE
}

$node = Get-NodeExe
if (-not $node) {
    Write-Host "Installing Node.js LTS via winget..."
    winget install OpenJS.NodeJS.LTS --accept-package-agreements --accept-source-agreements --silent
    $env:Path = "C:\Program Files\nodejs;" + $env:Path
    $node = Get-NodeExe
}

if (-not (Test-Path (Get-QmdJs))) {
    $npm = "C:\Program Files\nodejs\npm.cmd"
    & $npm install -g @tobilu/qmd
}

& $node (Get-QmdJs) --version
if ($SkipIndex) {
    Write-Host "SkipIndex set. Wrapper: 40_operations/scripts/qmd.ps1"
    exit 0
}

$wiki = Join-Path $RepoRoot "20_knowledge\wiki"
$books = Join-Path $wiki "sources\books_md"

Push-Location $wiki
& $node (Get-QmdJs) collection remove agent-rules-wiki 2>$null
& $node (Get-QmdJs) collection add . --name agent-rules-wiki
Pop-Location

if (Test-Path $books) {
    Push-Location $books
    & $node (Get-QmdJs) collection remove agent-rules-sources 2>$null
    & $node (Get-QmdJs) collection add . --name agent-rules-sources
    Pop-Location
}

& $node (Get-QmdJs) collection list
& $node (Get-QmdJs) status

if ($RunEmbed) {
    Write-Host "Embedding (may download models; CPU can take a long time)..."
    $env:QMD_FORCE_CPU = "1"
    & $node (Get-QmdJs) embed -c agent-rules-wiki --no-gpu
}

Write-Host "Done. Use: powershell -File 40_operations/scripts/qmd.ps1 query 'your question' -c agent-rules-wiki"
