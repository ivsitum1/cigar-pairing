#!/usr/bin/env python3
"""NotebookLM consumer integration helper (unofficial wrapper flow).

This script wraps the `notebooklm-py` CLI to provide a stable local workflow:
- session/auth bootstrap checks
- notebook lookup by id/title substring
- chat history export in normalized JSON
- YouTube source ingest + wait + optional prompt + export
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


def _run_notebooklm(args: list[str], storage: Path, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    cmd = [
        sys.executable,
        "-m",
        "notebooklm.notebooklm_cli",
        "--storage",
        str(storage),
        *args,
    ]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=False)


def _run_json_command(args: list[str], storage: Path, timeout: int = 180) -> dict[str, Any]:
    result = _run_notebooklm([*args, "--json"], storage=storage, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(
            f"NotebookLM CLI failed: {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            "NotebookLM CLI returned non-JSON output. "
            "Ensure notebooklm-py version is compatible."
        ) from exc


def _pick_notebook(notebooks: list[dict[str, Any]], selector: str) -> dict[str, Any]:
    selector_lc = selector.strip().lower()
    if not selector_lc:
        raise ValueError("Notebook selector is empty.")

    for nb in notebooks:
        if str(nb.get("id", "")).lower() == selector_lc:
            return nb

    matches = [
        nb
        for nb in notebooks
        if selector_lc in str(nb.get("title", "")).lower()
        or selector_lc in str(nb.get("id", "")).lower()
    ]
    if not matches:
        raise ValueError(f"No notebook matched selector: {selector}")
    if len(matches) > 1:
        titles = [f"{m.get('title','<untitled>')} ({m.get('id','?')})" for m in matches[:5]]
        raise ValueError(
            "Notebook selector is ambiguous. Matches:\n- " + "\n- ".join(titles)
        )
    return matches[0]


def _normalize_history(raw_history: dict[str, Any], notebook: dict[str, Any]) -> dict[str, Any]:
    history = raw_history.get("history", raw_history)
    turns = history.get("turns", history.get("items", []))
    normalized_turns: list[dict[str, Any]] = []

    for idx, turn in enumerate(turns):
        answer = turn.get("answer", turn.get("response", ""))
        citations = turn.get("citations", [])
        normalized_turns.append(
            {
                "turn_index": idx,
                "question": turn.get("question", turn.get("query", "")),
                "answer": answer,
                "citations": citations if citations else None,
                "source_refs": turn.get("source_refs", turn.get("sources", None)),
                "timestamp": turn.get("timestamp", turn.get("created_at", None)),
            }
        )

    return {
        "notebook_id": notebook.get("id"),
        "notebook_title": notebook.get("title"),
        "exported_at_epoch": int(time.time()),
        "chat_turns": normalized_turns,
    }


def cmd_check_auth(args: argparse.Namespace) -> int:
    storage = Path(args.storage).expanduser()
    if not storage.exists():
        print(
            f"Storage state not found at {storage}. "
            "Run login first: python -m notebooklm.notebooklm_cli login",
            file=sys.stderr,
        )
        return 2

    status = _run_notebooklm(["status"], storage=storage, timeout=60)
    if status.returncode != 0:
        print(
            "NotebookLM session invalid or expired. "
            "Re-authenticate: python -m notebooklm.notebooklm_cli auth refresh",
            file=sys.stderr,
        )
        print(status.stderr.strip(), file=sys.stderr)
        return 3

    print("NotebookLM session appears valid.")
    return 0


def cmd_export_chat(args: argparse.Namespace) -> int:
    storage = Path(args.storage).expanduser()
    notebooks_payload = _run_json_command(["list"], storage=storage)
    notebooks = notebooks_payload.get("notebooks", notebooks_payload if isinstance(notebooks_payload, list) else [])
    notebook = _pick_notebook(notebooks, args.notebook)

    _run_notebooklm(["use", notebook["id"]], storage=storage, timeout=60)
    history_payload = _run_json_command(["history"], storage=storage)
    normalized = _normalize_history(history_payload, notebook)

    out_path = Path(args.output).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Exported chat history to {out_path}")
    return 0


def _wait_for_source_ready(storage: Path, source_id: str, timeout_sec: int, poll_sec: int) -> None:
    start = time.time()
    while True:
        age = int(time.time() - start)
        if age > timeout_sec:
            raise TimeoutError(
                f"Source {source_id} did not become ready within {timeout_sec}s. "
                "Try a longer timeout or verify NotebookLM processing status."
            )

        payload = _run_json_command(["source", "get", source_id], storage=storage)
        state = str(payload.get("state", payload.get("status", ""))).lower()
        if state in {"ready", "completed", "indexed"}:
            return
        if state in {"error", "failed"}:
            raise RuntimeError(f"Source {source_id} failed in NotebookLM: {payload}")
        time.sleep(poll_sec)


def cmd_youtube_flow(args: argparse.Namespace) -> int:
    storage = Path(args.storage).expanduser()
    notebooks_payload = _run_json_command(["list"], storage=storage)
    notebooks = notebooks_payload.get("notebooks", notebooks_payload if isinstance(notebooks_payload, list) else [])
    notebook = _pick_notebook(notebooks, args.notebook)
    _run_notebooklm(["use", notebook["id"]], storage=storage, timeout=60)

    add_payload = _run_json_command(["source", "add", args.youtube_url], storage=storage, timeout=300)
    source_id = add_payload.get("id", add_payload.get("source_id"))
    if not source_id:
        raise RuntimeError(f"Could not read source id from response: {add_payload}")

    _wait_for_source_ready(
        storage=storage,
        source_id=source_id,
        timeout_sec=args.timeout_sec,
        poll_sec=args.poll_sec,
    )

    if args.prompt:
        ask_payload = _run_json_command(["ask", args.prompt], storage=storage, timeout=300)
        prompt_out = Path(args.prompt_output).expanduser()
        prompt_out.parent.mkdir(parents=True, exist_ok=True)
        prompt_out.write_text(json.dumps(ask_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved prompt response to {prompt_out}")

    history_args = argparse.Namespace(
        storage=str(storage),
        notebook=notebook["id"],
        output=args.history_output,
    )
    return cmd_export_chat(history_args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="NotebookLM consumer extraction helper (unofficial API path)."
    )
    def _default_storage() -> str:
        profile = Path.home() / ".notebooklm" / "profiles" / "default" / "storage_state.json"
        legacy = Path.home() / ".notebooklm" / "storage_state.json"
        return str(profile if profile.exists() else legacy)

    parser.add_argument(
        "--storage",
        default=_default_storage(),
        help="Path to notebooklm-py storage_state.json (default: profiles/default)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check-auth", help="Validate local NotebookLM session.")
    check.set_defaults(func=cmd_check_auth)

    export = sub.add_parser("export-chat", help="Export notebook chat history as normalized JSON.")
    export.add_argument("--notebook", required=True, help="Notebook id or unique title substring")
    export.add_argument("--output", required=True, help="Target JSON file path")
    export.set_defaults(func=cmd_export_chat)

    ytf = sub.add_parser(
        "youtube-flow",
        help="Add YouTube source, wait for indexing, optional ask, then export history.",
    )
    ytf.add_argument("--notebook", required=True, help="Notebook id or unique title substring")
    ytf.add_argument("--youtube-url", required=True, help="YouTube URL to ingest")
    ytf.add_argument("--timeout-sec", type=int, default=900, help="Max wait for source ready")
    ytf.add_argument("--poll-sec", type=int, default=15, help="Polling interval")
    ytf.add_argument("--prompt", help="Optional prompt after source is ready")
    ytf.add_argument(
        "--prompt-output",
        default="outputs/notebooklm/prompt_response.json",
        help="Path for prompt response JSON when --prompt is used",
    )
    ytf.add_argument(
        "--history-output",
        default="outputs/notebooklm/chat_history.json",
        help="Path for normalized history JSON",
    )
    ytf.set_defaults(func=cmd_youtube_flow)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        print("Interrupted.", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
