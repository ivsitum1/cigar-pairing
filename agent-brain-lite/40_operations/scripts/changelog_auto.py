#!/usr/bin/env python3
"""
Automatically update changelog from Git commits.
Appends each commit to 30_system/docs/CHANGELOG_AUTO.md and 30_system/docs/CHANGELOG_AUTO.jsonl
so changes can always be reconstructed.

Usage:
  python 40_operations/scripts/changelog_auto.py           # log HEAD (e.g. from post-commit)
  python 40_operations/scripts/changelog_auto.py HEAD~5..  # log last 5 commits
  python 40_operations/scripts/changelog_auto.py --backfill # log all commits (first time)
  python 40_operations/scripts/changelog_auto.py --rewrite-md-from-jsonl  # rebuild .md sorted by date
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# Repo root = parent of 40_operations/scripts/
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CHANGELOG_MD = REPO_ROOT / "30_system/docs" / "CHANGELOG_AUTO.md"
CHANGELOG_JSONL = REPO_ROOT / "30_system/docs" / "CHANGELOG_AUTO.jsonl"


def run_git(*args: str, cwd: Path | None = None) -> str:
    cwd = cwd or REPO_ROOT
    r = subprocess.run(
        ["git"] + list(args),
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr or r.stdout}")
    return (r.stdout or "").strip()


def get_commit_info(rev: str) -> dict | None:
    try:
        hash_full = run_git("rev-parse", rev)
        short = run_git("rev-parse", "--short", rev)
        msg = run_git("show", "-s", "--format=%B", rev)
        date_iso = run_git("show", "-s", "--format=%cI", rev)
        # list of changed files (relative to repo root)
        names = run_git("diff-tree", "--no-commit-id", "--name-only", "-r", rev)
        files = [n.strip() for n in names.splitlines() if n.strip()]
        return {
            "hash": hash_full,
            "short": short,
            "message": msg.strip(),
            "date": date_iso,
            "files": files,
        }
    except Exception:
        return None


def get_commit_range(spec: str, oldest_first: bool = False) -> list[str]:
    """Return list of commit hashes. oldest_first=True for chronological order (backfill)."""
    args = ["rev-list", "--first-parent"]
    if oldest_first:
        args.append("--reverse")
    args.append(spec)
    out = run_git(*args)
    return [h.strip() for h in out.splitlines() if h.strip()]


def _parse_sort_datetime(date_str: str) -> datetime:
    if not date_str:
        return datetime.min.replace(tzinfo=timezone.utc)
    s = date_str.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)


def format_md_block(info: dict) -> str:
    """Single ## section for CHANGELOG_AUTO.md (matches append_entry_md / manual layout)."""
    date_short = info["date"][:10] if info.get("date") and len(info["date"]) >= 10 else (info.get("date") or "")
    msg = (info.get("message") or "").strip()
    first_line = (msg.split("\n")[0] if msg else "(no message)").strip()
    first_line_esc = first_line.replace("|", "\\|")
    short = info.get("short") or "manual"
    files = info.get("files") or []

    lines: list[str] = []
    lines.append(f"\n## {date_short} `{short}` — {first_line_esc}\n\n")

    if info.get("hash") is None:
        files_str = ", ".join(files) if files else "(none)"
        lines.append(f"- **Files:** {files_str}\n")
        src = info.get("source")
        if src:
            lines.append(f"- **Source:** `{src}`\n")
        lines.append("\n")
        return "".join(lines)

    files_str = ", ".join(files[:30])
    if len(files) > 30:
        files_str += f" (+{len(files) - 30} more)"
    lines.append(f"- **Files:** {files_str}\n\n")
    if "\n" in msg:
        lines.append("```\n")
        lines.append(msg)
        if not msg.endswith("\n"):
            lines.append("\n")
        lines.append("```\n\n")
    return "".join(lines)


CHANGELOG_MD_HEADER = """# Auto Changelog (Git commits)

Updated automatically on each commit. For reconstructing changes use this file and `30_system/docs/CHANGELOG_AUTO.jsonl`.

---

"""


