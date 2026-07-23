# Git Worktree – Parallel agents and feature branching

**Purpose:** Isolate each parallel agent in its own checkout directory. They share the `.git` object database – no disk space duplication.

---

## When to use

- Parallel development of multiple feature branches (one agent per branch)
- Avoiding overwrite conflicts and test collisions
- Each agent in its own isolated folder

---

## Creating a worktree

### Windows (PowerShell)

```powershell
.\40_operations/scripts\worktree_add.ps1 -Branch feature/xyz -Path ..\agent-rules-feature-xyz
```

### Linux / Mac

```bash
./40_operations/scripts/worktree_add.sh -b feature/xyz -p ../agent-rules-feature-xyz
```

**Result:** New directory with checkout of branch `feature/xyz`. Symlink `.env` → main repo. If project uses DB, `.env.local` is created with `DB_NAME=project_test_<branch>` for test isolation.

---

## Symlinks

| File       | What it does                                      |
|------------|---------------------------------------------------|
| `.env`     | Symlink to main repo `.env` – single source of secrets |
| `.env.local` | Local override; `DB_NAME` for DB isolation      |

**Note:** Update main `.env` once; all worktrees immediately inherit the change.

---

## DB isolation

If the project has automated tests that use a database:

- In each worktree set `DB_NAME=project_test_<branch>` in `.env.local`
- Scripts automatically create `.env.local` with that name
- Each agent runs tests in its own database – no collisions

---

## Removing a worktree

### Before removing

1. Finish work on the branch
2. Merge to main (squash-and-merge recommended)
3. Close Cursor/IDE in that worktree

### Commands

```powershell
# Windows – list worktrees
.\40_operations/scripts\worktree_cleanup.ps1

# Windows – remove one
.\40_operations/scripts\worktree_cleanup.ps1 -Remove ..\agent-rules-feature-xyz
```

```bash
# Linux/Mac – list
./40_operations/scripts/worktree_cleanup.sh

# Linux/Mac – remove one
./40_operations/scripts/worktree_cleanup.sh -r ../agent-rules-feature-xyz
```

After removal: `git worktree prune` cleans internal references.

## Related Hubs

- [Folder index hub](FOLDER_INDEX.md)
- [All notes index](ALL_NOTES_INDEX.md)
- [Graph connectivity map](GRAPH_CONNECTIVITY_MAP.md)
