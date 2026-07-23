"""Tests for books_rag Cursor hook JSON output."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[3]
HOOK = WORKSPACE / ".cursor" / "hooks" / "books_rag_lifecycle.py"


def test_hook_allows_when_disabled() -> None:
    import os

    env = os.environ.copy()
    env["BOOKS_RAG_ENABLED"] = "0"
    env["PYTHONPATH"] = str(WORKSPACE)
    payload = json.dumps({"event": "beforeSubmitPrompt", "data": {"prompt": "citiraj knjigu"}})
    result = subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        capture_output=True,
        text=True,
        cwd=str(WORKSPACE),
        env=env,
        timeout=15,
        check=False,
    )
    out = json.loads(result.stdout)
    assert out.get("permission") == "allow"
    assert "additional_context" not in out or not out["additional_context"]
