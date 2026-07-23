# setup_mcp.ps1 – Copy project MCP config to global Cursor config
# Run from repo root. Merges .cursor/mcp.json into %APPDATA%\Cursor\mcp.json

$ErrorActionPreference = "Stop"
$ProjectRoot = (Get-Location).Path
$ProjectMcp = Join-Path $ProjectRoot ".cursor\mcp.json"
$GlobalMcp = Join-Path $env:APPDATA "Cursor\mcp.json"

if (-not (Test-Path $ProjectMcp)) {
    Write-Error "Not found: $ProjectMcp. Run from repo root."
}

# Load project config (raw JSON for merge)
$projectJson = Get-Content $ProjectMcp -Raw
$projectConfig = $projectJson | ConvertFrom-Json

# Resolve filesystem --root to absolute path
if ($projectConfig.mcpServers.filesystem) {
    $fsArgs = @($projectConfig.mcpServers.filesystem.args)
    $idx = [array]::IndexOf($fsArgs, "--root")
    if ($idx -ge 0 -and $idx + 1 -lt $fsArgs.Count) {
        $fsArgs[$idx + 1] = $ProjectRoot
        $projectConfig.mcpServers.filesystem.args = $fsArgs
    }
}

# Load or create global config
if (Test-Path $GlobalMcp) {
    $globalJson = Get-Content $GlobalMcp -Raw
    $globalConfig = $globalJson | ConvertFrom-Json
} else {
    $globalConfig = [PSCustomObject]@{ mcpServers = [PSCustomObject]@{} }
}

# Merge project servers
$merged = @{}
if ($globalConfig.mcpServers) {
    $globalConfig.mcpServers.PSObject.Properties | ForEach-Object { $merged[$_.Name] = $_.Value }
}
$projectConfig.mcpServers.PSObject.Properties | ForEach-Object { $merged[$_.Name] = $_.Value }
$globalConfig.mcpServers = [PSCustomObject]$merged

$globalDir = Split-Path $GlobalMcp -Parent
if (-not (Test-Path $globalDir)) { New-Item -ItemType Directory -Path $globalDir -Force | Out-Null }
$globalConfig | ConvertTo-Json -Depth 10 | Set-Content $GlobalMcp -Encoding UTF8 -NoNewline:$false
Write-Host "MCP config merged to $GlobalMcp" -ForegroundColor Green
Write-Host "Set NCBI_API_KEY in env for PubMed. Restart Cursor." -ForegroundColor Cyan
