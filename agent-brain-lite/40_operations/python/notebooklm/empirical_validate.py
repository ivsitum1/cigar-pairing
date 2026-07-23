"""Empirical validation of NotebookLM geometry benchmark claims against repo evidence."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

WORKSPACE = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY = WORKSPACE / "30_system" / "docs" / "notebooklm_benchmark_registry.json"
DEFAULT_LITERATURE = WORKSPACE / "30_system" / "docs" / "notebooklm_external_verification.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _path_exists(rel: str) -> bool:
    return (WORKSPACE / rel.replace("\\", "/")).is_file()


def _symbol_exists(rel_path: str, symbol: str) -> bool:
    path = WORKSPACE / rel_path
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    return bool(re.search(rf"\b{re.escape(symbol)}\b", text))


def _load_literature_index(path: Path | None = None) -> dict[str, dict[str, Any]]:
    lit_path = path or DEFAULT_LITERATURE
    if not lit_path.is_file():
        return {}
    data = json.loads(lit_path.read_text(encoding="utf-8"))
    return {c["registry_id"]: c for c in data.get("claims", []) if c.get("registry_id")}


def validate_claim(
    entry: dict[str, Any],
    *,
    literature: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    cid = entry["id"]
    ctype = entry.get("type", "external_benchmark")
    result: dict[str, Any] = {
        "id": cid,
        "theme": entry.get("theme", ""),
        "claim": entry.get("claim", ""),
        "type": ctype,
    }

    if ctype == "external_benchmark":
        lit = (literature or {}).get(cid)
        if lit:
            result["status"] = lit.get("status", "UNVERIFIED")
            result["evidence"] = {
                "summary": lit.get("summary", ""),
                "sources": lit.get("sources", []),
                "implementation_gate": lit.get("implementation_gate", ""),
            }
            result["literature_checked"] = True
            result["empirical"] = False
        else:
            result["status"] = "UNVERIFIED"
            result["evidence"] = entry.get("note", "External benchmark not reproduced in brain repo")
            result["literature_checked"] = False
            result["empirical"] = False
        return result

    if ctype == "repo_artifact":
        paths = entry.get("paths") or []
        symbols = entry.get("symbols") or []
        missing = [p for p in paths if not _path_exists(p)]
        sym_missing = []
        for sym in symbols:
            found = any(_symbol_exists(p, sym) for p in paths if _path_exists(p))
            if not found:
                sym_missing.append(sym)
        if not missing and not sym_missing:
            result["status"] = "VERIFIED"
            result["evidence"] = {"paths": paths, "symbols": symbols}
            result["empirical"] = True
        elif not missing:
            result["status"] = "INFERRED"
            result["evidence"] = {"paths_ok": paths, "symbols_missing": sym_missing}
            result["empirical"] = True
        else:
            result["status"] = "UNVERIFIED"
            result["evidence"] = {"missing_paths": missing, "symbols_missing": sym_missing}
            result["empirical"] = False
        return result

    result["status"] = "UNVERIFIED"
    result["evidence"] = "unknown claim type"
    result["empirical"] = False
    return result


def run_empirical_validation(
    registry_path: Path | None = None,
    literature_path: Path | None = None,
) -> dict[str, Any]:
    reg_path = registry_path or DEFAULT_REGISTRY
    registry = json.loads(reg_path.read_text(encoding="utf-8"))
    literature = _load_literature_index(literature_path)
    validated = [
        validate_claim(c, literature=literature) for c in registry.get("claims", [])
    ]
    verified = sum(1 for v in validated if v["status"] == "VERIFIED")
    inferred = sum(1 for v in validated if v["status"] == "INFERRED")
    unverified = sum(1 for v in validated if v["status"] == "UNVERIFIED")
    literature_discharged = sum(
        1
        for v in validated
        if v.get("type") == "external_benchmark" and v.get("literature_checked")
    )
    external = sum(1 for v in validated if v["type"] == "external_benchmark")

    procedural_only = external > 0 and unverified == external and literature_discharged == 0
    try:
        reg_rel = str(reg_path.relative_to(WORKSPACE)).replace("\\", "/")
    except ValueError:
        reg_rel = str(reg_path)
    return {
        "exported_at": _utc_now(),
        "registry": reg_rel,
        "summary": {
            "total": len(validated),
            "verified": verified,
            "inferred": inferred,
            "unverified": unverified,
            "external_benchmarks": external,
            "literature_discharged": literature_discharged,
            "implementation_coverage": round((verified + inferred) / max(len(validated), 1), 3),
        },
        "verdict": "GO_WITH_CAVEATS" if verified + inferred >= unverified else "NO-GO",
        "caveats": [
            "YouTube headline numbers are not replicated in this repo; see notebooklm_external_verification.json.",
            "LITERATURE_PARTIAL / LITERATURE_CONTRADICTED discharge procedural blockers only.",
            "Repo VERIFIED = implementation exists; not independent replication of video metrics.",
        ],
        "literature_verification": str(
            (literature_path or DEFAULT_LITERATURE).relative_to(WORKSPACE)
        ).replace("\\", "/")
        if (literature_path or DEFAULT_LITERATURE).is_file()
        else None,
        "claims": validated,
        "procedural_gate_superseded": not procedural_only,
    }


def merge_into_gate_report(gate: dict[str, Any], empirical: dict[str, Any]) -> dict[str, Any]:
    merged = dict(gate)
    merged["empirical_validation"] = empirical
    merged["exported_at"] = _utc_now()
    unverified_external = [
        c
        for c in empirical.get("claims", [])
        if c.get("type") == "external_benchmark"
        and c.get("status") == "UNVERIFIED"
        and not c.get("literature_checked")
    ]
    if unverified_external:
        merged.setdefault("blockers", [])
        if "unverified_youtube_benchmarks" not in merged["blockers"]:
            merged["blockers"].append("unverified_youtube_benchmarks")
    impl_cov = empirical.get("summary", {}).get("implementation_coverage", 0)
    if impl_cov >= 0.6 and empirical.get("verdict") == "GO_WITH_CAVEATS":
        merged["verdict"] = "GO"
    merged["notes"] = list(merged.get("notes") or []) + [
        f"Empirical validation: {empirical['summary']['verified']} VERIFIED, "
        f"{empirical['summary']['inferred']} INFERRED, "
        f"{empirical['summary']['unverified']} UNVERIFIED "
        f"(coverage {impl_cov:.0%}).",
    ]
    return merged
