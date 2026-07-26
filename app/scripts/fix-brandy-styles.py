# -*- coding: utf-8 -*-
"""One-shot fixes for brandies.json after MASTER export."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "src" / "data" / "brandies.json"


def fold(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def fix_style(name: str, style: str) -> str:
    f = fold(name)
    if re.search(r"(?:\bxo\b|x\.o\.|extra old|hors d|paradis|louis xiii)", f):
        if re.search(r"cognac|hennessy|martell|remy|camus|hine|delamain|courvoisier|davidoff|frapin|gautier|ferrand|leyrat", f):
            return "cognac-xo"
    if re.search(r"vsop|v\.s\.o\.p|1738", f):
        if re.search(r"cognac|hennessy|martell|remy|camus|hine|delamain|courvoisier|davidoff", f):
            return "cognac-vsop"
    if re.search(r"\bvs\b|very special", f) and re.search(r"hennessy|martell|remy|cognac", f):
        return "cognac-vs"
    return style


def main() -> int:
    items = json.loads(OUT.read_text(encoding="utf-8"))
    n = 0
    for d in items:
        old = d.get("style")
        new = fix_style(d["name"], old)
        if new != old:
            d["style"] = new
            n += 1
        notes = d.get("notes") or {}
        for lang in ("hr", "en"):
            t = notes.get(lang) or ""
            if re.search(r"purist", t, re.I):
                t = re.sub(r"\b[Pp]urist\b", "Precizan", t)
                t = re.sub(r"\bpurist\b", "precise", t, flags=re.I)
                notes[lang] = t
                d["notes"] = notes
                n += 1
        # additiveDetail may be dict after localize — skip string pejoratives already handled
    OUT.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"fixed {n} fields in brandies.json ({len(items)} items)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
