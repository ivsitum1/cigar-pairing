"""HTTP worker service exposing memory health and search APIs."""
from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from .config import load_config
from .ingest import MemoryIngestor
from .injection import ContextInjector
from .models import MemoryEvent, utc_now_iso
from .retrieval import MemoryRetriever
from .self_eval import MemorySelfEvaluator
from .store import MemoryStore


class MemoryWorkerHandler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

    def _services(self) -> tuple[MemoryIngestor, MemoryRetriever, ContextInjector]:
        config = load_config()
        store = MemoryStore(config.sqlite_path)
        evaluator = MemorySelfEvaluator(config.self_eval_log_path)
        ingestor = MemoryIngestor(store, config.raw_events_path, self_evaluator=evaluator)
        retriever = MemoryRetriever(store, self_evaluator=evaluator)
        injector = ContextInjector(retriever, config.context_cache_path, config.max_injection_chars, self_evaluator=evaluator)
        return ingestor, retriever, injector

    @staticmethod
    def _int_param(params: dict, name: str, default: int) -> int:
        try:
            return int(params.get(name, [str(default)])[0])
        except (ValueError, TypeError):
            return default

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        _, retriever, injector = self._services()
        if parsed.path == "/":
            html = """<!doctype html><html><head><meta charset="utf-8"><title>Agent Memory Viewer</title></head>
            <body><h1>Agent Memory Viewer</h1><p>Use /api/search, /api/timeline, /api/get_observations, /api/inject.</p></body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return
        if parsed.path == "/health":
            self._json(
                200,
                {"ok": True, "service": "agent-rules-memory", "self_eval_summary": retriever.store.self_eval_summary()},
            )
            return
        if parsed.path == "/api/search":
            query = params.get("query", [""])[0]
            scope = params.get("project_scope", ["default"])[0]
            limit = self._int_param(params, "limit", 10)
            self._json(200, retriever.search(query=query, project_scope=scope, limit=limit))
            return
        if parsed.path == "/api/timeline":
            scope = params.get("project_scope", ["default"])[0]
            limit = self._int_param(params, "limit", 25)
            self._json(200, retriever.timeline(project_scope=scope, limit=limit))
            return
        if parsed.path == "/api/get_observations":
            ids = [x.strip() for x in params.get("ids", [""])[0].split(",") if x.strip()]
            self._json(200, retriever.get_observations(ids))
            return
        if parsed.path == "/api/inject":
            scope = params.get("project_scope", ["default"])[0]
            query = params.get("query", ["recent context"])[0]
            context = injector.build_context(project_scope=scope, query=query)
            injector.cache_context(context)
            self._json(200, {"context": context})
            return
        self._json(404, {"error": "Not found"})

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/ingest":
            self._json(404, {"error": "Not found"})
            return
        ingestor, _, _ = self._services()
        try:
            content_len = int(self.headers.get("Content-Length", "0"))
        except (ValueError, TypeError):
            content_len = 0
        body = self.rfile.read(content_len).decode("utf-8") if content_len else "{}"
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._json(400, {"error": "Invalid JSON body"})
            return
        if not isinstance(payload, dict):
            self._json(400, {"error": "JSON body must be an object"})
            return
        event = MemoryEvent(
            lifecycle=payload.get("lifecycle", "unknown"),
            session_id=payload.get("session_id", "unknown"),
            project_scope=payload.get("project_scope", "default"),
            payload=payload.get("payload", {}),
            ts=payload.get("ts") or utc_now_iso(),
        )
        self._json(200, ingestor.ingest(event))


def run_worker() -> None:
    config = load_config()
    server = HTTPServer((config.worker_host, config.worker_port), MemoryWorkerHandler)
    print(f"Memory worker running at http://{config.worker_host}:{config.worker_port}")
    server.serve_forever()

