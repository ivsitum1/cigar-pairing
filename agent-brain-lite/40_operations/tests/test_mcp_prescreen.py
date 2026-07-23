"""Tests for MCP prescreen (LifeHarness Layer 1)."""
from __future__ import annotations

import sys
from pathlib import Path

PY_ROOT = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PY_ROOT))

from harness.mcp_prescreen import prescreen_tool_args  # noqa: E402


def test_empty_arguments_flagged():
    r = prescreen_tool_args("CallMcpTool", {})
    assert not r.ok
    assert any("empty" in i.lower() or "empty" in h.lower() for i in r.issues + r.hints)


def test_invalid_json_string():
    r = prescreen_tool_args("CallMcpTool", "{bad json")
    assert not r.ok
    assert r.hints


def test_valid_dict_ok():
    r = prescreen_tool_args("CallMcpTool", {"server": "x", "toolName": "y", "arguments": {}})
    assert r.ok


def test_path_traversal_hint():
    r = prescreen_tool_args("write_file", {"path": "../../etc/passwd"})
    assert not r.ok
    assert any("path_traversal" in i for i in r.issues)
