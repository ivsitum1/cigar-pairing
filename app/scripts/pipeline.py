# -*- coding: utf-8 -*-
"""Orkestrator data pipelinea — vrti korake ispravnim redoslijedom i staje na
prvoj gresci, umjesto rucnog nabrajanja skripti iz README-a.

    python scripts/pipeline.py --category whisky            # regeneracija iz Excela
    python scripts/pipeline.py --category whisky --scrape   # + osvjezi shop katalog
    python scripts/pipeline.py --category cigars --humidor-catalog path/do/humidor_catalog.txt
    python scripts/pipeline.py --category rum --list        # samo ispisi korake
    python scripts/pipeline.py --category brandy --from excel-to-brandy-json.py
    python scripts/pipeline.py --category all               # sve kategorije (bez scrape)

Rucna kalibracija MASTER sheetova u Excelu ide izmedju build-*-excel i
excel-to-*-json koraka: pokreni pipeline s --list, stani gdje treba pa
nastavi s --from.
"""
import argparse
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE.parent

# redoslijed koraka po kategoriji; (skripta, [dodatni argumenti])
# scrape koraci se preskacu bez --scrape (koriste postojeci raw katalog)
SCRAPE = {"whisky": "scrape-whisky-catalog.py", "brandy": "scrape-brandy-catalog.py"}

PIPELINES = {
    "rum": [
        "excel-to-json.py",
        "apply-neutral-overrides.py",
        "localize-detail-fields.py",
        "dedupe-data.py",
        "export-indexes.py",
    ],
    "whisky": [
        "build-whisky-excel.py",
        "excel-to-whisky-json.py",
        "merge-extras.py",
        "apply-neutral-overrides.py",
        "localize-detail-fields.py",
        "dedupe-data.py",
        "export-indexes.py",
    ],
    "brandy": [
        "build-brandy-excel.py",
        "excel-to-brandy-json.py",
        "apply-neutral-overrides.py",
        "localize-detail-fields.py",
        "dedupe-data.py",
        "export-indexes.py",
    ],
    "cigars": [
        "enrich-cigars.py",  # dobiva --humidor-catalog putanju kao argv[1]
        "profile-cigars.py",
        "dedupe-data.py",
    ],
}


def run(cmd: list[str]) -> None:
    print(f"\n=== {' '.join(cmd)} ===", flush=True)
    result = subprocess.run(cmd, cwd=APP)
    if result.returncode != 0:
        sys.exit(f"KORAK PAO ({result.returncode}): {' '.join(cmd)} — pipeline zaustavljen.")


def steps_for(category: str, scrape: bool) -> list[str]:
    steps = list(PIPELINES[category])
    if scrape and category in SCRAPE:
        steps.insert(0, SCRAPE[category])
    return steps


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--category", required=True, choices=[*PIPELINES, "all"])
    ap.add_argument("--scrape", action="store_true", help="ukljuci scrape shop kataloga")
    ap.add_argument("--humidor-catalog", help="putanja do humidor_catalog.txt (za cigars)")
    ap.add_argument("--from", dest="from_step", metavar="SKRIPTA", help="nastavi od ovog koraka")
    ap.add_argument("--list", action="store_true", help="samo ispisi korake, ne pokreci")
    ap.add_argument("--no-test", action="store_true", help="preskoci npm test na kraju")
    args = ap.parse_args()

    categories = list(PIPELINES) if args.category == "all" else [args.category]
    if "cigars" in categories and not args.humidor_catalog and not args.list:
        sys.exit("cigars pipeline treba --humidor-catalog (ulaz za enrich-cigars.py)")

    for cat in categories:
        steps = steps_for(cat, args.scrape)
        if args.from_step:
            if args.from_step not in steps:
                sys.exit(f"'{args.from_step}' nije korak {cat} pipelinea: {steps}")
            steps = steps[steps.index(args.from_step):]
        if args.list:
            print(f"{cat}: " + " -> ".join(steps) + ("" if args.no_test else " -> npm test"))
            continue
        for step in steps:
            cmd = [sys.executable, str(HERE / step)]
            if step == "enrich-cigars.py":
                cmd.append(args.humidor_catalog)
            run(cmd)

    if not args.list and not args.no_test:
        run(["npm", "test"])
    if not args.list:
        print("\npipeline gotov ✔")


if __name__ == "__main__":
    main()
