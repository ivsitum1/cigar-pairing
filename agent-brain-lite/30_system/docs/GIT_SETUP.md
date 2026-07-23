# Git Setup and GitHub Push Instructions

## Quick Setup

### Windows (PowerShell)

```powershell
# Run the setup script (from project root)
.\40_operations/scripts\setup_git_and_push.ps1

# Or with GitHub URL (if you already created the repository)
.\40_operations/scripts\setup_git_and_push.ps1 -GitHubUrl "https://github.com/yourusername/your-repo.git"
```

### Linux/Mac (Bash)

```bash
# Make script executable (once)
chmod +x 40_operations/scripts/setup_git_and_push.sh

# Run the setup script (from project root)
./40_operations/scripts/setup_git_and_push.sh

# Or with GitHub URL (if you already created the repository)
./40_operations/scripts/setup_git_and_push.sh "https://github.com/yourusername/your-repo.git"
```

## Manual Setup

If you prefer to do it manually or the script doesn't work:

### 1. Initialize Git Repository

```bash
git init
```

### 2. Add All Files

```bash
git add .
```

This will respect the `.gitignore` file and won't add:
- PDF files from reference_library
- Python cache files
- Test artifacts
- OS files
- Virtual environments
- Temporary files

### 3. Create Initial Commit

```bash
git commit -m "Initial commit: Optimized agent rules project

- Removed duplicate files (DESKTOP-8FP2N9R versions)
- Removed temporary/analysis files
- Added root .gitignore
- Added comprehensive root README.md
- Verified portability (all paths are relative)
- Project is ready for use in new 10_projects/projects"
```

### 4. Set Branch to Main

```bash
git branch -M main
```

### 5. Create GitHub Repository

1. Go to [GitHub](https://github.com)
2. Click "New repository"
3. Name it (e.g., "agent-rules")
4. **Don't** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"

### 6. Add Remote and Push

```bash
# Add remote (replace with your GitHub URL)
git remote add origin https://github.com/yourusername/your-repo.git

# Push to GitHub
git push -u origin main
```

## Authentication

If you get authentication errors:

### Option 1: Personal Access Token (Recommended)

1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with `repo` scope
3. Use token as password when pushing

### Option 2: SSH Key

1. Generate SSH key: `ssh-keygen -t ed25519 -C "your_email@example.com"`
2. Add to GitHub: Settings → SSH and GPG keys → New SSH key
3. Use SSH URL: `git@github.com:yourusername/your-repo.git`

## What Gets Pushed

The `.gitignore` file ensures that:

✅ **Will be pushed:**
- All markdown files (rules, documentation)
- Python scripts
- Configuration files (pytest.ini, requirements.txt)
- JSON metadata files
- Test files
- Setup scripts

❌ **Will NOT be pushed:**
- PDF files (too large, copyright)
- Python cache (`__pycache__/`, `*.pyc`)
- Test artifacts (`.pytest_cache/`, coverage reports)
- OS files (`.DS_Store`, `Thumbs.db`)
- Virtual environments
- Temporary files

## Verification

After pushing, verify on GitHub:

1. Check that all expected files are there
2. Verify README.md displays correctly
3. Check that PDF files are NOT there (as intended)
4. Verify folder structure is correct

## Troubleshooting

### "Git is not recognized"

**Solution:** Install Git from [https://git-scm.com/downloads](https://git-scm.com/downloads)

### "Authentication failed"

**Solution:** Set up authentication (see Authentication section above)

### "Repository not found"

**Solution:** 
- Make sure the repository exists on GitHub
- Check the URL is correct
- Verify you have access to the repository

### "Nothing to commit"

**Solution:** This is normal if you've already committed. Check with `git status` to see current state.

## Next Steps After Push

1. ✅ Verify all files are on GitHub
2. ✅ Check README displays correctly
3. ✅ Add repository description on GitHub
4. ✅ Add topics/tags (e.g., "ai", "agent-rules", "scientific-writing")
5. ✅ Consider adding a LICENSE file
6. ✅ Set up GitHub Actions for CI/CD (optional)

---

**Note:** This project is designed to be portable. You can copy the entire folder to any new project and it will work automatically.

## Semantic graph (auto)

- [[Behavior rules hub]]
- [30 system INDEX](indexes/30_system_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)
- [FOLDER INDEX](FOLDER_INDEX.md)

## Semantic neighbors (embedding)

- [[SKILL_setup-project]]
- [[SKILL_validate-setup]]
- [[SKILL_skill-discovery]]
- [[13_agentic_workflow]]
- [[09_workflow_optimization]]
