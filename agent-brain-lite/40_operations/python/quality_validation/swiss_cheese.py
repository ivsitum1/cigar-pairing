"""
Five-layer Swiss Cheese validation (former swiss_cheese_validation.R).
"""

from __future__ import annotations

import traceback
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from quality_validation.self_assessment import default_rubric, mandatory_self_assess

Task = Dict[str, Any]
Validator = Callable[[Any, Task], dict]


def layer_1_pre_execution(task: Task) -> dict:
    issues: List[str] = []
    if task.get("task_type") is None:
        issues.append("task_type missing")
    if task.get("inputs") is None:
        issues.append("inputs missing")
    return {
        "pass": len(issues) == 0,
        "issues": issues,
        "fixes": ["Provide task_type and inputs."] if issues else [],
    }


def layer_2_monitored_execution(
    task: Task, executor: Callable[[Task], Any]
) -> dict:
    log: dict = {"start": datetime.now(timezone.utc).isoformat(), "error": None, "end": None}
    try:
        out = executor(task)
        log["end"] = datetime.now(timezone.utc).isoformat()
        return {"output": out, "log": log}
    except Exception as e:  # noqa: BLE001
        log["error"] = f"{e}\n{traceback.format_exc()}"
        log["end"] = datetime.now(timezone.utc).isoformat()
        return {"output": None, "log": log}


def layer_3_post_validation(
    output: Any,
    task: Task,
    existing_validators: Optional[List[Validator]] = None,
) -> dict:
    issues: List[str] = []
    if output is None and task.get("expect_output"):
        issues.append("Output missing")
    for v in existing_validators or []:
        try:
            res = v(output, task)
        except Exception as e:  # noqa: BLE001
            res = {"pass": False, "issues": str(e)}
        if not res.get("pass", True):
            msg = res.get("issues")
            if isinstance(msg, list):
                issues.extend(str(x) for x in msg)
            elif msg:
                issues.append(str(msg))
            else:
                issues.append("Validation failed")
    return {"pass": len(issues) == 0, "issues": issues}


def layer_4_meta_review(task: Task, execution_log: dict, validation_results: dict) -> dict:
    start = execution_log.get("start")
    end = execution_log.get("end")
    duration_sec = None
    if start and end:
        try:
            t0 = datetime.fromisoformat(start.replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(end.replace("Z", "+00:00"))
            duration_sec = (t1 - t0).total_seconds()
        except (ValueError, TypeError):
            duration_sec = None
    return {
        "task_type": task.get("task_type"),
        "had_error": execution_log.get("error") is not None,
        "validation_passed": validation_results.get("pass"),
        "duration_sec": duration_sec,
    }


def run_layer_5(output: Any, target_score: int = 10) -> dict:
    del target_score  # reserved; default rubric targets 10 via loop
    res = mandatory_self_assess(output, rubric=default_rubric(), max_iterations=3)
    return {
        "score": res["final_score"],
        "output": res["output"],
        "history": res["history"],
    }


def validate_with_swiss_cheese(
    task: Task,
    executor: Callable[[Task], Any],
    existing_validators: Optional[List[Validator]] = None,
) -> dict:
    pre = layer_1_pre_execution(task)
    if not pre["pass"]:
        return {
            "success": False,
            "layer": "pre_execution",
            "issues": pre["issues"],
            "recommendations": pre["fixes"],
        }

    monitored = layer_2_monitored_execution(task, executor)
    if monitored["log"].get("error"):
        return {
            "success": False,
            "layer": "execution",
            "issues": [monitored["log"]["error"]],
            "execution_log": monitored["log"],
        }

    post = layer_3_post_validation(
        monitored["output"], task, existing_validators=existing_validators
    )
    if not post["pass"]:
        return {
            "success": False,
            "layer": "post_validation",
            "issues": post["issues"],
            "execution_log": monitored["log"],
        }

    meta = layer_4_meta_review(task, monitored["log"], post)
    layer5 = run_layer_5(monitored["output"])

    return {
        "success": True,
        "output": layer5["output"],
        "assessment": {
            "score": layer5["score"],
            "meta_review": meta,
            "history": layer5["history"],
        },
        "execution_log": monitored["log"],
    }


def validate_with_swiss_cheese_fn(
    existing_function: Callable[..., Any], *args: Any, **kwargs: Any
) -> dict:
    task: Task = {
        "task_type": getattr(existing_function, "__name__", str(existing_function)),
        "inputs": {"args": args, "kwargs": kwargs},
    }

    def executor(t: Task) -> Any:
        inp = t["inputs"]
        return existing_function(*inp["args"], **inp["kwargs"])

    return validate_with_swiss_cheese(task, executor)
