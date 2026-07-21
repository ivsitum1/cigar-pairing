from __future__ import annotations

import io
import xml.etree.ElementTree as ET


def iter_sitemap_locs(xml_text: str) -> list[str]:
    """Extract <loc> values from both urlset and sitemapindex documents."""
    locs: list[str] = []
    src = io.BytesIO(xml_text.encode("utf-8", "replace"))
    for _event, elem in ET.iterparse(src, events=("end",)):
        if elem.tag.endswith("loc") and elem.text:
            locs.append(elem.text.strip())
        elem.clear()
    return locs

