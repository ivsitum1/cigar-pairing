"""Regression test: capture hook must strip a UTF-8 BOM before JSON parsing.

Windows/PowerShell piping prepends a BOM (U+FEFF) that str.strip() does not
remove. Before the fix, json.loads failed on every event and the hook stored an
opaque {"raw_input": ...} blob with lifecycle "unknown" — which is why the
memory DB filled with unmineable dumps and the learning loop had no signal.
"""
from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK = REPO_ROOT / ".cursor" / "hooks" / "memory_lifecycle.py"


def _load_hook():
    spec = importlib.util.spec_from_file_location("memory_lifecycle_hook", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.unit
def test_bom_prefixed_event_parses_structurally(monkeypatch):
    mod = _load_hook()
    payload = '﻿{"hook_event_name":"sessionStart","data":{"k":"v"}}'
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload))

    parsed = mod._read_stdin_json()

    assert "raw_input" not in parsed, "BOM not stripped — event stored as raw dump"
    assert parsed.get("hook_event_name") == "sessionStart"
    assert mod._lifecycle_name(mod._event_name(parsed)) == "SessionStart"


@pytest.mark.unit
def test_plain_event_still_parses(monkeypatch):
    mod = _load_hook()
    monkeypatch.setattr(sys, "stdin", io.StringIO('{"type":"stop"}'))
    parsed = mod._read_stdin_json()
    assert parsed == {"type": "stop"}
