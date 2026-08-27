"""Second pass: vitola name has lancero but url does not."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

PATH = Path(__file__).resolve().parents[1] / "src/data/cigars.json"
LANCERO = re.compile(r"lancero|laguito", re.I)

data = json.loads(PATH.read_text(encoding="utf-8"))
n = 0
for c in data:
    for v in c.get("vitolas") or []:
        name = v.get("name") or ""
        url = v.get("url") or ""
        if not url or not LANCERO.search(name):
            continue
        if LANCERO.search(url):
            continue
        repl = None
        for link in (v.get("regionLinks") or {}).values():
            u = (link or {}).get("url") or ""
            if u and LANCERO.search(u):
                repl = u
                break
        print(f"{'REPAIR' if repl else 'CLEAR'} {c['brand']} / {c['line']} · {name}")
        print(f"  was: {url}")
        v["url"] = repl
        if repl:
            print(f"  now: {repl}")
        n += 1

PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"total={n}")
