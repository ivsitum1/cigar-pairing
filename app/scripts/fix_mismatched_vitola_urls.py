"""Clear or repair vitola.url when path shape contradicts vitola name.

Safe rules:
1) Name encodes shape F; primary url encodes different shape G.
2) Prefer regionLinks.*.url that encodes F (keep as url if Neptune/HR product).
3) Else set url to null (regionLinks remain for EU/USA).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "src/data/cigars.json"

URL_SHAPE = {
    "lancero": re.compile(r"lancero|laguito", re.I),
    "robusto": re.compile(r"robusto|rothschild", re.I),
    "toro": re.compile(r"(?<![a-z])toro(?![a-z])", re.I),
    "churchill": re.compile(r"churchill|double-?corona|lonsdale", re.I),
    "gordo": re.compile(r"gordo|gigante", re.I),
    "corona": re.compile(r"corona|panetela|panatela", re.I),
    "figurado": re.compile(r"torpedo|belicoso|piramide|perfecto|diadema|figurado", re.I),
}

NAME_RULES = [
    ("figurado", re.compile(r"figurado|torpedo|belicoso|pir[aá]mide|piramide|pyramid|perfecto|diadema|salomon|culebra", re.I)),
    ("lancero", re.compile(r"lancero|laguito\s*no\.?\s*1", re.I)),
    ("churchill", re.compile(r"churchill|julieta|double corona|doble corona|prominente|presidente|lonsdale|larga corona", re.I)),
    ("gordo", re.compile(r"gordo|gigante|magnum 60|grande extra|\bgrande\b", re.I)),
    ("toro", re.compile(r"\btoro\b|ca[nñ]onazo", re.I)),
    ("corona", re.compile(r"corona gorda|gran corona|grand corona|half corona|petit corona|short corona|\bcorona\b|mareva|minuto|\bperla\b|cadete|pan[ae]tela", re.I)),
    ("robusto", re.compile(r"robusto|rothschild|epicure no\.?\s?2", re.I)),
]


def classify_name(name: str) -> str | None:
    for fam, rx in NAME_RULES:
        if rx.search(name):
            return fam
    return None


def shapes_in(text: str) -> set[str]:
    return {fam for fam, rx in URL_SHAPE.items() if rx.search(text)}


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    cleared = 0
    repaired = 0
    examples: list[str] = []

    for c in data:
        for v in c.get("vitolas") or []:
            name = v.get("name") or ""
            primary = v.get("url") or ""
            if not primary:
                continue
            fam = classify_name(name)
            if not fam:
                continue
            own = URL_SHAPE[fam]
            if not own.search(name):
                continue
            if own.search(primary):
                continue
            foreign = shapes_in(primary) - {fam}
            if not foreign:
                continue

            # try regionLinks with matching shape
            replacement = None
            for link in (v.get("regionLinks") or {}).values():
                u = (link or {}).get("url") or ""
                if u and own.search(u) and not (shapes_in(u) - {fam}):
                    replacement = u
                    break
                if u and own.search(u):
                    replacement = u
                    break

            old = primary
            if replacement and replacement != primary:
                v["url"] = replacement
                repaired += 1
                action = f"REPAIR → {replacement}"
            else:
                v["url"] = None
                cleared += 1
                action = "CLEAR"
            if len(examples) < 25:
                examples.append(
                    f"{c['brand']} / {c['line']} · {name}: {action}\n  was: {old}"
                )

    PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"repaired={repaired} cleared={cleared}")
    for e in examples:
        print(e)


if __name__ == "__main__":
    main()
