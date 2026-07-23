# Runbook — Git History Purge (restore portability)

> Status: **pending user execution.** The automated harness blocks history
> rewrites, so this step must be run manually by the repo owner.

## Why

`.git` is ~2.6 GB and the working tree ~5.8 GB because large PDFs/e-books and
archived data blobs (40–96 MB each) were committed then deleted — they live on
in history forever. This contradicts the README's core "just copy the folder,
it's portable" promise and makes clones slow. The current tracked tree is clean
(largest file ~5 MB); only history carries the bloat.

## One-time fix

`git-filter-repo` is already installed (`pip show git-filter-repo`). Run from the
repo root:

```bash
# 1. Fresh backup that includes the latest fixes (the session bundle predates them)
git bundle create ../agent-rules-backup-$(date +%Y%m%d-%H%M%S).bundle --all

# 2. Strip every blob over 10 MB from all history (no current file exceeds ~5 MB)
python -m git_filter_repo --strip-blobs-bigger-than 10M --force

# 3. Reclaim space
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# 4. Confirm (.git should drop from ~2.6 GB to <100 MB)
du -sh .git
```

filter-repo removes the `origin` remote as a safety measure. Re-add and, when
ready, publish the rewritten history:

```bash
git remote add origin https://github.com/ivsitum1/agent-rules.git
git push --force-with-lease origin master
```

> ⚠️ `--force` push rewrites remote history. This repo is single-owner
> (`ivsitum1`), so that is safe here, but any existing clones must re-clone
> afterwards rather than pull.

## Keep it from coming back

Already in place after the 2026-07-05 remediation:
- `.gitignore` blocks new PDFs/e-books/binaries.
- Pre-commit `check-added-large-files` (10 MB cap) — enable with
  `pip install pre-commit && pre-commit install`.

## Where the big files should live instead

PDFs/e-books stay on disk (already gitignored) or move to an external store
(DVC / git-annex) referenced by a manifest, so the graph keeps pointers without
versioning the binaries.

## Recovery

If anything goes wrong, restore from the bundle:

```bash
git clone ../agent-rules-backup-<stamp>.bundle recovered-repo
```
