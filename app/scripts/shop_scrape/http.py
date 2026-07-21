from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


def iso_utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _cache_key(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class HttpConfig:
    user_agent: str
    cache_dir: Path
    cache_ttl_s: int
    per_host_delay_s: float
    timeout_s: int
    max_retries: int
    cache_enabled: bool = True


class HttpClient:
    def __init__(self, config: HttpConfig):
        self._cfg = config
        self._last_by_host: dict[str, float] = {}
        self._cfg.cache_dir.mkdir(parents=True, exist_ok=True)

    def _throttle(self, url: str) -> None:
        host = urllib.parse.urlparse(url).netloc
        last = self._last_by_host.get(host)
        if last is None:
            self._last_by_host[host] = time.time()
            return
        wait = self._cfg.per_host_delay_s - (time.time() - last)
        if wait > 0:
            time.sleep(wait)
        self._last_by_host[host] = time.time()

    def _cache_path(self, url: str) -> Path:
        return self._cfg.cache_dir / f"{_cache_key(url)}.json"

    def _read_cache(self, url: str) -> str | None:
        if not self._cfg.cache_enabled:
            return None
        p = self._cache_path(url)
        if not p.exists():
            return None
        try:
            st = p.stat()
        except OSError:
            return None
        if self._cfg.cache_ttl_s > 0 and (time.time() - st.st_mtime) > self._cfg.cache_ttl_s:
            return None
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
            body = obj.get("body")
            return body if isinstance(body, str) else None
        except Exception:
            return None

    def _write_cache(self, url: str, body_text: str) -> None:
        if not self._cfg.cache_enabled:
            return
        p = self._cache_path(url)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps({"url": url, "body": body_text}, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, p)

    def get_text(self, url: str, *, headers: dict[str, str] | None = None) -> str:
        cached = self._read_cache(url)
        if cached is not None:
            return cached

        merged_headers = {"User-Agent": self._cfg.user_agent, "Accept": "*/*"}
        if headers:
            merged_headers.update(headers)

        for attempt in range(self._cfg.max_retries + 1):
            try:
                self._throttle(url)
                req = urllib.request.Request(url, headers=merged_headers)
                with urllib.request.urlopen(req, timeout=self._cfg.timeout_s) as resp:
                    raw = resp.read()
                text = raw.decode("utf-8", "replace")
                self._write_cache(url, text)
                return text
            except urllib.error.HTTPError as e:
                if e.code in (429, 500, 502, 503, 504) and attempt < self._cfg.max_retries:
                    time.sleep(2**attempt)
                    continue
                raise
            except Exception:
                if attempt < self._cfg.max_retries:
                    time.sleep(2**attempt)
                    continue
                raise

        raise RuntimeError("unreachable")

    def get_json(self, url: str, *, headers: dict[str, str] | None = None) -> object:
        text = self.get_text(url, headers=headers)
        return json.loads(text)

