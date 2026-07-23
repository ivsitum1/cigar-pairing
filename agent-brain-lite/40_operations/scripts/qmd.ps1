# Windows wrapper for QMD (bypasses broken npm qmd.ps1 /bin/sh launcher).
param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Args)

$node = "C:\Program Files\nodejs\node.exe"
if (-not (Test-Path $node)) {
    $node = (Get-Command node -ErrorAction SilentlyContinue).Source
}
$qmdJs = Join-Path $env:APPDATA "npm\node_modules\@tobilu\qmd\dist\cli\qmd.js"
if (-not (Test-Path $qmdJs)) {
    Write-Error "QMD not installed. Run: npm install -g @tobilu/qmd"
    exit 1
}
& $node $qmdJs @Args
exit $LASTEXITCODE
