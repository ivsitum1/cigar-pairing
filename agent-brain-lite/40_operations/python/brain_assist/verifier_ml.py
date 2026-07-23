"""Sklearn verifier assist: TF-IDF + numeric features from usage ledger."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

from .skill_rerank import rank_skills
from .skill_verifier import verify_skill
from .verifier_registry import load_verifier_registry
from .verifier_usage_ledger import read_rows

WORKSPACE = Path(__file__).resolve().parents[3]
DEFAULT_MODEL = WORKSPACE / "40_operations" / "models" / "verifier_sklearn.joblib"
MIN_LABELED_ROWS = 50
MIN_NEW_ROWS_RETRAIN = 5
ML_STATE_PATH = WORKSPACE / ".agent" / "memory" / "verifier_ml_state.json"

ACTIONS = ["ACCEPT", "DECOMPOSE", "SKIP", "REWRITE"]
GRANULARITY_MAP = {"primitive": 0.0, "procedure": 0.33, "strategy": 0.66, "policy": 1.0}
REGISTRY_PATH = WORKSPACE / "30_system" / "SKILLS" / "registry.json"


def model_path() -> Path:
    reg = load_verifier_registry()
    override = reg.get("ml_model_path") or os.environ.get("VERIFIER_ML_MODEL_PATH", "")
    if override:
        p = Path(override).expanduser()
        if not p.is_absolute():
            p = WORKSPACE / p
        return p
    return DEFAULT_MODEL


def blend_weight() -> float:
    reg = load_verifier_registry()
    if reg.get("ml_blend_weight") is not None:
        return float(reg["ml_blend_weight"])
    env = os.environ.get("VERIFIER_ML_BLEND_WEIGHT", "")
    if env.strip():
        return float(env)
    return 0.3


def _labeled_rows_from_ledger(path: Path | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in read_rows(path):
        if row.get("event") != "beforeSubmitPrompt":
            continue
        prompt = row.get("prompt_preview") or ""
        if not prompt:
            continue
        label = row.get("expected_action")
        skill_filter = row.get("skill_id")
        for d in row.get("decisions") or []:
            sid = d.get("id")
            if not sid:
                continue
            if skill_filter and sid != skill_filter:
                continue
            action = label or d.get("action")
            if action not in ACTIONS:
                continue
            rows.append(
                {
                    "prompt": prompt,
                    "skill_id": sid,
                    "label": action,
                    "relation_tag": row.get("relation_tag") or "none",
                    "heuristic_score": float(d.get("score") or 0.0),
                    "trigger_overlap": float(d.get("trigger_overlap") or 0.0),
                }
            )
    return rows


def _labeled_rows_from_evals() -> list[dict[str, Any]]:
    eval_path = WORKSPACE / "30_system" / "SKILLS" / "evals" / "skill-verifier-gate.json"
    if not eval_path.is_file():
        return []
    data = json.loads(eval_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for case in data.get("cases") or []:
        inp = case.get("input") or {}
        prompt = inp.get("prompt") or inp.get("text") or ""
        skill_id = case.get("skill_id")
        label = None
        for a in case.get("assertions") or []:
            val = a.get("value") or ""
            if '"action"' in val:
                for act in ACTIONS:
                    if act in val:
                        label = act
                        break
        if not prompt or not skill_id or not label:
            continue
        bundle = rank_skills(prompt, top_k=8, dag_mode=True, include_body=False)
        score_row = next((r for r in bundle if r.get("id") == skill_id), None)
        rows.append(
            {
                "prompt": prompt,
                "skill_id": skill_id,
                "label": label,
                "relation_tag": "none",
                "heuristic_score": float(score_row.get("score") or 0.0) if score_row else 0.0,
                "trigger_overlap": 0.0,
            }
        )
    return rows


def collect_training_rows(*, ledger_path: Path | None = None) -> list[dict[str, Any]]:
    seen: set[tuple[str, str, str]] = set()
    out: list[dict[str, Any]] = []
    for row in _labeled_rows_from_ledger(ledger_path) + _labeled_rows_from_evals():
        key = (row["prompt"], row["skill_id"], row["label"])
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


def _granularity_lookup() -> dict[str, str]:
    if not REGISTRY_PATH.is_file():
        return {}
    try:
        reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        return {s["id"]: s.get("granularity", "procedure") for s in reg.get("skills") or [] if s.get("id")}
    except (json.JSONDecodeError, OSError):
        return {}


def _granularity_score(skill_id: str, gran_map: dict[str, str]) -> float:
    gran = gran_map.get(skill_id, "procedure")
    return GRANULARITY_MAP.get(gran, 0.33)


def _enrich_dag_scores(rows: list[dict[str, Any]]) -> None:
    gran_map = _granularity_lookup()
    for r in rows:
        ranked = rank_skills(r["prompt"], top_k=8, dag_mode=True, include_body=False)
        match = next((x for x in ranked if x.get("id") == r["skill_id"]), {})
        r["dag_score"] = float(match.get("dag_score") or 0.0)
        r["rwr_score"] = float(match.get("rwr_score") or 0.0)
        r["granularity_score"] = _granularity_score(str(r.get("skill_id") or ""), gran_map)


def _rows_to_matrix(
    rows: list[dict[str, Any]],
    *,
    vectorizer: TfidfVectorizer | None = None,
    rel_encoder: LabelEncoder | None = None,
    fit: bool = False,
) -> tuple[np.ndarray, TfidfVectorizer, LabelEncoder]:
    texts = [r["prompt"] for r in rows]
    rels = [r.get("relation_tag") or "none" for r in rows]
    vec = vectorizer or TfidfVectorizer(max_features=8000, ngram_range=(1, 2), sublinear_tf=True)
    if fit:
        tfidf = vec.fit_transform(texts).toarray()
    else:
        tfidf = vec.transform(texts).toarray()

    enc = rel_encoder or LabelEncoder()
    if fit:
        rel_idx = enc.fit_transform(rels)
    else:
        rel_idx = enc.transform(rels)

    rel_one_hot = np.zeros((len(rows), len(enc.classes_)))
    for i, idx in enumerate(rel_idx):
        rel_one_hot[i, idx] = 1.0

    numeric = np.array(
        [
            [
                r.get("heuristic_score", 0.0),
                r.get("trigger_overlap", 0.0),
                float(r.get("dag_score", 0.0)),
                float(r.get("rwr_score", 0.0)),
                float(r.get("granularity_score", 0.33)),
            ]
            for r in rows
        ]
    )
    x = np.hstack([tfidf, rel_one_hot, numeric])
    return x, vec, enc


def evolution_gate_passes(*, skill_id: str, case_count: int | None = None) -> tuple[bool, list[str]]:
    """Run skill_gap_optimize_gate before auto accept_score changes from ledger/ML signals."""
    import subprocess

    eval_path = WORKSPACE / "30_system" / "SKILLS" / "evals" / f"{skill_id}.json"
    harness_eval = WORKSPACE / "30_system" / "SKILLS" / "evals" / "skill-verifier-gate.json"
    count = case_count
    if count is None:
        for path in (eval_path, harness_eval):
            if path.is_file():
                try:
                    count = len(json.loads(path.read_text(encoding="utf-8")).get("cases") or [])
                    break
                except json.JSONDecodeError:
                    pass
        count = count or 0
    script = WORKSPACE / "40_operations" / "scripts" / "skill_gap_optimize_gate.py"
    cmd = [
        sys.executable,
        str(script),
        "--procedural",
        "--case-count",
        str(count),
        "--severity",
        "medium",
        "--category",
        "code",
        "--phi-risk",
        "none",
        "--json",
    ]
    if count > 0:
        cmd.append("--eval-exists")
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(WORKSPACE),
            timeout=45,
            check=False,
        )
        data = json.loads(proc.stdout or "{}")
        return bool(data.get("gate_passes")), list(data.get("blockers") or [])
    except Exception as exc:
        return False, [str(exc)]


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        return max(0, int(raw))
    except ValueError:
        return default


def load_ml_state() -> dict[str, Any]:
    if not ML_STATE_PATH.is_file():
        return {}
    try:
        return json.loads(ML_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_ml_state(state: dict[str, Any]) -> None:
    ML_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    ML_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def ml_blend_active() -> bool:
    """Auto-enable blend when a trained model exists; opt-out with VERIFIER_ML_BLEND=0."""
    if os.environ.get("VERIFIER_ML_BLEND", "").strip() in {"0", "false", "FALSE"}:
        return False
    artifact = load_model()
    min_rows = _env_int("VERIFIER_ML_MIN_ROWS", MIN_LABELED_ROWS)
    if artifact and int(artifact.get("train_count") or 0) >= min_rows:
        return True
    return os.environ.get("VERIFIER_ML_BLEND", "").strip() in {"1", "true", "TRUE"}


def maybe_incremental_train(*, force: bool = False) -> dict[str, Any]:
    """Train or retrain when labeled rows accumulate (usage-driven)."""
    rows = collect_training_rows()
    count = len(rows)
    min_rows = _env_int("VERIFIER_ML_MIN_ROWS", MIN_LABELED_ROWS)
    min_new = _env_int("VERIFIER_ML_MIN_NEW_ROWS", MIN_NEW_ROWS_RETRAIN)
    ml_state = load_ml_state()
    last_train_count = int(ml_state.get("last_train_row_count") or 0)
    model_exists = model_path().is_file()

    should_train = False
    if force and count >= min_rows:
        should_train = True
    elif count >= min_rows and not model_exists:
        should_train = True
    elif count >= min_rows and (count - last_train_count) >= min_new:
        should_train = True

    if not should_train:
        return {
            "ok": False,
            "reason": "accumulating",
            "count": count,
            "min_rows": min_rows,
            "rows_until_train": max(0, min_rows - count),
            "rows_until_retrain": max(0, min_new - (count - last_train_count)) if count >= min_rows else None,
            "last_train_row_count": last_train_count,
        }

    result = train_model(rows, min_rows=min_rows)
    if result.get("ok"):
        save_ml_state(
            {
                "last_train_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "last_train_row_count": count,
                "train_count": result.get("train_count"),
                "classes": result.get("classes"),
            }
        )
    return result


def train_model(
    rows: list[dict[str, Any]] | None = None,
    *,
    out_path: Path | None = None,
    min_rows: int | None = None,
) -> dict[str, Any]:
    if min_rows is None:
        min_rows = _env_int("VERIFIER_ML_MIN_ROWS", MIN_LABELED_ROWS)
    data = rows if rows is not None else collect_training_rows()
    if len(data) < min_rows:
        return {"ok": False, "reason": "insufficient_rows", "count": len(data), "min_rows": min_rows}

    _enrich_dag_scores(data)
    x, vectorizer, rel_encoder = _rows_to_matrix(data, fit=True)
    y = [r["label"] for r in data]
    label_enc = LabelEncoder()
    y_enc = label_enc.fit_transform(y)
    clf = LogisticRegression(max_iter=400)
    clf.fit(x, y_enc)

    artifact = {
        "model": clf,
        "label_encoder": label_enc,
        "relation_encoder": rel_encoder,
        "vectorizer": vectorizer,
        "feature_dim": x.shape[1],
        "train_count": len(data),
    }
    dest = out_path or model_path()
    dest.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(artifact, dest)
    save_ml_state(
        {
            "last_train_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "last_train_row_count": len(data),
            "train_count": len(data),
            "classes": list(label_enc.classes_),
        }
    )
    return {"ok": True, "path": str(dest), "train_count": len(data), "classes": list(label_enc.classes_)}


def load_model(path: Path | None = None) -> dict[str, Any] | None:
    p = path or model_path()
    if not p.is_file():
        return None
    try:
        return joblib.load(p)
    except Exception:
        return None


def predict_action_proba(
    prompt: str,
    skill: dict,
    *,
    relation_tag: str | None = None,
    artifact: dict[str, Any] | None = None,
) -> dict[str, float] | None:
    art = artifact or load_model()
    if not art:
        return None
    rel = relation_tag or "none"
    gran_map = _granularity_lookup()
    row = {
        "prompt": prompt,
        "skill_id": skill.get("id"),
        "relation_tag": rel,
        "heuristic_score": float(skill.get("score") or 0.0),
        "trigger_overlap": float(skill.get("trigger_overlap") or 0.0),
        "dag_score": float(skill.get("dag_score") or 0.0),
        "rwr_score": float(skill.get("rwr_score") or 0.0),
        "granularity_score": _granularity_score(str(skill.get("id") or ""), gran_map),
    }
    try:
        x, _, _ = _rows_to_matrix(
            [row],
            vectorizer=art["vectorizer"],
            rel_encoder=art["relation_encoder"],
            fit=False,
        )
    except ValueError:
        return None
    if x.shape[1] != art.get("feature_dim"):
        return None
    clf = art["model"]
    label_enc: LabelEncoder = art["label_encoder"]
    probs = clf.predict_proba(x)[0]
    return {label_enc.classes_[i]: float(probs[i]) for i in range(len(probs))}


def blend_verify_skill(
    prompt: str,
    skill: dict,
    *,
    verifier_reg: dict | None = None,
    pending_rewrites: set[str] | None = None,
    relation_tag: str | None = None,
) -> dict:
    """Heuristic verify_skill with optional ML probability blend."""
    base = verify_skill(
        prompt,
        skill,
        verifier_reg=verifier_reg,
        pending_rewrites=pending_rewrites,
    )
    if not ml_blend_active():
        return base
    artifact = load_model()
    min_rows = _env_int("VERIFIER_ML_MIN_ROWS", MIN_LABELED_ROWS)
    if not artifact or int(artifact.get("train_count", 0) or 0) < min_rows:
        return base
    probs = predict_action_proba(prompt, skill, relation_tag=relation_tag, artifact=artifact)
    if not probs:
        return base
    w = blend_weight()
    accept_p = probs.get("ACCEPT", 0.0) + probs.get("DECOMPOSE", 0.0) * 0.5
    blended = (1.0 - w) * float(base.get("score") or 0.0) + w * accept_p
    skill_blended = {**skill, "score": round(blended, 4)}
    out = verify_skill(
        prompt,
        skill_blended,
        verifier_reg=verifier_reg,
        pending_rewrites=pending_rewrites,
    )
    out["ml_accept_proba"] = round(accept_p, 4)
    out["blended_score"] = round(blended, 4)
    return out
