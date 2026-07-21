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


def _wc_attr_map(attributes: list[Any] | None) -> dict[str, str]:
    out: dict[str, str] = {}
    if not isinstance(attributes, list):
        return out
    for attr in attributes:
        if not isinstance(attr, dict):
            continue
        name = attr.get("name") if isinstance(attr.get("name"), str) else ""
        taxonomy = attr.get("taxonomy") if isinstance(attr.get("taxonomy"), str) else ""
        terms = attr.get("terms") if isinstance(attr.get("terms"), list) else []
        values: list[str] = []
        for t in terms:
            if isinstance(t, dict) and isinstance(t.get("name"), str) and t["name"].strip():
                values.append(t["name"].strip())
        if not name or not values:
            continue
        key = (taxonomy or name).lower()
        out[key] = " / ".join(values)
        out[name.lower()] = " / ".join(values)
    return out


def _map_strength_label(value: str) -> int | None:
    v = value.casefold()
    if any(x in v for x in ("blag", "mild", "light")):
        return 2
    if "srednje jak" in v or "medium-full" in v or "medium full" in v:
        return 4
    if any(x in v for x in ("srednj", "medium")):
        return 3
    if any(x in v for x in ("jak", "full", "strong")):
        return 5
    return None


def parse_wc_store_attributes(attributes: list[Any] | None) -> dict[str, Any]:
    """Map WooCommerce Store API product attributes → details (Havana etc.)."""
    out = _empty_details()
    amap = _wc_attr_map(attributes)
    if not amap:
        return out

    def pick(*keys: str) -> str | None:
        for k in keys:
            v = amap.get(k.lower())
            if v:
                return v
        return None

    out["wrapper"] = pick("wrapper", "pa_wrapper", "omot")
    out["binder"] = pick("binder", "pa_binder", "spona", "podveza")
    out["filler"] = pick("filler", "pa_filler", "punilo")
    out["origin"] = pick("zemlja porijekla", "pa_zemlja-porijekla", "origin", "country")
    out["brandLabel"] = pick("brand", "pa_brand")
    out["size"] = pick("vitola", "pa_vitola")

    ring = pick("ring", "pa_ring")
    if ring:
        ring_m = re.search(r"\d{2,3}", ring)
        if ring_m:
            out["ringGauge"] = int(ring_m.group(0))

    length = pick("duljina", "pa_duljina", "length")
    if length:
        cm_m = re.search(r"([\d]+(?:[.,]\d+)?)\s*cm", length, re.IGNORECASE)
        inch_m = re.search(r"([\d]+(?:[.,]\d+)?)\s*(?:inch|in)\b", length, re.IGNORECASE)
        if cm_m:
            out["lengthCm"] = float(cm_m.group(1).replace(",", "."))
        if inch_m:
            out["lengthIn"] = float(inch_m.group(1).replace(",", "."))
        elif out["lengthCm"] is not None:
            out["lengthIn"] = round(out["lengthCm"] / 2.54, 2)

    strength = pick("jačina", "jacina", "pa_jacina", "strength")
    if strength:
        out["strength"] = _map_strength_label(strength)

    burn = pick("vrijeme pušenja", "vrijeme pusenja", "pa_vrijeme-pusenja", "burn")
    if burn:
        # "45-60" → midpoint
        range_m = re.search(r"(\d+)\s*[-–]\s*(\d+)", burn)
        if range_m:
            out["burnTimeMin"] = int(round((int(range_m.group(1)) + int(range_m.group(2))) / 2))
        else:
            one = re.search(r"(\d+)", burn)
            if one:
                out["burnTimeMin"] = int(one.group(1))

    return out


