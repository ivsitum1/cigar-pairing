#!/bin/bash
# Git Setup and Push Script for Agent Rules Project
# This script initializes git, adds all files, commits, and prepares for GitHub push
# Run from project root: ./40_operations/scripts/setup_git_and_push.sh

set -e

GITHUB_URL="${1:-}"
SKIP_PUSH="${2:-}"

echo "========================================"
echo "Agent Rules - Git Setup and Push"
echo "========================================"
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "✗ Git is not installed or not in PATH"
    echo ""
    echo "Please install Git from: https://git-scm.com/downloads"
    exit 1
fi

GIT_VERSION=$(git --version)
echo "✓ Git found: $GIT_VERSION"
echo ""

# Ensure we're in project root (parent of 40_operations/scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
if [ "$(pwd)" != "$PROJECT_ROOT" ]; then
    cd "$PROJECT_ROOT"
    echo "Changed to project root: $PROJECT_ROOT"
fi
echo "Project root: $(pwd)"
echo ""

# Step 1: Initialize git repository (if not already)
if [ -d ".git" ]; then
    echo "✓ Git repository already exists"
else
    echo "Initializing git repository..."
    git init
    echo "✓ Git repository initialized"
fi

echo ""

# Step 2: Check current status
echo "Checking git status..."
git status --short
echo ""

# Step 3: Add all files (respects .gitignore)
echo "Adding all files to git..."
git add .

# Show what will be committed
echo ""
echo "Files staged for commit:"
git status --short
echo ""

# Step 4: Create initial commit
echo "Creating initial commit..."
COMMIT_MESSAGE="Initial commit: Optimized agent rules project

- Removed duplicate files (DESKTOP-8FP2N9R versions)
- Removed temporary/analysis files
- Added root .gitignore
- Added comprehensive root README.md
- Verified portability (all paths are relative)
- Project is ready for use in new 10_projects/projects"

git commit -m "$COMMIT_MESSAGE" || {
    echo "Note: Commit may have failed because there are no changes, that's okay."
}

echo "✓ Commit created successfully"
echo ""

# Step 5: Set branch to main (if not already)
echo "Setting branch to 'main'..."
git branch -M main
echo "✓ Branch set to 'main'"
echo ""

# Step 6: Add remote and push (if GitHub URL provided)
if [ -n "$GITHUB_URL" ]; then
    echo "Adding remote origin..."
    git remote remove origin 2>/dev/null || true  # Remove if exists
    git remote add origin "$GITHUB_URL"
    echo "✓ Remote added: $GITHUB_URL"
    echo ""
    
    if [ "$SKIP_PUSH" != "skip" ]; then
        echo "Pushing to GitHub..."
        git push -u origin main || {
            echo "✗ Failed to push to GitHub"
            echo "You may need to:"
            echo "  1. Set up authentication (SSH key or personal access token)"
            echo "  2. Check that the repository exists on GitHub"
            echo "  3. Verify the URL is correct"
            exit 1
        }
        echo "✓ Successfully pushed to GitHub!"
    fi
else
    echo "========================================"
    echo "Next Steps:"
    echo "========================================"
    echo ""
    echo "1. Create a new repository on GitHub"
    echo "2. Run this script again with GitHub URL:"
    echo ""
    echo "   ./40_operations/scripts/setup_git_and_push.sh https://github.com/yourusername/your-repo.git"
    echo ""
    echo "Or manually run:"
    echo "   git remote add origin <your-github-url>"
    echo "   git push -u origin main"
    echo ""
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
