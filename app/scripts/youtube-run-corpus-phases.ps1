# Local ops: caption phases + classify/match (no network in CI).
# Usage:
#   powershell -File scripts/youtube-run-corpus-phases.ps1 -Phase 1A
#   powershell -File scripts/youtube-run-corpus-phases.ps1 -Phase 1B
#   powershell -File scripts/youtube-run-corpus-phases.ps1 -Phase 2
param(
    [ValidateSet("1A", "1B", "2", "all")]
    [string]$Phase = "1A"
)

$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"

$cookies = Join-Path $here "data\youtube\cookies.txt"

function Run-Captions($channel, $useCookies = $false) {
    Write-Host "=== captions $channel ===" -ForegroundColor Cyan
    if ($useCookies) {
        if (-not (Test-Path $cookies)) {
            Write-Warning "missing cookies: $cookies — export fresh cookies.txt first"
            return 1
        }
        python youtube-batch.py captions --channel $channel --cookies "data/youtube/cookies.txt"
    } else {
        python youtube-batch.py captions --channel $channel
    }
}

if ($Phase -eq "1A" -or $Phase -eq "all") {
    $phase1a = @(
        "therumrevival",
        "williamhansonetiquette",
        "rumverdict",
        "liquidinfo",
        "mayfaircigarledger",
        "cigarrnation",
        "cigaraficionado",
        "stevethebarmanuk"
    )
    foreach ($ch in $phase1a) {
        Run-Captions $ch $false
    }
}

if ($Phase -eq "1B" -or $Phase -eq "all") {
    $phase1b = @("holtscigars", "cigarsdaily", "cigarsdotcom")
    foreach ($ch in $phase1b) {
        python youtube-reset-age-gate.py --channel $ch
        Run-Captions $ch $true
    }
}

if ($Phase -eq "2" -or $Phase -eq "all") {
    python youtube-batch.py classify --all-enabled
    python youtube-batch.py match-rums --all-enabled
    python youtube-batch.py match-cigars --all-enabled
    python youtube-batch.py summarize-cigars --prefer-stubs
    python youtube-export-etiquette-index.py
    python youtube-caption-status.py
}

Write-Host "Phase $Phase done." -ForegroundColor Green
