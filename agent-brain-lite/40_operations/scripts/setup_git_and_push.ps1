# Git Setup and Push Script for Agent Rules Project
# This script initializes git, adds all files, commits, and prepares for GitHub push
# Run from project root: .\40_operations/scripts\setup_git_and_push.ps1

param(
    [string]$GitHubUrl = "",
    [switch]$SkipPush = $false
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Agent Rules - Git Setup and Push" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "✓ Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git from: https://git-scm.com/download/win" -ForegroundColor Yellow
    Write-Host "Or add Git to your PATH environment variable" -ForegroundColor Yellow
    exit 1
}

# Ensure we're in project root (parent of 40_operations/scripts/)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
if ((Get-Location).Path -ne $projectRoot) {
    Set-Location $projectRoot
    Write-Host "Changed to project root: $projectRoot" -ForegroundColor Gray
}
Write-Host "Project root: $projectRoot" -ForegroundColor Gray
Write-Host ""

# Step 1: Initialize git repository (if not already)
if (Test-Path ".git") {
    Write-Host "✓ Git repository already exists" -ForegroundColor Green
} else {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to initialize git repository" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Git repository initialized" -ForegroundColor Green
}

Write-Host ""

# Step 2: Check current status
Write-Host "Checking git status..." -ForegroundColor Yellow
git status --short
Write-Host ""

# Step 3: Add all files (respects .gitignore)
Write-Host "Adding all files to git..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to add files" -ForegroundColor Red
    exit 1
}

# Show what will be committed
Write-Host ""
Write-Host "Files staged for commit:" -ForegroundColor Cyan
git status --short
Write-Host ""

# Step 4: Create initial commit
Write-Host "Creating initial commit..." -ForegroundColor Yellow
$commitMessage = @"
Initial commit: Optimized agent rules project

- Removed duplicate files (DESKTOP-8FP2N9R versions)
- Removed temporary/analysis files
- Added root .gitignore
- Added comprehensive root README.md
- Verified portability (all paths are relative)
- Project is ready for use in new projects
"@

git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Failed to create commit" -ForegroundColor Red
    Write-Host "Note: If commit failed because there are no changes, that's okay." -ForegroundColor Yellow
} else {
    Write-Host "✓ Commit created successfully" -ForegroundColor Green
}

Write-Host ""

# Step 5: Set branch to main (if not already)
Write-Host "Setting branch to 'main'..." -ForegroundColor Yellow
git branch -M main
Write-Host "✓ Branch set to 'main'" -ForegroundColor Green
Write-Host ""

# Step 6: Add remote and push (if GitHub URL provided)
if ($GitHubUrl -ne "") {
    Write-Host "Adding remote origin..." -ForegroundColor Yellow
    git remote remove origin 2>$null  # Remove if exists
    git remote add origin $GitHubUrl
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to add remote" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Remote added: $GitHubUrl" -ForegroundColor Green
    Write-Host ""
    
    if (-not $SkipPush) {
        Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
        git push -u origin main
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Failed to push to GitHub" -ForegroundColor Red
            Write-Host "You may need to:" -ForegroundColor Yellow
            Write-Host "  1. Set up authentication (SSH key or personal access token)" -ForegroundColor Yellow
            Write-Host "  2. Check that the repository exists on GitHub" -ForegroundColor Yellow
            Write-Host "  3. Verify the URL is correct" -ForegroundColor Yellow
            exit 1
        }
        Write-Host "✓ Successfully pushed to GitHub!" -ForegroundColor Green
    }
} else {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Next Steps:" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Create a new repository on GitHub" -ForegroundColor Yellow
    Write-Host "2. Run this script again with GitHub URL:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   .\40_operations/scripts\setup_git_and_push.ps1 -GitHubUrl 'https://github.com/yourusername/your-repo.git'" -ForegroundColor White
    Write-Host ""
    Write-Host "Or manually run:" -ForegroundColor Yellow
    Write-Host "   git remote add origin <your-github-url>" -ForegroundColor White
    Write-Host "   git push -u origin main" -ForegroundColor White
    Write-Host ""
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
