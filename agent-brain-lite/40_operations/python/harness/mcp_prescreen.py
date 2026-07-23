"""Prescreen MCP tool arguments for common syntax/contract failures."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


@dataclass
class PrescreenResult:
    ok: bool
    issues: list[str]
    hints: list[str]


def _check_json_string(value: str) -> list[str]:
    hints: list[str] = []
    try:
        json.loads(value)
    except json.JSONDecodeError as exc:
        hints.append(f"Invalid JSON: {exc.msg} at position {exc.pos}")
        if value.count("{") != value.count("}"):
            hints.append("Unbalanced curly braces in JSON argument")
        if value.count("[") != value.count("]"):
            hints.append("Unbalanced square brackets in JSON argument")
    return hints


def prescreen_tool_args(tool_name: str, arguments: dict[str, Any] | str | None) -> PrescreenResult:
    """Return deterministic hints before MCP retry. Does not mutate arguments."""
    issues: list[str] = []
    hints: list[str] = []

    if arguments is None:
        issues.append("arguments_missing")
        hints.append("Provide a non-null arguments object for MCP tool call")
        return PrescreenResult(ok=False, issues=issues, hints=hints)

    if isinstance(arguments, str):
        json_hints = _check_json_string(arguments)
        if json_hints:
            issues.append("json_parse_error")
            hints.extend(json_hints)
        try:
            parsed = json.loads(arguments)
            arguments = parsed if isinstance(parsed, dict) else {"value": parsed}
        except json.JSONDecodeError:
            return PrescreenResult(ok=False, issues=issues, hints=hints)

    if not isinstance(arguments, dict):
        issues.append("arguments_not_object")
        hints.append("MCP arguments should be a JSON object (dict)")
        return PrescreenResult(ok=False, issues=issues, hints=hints)

    if not arguments:
        issues.append("arguments_empty")
        hints.append("Empty arguments object; verify required parameters for this tool")

    tool_lower = (tool_name or "").lower()
    path_keys = {"path", "file_path", "filepath", "directory", "dir", "root"}
    for key, value in arguments.items():
        if key.lower() in path_keys and isinstance(value, str):
            norm = value.replace("\\", "/")
            if ".." in norm or norm.startswith("/etc") or re.match(r"^[A-Za-z]:\.\.", value):
                issues.append(f"path_traversal_risk:{key}")
                hints.append(
                    f"Parameter '{key}' may escape workspace; resolve to absolute path inside project root"
                )
        if value is None:
            issues.append(f"null_param:{key}")
            hints.append(f"Parameter '{key}' is null; check required fields in tool schema")
        if isinstance(value, str):
            if tool_lower.endswith("sql") or "sql" in tool_lower:
                if "'" in value and "''" not in value and "\\'" not in value:
                    if re.search(r"\bSELECT\b", value, re.I):
                        hints.append("SQL string may need escaped quotes for dialect-specific syntax")
            stripped = value.strip()
            if stripped.startswith("{") or stripped.startswith("["):
                hints.extend(_check_json_string(stripped))

    ok = len(issues) == 0
    return PrescreenResult(ok=ok, issues=issues, hints=hints)


def backoff_hint(attempt: int, *, base_ms: int = 500, cap_ms: int = 8000) -> str:
    """Exponential backoff suggestion for MCP retry (RAG Anatomy harness prescreen)."""
    delay = min(cap_ms, base_ms * (2 ** max(0, attempt - 1)))
    return f"Retry after ~{delay}ms backoff (attempt {attempt})"