def rewrite_md_from_jsonl() -> int:
    """
    Rebuild CHANGELOG_AUTO.md from JSONL: chronological order (oldest first).
    Deduplicates git commits by full hash (last JSONL occurrence wins). Keeps all manual (hash null) rows.
    """
    rows = read_all_jsonl_records()
    if not rows:
        CHANGELOG_MD.parent.mkdir(parents=True, exist_ok=True)
        CHANGELOG_MD.write_text(CHANGELOG_MD_HEADER, encoding="utf-8")
        print("rewrite-md: empty JSONL; wrote header only.")
        return 0

    by_hash: dict[str, dict] = {}
    manuals: list[dict] = []
    for r in rows:
        h = r.get("hash")
        if h is None:
            manuals.append(r)
        else:
            by_hash[str(h)] = r

    merged = list(by_hash.values()) + manuals
    merged.sort(
        key=lambda r: (
            _parse_sort_datetime(str(r.get("date") or "")),
            str(r.get("hash") or ""),
            str(r.get("short") or ""),
        )
    )

    parts = [CHANGELOG_MD_HEADER]
    for r in merged:
        parts.append(format_md_block(r))

    CHANGELOG_MD.parent.mkdir(parents=True, exist_ok=True)
    CHANGELOG_MD.write_text("".join(parts), encoding="utf-8")
    print(f"rewrite-md: wrote {len(merged)} entries (chronological).")
    return 0


def append_entry_md(info: dict) -> None:
    CHANGELOG_MD.parent.mkdir(parents=True, exist_ok=True)
    date_short = info["date"][:10] if len(info["date"]) >= 10 else info["date"]
    first_line = (info["message"].split("\n")[0] or "(no message)").strip()
    first_line_esc = first_line.replace("|", "\\|")
    files_str = ", ".join(info["files"][:30])
    if len(info["files"]) > 30:
        files_str += f" (+{len(info['files']) - 30} more)"
    with open(CHANGELOG_MD, "a", encoding="utf-8") as f:
        f.write(f"\n## {date_short} `{info['short']}` — {first_line_esc}\n\n")
        f.write(f"- **Files:** {files_str}\n\n")
        if "\n" in info["message"]:
            f.write("```\n")
            f.write(info["message"])
            if not info["message"].endswith("\n"):
                f.write("\n")
            f.write("```\n\n")


