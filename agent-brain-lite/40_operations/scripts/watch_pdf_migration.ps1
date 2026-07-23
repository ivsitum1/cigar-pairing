# Watchdog: every 15 min — detect stuck OCR, mark PDF failed, restart batch with --resume.
param(
    [string]$Root = ".",
    [int]$IntervalMinutes = 15,
    [int]$StaleMinutes = 75,
    [switch]$Once,
    [switch]$AutoKillStuck = $true
)

$ErrorActionPreference = "Continue"
$Repo = (Resolve-Path (Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) $Root)).Path
$LogDir = Join-Path $Repo "data\pdf_extract"
$WatchLog = Join-Path $LogDir "watchdog.log"
$StatePath = Join-Path $LogDir "watchdog_state.json"
$ExtractPs1 = Join-Path $Repo "40_operations\scripts\extract_pdf_ocr.ps1"
$SkipPy = Join-Path $Repo "40_operations\scripts\skip_stuck_pdf.py"
$Py = Join-Path $Repo ".venv-ocr\Scripts\python.exe"
if (-not (Test-Path $Py)) { $Py = "python" }

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

$env:PADDLE_OCR_DEVICE = "gpu"
$env:FLAGS_use_mkldnn = "0"
$env:FLAGS_use_onednn = "0"
$env:FLAGS_enable_mkldnn = "0"

function Write-WatchLog([string]$Msg, [string]$Level = "INFO") {
    $line = "[{0:yyyy-MM-dd HH:mm:ss}] [{1}] {2}" -f (Get-Date), $Level, $Msg
    Write-Host $line
    Add-Content -Path $WatchLog -Value $line -Encoding utf8
}

function Get-WatchState {
    if (Test-Path $StatePath) {
        try { return Get-Content $StatePath -Raw | ConvertFrom-Json } catch { }
    }
    return [PSCustomObject]@{
        last_newest_md_utc = $null
        last_progress_count = 0
        stale_checks = 0
        last_action = ""
        last_md_name = ""
    }
}

function Save-WatchState($s) {
    $s | ConvertTo-Json | Set-Content -Path $StatePath -Encoding utf8
}

function Get-ExtractProcs {
    @(Get-CimInstance Win32_Process -Filter "name='python.exe'" -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match 'extract_pdf_library_to_md\.py' })
}

function Get-ActivePrefix($procs) {
    foreach ($p in $procs) {
        if ($p.CommandLine -match '--only-prefix\s+(\S+)') {
            return $Matches[1]
        }
    }
    return $null
}

function Get-NewestMdInfo {
    $books = Join-Path $Repo "20_knowledge\wiki\sources\books_md"
    if (-not (Test-Path $books)) { return $null }
    $f = Get-ChildItem $books -Recurse -Filter *.md -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne "INDEX.md" } |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if (-not $f) { return $null }
    [PSCustomObject]@{
        Path = $f.FullName
        Name = $f.Name
        LastWrite = $f.LastWriteTime
        IsFailedStub = $f.Name -like "*_EXTRACTION_FAILED.md"
    }
}

function Get-RagBuildInfo {
    . (Join-Path $Repo "40_operations\scripts\_books_rag_paths.ps1")
    $lock = Join-Path $BooksRagDataDir ".build.lock"
    $prog = Join-Path $BooksRagDataDir "build_progress.json"
    if (-not (Test-Path $lock)) { return $null }
    $info = [PSCustomObject]@{ LockPath = $lock; LockAgeMin = 0; BuildPid = $null; FilesDone = 0; FilesTotal = 0 }
    try {
        $lockJson = Get-Content $lock -Raw | ConvertFrom-Json
        $info.BuildPid = $lockJson.pid
    } catch { }
    $info.LockAgeMin = ((Get-Date) - (Get-Item $lock).LastWriteTime).TotalMinutes
    if (Test-Path $prog) {
        try {
            $bp = Get-Content $prog -Raw | ConvertFrom-Json
            $info.FilesDone = [int]$bp.files_done
            $info.FilesTotal = [int]$bp.files_total
        } catch { }
    }
    $alive = $false
    if ($info.BuildPid) {
        $alive = $null -ne (Get-Process -Id $info.BuildPid -ErrorAction SilentlyContinue)
    }
    $info | Add-Member -NotePropertyName BuildAlive -NotePropertyValue $alive -Force
    return $info
}

