import json
import os
import subprocess
import sys
from pathlib import Path


def test_cursor_hook_script_auto_captures_event(tmp_path):
    workspace = Path(__file__).resolve().parents[3]
    hook_script = workspace / ".cursor" / "hooks" / "memory_lifecycle.py"
    env = dict(os.environ)
    env["WORKSPACE_ROOT"] = str(tmp_path)
    env["AGENT_MEMORY_ENABLED"] = "1"
    (tmp_path / ".agent" / "memory").mkdir(parents=True, exist_ok=True)

    hook_input = {"event": "postToolUse", "data": {"tool": "ReadFile", "status": "ok"}}
    run = subprocess.run(
        [sys.executable, str(hook_script)],
        input=json.dumps(hook_input),
        capture_output=True,
        text=True,
        env=env,
        check=True,
    )
    output = json.loads(run.stdout.strip())
    assert output["permission"] == "allow"
    assert "memory:PostToolUse" in output.get("agent_message", "")

