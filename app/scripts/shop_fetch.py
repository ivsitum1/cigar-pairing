# -*- coding: utf-8 -*-
"""Fetch product HTML. Scrapling when installed; urllib otherwise.

StealthyFetcher is only used for hosts in STEALTH_HOSTS (Famous Smoke).
Callers must treat fetch failure as 'leave previous stock fields alone'.
"""
from __future__ import annotations

import ssl
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from availability_catalog import wants_stealth

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class FetchResult:
    url: str
    html: str | None
    status: int | None
    error: str | None = None


def scrapling_available() -> bool:
    try:
        from scrapling.fetchers import Fetcher  # noqa: F401
    except ImportError:
        return False
    return True


def _urllib_fetch(url: str, timeout: int) -> FetchResult:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "en,hr;q=0.8"},
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            raw = resp.read()
            charset = resp.headers.get_content_charset() or "utf-8"
            html = raw.decode(charset, "replace")
            return FetchResult(url=url, html=html, status=getattr(resp, "status", 200))
    except urllib.error.HTTPError as e:
        body = None
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:  # noqa: BLE001
            pass
        return FetchResult(url=url, html=body, status=e.code, error=str(e.reason))
    except Exception as e:  # noqa: BLE001 — network, TLS, timeout
        return FetchResult(url=url, html=None, status=None, error=str(e))


def _scrapling_fetch(url: str, timeout: int, stealth: bool) -> FetchResult:
    try:
        if stealth:
            from scrapling.fetchers import StealthyFetcher

            page = StealthyFetcher.fetch(url, headless=True, timeout=timeout * 1000)
        else:
            from scrapling.fetchers import Fetcher

            get = getattr(Fetcher, "get", None) or Fetcher.fetch
            try:
                page = get(url, impersonate="chrome", timeout=timeout)
            except TypeError:
                page = get(url, timeout=timeout)
        html = getattr(page, "text", None) or getattr(page, "body", None) or str(page)
        status = getattr(page, "status", 200) or getattr(page, "status_code", 200)
        if not html:
            return FetchResult(url=url, html=None, status=status, error="empty body")
        return FetchResult(url=url, html=html, status=int(status) if status else 200)
    except Exception as e:  # noqa: BLE001
        return FetchResult(url=url, html=None, status=None, error=str(e))


def fetch_html(
    url: str,
    *,
    timeout: int = 45,
    stealth: bool | None = None,
    prefer_scrapling: bool = True,
    retries: int = 2,
    retry_sleep: float = 8.0,
) -> FetchResult:
    """Lowest fetcher that can work: urllib, or Scrapling when asked/needed."""
    use_stealth = wants_stealth(url) if stealth is None else stealth
    attempt = 0
    while True:
        if prefer_scrapling and scrapling_available():
            result = _scrapling_fetch(url, timeout, stealth=use_stealth)
            if result.html:
                return result
            if result.status and result.status >= 400 and not use_stealth:
                pass
            elif result.html is None and not use_stealth:
                result = _urllib_fetch(url, timeout)
        else:
            result = _urllib_fetch(url, timeout)

        if result.status != 429 or attempt >= retries:
            return result
        attempt += 1
        time.sleep(retry_sleep * attempt)
