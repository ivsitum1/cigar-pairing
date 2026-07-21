from __future__ import annotations

import json
import re
from typing import Any


_JSONLD_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)


def _flatten_jsonld(obj: Any) -> list[dict]:
    out: list[dict] = []
    if isinstance(obj, dict):
        if isinstance(obj.get("@graph"), list):
            for x in obj["@graph"]:
                out.extend(_flatten_jsonld(x))
        out.append(obj)
    elif isinstance(obj, list):
        for x in obj:
            out.extend(_flatten_jsonld(x))
    return [x for x in out if isinstance(x, dict)]


def _is_product_type(t: Any) -> bool:
    if isinstance(t, str):
        return t.lower() == "product"
    if isinstance(t, list):
        return any(isinstance(x, str) and x.lower() == "product" for x in t)
    return False


def extract_jsonld_products(html: str) -> list[dict]:
    """Return JSON-LD dicts that look like schema.org Product nodes."""
    products: list[dict] = []
    for m in _JSONLD_RE.finditer(html):
        raw = (m.group(1) or "").strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except Exception:
            continue
        for node in _flatten_jsonld(data):
            if _is_product_type(node.get("@type")):
                products.append(node)
    return products

