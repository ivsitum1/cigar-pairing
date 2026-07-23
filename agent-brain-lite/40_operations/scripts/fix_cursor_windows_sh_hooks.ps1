# fix_cursor_windows_sh_hooks.ps1
# Re-apply Windows-safe .cmd wrappers for Cursor plugin hooks that point at .sh files.
# Run after Cursor plugin updates if .sh files open in the editor again on chat/session start.
# Usage: powershell -NoProfile -ExecutionPolicy Bypass -File 40_operations/scripts/fix_cursor_windows_sh_hooks.ps1

$ErrorActionPreference = "Stop"
$pluginRoot = Join-Path $env:USERPROFILE ".cursor\plugins\cache\cursor-public"

function Write-BashWrapperCmd {
    param(
        [string]$TargetPath,
        [string]$ShFileName
    )
    $content = @"
@echo off
REM Windows wrapper: run $ShFileName via Git Bash (avoids opening .sh in editor)
set "SCRIPT_DIR=%~dp0"
if exist "C:\Program Files\Git\bin\bash.exe" (
    "C:\Program Files\Git\bin\bash.exe" "%SCRIPT_DIR%$ShFileName" %*
    exit /b %ERRORLEVEL%
)
if exist "C:\Program Files (x86)\Git\bin\bash.exe" (
    "C:\Program Files (x86)\Git\bin\bash.exe" "%SCRIPT_DIR%$ShFileName" %*
    exit /b %ERRORLEVEL%
)
where bash >nul 2>nul
if %ERRORLEVEL% equ 0 (
    bash "%SCRIPT_DIR%$ShFileName" %*
    exit /b %ERRORLEVEL%
)
exit /b 0
"@
    Set-Content -Path $TargetPath -Value $content -Encoding ASCII
}

function Get-LatestPluginDir {
    param([string]$Name)
    $base = Join-Path $pluginRoot $Name
    if (-not (Test-Path $base)) { return $null }
    Get-ChildItem $base -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
}

$fixed = @()

function Set-SuperpowersHooksCursor {
    param([string]$HooksCursorPath)
    if (-not (Test-Path $HooksCursorPath)) { return }
    @{
        version = 1
        hooks   = @{
            sessionStart = @(
                @{ command = "./hooks/run-hook.cmd session-start" }
            )
        }
    } | ConvertTo-Json -Depth 6 | Set-Content -Path $HooksCursorPath -Encoding UTF8
    $script:fixed += "superpowers: $HooksCursorPath"
}

# Superpowers (Cursor plugin cache)
$sp = Get-LatestPluginDir "superpowers"
if ($sp) {
    Set-SuperpowersHooksCursor (Join-Path $sp.FullName "hooks\hooks-cursor.json")
}

# Superpowers (Claude Code cache — Cursor also loads these hooks on Windows)
$claudeSp = Join-Path $env:USERPROFILE ".claude\plugins\cache\claude-plugins-official\superpowers"
if (Test-Path $claudeSp) {
    Get-ChildItem $claudeSp -Directory | ForEach-Object {
        Set-SuperpowersHooksCursor (Join-Path $_.FullName "hooks\hooks-cursor.json")
    }
}

# Runlayer
$rl = Get-LatestPluginDir "runlayer"
if ($rl) {
    $cmd = Join-Path $rl.FullName "scripts\runlayer-hook.cmd"
    Write-BashWrapperCmd -TargetPath $cmd -ShFileName "runlayer-hook.sh"
    $hj = Join-Path $rl.FullName "hooks\hooks.json"
    if (Test-Path $hj) {
        @{
            hooks = @{
                sessionStart        = @(@{ command = "./scripts/runlayer-hook.cmd" })
                beforeMCPExecution  = @(@{ command = "./scripts/runlayer-hook.cmd" })
                beforeReadFile      = @(@{ command = "./scripts/runlayer-hook.cmd" })
            }
        } | ConvertTo-Json -Depth 6 | Set-Content -Path $hj -Encoding UTF8
        $fixed += "runlayer: $hj"
    }
}

# 1Password
$op = Get-LatestPluginDir "1password"
if ($op) {
    $cmd = Join-Path $op.FullName "scripts\validate-mounted-env-files.cmd"
    Write-BashWrapperCmd -TargetPath $cmd -ShFileName "validate-mounted-env-files.sh"
    $hj = Join-Path $op.FullName "hooks\hooks.json"
    if (Test-Path $hj) {
        @{
            version = 1
            hooks   = @{
                beforeShellExecution = @(
                    @{ command = "./scripts/validate-mounted-env-files.cmd" }
                )
            }
        } | ConvertTo-Json -Depth 6 | Set-Content -Path $hj -Encoding UTF8
        $fixed += "1password: $hj"
    }
}

if ($fixed.Count -eq 0) {
    Write-Host "No plugin hook folders found under $pluginRoot"
    exit 1
}

Write-Host "Patched hook configs:"
$fixed | ForEach-Object { Write-Host "  $_" }
Write-Host ""
Write-Host "Restart Cursor completely (File > Exit, then reopen)."
