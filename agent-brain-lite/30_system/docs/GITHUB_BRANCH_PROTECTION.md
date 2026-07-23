# GitHub Branch Protection (master)

**Purpose:** Prevent accidental force-push or direct commits that could break the shared agent-rules brain.

## Setup (manual, GitHub UI)

1. Open repository **Settings** → **Branches** → **Add branch ruleset** (or classic rule).
2. Branch name pattern: `master`
3. Enable:
   - **Require a pull request before merging** (0 reviews OK for solo maintainer)
   - **Do not allow bypassing the above settings**
   - **Block force pushes**
   - **Restrict who can push** (optional: only repository owner)
4. Save.

## Solo workflow

- Create feature branch → PR → merge (self-review).
- Emergency hotfix: still use PR; avoids `git push --force` on `master`.

## Related

- [GIT_SETUP.md](GIT_SETUP.md)
- [BRAIN_AND_PROJECT.md](BRAIN_AND_PROJECT.md)

**Last updated:** 2026-06-28
