"""SQLite-backed store for memory observations and events."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Iterable

from .models import Observation


class MemoryStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        # WAL + busy_timeout: hooks/MCP can open the DB concurrently (Windows/OneDrive).
        conn = sqlite3.connect(str(self.db_path), timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_hash TEXT UNIQUE NOT NULL,
                    session_id TEXT NOT NULL,
                    project_scope TEXT NOT NULL,
                    lifecycle TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    ts TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    observation_id TEXT UNIQUE NOT NULL,
                    event_hash TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    project_scope TEXT NOT NULL,
                    lifecycle TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    source_ref TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    tags_json TEXT NOT NULL,
                    self_eval_json TEXT NOT NULL DEFAULT '{}',
                    mem_type TEXT NOT NULL DEFAULT 'explicit',
                    ts TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS self_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    layer TEXT NOT NULL,
                    score REAL NOT NULL,
                    payload_json TEXT NOT NULL,
                    ts TEXT NOT NULL
                );

                CREATE VIRTUAL TABLE IF NOT EXISTS observations_fts
                USING fts5(
                    observation_id,
                    project_scope,
                    summary,
                    detail,
                    tags
                );
                """
            )
            cols = [row["name"] for row in conn.execute("PRAGMA table_info(observations)").fetchall()]
            if "self_eval_json" not in cols:
                conn.execute("ALTER TABLE observations ADD COLUMN self_eval_json TEXT NOT NULL DEFAULT '{}'")
            if "mem_type" not in cols:
                conn.execute("ALTER TABLE observations ADD COLUMN mem_type TEXT NOT NULL DEFAULT 'explicit'")

    def upsert_event(
        self,
        event_hash: str,
        session_id: str,
        project_scope: str,
        lifecycle: str,
        payload: dict,
        ts: str,
    ) -> bool:
        with self._connect() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO events(event_hash, session_id, project_scope, lifecycle, payload_json, ts)
                    VALUES(?, ?, ?, ?, ?, ?)
                    """,
                    (event_hash, session_id, project_scope, lifecycle, json.dumps(payload, ensure_ascii=False), ts),
                )
                return True
            except sqlite3.IntegrityError:
                return False

    def insert_observation(self, observation_id: str, obs: Observation, self_eval: dict | None = None) -> None:
        tags = ",".join(obs.tags)
        self_eval = self_eval or {}
        # Single transaction so the observations row and its FTS mirror stay in
        # sync. The FTS row is deleted first to avoid duplicates when an
        # observation_id is re-inserted (INSERT OR REPLACE on observations does
        # not cascade to the contentless FTS table).
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO observations(
                    observation_id, event_hash, session_id, project_scope, lifecycle,
                    summary, detail, source_ref, confidence, tags_json, self_eval_json, mem_type, ts
                )
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    observation_id,
                    obs.event_hash,
                    obs.session_id,
                    obs.project_scope,
                    obs.lifecycle,
                    obs.summary,
                    obs.detail,
                    obs.source_ref,
                    obs.confidence,
                    json.dumps(obs.tags, ensure_ascii=False),
                    json.dumps(self_eval, ensure_ascii=False),
                    obs.mem_type,
                    obs.ts,
                ),
            )
            conn.execute(
                "DELETE FROM observations_fts WHERE observation_id = ?",
                (observation_id,),
            )
            conn.execute(
                """
                INSERT INTO observations_fts(observation_id, project_scope, summary, detail, tags)
                VALUES(?, ?, ?, ?, ?)
                """,
                (observation_id, obs.project_scope, obs.summary, obs.detail, tags),
            )

    def insert_self_eval(self, layer: str, score: float, payload: dict, ts: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO self_evaluations(layer, score, payload_json, ts)
                VALUES(?, ?, ?, ?)
                """,
                (layer, score, json.dumps(payload, ensure_ascii=False), ts),
            )

    def cleanup_old(self, cutoff_iso: str) -> dict[str, int]:
        """Delete events/observations (and their FTS mirror) older than cutoff.

        cutoff_iso is an ISO-8601 timestamp; rows with ts < cutoff_iso are
        removed. Returns counts of deleted rows per table.
        """
        with self._connect() as conn:
            stale_ids = [
                row["observation_id"]
                for row in conn.execute(
                    "SELECT observation_id FROM observations WHERE ts < ?",
                    (cutoff_iso,),
                ).fetchall()
            ]
            for obs_id in stale_ids:
                conn.execute(
                    "DELETE FROM observations_fts WHERE observation_id = ?",
                    (obs_id,),
                )
            obs_deleted = conn.execute(
                "DELETE FROM observations WHERE ts < ?", (cutoff_iso,)
            ).rowcount
            ev_deleted = conn.execute(
                "DELETE FROM events WHERE ts < ?", (cutoff_iso,)
            ).rowcount
            se_deleted = conn.execute(
                "DELETE FROM self_evaluations WHERE ts < ?", (cutoff_iso,)
            ).rowcount
        return {
            "observations": int(obs_deleted),
            "events": int(ev_deleted),
            "self_evaluations": int(se_deleted),
        }

    def prune_stale(
        self,
        cutoff_iso: str,
        *,
        min_confidence: float = 0.2,
        dry_run: bool = False,
    ) -> dict[str, int]:
        """Prune stale observations: older than cutoff AND low-confidence.

        Addresses the named "stale facts never pruned" failure mode: memory
        that is both old and low-confidence actively degrades retrieval quality.
        High-confidence facts survive regardless of age. With dry_run=True no
        rows are deleted; the candidate count is returned for inspection.
        """
        with self._connect() as conn:
            stale_ids = [
                row["observation_id"]
                for row in conn.execute(
                    "SELECT observation_id FROM observations WHERE ts < ? AND confidence < ?",
                    (cutoff_iso, min_confidence),
                ).fetchall()
            ]
            if dry_run or not stale_ids:
                return {"candidates": len(stale_ids), "pruned": 0}
            placeholders = ",".join("?" for _ in stale_ids)
            conn.execute(
                f"DELETE FROM observations_fts WHERE observation_id IN ({placeholders})",
                tuple(stale_ids),
            )
            pruned = conn.execute(
                f"DELETE FROM observations WHERE observation_id IN ({placeholders})",
                tuple(stale_ids),
            ).rowcount
        return {"candidates": len(stale_ids), "pruned": int(pruned)}

    def search(self, query: str, project_scope: str, limit: int = 10) -> list[dict]:
        with self._connect() as conn:
            try:
                rows = conn.execute(
                    """
                    SELECT o.observation_id, o.lifecycle, o.summary, o.source_ref, o.ts, o.confidence
                    FROM observations_fts f
                    JOIN observations o ON o.observation_id = f.observation_id
                    WHERE observations_fts MATCH ?
                      AND o.project_scope = ?
                    ORDER BY o.ts DESC
                    LIMIT ?
                    """,
                    (query, project_scope, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                like_query = f"%{query}%"
                rows = conn.execute(
                    """
                    SELECT observation_id, lifecycle, summary, source_ref, ts, confidence
                    FROM observations
                    WHERE project_scope = ?
                      AND (summary LIKE ? OR detail LIKE ?)
                    ORDER BY ts DESC
                    LIMIT ?
                    """,
                    (project_scope, like_query, like_query, limit),
                ).fetchall()
            return [dict(row) for row in rows]

    def search_cross_project(self, query: str, limit: int = 10) -> list[dict]:
        """Conscious cross-project search; hooks must never call this."""
        with self._connect() as conn:
            try:
                rows = conn.execute(
                    """
                    SELECT o.observation_id, o.project_scope, o.lifecycle, o.summary,
                           o.source_ref, o.ts, o.confidence
                    FROM observations_fts f
                    JOIN observations o ON o.observation_id = f.observation_id
                    WHERE observations_fts MATCH ?
                    ORDER BY o.ts DESC
                    LIMIT ?
                    """,
                    (query, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                like_query = f"%{query}%"
                rows = conn.execute(
                    """
                    SELECT observation_id, project_scope, lifecycle, summary, source_ref, ts, confidence
                    FROM observations
                    WHERE summary LIKE ? OR detail LIKE ?
                    ORDER BY ts DESC
                    LIMIT ?
                    """,
                    (like_query, like_query, limit),
                ).fetchall()
            return [dict(row) for row in rows]

    def timeline(self, project_scope: str, limit: int = 25) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT observation_id, lifecycle, summary, source_ref, ts, confidence
                FROM observations
                WHERE project_scope = ?
                ORDER BY ts DESC
                LIMIT ?
                """,
                (project_scope, limit),
            ).fetchall()
            return [dict(row) for row in rows]

    def get_observations(self, ids: Iterable[str]) -> list[dict]:
        ids = list(ids)
        if not ids:
            return []
        placeholders = ",".join("?" for _ in ids)
        with self._connect() as conn:
            rows = conn.execute(
                f"""
                SELECT observation_id, lifecycle, summary, detail, source_ref, ts, confidence, tags_json, self_eval_json, mem_type
                FROM observations
                WHERE observation_id IN ({placeholders})
                ORDER BY ts DESC
                """,
                tuple(ids),
            ).fetchall()
            out: list[dict] = []
            for row in rows:
                row_dict = dict(row)
                row_dict["tags"] = json.loads(row_dict.pop("tags_json"))
                row_dict["self_eval"] = json.loads(row_dict.pop("self_eval_json"))
                out.append(row_dict)
            return out

    def self_eval_summary(self) -> dict:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT layer, COUNT(*) as count, AVG(score) as avg_score
                FROM self_evaluations
                GROUP BY layer
                """
            ).fetchall()
            out = {}
            for row in rows:
                out[row["layer"]] = {"count": row["count"], "avg_score": round(row["avg_score"], 3)}
            return out

