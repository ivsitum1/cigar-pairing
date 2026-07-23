# Post-commit: append to auto changelog only (no amend — avoids recursive hook loops).
# Install: copy to .git/hooks/post-commit or use Git Bash with post-commit-hook.sh
#
# Skip hook: $env:SKIP_CHANGELOG = '1'; git commit --amend --no-edit; Remove-Item Env:SKIP_CHANGELOG

Set-Location (git rev-parse --show-toplevel)

if ($env:SKIP_CHANGELOG) {
    exit 0
}

if (Get-Command python3 -ErrorAction SilentlyContinue) {
    python3 40_operations/scripts/changelog_auto.py
} else {
    python 40_operations/scripts/changelog_auto.py
}