def parse_holts_line_details(page_html: str) -> dict[str, Any]:
    """Country / wrapper / strength from Holt's PDP cigar-details block."""
    out = _empty_details()
    block_m = re.search(
        r'class="pdp-cigar-details"(.*?)<div class="sizes"',
        page_html,
        re.IGNORECASE | re.DOTALL,
    )
    if not block_m:
        block_m = re.search(
            r'class="pdp-cigar-details"(.*?)</div>\s*<div class="clear"',
            page_html,
            re.IGNORECASE | re.DOTALL,
        )
    scope = block_m.group(1) if block_m else ""

    strength_m = re.search(
        r'Strength:.*?<div class="value">\s*([^<]+)',
        scope,
        re.IGNORECASE | re.DOTALL,
    )
    if strength_m:
        out["strength"] = _map_strength_label(_strip_html(strength_m.group(1)))

    for key, field in (
        ("Country", "origin"),
        ("Wrapper", "wrapper"),
        ("Binder", "binder"),
        ("Filler", "filler"),
    ):
        m = re.search(
            rf'{key}:\s*<span class="value">\s*([^<]+)',
            scope,
            re.IGNORECASE,
        )
        if m:
            val = _strip_html(m.group(1))
            out[field] = val or None

    return out


def parse_holts_vitola_rows(page_html: str) -> list[dict[str, Any]]:
    """Extract vitola rows (name, size, pack prices) from Holt's products-list-table."""
    table_m = re.search(
        r'id="products-list-table"(.*?)</table>',
        page_html,
        re.IGNORECASE | re.DOTALL,
    )
    if not table_m:
        return []
    table = table_m.group(1)
    rows: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    pending_pack: str | None = None

    for m in re.finditer(
        r'<td class="tproduct-name"[^>]*>(.*?)</td>'
        r'|<td class="tpacking"[^>]*>\s*<span>(.*?)</span>\s*</td>'
        r'|<td class="tprice[^"]*"[^>]*>\s*<span>\s*\$?\s*([\d]+(?:\.\d{2})?)\s*</span>',
        table,
        re.IGNORECASE | re.DOTALL,
    ):
        if m.group(1) is not None:
            name_html = m.group(1)
            name_block = re.search(
                r'class="name"[^>]*>(.*?)</div>',
                name_html,
                re.IGNORECASE | re.DOTALL,
            )
            raw_name = _strip_html(name_block.group(1) if name_block else name_html)
            ring_m = re.search(r"-\s*([\d]+(?:\.\d+)?)\s*[x×]\s*(\d+)", raw_name)
            vitola_name = re.sub(r"\s*-\s*[\d.]+\s*[x×]\s*\d+\s*$", "", raw_name).strip()
            current = {
                "name": vitola_name or raw_name,
                "lengthIn": float(ring_m.group(1)) if ring_m else None,
                "ringGauge": int(ring_m.group(2)) if ring_m else None,
                "packs": [],
            }
            rows.append(current)
            pending_pack = None
            continue
        if current is None:
            continue
        if m.group(2) is not None:
            pending_pack = _strip_html(m.group(2))
            continue
        if m.group(3) is not None:
            price = float(m.group(3))
            pack_label = pending_pack or "unknown"
            pending_pack = None
            count = None
            pack_type = "unknown"
            low = pack_label.lower()
            if low.startswith("single"):
                pack_type = "single"
                count = 1
            else:
                cm = re.search(r"(\d+)", pack_label)
                if cm:
                    count = int(cm.group(1))
                if "box" in low:
                    pack_type = "box"
                elif "tin" in low:
                    pack_type = "tin"
                elif "pack" in low:
                    pack_type = "pack"
            current["packs"].append(
                {"label": pack_label, "type": pack_type, "count": count, "price": price}
            )

    return [r for r in rows if r.get("name")]


def prefer_holts_pack(packs: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not packs:
        return None
    singles = [p for p in packs if p.get("type") == "single" and p.get("price") is not None]
    if singles:
        return min(singles, key=lambda p: float(p["price"]))
    priced = [p for p in packs if p.get("price") is not None]
    if not priced:
        return None

    def unit_price(p: dict[str, Any]) -> float:
        count = p.get("count") or 1
        return float(p["price"]) / max(int(count), 1)

    best = min(priced, key=unit_price)
    return {
        "label": best.get("label"),
        "type": "single_equiv",
        "count": 1,
        "price": round(unit_price(best), 2),
        "sourcePack": best,
    }


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
