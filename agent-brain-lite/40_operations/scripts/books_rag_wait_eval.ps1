# Wait for books_rag build (resume if stale), then run eval.
param(
    [string]$Root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [int]$PollSeconds = 120
)

Set-Location $Root
$dataDir = if ($env:BOOKS_RAG_DATA_DIR) { $env:BOOKS_RAG_DATA_DIR } else { "C:\books_rag" }
$progressPath = Join-Path $dataDir "build_progress.json"
$lockPath = Join-Path $dataDir ".build.lock"
$buildPy = Join-Path $Root "40_operations\scripts\build_books_rag_index.py"
$evalPy = Join-Path $Root "40_operations\scripts\books_rag_eval.py"

function Get-Progress {
    if (-not (Test-Path $progressPath)) { return $null }
    return Get-Content $progressPath -Raw | ConvertFrom-Json
}

function Test-LockAlive {
    if (-not (Test-Path $lockPath)) { return $false }
    try {
        $lock = Get-Content $lockPath -Raw | ConvertFrom-Json
        $buildPid = [int]$lock.pid
        $out = & tasklist /FI "PID eq $buildPid" 2>$null
        return ($out -match [string]$buildPid) -and ($out -notmatch "No tasks")
    } catch { return $false }
}

Write-Host "[books_rag_wait] monitoring $progressPath"
while ($true) {
    $p = Get-Progress
    if ($p -and $p.files_total -gt 0 -and $p.files_done -ge $p.files_total) {
        Write-Host "[books_rag_wait] complete: $($p.files_done)/$($p.files_total)"
        break
    }
    $alive = Test-LockAlive
    $done = if ($p) { $p.files_done } else { 0 }
    $total = if ($p) { $p.files_total } else { "?" }
    Write-Host "[books_rag_wait] progress $done/$total lock_alive=$alive"
    if (-not $alive) {
        Write-Host "[books_rag_wait] resuming incremental build..."
        python $buildPy --root $Root --max-files 100
        if ($LASTEXITCODE -eq 2) {
            Write-Host "[books_rag_wait] lock held; retry in $PollSeconds s"
        }
    }
    Start-Sleep -Seconds $PollSeconds
}

Write-Host "[books_rag_wait] running eval..."
python $evalPy
exit $LASTEXITCODE