function Get-ProgressCount {
    $p = Join-Path $Repo "data\pdf_extract\progress.json"
    if (-not (Test-Path $p)) { return 0 }
    try {
        return @((Get-Content $p -Raw | ConvertFrom-Json).entries.PSObject.Properties).Count
    } catch { return 0 }
}

function Restart-ExtractBatch([string]$Prefix) {
    if (-not $Prefix) { return }
    Write-WatchLog "Restart extract: $Prefix (background, --resume)" "ACTION"
    $argList = @(
        "-NoProfile", "-ExecutionPolicy", "Bypass",
        "-File", $ExtractPs1,
        "-Root", $Repo,
        "-Ocr", "paddle",
        "-OnlyPrefix", $Prefix,
        "-ForceOcr",
        "-PruneStale",
        "-Resume",
        "-Report", "auto"
    )
    Start-Process powershell -ArgumentList $argList -WindowStyle Hidden -WorkingDirectory $Repo
}

function Invoke-WatchCheck {
    $state = Get-WatchState
    $procs = Get-ExtractProcs
    $md = Get-NewestMdInfo
    $prog = Get-ProgressCount
    $gpu = (nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader 2>$null)
    $prefix = Get-ActivePrefix $procs
    $issues = @()

    $mdStale = $false
    $mdAgeMin = 0
    if ($md) {
        $mdAgeMin = ((Get-Date) - $md.LastWrite).TotalMinutes
        if ($procs.Count -gt 0 -and $mdAgeMin -ge $StaleMinutes) {
            $mdStale = $true
            $issues += "STALE: nema novog .md ${mdAgeMin} min (zadnji: $($md.Name))"
        }
    }

    if ($procs.Count -gt 0 -and $state.last_progress_count -eq $prog -and $prog -gt 0) {
        $state.stale_checks = [int]$state.stale_checks + 1
        if ($state.stale_checks -ge 2) {
            $issues += "STALE: progress.json=$prog nepromijenjen 2+ provjere (30+ min)"
        }
    } else {
        $state.stale_checks = 0
    }

    if ($procs.Count -gt 2) {
        $issues += "WARN: $($procs.Count) extract procesa"
    }

  # Stale progress + stale md together => kill even if last md is not EXTRACTION_FAILED (v1 gap)
    if ($procs.Count -gt 0 -and $mdStale -and $state.stale_checks -ge 2) {
        $issues += "STALE: kombinacija md+progress (preskoci PDF)"
    }

    $rag = Get-RagBuildInfo
    if ($rag) {
        Write-WatchLog "RAG lock age=$([math]::Round($rag.LockAgeMin,0))m done=$($rag.FilesDone)/$($rag.FilesTotal) alive=$($rag.BuildAlive)" "INFO"
        if (-not $rag.BuildAlive -and $rag.LockAgeMin -ge 30) {
            $issues += "RAG: .build.lock bez zivog procesa ($([math]::Round($rag.LockAgeMin,0)) min); ukloni lock i ponovi build"
            if ($AutoKillStuck) {
                Remove-Item $rag.LockPath -Force -ErrorAction SilentlyContinue
                Write-WatchLog "Removed stale $BooksRagDataDir\.build.lock" "ACTION"
                $RagPy = if (Get-Command python -ErrorAction SilentlyContinue) { "python" } else { "py" }
                $ragLog = Join-Path $BooksRagDataDir "rag_rebuild_watchdog.log"
                Start-Process powershell -ArgumentList @(
                    "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                    "Set-Location '$Repo'; `$env:BOOKS_RAG_DATA_DIR='$BooksRagDataDir'; & '$RagPy' '$Repo\40_operations\scripts\build_books_rag_index.py' --root '$Repo' --force *> '$ragLog'"
                ) -WindowStyle Hidden
                Write-WatchLog "Started RAG --force in background (rag_rebuild_watchdog.log)" "ACTION"
            }
        }
    }

    if ($procs.Count -eq 0) {
        Write-WatchLog "IDLE: nema OCR procesa (migracija OCR vjerojatno gotova). progress=$prog mdAge=${mdAgeMin}m (starost zadnjeg .md na disku)" "INFO"
    } else {
        Write-WatchLog "check OCR=$($procs.Count) gpu=$gpu progress=$prog prefix=$prefix mdAge=${mdAgeMin}m" "INFO"
    }

    foreach ($i in $issues) { Write-WatchLog $i "WARN" }

    $shouldSkip = $AutoKillStuck -and $mdStale -and $procs.Count -gt 0

    if ($shouldSkip) {
        if (-not $prefix) { $prefix = "00_inbox/raw" }
        foreach ($p in $procs) {
            Stop-Process -Id $p.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Write-WatchLog "Killed $($procs.Count) extract procesa; preskacem zaglavljeni PDF" "ACTION"

        $skipArgs = @($SkipPy, "--root", $Repo, "--only-prefix", $prefix, "--from-newest-md",
            "--reason", "watchdog stale ${mdAgeMin}m, skip to continue pipeline")
        & $Py @skipArgs 2>&1 | ForEach-Object { Write-WatchLog $_ "SKIP" }

        Start-Sleep -Seconds 3
        Restart-ExtractBatch $prefix
        $state.last_action = "skip_restart_${prefix}_$(Get-Date -Format 'yyyy-MM-dd_HHmm')"
        $state.stale_checks = 0

        & $Py (Join-Path $Repo "40_operations\scripts\report_pdf_migration.py") --root $Repo 2>&1 | Out-Null
    }

    if ($md) {
        $state | Add-Member -NotePropertyName last_newest_md_utc -NotePropertyValue $md.LastWrite.ToString("o") -Force
        $state | Add-Member -NotePropertyName last_md_name -NotePropertyValue $md.Name -Force
    }
    $state | Add-Member -NotePropertyName last_progress_count -NotePropertyValue $prog -Force
    Save-WatchState $state
}

# Stop older 30-min watchdog instances (same script, different interval in cmdline)
Get-CimInstance Win32_Process -Filter "name='powershell.exe'" -ErrorAction SilentlyContinue |
    Where-Object {
        $_.CommandLine -match 'watch_pdf_migration\.ps1' -and
        $_.CommandLine -notmatch "IntervalMinutes\s+15" -and
        $_.ProcessId -ne $PID
    } |
    ForEach-Object {
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
        Write-WatchLog "Stopped old watchdog PID $($_.ProcessId)" "INFO"
    }

Write-WatchLog "Watchdog v2 interval=${IntervalMinutes}m stale=${StaleMinutes}m repo=$Repo"

$Marker = Join-Path $LogDir "migration_pipeline_complete.marker"

do {
    Invoke-WatchCheck
    # Stop watchdog loop when OCR done and no RAG lock (saves noise); user can restart manually
    $ragNow = Get-RagBuildInfo
    $ocrOff = (@(Get-ExtractProcs)).Count -eq 0
    if ($ocrOff -and (-not $ragNow) -and (Test-Path $Marker)) {
        Write-WatchLog "Pipeline complete marker present; watchdog exiting." "INFO"
        break
    }
    if ($ocrOff -and (-not $ragNow) -and -not (Test-Path $Marker)) {
        $ingestDone = Select-String -Path (Join-Path $LogDir "background_migration_*.log") -Pattern "ingest_pdf_sources" -Quiet
        . (Join-Path $Repo "40_operations\scripts\_books_rag_paths.ps1")
        $ragLog = Join-Path $BooksRagDataDir "rag_rebuild_watchdog.log"
        $ragRunning = Test-Path $ragLog -and ((Get-Item $ragLog).LastWriteTime -gt (Get-Date).AddMinutes(-120))
        if ($ingestDone -and -not $ragRunning) {
            Set-Content -Path $Marker -Value (Get-Date).ToString("o") -Encoding utf8
            Write-WatchLog "Created migration_pipeline_complete.marker (OCR+ingest done, RAG idle)" "INFO"
            break
        }
    }
    if ($Once) { break }
    Start-Sleep -Seconds ($IntervalMinutes * 60)
} while ($true)