def append_entry_jsonl(info: dict) -> None:
    CHANGELOG_JSONL.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "date": info["date"],
        "hash": info["hash"],
        "short": info["short"],
        "message": info["message"],
        "files": info["files"],
    }
    with open(CHANGELOG_JSONL, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def append_manual_entry(message: str, files: list[str], source: str = "manual") -> None:
    ts = datetime.now(timezone.utc).isoformat()
    record = {
        "date": ts,
        "hash": None,
        "short": "manual",
        "message": message,
        "files": files,
        "source": source,
    }
    CHANGELOG_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(CHANGELOG_JSONL, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

    ensure_md_header()
    with open(CHANGELOG_MD, "a", encoding="utf-8") as f:
        f.write(f"\n## {ts[:10]} `manual` — {message}\n\n")
        f.write(f"- **Files:** {', '.join(files) if files else '(none)'}\n")
        f.write(f"- **Source:** `{source}`\n\n")


def read_all_jsonl_records() -> list[dict]:
    if not CHANGELOG_JSONL.exists():
        return []
    out = []
    with open(CHANGELOG_JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def read_last_jsonl_record() -> dict | None:
    rows = read_all_jsonl_records()
    return rows[-1] if rows else None


def hash_logged(full_hash: str) -> bool:
    return any(r.get("hash") == full_hash for r in read_all_jsonl_records())


def last_reflog_suggests_amend() -> bool:
    """True if the last HEAD movement was an amend (replace last log line, do not append)."""
    try:
        gs = run_git("reflog", "-1", "--format=%gs")
    except RuntimeError:
        return False
    g = gs.lower()
    return "amend" in g or "reword" in g


def pop_last_changelog_entries() -> None:
    """Remove last JSONL line and last ## section from markdown."""
    rows = read_all_jsonl_records()
    if not rows:
        return
    rows.pop()
    CHANGELOG_JSONL.parent.mkdir(parents=True, exist_ok=True)
    with open(CHANGELOG_JSONL, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    if not CHANGELOG_MD.exists():
        return
    text = CHANGELOG_MD.read_text(encoding="utf-8")
    # Strip last ## block (from last "\n## " to EOF); keep header before first ##
    idx = text.rfind("\n## ")
    if idx == -1:
        return
    # Keep everything before last section (preserve header + ---)
    trimmed = text[:idx].rstrip() + "\n"
    CHANGELOG_MD.write_text(trimmed, encoding="utf-8")


def log_current_commit_if_needed() -> bool:
    """
    Append HEAD to changelog if missing. If the last reflog action was amend,
    replace the last entry (same logical edit) instead of appending a duplicate line.
    Returns True if files were modified.
    """
    info = get_commit_info("HEAD")
    if not info:
        return False
    if hash_logged(info["hash"]):
        return False

    ensure_md_header()
    last = read_last_jsonl_record()
    try:
        head_at1 = run_git("rev-parse", "HEAD@{1}")
    except RuntimeError:
        head_at1 = None

    replace_last = (
        last is not None
        and head_at1 is not None
        and last.get("hash") == head_at1
        and last_reflog_suggests_amend()
    )
    if replace_last:
        pop_last_changelog_entries()

    append_entry_jsonl(info)
    append_entry_md(info)
    print(f"Logged {info['short']} to CHANGELOG_AUTO.")
    return True


def ensure_md_header() -> None:
    if not CHANGELOG_MD.exists():
        CHANGELOG_MD.parent.mkdir(parents=True, exist_ok=True)
        with open(CHANGELOG_MD, "w", encoding="utf-8") as f:
            f.write(CHANGELOG_MD_HEADER)


def main() -> int:
    spec = "HEAD"
    backfill = False
    rewrite_md = False
    manual_message: str | None = None
    manual_files: list[str] = []
    manual_source = "manual"
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--manual-message" and i + 1 < len(args):
            manual_message = args[i + 1]
            i += 2
            continue
        if a == "--manual-file" and i + 1 < len(args):
            manual_files.append(args[i + 1])
            i += 2
            continue
        if a == "--manual-source" and i + 1 < len(args):
            manual_source = args[i + 1]
            i += 2
            continue
        if a == "--backfill":
            backfill = True
        elif a == "--rewrite-md-from-jsonl":
            rewrite_md = True
        elif not a.startswith("-"):
            spec = a
            i += 1
            continue
        i += 1

    if manual_message:
        append_manual_entry(manual_message, manual_files, manual_source)
        print("Logged manual changelog entry.")
        return 0

    if rewrite_md:
        return rewrite_md_from_jsonl()

    if backfill:
        # Log all commits (avoid re-logging: only add if not already in jsonl)
        seen = set()
        if CHANGELOG_JSONL.exists():
            with open(CHANGELOG_JSONL, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            seen.add(json.loads(line)["hash"])
                        except Exception:
                            pass
        ensure_md_header()
        hashes = get_commit_range("HEAD", oldest_first=True)
        added = 0
        for h in hashes:
            if h in seen:
                continue
            info = get_commit_info(h)
            if info:
                append_entry_jsonl(info)
                append_entry_md(info)
                added += 1
        print(f"Backfill: added {added} commits to auto changelog.")
        return 0

    if spec == "HEAD":
        log_current_commit_if_needed()
        return 0

    info = get_commit_info(spec)
    if not info:
        print("Could not read commit.", file=sys.stderr)
        return 1
    ensure_md_header()
    append_entry_jsonl(info)
    append_entry_md(info)
    print(f"Logged {info['short']} to CHANGELOG_AUTO.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
