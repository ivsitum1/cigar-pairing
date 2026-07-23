"""SkillLens + LARGER hook helpers (Cursor beforeSubmitPrompt / postToolUse)."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[3]
GRAPH_DIR = WORKSPACE / "graphify-out"

_GREP_TOOLS = frozenset({"grep", "Grep", "ripgrep", "Ripgrep"})
_SHELL_TOOLS = frozenset({"shell", "Shell", "Bash", "bash", "run_terminal_cmd"})


def env_disabled(name: str) -> bool:
    return os.environ.get(name, "").strip() in {"1", "true", "TRUE"}


def extract_user_prompt(hook_input: dict[str, Any], data: dict[str, Any] | None = None) -> str:
    payload = data if data is not None else hook_input
    for container in (payload, hook_input):
        for key in ("prompt", "userPrompt", "user_prompt", "text", "message"):
            val = container.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        messages = container.get("messages")
        if isinstance(messages, list):
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get("role") == "user":
                    content = msg.get("content")
                    if isinstance(content, str) and content.strip():
                        return content.strip()
    return ""


def _tool_name(payload: dict[str, Any]) -> str:
    for key in ("toolName", "tool_name", "tool", "name"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _tool_args(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("arguments", "args", "input", "tool_input", "toolInput"):
        val = payload.get(key)
        if isinstance(val, dict):
            return val
        if isinstance(val, str) and val.strip():
            try:
                parsed = json.loads(val)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
    return {}


def _tool_output_text(payload: dict[str, Any]) -> str:
    for key in ("result", "output", "toolResult", "content", "stdout"):
        val = payload.get(key)
        if isinstance(val, str):
            return val
        if isinstance(val, dict):
            for sub in ("content", "text", "output", "stdout"):
                inner = val.get(sub)
                if isinstance(inner, str):
                    return inner
                if isinstance(inner, list):
                    parts = []
                    for item in inner:
                        if isinstance(item, dict) and isinstance(item.get("text"), str):
                            parts.append(item["text"])
                        elif isinstance(item, str):
                            parts.append(item)
                    if parts:
                        return "\n".join(parts)
    return ""


def is_grep_tool_use(payload: dict[str, Any]) -> bool:
    tool = _tool_name(payload)
    if tool in _GREP_TOOLS:
        return True
    if tool in _SHELL_TOOLS:
        cmd = str(_tool_args(payload).get("command") or payload.get("command") or "")
        cmd_l = cmd.lower()
        return " rg " in f" {cmd_l} " or cmd_l.startswith("rg ") or " grep " in f" {cmd_l} "
    return False


def extract_grep_hit(payload: dict[str, Any]) -> str | None:
    args = _tool_args(payload)
    for key in ("pattern", "grep_hit", "query", "search"):
        val = args.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()[:500]

    tool = _tool_name(payload)
    if tool in _SHELL_TOOLS:
        cmd = str(args.get("command") or payload.get("command") or "")
        m = re.search(r"\brg\s+(?:-[^\s]+\s+)*['\"]?([^\s'\"]+)", cmd)
        if m:
            return m.group(1)[:500]
        m = re.search(r"\bgrep\s+(?:-[^\s]+\s+)+['\"]?([^\s'\"]+)", cmd)
        if m:
            return m.group(1)[:500]

    output = _tool_output_text(payload)
    if output:
        for line in output.splitlines()[:40]:
            line = line.strip()
            if not line or line.startswith("---"):
                continue
            m = re.match(r"^(.+?):\d+:", line)
            if m:
                hit = m.group(1).strip().replace("\\", "/")
                if hit:
                    return hit[-200:]
            if "/" in line or "\\" in line:
                token = line.split(":", 1)[0].strip()
                if token and len(token) > 3:
                    return token[-200:]

    path_arg = args.get("path")
    if isinstance(path_arg, str) and path_arg.strip():
        return path_arg.strip()[-200:]

    return None


def graph_available() -> bool:
    return (GRAPH_DIR / "merged.json").is_file() or (GRAPH_DIR / "graph.json").is_file()


def run_skill_lens(prompt: str, *, rwr: bool = False, top_k: int = 5) -> tuple[str | None, dict | None]:
    """Run SkillLens rerank + verifier; return (context_block, bundle_dict)."""
    if env_disabled("SKILL_LENS_HOOK_DISABLED"):
        return None, None
    if len(prompt.strip()) < 12:
        return None, None

    try:
        from brain_assist.skill_rerank import rank_skills
        from brain_assist.skill_verifier import verify_bundle
    except ImportError:
        return None, None

    try:
        ranked = rank_skills(prompt, top_k=top_k, dag_mode=True, rwr_mode=rwr, include_body=False)
        bundle = verify_bundle(prompt, ranked=ranked, dag_mode=True)
    except Exception:
        return None, None

    return _format_skill_lens_context(bundle), bundle


def _format_skill_lens_context(bundle: dict) -> str:
    lines = ["[SkillLens verifier — run before Tier-3 SKILL load]"]
    rel = bundle.get("relation_tag")
    if rel:
        lines.append(f"relation_tag: {rel}")

    for d in bundle.get("decisions") or []:
        action = d.get("action", "?")
        sid = d.get("id", "?")
        score = d.get("score", 0)
        lines.append(f"  {sid}: {action} (score={score})")

    to_load = [d["id"] for d in bundle.get("to_load") or [] if d.get("id")]
    if to_load:
        lines.append(f"to_load: {', '.join(to_load)}")
    lines.append("ACCEPT/REWRITE → full SKILL; DECOMPOSE → skill_decompose subunits; SKIP → do not inject.")

    rewrites = bundle.get("rewrites") or []
    if rewrites:
        ids = ", ".join(d.get("id", "?") for d in rewrites)
        lines.append(f"REWRITE pending: {ids} — check outputs/skill_rewrites/proposals/")

    return "\n".join(lines)


def build_skill_lens_context(prompt: str, *, rwr: bool = False, top_k: int = 5) -> str | None:
    context, _bundle = run_skill_lens(prompt, rwr=rwr, top_k=top_k)
    return context


def run_larger_expand(grep_hit: str, *, max_neighbors: int = 8) -> tuple[str | None, dict | None]:
    """Expand grep hit via Graphify; return (context_block, expand_result)."""
    if env_disabled("LARGER_HOOK_DISABLED"):
        return None, None
    enabled = os.environ.get("LARGER_HOOK_ENABLED", "1").strip() not in {"0", "false", "FALSE"}
    if not enabled:
        return None, None
    if not grep_hit or not graph_available():
        return None, None

    try:
        from harness.larger_graph_expand import expand_from_grep
    except ImportError:
        return None, None

    try:
        result = expand_from_grep(grep_hit, max_neighbors=max_neighbors)
    except FileNotFoundError:
        return None, None
    except Exception:
        return None, None

    if not result.get("anchors") and not result.get("neighbors"):
        return None, result

    return _format_larger_context(grep_hit, result, max_neighbors=max_neighbors), result


def _format_larger_context(grep_hit: str, result: dict, *, max_neighbors: int = 8) -> str:
    lines = [f"[LARGER graph expand — grep hit: {grep_hit[:120]}]"]
    for a in (result.get("anchors") or [])[:4]:
        sf = a.get("source_file") or a.get("label") or a.get("id")
        lines.append(f"  anchor: {sf}")
    for n in (result.get("neighbors") or [])[:max_neighbors]:
        sf = n.get("source_file") or n.get("label") or n.get("id")
        rel = n.get("relation") or "?"
        w = n.get("weight", 0)
        lines.append(f"  neighbor {w:.2f} {rel}: {sf}")
    lines.append("Prefer these files before repo-wide grep retry.")
    return "\n".join(lines)


def build_larger_context(grep_hit: str, *, max_neighbors: int = 8) -> str | None:
    context, _result = run_larger_expand(grep_hit, max_neighbors=max_neighbors)
    return context


def merge_additional_context(existing: str | None, new_block: str | None) -> str | None:
    if not new_block:
        return existing or None
    if existing and existing.strip():
        return existing.strip() + "\n\n" + new_block.strip()
    return new_block.strip()
