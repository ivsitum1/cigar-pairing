import json
import subprocess
import sys
from pathlib import Path


def test_memory_hook_cli_ingest_and_inject(tmp_path):
    workspace = Path(__file__).resolve().parents[3]
    script = workspace / "40_operations/scripts" / "memory_hook.py"

    env = dict(**__import__("os").environ)
    env["WORKSPACE_ROOT"] = str(tmp_path)
    env["AGENT_MEMORY_ENABLED"] = "1"
    (tmp_path / ".agent" / "memory").mkdir(parents=True, exist_ok=True)

    ingest_cmd = [
        sys.executable,
        str(script),
        "ingest",
        "--lifecycle",
        "PostToolUse",
        "--session-id",
        "s-4",
        "--project-scope",
        "agent-rules",
        "--payload",
        '{"message":"timeline retrieval fixed"}',
    ]
    ingest_run = subprocess.run(ingest_cmd, capture_output=True, text=True, env=env, check=True)
    ingest_data = json.loads(ingest_run.stdout.strip())
    assert "event_hash" in ingest_data

    inject_cmd = [
        sys.executable,
        str(script),
        "inject",
        "--project-scope",
        "agent-rules",
        "--query",
        "retrieval",
    ]
    inject_run = subprocess.run(inject_cmd, capture_output=True, text=True, env=env, check=True)
    assert inject_run.stdout.strip().startswith("# Memory Context")

