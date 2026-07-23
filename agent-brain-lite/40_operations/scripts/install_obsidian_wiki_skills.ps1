# Install ar9av/obsidian-wiki skills into .cursor/skills/ via directory junctions (Windows).
# Idempotent: skips existing junctions pointing at the same target; re-links stale links.
# Usage: powershell -ExecutionPolicy Bypass -File 40_operations/scripts/install_obsidian_wiki_skills.ps1

param(
    [string]$RepoRoot = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

$UpstreamSkills = Join-Path $RepoRoot "90_archive\imports\obsidian-wiki_2026-05\obsidian-wiki\.skills"
$CursorSkills = Join-Path $RepoRoot ".cursor\skills"

if (-not (Test-Path $UpstreamSkills)) {
    Write-Error "Upstream .skills not found: $UpstreamSkills. Run git clone per IMPORT_MANIFEST.md first."
}

New-Item -ItemType Directory -Path $CursorSkills -Force | Out-Null

$installed = 0
$skipped = 0
$failed = @()

Get-ChildItem -Path $UpstreamSkills -Directory | ForEach-Object {
    $name = $_.Name
    $target = $_.FullName
    $link = Join-Path $CursorSkills $name

    if (Test-Path $link) {
        $item = Get-Item $link -Force
        $targetOk = ($item.LinkType -eq "Junction") -and ($item.Target -contains $target)
        $staleOneDrive = ($item.LinkType -eq "Junction") -and (($item.Target -join ";") -match "OneDrive")
        if ($targetOk -and -not $staleOneDrive) {
            $skipped++
            return
        }
        if ($Force -or $staleOneDrive) {
            if ($staleOneDrive) {
                Write-Host "Re-linking stale OneDrive junction: $name"
            }
            Remove-Item $link -Recurse -Force
        } else {
            Write-Warning "Skip $name (exists and not a matching junction; use -Force to replace)"
            $skipped++
            return
        }
    }

    try {
        cmd /c mklink /J "`"$link`"" "`"$target`"" | Out-Null
        $installed++
        Write-Host "Linked: $name"
    } catch {
        $failed += $name
        Write-Warning "Junction failed for $name : $_"
    }
}

Write-Host ""
Write-Host "Done. Installed: $installed  Skipped: $skipped  Failed: $($failed.Count)"
if ($failed.Count -gt 0) {
    Write-Host "Failed skills: $($failed -join ', ')"
    Write-Host "Try: run PowerShell as Administrator, or enable Developer Mode for symlinks."
    exit 1
}

exit 0
