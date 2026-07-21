from __future__ import annotations

import html as html_lib
import re
from typing import Any


_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")


def _strip_html(s: str) -> str:
    s = _TAG_RE.sub(" ", s)
    s = html_lib.unescape(s)
    return _WS_RE.sub(" ", s).strip()


def _empty_details() -> dict[str, Any]:
    return {
        "wrapper": None,
        "binder": None,
        "filler": None,
        "origin": None,
        "strength": None,
        "burnTimeMin": None,
        "size": None,
        "ringGauge": None,
        "lengthIn": None,
        "lengthCm": None,
        "diameterCm": None,
        "boxPressed": None,
        "flavoured": None,
        "tabacalera": None,
        "brandLabel": None,
    }


def _parse_yes_no(value: str) -> bool | None:
    v = value.lower().strip()
    if v in ("yes", "ja", "da", "true", "1"):
        return True
    if v in ("no", "nein", "ne", "false", "0"):
        return False
    return None


def parse_humidor_product_details(page_html: str) -> dict[str, Any]:
    """Extract SPECIFIKACIJE cards from a Humidor product page."""
    out = _empty_details()

    # Prefer brand label from the main product area (avoid related products).
    brand_scope = page_html
    related_idx = page_html.lower().find("related products")
    if related_idx > 0:
        brand_scope = page_html[:related_idx]
    brand_m = re.search(
        r'<span[^>]*class="[^"]*product-brand-label[^"]*"[^>]*>(.*?)</span>',
        brand_scope,
        re.IGNORECASE | re.DOTALL,
    )
    if brand_m:
        out["brandLabel"] = _strip_html(brand_m.group(1)) or None

    # Prefer the specs grid block when present.
    grid_m = re.search(
        r'<div class="product-specs-grid">(.*?)</div>\s*(?=<section|</main|</div>\s*<section)',
        page_html,
        re.IGNORECASE | re.DOTALL,
    )
    scope = grid_m.group(1) if grid_m else page_html

    pairs = re.findall(
        r'class="product-spec-card__label"[^>]*>(.*?)</div>\s*'
        r'<div class="product-spec-card__value"[^>]*>(.*?)</div>',
        scope,
        re.IGNORECASE | re.DOTALL,
    )
    for label_html, value_html in pairs:
        label = _strip_html(label_html).lower()
        value = _strip_html(value_html)

        if "wrapper" in label:
            out["wrapper"] = value or None
        elif "binder" in label:
            out["binder"] = value or None
        elif "filler" in label:
            out["filler"] = value or None
        elif "origin" in label:
            out["origin"] = value or None
        elif "length" in label or "dužina" in label or "duzina" in label:
            inch_m = re.search(r"([\d]+(?:[.,]\d+)?)\s*inch", value, re.IGNORECASE)
            cm_m = re.search(r"([\d]+(?:[.,]\d+)?)\s*cm", value, re.IGNORECASE)
            if inch_m:
                out["lengthIn"] = float(inch_m.group(1).replace(",", "."))
            if cm_m:
                out["lengthCm"] = float(cm_m.group(1).replace(",", "."))
        elif "diameter" in label or "ring" in label:
            ring_m = re.search(r"ring\s*(\d+)", value, re.IGNORECASE)
            if ring_m:
                out["ringGauge"] = int(ring_m.group(1))
            cm_m = re.search(r"([\d]+(?:[.,]\d+)?)\s*cm", value, re.IGNORECASE)
            if cm_m:
                out["diameterCm"] = float(cm_m.group(1).replace(",", "."))
        elif "strength" in label or "snaga" in label:
            aria_m = re.search(r'aria-label="(\d+)\s*/\s*5"', value_html, re.IGNORECASE)
            if aria_m:
                out["strength"] = int(aria_m.group(1))
            else:
                class_m = re.search(r'class="[^"]*\bs(\d)\b', value_html, re.IGNORECASE)
                if class_m:
                    out["strength"] = int(class_m.group(1))
        elif "burning" in label or "vrijeme" in label:
            min_m = re.search(r"(\d+)\s*min", value, re.IGNORECASE)
            if min_m:
                out["burnTimeMin"] = int(min_m.group(1))

    return out


def parse_cigarworld_variant_info(page_html: str) -> dict[str, Any]:
    """Extract VariantInfo key/value pairs from a Cigarworld product page."""
    out = _empty_details()

    items = re.findall(
        r'class="[^"]*VariantInfo-itemName[^"]*"[^>]*>(.*?)</div>\s*'
        r'<div class="[^"]*VariantInfo-itemValue[^"]*"[^>]*>(.*?)</div>',
        page_html,
        re.IGNORECASE | re.DOTALL,
    )
    for name_html, value_html in items:
        name = _strip_html(name_html).lower()
        value = _strip_html(value_html)
        if not name:
            continue

        if name == "size":
            out["size"] = value or None
        elif "wrapper" in name:
            out["wrapper"] = value or None
        elif "binder" in name:
            out["binder"] = value or None
        elif "filler" in name:
            out["filler"] = value or None
        elif "ring" in name or "diameter" in name:
            ring_m = re.search(r"\b(\d{2,3})\b", value)
            if ring_m:
                out["ringGauge"] = int(ring_m.group(1))
            cm_m = re.search(r"([\d]+(?:[.,]\d+)?)\s*cm", value, re.IGNORECASE)
            if cm_m:
                out["diameterCm"] = float(cm_m.group(1).replace(",", "."))
        elif "boxpress" in name:
            out["boxPressed"] = _parse_yes_no(value)
        elif "flavour" in name or "flavor" in name:
            out["flavoured"] = _parse_yes_no(value)
        elif "tabacalera" in name:
            out["tabacalera"] = value or None

    return out


def apply_details_to_item(item: dict, details: dict[str, Any]) -> None:
    """Copy parsed details into item.details and best-effort attribute fields."""
    item["details"] = details
    attrs = item.setdefault("attributes", {})
    if not isinstance(attrs, dict):
        attrs = {}
        item["attributes"] = attrs

    if details.get("brandLabel") and not attrs.get("brand"):
        attrs["brand"] = details["brandLabel"]
    if details.get("size") and not attrs.get("vitola"):
        attrs["vitola"] = details["size"]

    dims = attrs.get("dimensions")
    if not isinstance(dims, dict):
        dims = {"lengthIn": None, "ringGauge": None}
        attrs["dimensions"] = dims
    if details.get("lengthIn") is not None and dims.get("lengthIn") is None:
        dims["lengthIn"] = details["lengthIn"]
    if details.get("ringGauge") is not None and dims.get("ringGauge") is None:
        dims["ringGauge"] = details["ringGauge"]
