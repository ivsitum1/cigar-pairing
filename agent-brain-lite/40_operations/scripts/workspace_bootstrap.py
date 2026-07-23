#!/usr/bin/env python3
"""Post-clone / post-pull bootstrap for multi-PC agent-rules workspaces.

Recreates machine-local junctions, seeds .env from template, validates links.
Git tracks content; junctions and .env stay local per machine.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
UPSTREAM_ROOT = REPO_ROOT / "90_archive" / "imports" / "obsidian-wiki_2026-05" / "obsidian-wiki"
UPSTREAM_SKILLS = UPSTREAM_ROOT / ".skills"
UPSTREAM_GIT_URL = "https://github.com/Ar9av/obsidian-wiki.git"
UPSTREAM_COMMIT = "6f20faaa0f3b53fa8917816baf5ccbb36f93da72"
CURSOR_SKILLS = REPO_ROOT / ".cursor" / "skills"
ENV_EXAMPLE = REPO_ROOT / ".env.example"
ENV_FILE = REPO_ROOT / ".env"
INSTALL_PS1 = REPO_ROOT / "40_operations" / "scripts" / "install_obsidian_wiki_skills.ps1"

# Files kept in git under .cursor/skills (not junctions)
CURSOR_SKILLS_KEEP = frozenset({"README.md", "skill-builder.md"})


def _repo_root_slashes() -> str:
    return str(REPO_ROOT.resolve()).replace("\\", "/")


def _upstream_skills_populated() -> bool:
    return UPSTREAM_SKILLS.is_dir() and any(UPSTREAM_SKILLS.iterdir())


def ensure_obsidian_wiki_upstream(force: bool = False) -> tuple[bool, str]:
    """Clone pinned obsidian-wiki upstream when .skills is missing (empty gitlink)."""
    if _upstream_skills_populated() and not force:
        return True, "upstream .skills already present"

    import shutil

    if UPSTREAM_ROOT.exists():
        if _upstream_skills_populated():
            return True, "upstream .skills already present"
        try:
            shutil.rmtree(UPSTREAM_ROOT)
        except OSError as exc:
            return False, f"cannot replace empty upstream dir: {exc}"

    UPSTREAM_ROOT.parent.mkdir(parents=True, exist_ok=True)
    clone = subprocess.run(
        [
            "git",
            "clone",
            "--filter=blob:none",
            "--no-checkout",
            UPSTREAM_GIT_URL,
            str(UPSTREAM_ROOT),
        ],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if clone.returncode != 0:
        err = (clone.stderr or clone.stdout or "").strip()
        return False, f"git clone failed: {err}"

    checkout = subprocess.run(
        ["git", "checkout", UPSTREAM_COMMIT],
        capture_output=True,
        text=True,
        cwd=str(UPSTREAM_ROOT),
    )
    if checkout.returncode != 0:
        err = (checkout.stderr or checkout.stdout or "").strip()
        return False, f"git checkout {UPSTREAM_COMMIT[:8]} failed: {err}"

    if not _upstream_skills_populated():
        return False, f".skills missing after clone: {UPSTREAM_SKILLS}"

    return True, f"cloned upstream at {UPSTREAM_COMMIT[:8]}"


STALE_MARKER = "_STARA_KOPIJA_NE_KORISTITI.md"


def check_session_cwd() -> dict:
    """Report whether the session runs from the stale OneDrive copy.

    The junction check below validates symlink *targets* but not the session's
    launch directory, so a session started inside the OneDrive copy previously
    passed silently. This closes that gap.
    """
    cwd = Path.cwd()
    marker_present = (cwd / STALE_MARKER).is_file()
    onedrive_path = "onedrive" in str(cwd).lower()
    session_cwd_onedrive = marker_present or onedrive_path
    return {
        "ok": not session_cwd_onedrive,
        "cwd": str(cwd),
        "session_cwd_onedrive": session_cwd_onedrive,
        "stale_marker_present": marker_present,
    }


def check_cursor_skill_junctions() -> dict:
    """Return junction health: ok, total, broken, stale_onedrive."""
    report: dict = {"ok": True, "total": 0, "broken": [], "stale_onedrive": 0, "missing_upstream": 0}
    if not CURSOR_SKILLS.is_dir():
        report["ok"] = False
        report["broken"].append({"name": "(dir)", "target": "", "reason": ".cursor/skills missing"})
        return report
    if not UPSTREAM_SKILLS.is_dir():
        report["ok"] = False
        report["missing_upstream"] = 1
        return report

    expected_names = {p.name for p in UPSTREAM_SKILLS.iterdir() if p.is_dir()}
    for name in sorted(expected_names):
        link = CURSOR_SKILLS / name
        target_expected = (UPSTREAM_SKILLS / name).resolve()
        report["total"] += 1
        if not link.exists():
            report["ok"] = False
            report["broken"].append({"name": name, "target": "", "reason": "junction missing"})
            continue
        if sys.platform == "win32":
            try:
                out = subprocess.check_output(
                    [
                        "powershell",
                        "-NoProfile",
                        "-Command",
                        f"$i=Get-Item -LiteralPath '{link}' -Force; "
                        f"@{{LinkType=$i.LinkType; Target=($i.Target -join ';')}} | ConvertTo-Json -Compress",
                    ],
                    text=True,
                    errors="replace",
                )
                meta = json.loads(out)
                link_type = meta.get("LinkType") or ""
                target_raw = meta.get("Target") or ""
            except Exception as exc:
                report["ok"] = False
                report["broken"].append({"name": name, "target": "", "reason": str(exc)})
                continue
            if link_type != "Junction":
                report["ok"] = False
                report["broken"].append(
                    {"name": name, "target": target_raw, "reason": f"not a junction ({link_type})"}
                )
                continue
            target_path = Path(str(target_raw).strip())
            if "onedrive" in str(target_path).lower():
                report["stale_onedrive"] += 1
                report["ok"] = False
                report["broken"].append(
                    {"name": name, "target": str(target_path), "reason": "stale OneDrive path"}
                )
                continue
            try:
                if target_path.resolve() != target_expected:
                    report["ok"] = False
                    report["broken"].append(
                        {
                            "name": name,
                            "target": str(target_path),
                            "reason": f"wrong target (expected {target_expected})",
                        }
                    )
                    continue
            except OSError:
                report["ok"] = False
                report["broken"].append(
                    {"name": name, "target": str(target_path), "reason": "target path does not exist"}
                )
        elif link.is_symlink():
            try:
                if link.resolve() != target_expected:
                    report["ok"] = False
                    report["broken"].append(
                        {"name": name, "target": str(link.readlink()), "reason": "wrong symlink target"}
                    )
            except OSError:
                report["ok"] = False
                report["broken"].append({"name": name, "target": "", "reason": "broken symlink"})
        else:
            report["ok"] = False
            report["broken"].append({"name": name, "target": "", "reason": "expected symlink on Unix"})
    return report


def install_obsidian_wiki_skills(force: bool = True) -> tuple[int, str]:
    if sys.platform != "win32":
        return _install_skills_unix(force)
    if not INSTALL_PS1.is_file():
        return 1, f"Missing {INSTALL_PS1}"
    cmd = [
        "powershell",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(INSTALL_PS1),
        "-RepoRoot",
        str(REPO_ROOT),
    ]
    if force:
        cmd.append("-Force")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    out = (result.stdout or "") + (result.stderr or "")
    return result.returncode, out


def _install_skills_unix(force: bool) -> tuple[int, str]:
    if not UPSTREAM_SKILLS.is_dir():
        return 1, f"Upstream .skills not found: {UPSTREAM_SKILLS}"
    CURSOR_SKILLS.mkdir(parents=True, exist_ok=True)
    linked = 0
    for skill_dir in sorted(UPSTREAM_SKILLS.iterdir()):
        if not skill_dir.is_dir():
            continue
        link = CURSOR_SKILLS / skill_dir.name
        target = skill_dir.resolve()
        if link.is_symlink() or link.exists():
            if force:
                link.unlink(missing_ok=True)
            else:
                continue
        link.symlink_to(target, target_is_directory=True)
        linked += 1
    return 0, f"Linked {linked} skills (Unix symlinks)"


def seed_env(overwrite: bool = False) -> tuple[bool, str]:
    if ENV_FILE.exists() and not overwrite:
        return True, ".env exists (skipped; use --seed-env --overwrite-env to replace)"
    if not ENV_EXAMPLE.is_file():
        return False, ".env.example missing"
    root = _repo_root_slashes()
    text = ENV_EXAMPLE.read_text(encoding="utf-8")
    # Replace any legacy OneDrive or Ivan-specific Documents paths with this machine's repo root
    text = re.sub(
        r'"C:/Users/[^"]+/Documents/agent rules',
        f'"{root}',
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'"C:/Users/[^"]+/OneDrive/Dokumenti/agent rules',
        f'"{root}',
        text,
        flags=re.IGNORECASE,
    )
    text = text.replace("<REPO_ROOT>", root)
    ENV_FILE.write_text(text, encoding="utf-8")
    return True, f"Wrote {ENV_FILE} with repo root {root}"


def bootstrap(*, force_links: bool = True, seed: bool = False, overwrite_env: bool = False) -> dict:
    report: dict = {"ok": True, "steps": {}}

    session_cwd = check_session_cwd()
    report["steps"]["session_cwd"] = session_cwd
    if not session_cwd["ok"]:
        report["ok"] = False

    fetch_ok, fetch_msg = ensure_obsidian_wiki_upstream()
    report["steps"]["fetch_upstream"] = {"ok": fetch_ok, "message": fetch_msg}
    if not fetch_ok:
        report["ok"] = False
        report["steps"]["junctions"] = check_cursor_skill_junctions()
        return report

    code, out = install_obsidian_wiki_skills(force=force_links)
    report["steps"]["install_skills"] = {"exit_code": code, "output_tail": out.strip()[-500:] if out else ""}
    if code != 0:
        report["ok"] = False

    if seed:
        ok, msg = seed_env(overwrite=overwrite_env)
        report["steps"]["seed_env"] = {"ok": ok, "message": msg}
        if not ok:
            report["ok"] = False

    junctions = check_cursor_skill_junctions()
    report["steps"]["junctions"] = junctions
    if not junctions.get("ok"):
        report["ok"] = False

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap agent-rules workspace after clone/pull")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check-only", action="store_true", help="Validate junctions only; no install")
    parser.add_argument("--no-force", action="store_true", help="Do not replace stale junctions")
    parser.add_argument("--seed-env", action="store_true", help="Create .env from .env.example if missing")
    parser.add_argument("--overwrite-env", action="store_true", help="With --seed-env, replace existing .env")
    args = parser.parse_args()

    if args.check_only:
        session_cwd = check_session_cwd()
        junctions = check_cursor_skill_junctions()
        if not junctions.get("ok") and junctions.get("missing_upstream"):
            fetch_ok, fetch_msg = ensure_obsidian_wiki_upstream()
            if fetch_ok:
                install_obsidian_wiki_skills(force=not args.no_force)
                junctions = check_cursor_skill_junctions()
            report = {
                "ok": junctions.get("ok", False) and session_cwd["ok"],
                "steps": {
                    "session_cwd": session_cwd,
                    "fetch_upstream": {"ok": fetch_ok, "message": fetch_msg},
                    "junctions": junctions,
                },
            }
        else:
            report = {"ok": True, "steps": {"session_cwd": session_cwd, "junctions": junctions}}
            if not junctions.get("ok") or not session_cwd["ok"]:
                report["ok"] = False
    else:
        report = bootstrap(
            force_links=not args.no_force,
            seed=args.seed_env,
            overwrite_env=args.overwrite_env,
        )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("=== WORKSPACE BOOTSTRAP ===")
        print(f"Repo: {REPO_ROOT}")
        for step, data in report.get("steps", {}).items():
            print(f"\n[{step}]")
            if isinstance(data, dict):
                for k, v in data.items():
                    if k == "broken" and v:
                        print(f"  {k}: {len(v)} issue(s)")
                        for item in v[:5]:
                            print(f"    - {item}")
                        if len(v) > 5:
                            print(f"    ... and {len(v) - 5} more")
                    elif k == "output_tail" and v:
                        print(f"  install log (tail): ...{v}")
                    else:
                        print(f"  {k}: {v}")
        print("\nResult:", "PASS" if report["ok"] else "FAIL")
        if not report["ok"]:
            print("Fix: python 40_operations/scripts/workspace_bootstrap.py")

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
