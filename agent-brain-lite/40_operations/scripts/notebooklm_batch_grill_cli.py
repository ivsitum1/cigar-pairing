#!/usr/bin/env python3
"""Grill NotebookLM via notebooklm-py CLI (preferred over Playwright)."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
import time
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
CFG = WORKSPACE / "30_system/docs/reference/notebooklm_batch_2026-06_questions.json"
OUT_DIR = WORKSPACE / "outputs" / "notebooklm"


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_cfg() -> dict:
    return json.loads(CFG.read_text(encoding="utf-8"))


def _questions(slug: str, pass_num: int) -> list[str]:
    cfg = _load_cfg()
    if pass_num == 2:
        return list(cfg.get("pass2", []))
    return list(cfg.get("common", [])) + list(cfg.get("topic", {}).get(slug, []))


def _run_cli(args: list[str], timeout: int = 300, retries: int = 3) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, "-m", "notebooklm.notebooklm_cli", *args]
    last: subprocess.CompletedProcess[str] | None = None
    for attempt in range(retries):
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=WORKSPACE,
                encoding="utf-8",
                errors="replace",
            )
            last = result
            err = (result.stderr or "") + (result.stdout or "")
            if result.returncode == 0:
                return result
            if "TransportServerError" in err or result.returncode == 2:
                wait = 15 * (attempt + 1)
                print(f"CLI retry {attempt + 1}/{retries} after rc={result.returncode}, wait {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            return result
        except subprocess.TimeoutExpired as exc:
            wait = 15 * (attempt + 1)
            print(f"CLI timeout retry {attempt + 1}/{retries}, wait {wait}s", file=sys.stderr)
            time.sleep(wait)
            if attempt == retries - 1:
                raise exc
    assert last is not None
    return last


def _ask(
    notebook_id: str,
    question: str,
    *,
    conversation_id: str | None,
    fresh: bool,
) -> dict:
    cmd = ["use", notebook_id]
    _run_cli(cmd)
    ask_cmd = ["ask", "--json", "--yes", "--timeout", "180"]
    if fresh:
        ask_cmd.append("--new")
    elif conversation_id:
        ask_cmd.extend(["-c", conversation_id])
    ask_cmd.append(question)
    result = _run_cli(ask_cmd, timeout=240)
    if result.returncode != 0:
        return {
            "success": False,
            "answer": result.stderr or result.stdout,
            "error": f"cli_exit_{result.returncode}",
        }
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"success": False, "answer": result.stdout, "error": "non_json"}
    return {
        "success": bool(data.get("answer")),
        "answer": data.get("answer", ""),
        "conversation_id": data.get("conversation_id"),
        "references": data.get("references"),
    }


def grill_slug(slug: str, pass_num: int, start: int, force: bool = False) -> Path:
    cfg = _load_cfg()
    nb = cfg["notebooks"][slug]
    nb_id = nb["id"]
    suffix = "_pass2" if pass_num == 2 else ""
    out = OUT_DIR / f"{slug}_query_batch{suffix}.json"
    existing: dict = {}
    if out.exists():
        existing = json.loads(out.read_text(encoding="utf-8"))
    questions = _questions(slug, pass_num)
    results = list(existing.get("results") or [])
    if len(results) < len(questions):
        results.extend([None] * (len(questions) - len(results)))
    conversation_id = existing.get("conversation_id")
    url = f"https://notebooklm.google.com/notebook/{nb_id}"
    title = nb.get("title_hint", slug)

    for i in range(start, len(questions)):
        if (
            not force
            and i < len(results)
            and results[i]
            and results[i].get("result", {}).get("success")
        ):
            conversation_id = (results[i].get("result") or {}).get("conversation_id") or conversation_id
            continue
        q = questions[i]
        print(f"[{slug}] [{i+1}/{len(questions)}] {q[:60]}...", file=sys.stderr)
        fresh = force or (conversation_id is None and i == 0)
        r = _ask(nb_id, q, conversation_id=conversation_id, fresh=fresh)
        if r.get("conversation_id"):
            conversation_id = r["conversation_id"]
        results[i] = {"question": q, "result": r}
        payload = {
            "notebook_title": title,
            "notebook_url": url,
            "notebook_id": nb_id,
            "slug": slug,
            "conversation_id": conversation_id,
            "exported_at": _utc(),
            "grill_backend": "notebooklm_cli",
            "results": results,
        }
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        time.sleep(2)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slug")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--pass", dest="pass_num", type=int, default=1, choices=[1, 2])
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--force", action="store_true", help="Re-ask all questions (new notebook sources)")
    args = parser.parse_args()
    slugs = [args.slug] if args.slug else (list(_load_cfg().get("notebooks", {}).keys()) if args.all else [])
    if not slugs:
        parser.error("--slug or --all required")
    for slug in slugs:
        grill_slug(slug, args.pass_num, args.start, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
