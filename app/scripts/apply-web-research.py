# -*- coding: utf-8 -*-
"""Apply web-researched profiles to cigars.json.

Profiles verified from halfwheel, Cigar Coop, Cigar Aficionado, etc.
Run after bulk-import and before final estimation.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "data"
CIGARS = DATA / "cigars.json"

def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


RESEARCHED: list[dict] = [
    # === CLE (verified: Cigar Coop, Cigar Aficionado, halfwheel) ===
    {"brand": "CLE", "match": "connecticut", "strength": 2, "body": 3,
     "wrapper": "Ecuador Connecticut", "tags": ["kremasto", "cedar", "orasasti", "suho-voce", "citrus"]},
    {"brand": "CLE", "match": "corojo", "strength": 4, "body": 4,
     "wrapper": "Honduran Corojo", "tags": ["cedar", "papar", "orasasti", "kava", "karamela"]},
    {"brand": "CLE", "match": "criollo", "strength": 3, "body": 3,
     "wrapper": "Honduran Habano", "tags": ["kremasto", "zacini", "zemljano", "cedar", "kakao"]},
    {"brand": "CLE", "match": "prieto", "strength": 4, "body": 5,
     "wrapper": "Connecticut Broadleaf", "tags": ["kakao", "kava", "orasasti", "koza", "papar"]},
    {"brand": "CLE", "match": "25th", "strength": 4, "body": 4,
     "wrapper": "Honduran Corojo", "tags": ["kakao", "zacini-slatki", "cedar", "kava", "koza"]},

    # === Saga (verified: Cigar Coop, halfwheel, Cigar Aficionado) ===
    {"brand": "Saga", "match": "tomo i", "strength": 5, "body": 5,
     "wrapper": "Nicaraguan Jalapa", "tags": ["cedar", "drvo", "duhan", "papar", "tamno-voce", "kakao"]},
    {"brand": "Saga", "match": "tomo ii", "strength": 3, "body": 4,
     "wrapper": "Dominican Cotuí", "tags": ["zacini-slatki", "cedar", "drvo", "papar", "zemljano"]},
    {"brand": "Saga", "match": "tomo iii", "strength": 3, "body": 3,
     "wrapper": "Ecuador Habano", "tags": ["duhan", "zemljano", "drvo", "papar", "orasasti"]},
    {"brand": "Saga", "match": "tomo iv", "strength": 4, "body": 4,
     "wrapper": "Ecuador Sumatra", "tags": ["duhan", "zemljano", "cedar", "papar", "kakao", "kava"]},
    {"brand": "Saga", "match": "tomo v", "strength": 2, "body": 2,
     "wrapper": "Ecuador Claro", "tags": ["kremasto", "slatko", "cedar", "papar", "kava"]},
    {"brand": "Saga", "match": "tomo vi", "strength": 3, "body": 3,
     "wrapper": "Mexican San Andrés Maduro", "tags": ["kakao", "kava", "zemljano", "cedar", "suho-voce"]},
    {"brand": "Saga", "match": "tomo vii", "strength": 4, "body": 4,
     "wrapper": "Nicaraguan Habano", "tags": ["kakao", "kava", "zemljano", "cedar", "papar"]},
    {"brand": "Saga", "match": "solaz", "strength": 2, "body": 2,
     "wrapper": "Ecuador Connecticut", "tags": ["kremasto", "citrus", "drvo", "cedar", "orasasti"]},
    {"brand": "Saga", "match": "golden age", "strength": 3, "body": 3,
     "wrapper": "Dominican Yamasá", "tags": ["duhan", "cedar", "zemljano", "papar", "orasasti"]},

    # === San Lotano (verified: halfwheel, Cigar Aficionado, Cigar Coop) ===
    {"brand": "San Lotano", "match": "bull", "strength": 4, "body": 4,
     "wrapper": "Ecuador Sumatra", "tags": ["cedar", "papar", "kakao", "kava", "koza"]},
    {"brand": "San Lotano", "match": "habano", "strength": 4, "body": 4,
     "wrapper": "Brazilian Habano", "tags": ["papar", "zacini", "cedar", "kremasto", "koza"]},
    {"brand": "San Lotano", "match": "oval pyramid", "strength": 4, "body": 4,
     "wrapper": "Ecuador Habano", "tags": ["kava", "koza", "kakao", "papar", "drvo"]},
    {"brand": "San Lotano", "match": "oval robusto", "strength": 3, "body": 3,
     "wrapper": "Ecuador Habano", "tags": ["kava", "koza", "kakao", "papar", "kremasto"]},
    {"brand": "San Lotano", "match": "requiem", "strength": 2, "body": 3,
     "wrapper": "Ecuador Connecticut", "tags": ["cedar", "zacini-slatki", "citrus", "orasasti", "med"]},

    # === Asylum 13 (verified: Cigar Coop, Cigar Aficionado, halfwheel) ===
    {"brand": "Asylum 13", "match": "insidious", "strength": 1, "body": 2,
     "wrapper": "Ecuador Connecticut", "tags": ["kremasto", "cedar", "zemljano", "trava-slatka", "slatko"]},
    {"brand": "Asylum 13", "match": "connecticut", "strength": 2, "body": 2,
     "wrapper": "Ecuador Connecticut", "tags": ["kremasto", "cedar", "drvo", "zemljano", "slatko"]},
    {"brand": "Asylum 13", "match": "medulla", "strength": 3, "body": 3,
     "wrapper": "Honduran Corojo", "tags": ["cedar", "citrus", "kava", "zemljano", "papar", "kakao"]},
    {"brand": "Asylum 13", "match": "pandemonium", "strength": 3, "body": 3,
     "wrapper": "Nicaraguan Habano", "tags": ["kava", "kakao", "papar", "zemljano", "cedar"]},
    {"brand": "Asylum 13", "match": "hercule", "strength": 4, "body": 4,
     "wrapper": "Nicaraguan Habano", "tags": ["zemljano", "kakao", "kava", "koza", "papar"]},
    {"brand": "Asylum 13", "match": "april", "strength": 4, "body": 4,
     "wrapper": "Nicaraguan Habano", "tags": ["zemljano", "kakao", "kava", "koza", "papar"]},
    {"brand": "Asylum 13", "match": "toro", "strength": 4, "body": 3,
     "wrapper": "Nicaraguan Habano", "tags": ["kakao", "cedar", "zemljano", "koza", "papar"]},
    {"brand": "Asylum 13", "match": "robusto", "strength": 4, "body": 3,
     "wrapper": "Nicaraguan Habano", "tags": ["kakao", "cedar", "zemljano", "koza", "papar"]},

    # === PDR (verified: Cigar Coop, halfwheel, Stogie Press) ===
    {"brand": "PDR", "match": "1878", "strength": 3, "body": 3,
     "wrapper": "Ecuador Habano", "tags": ["kremasto", "koza", "cedar", "papar", "karamela"]},
    {"brand": "PDR", "match": "corojo 2006", "strength": 4, "body": 4,
     "wrapper": "Dominican Corojo", "tags": ["cedar", "zacini-slatki", "zemljano", "papar", "kava"]},
    {"brand": "PDR", "match": "gran reserva corojo", "strength": 4, "body": 4,
     "wrapper": "Dominican Corojo", "tags": ["cedar", "zacini-slatki", "zemljano", "papar", "kava"]},
    {"brand": "PDR", "match": "desflorado", "strength": 2, "body": 2,
     "wrapper": "Ecuador Connecticut", "tags": ["citrus", "kremasto", "trava-slatka", "slatko", "cedar"]},
    {"brand": "PDR", "match": "gran reserva maduro", "strength": 4, "body": 4,
     "wrapper": "Mexican San Andrés Maduro", "tags": ["kakao", "kava", "karamela", "tamno-voce", "koza"]},
    {"brand": "PDR", "match": "gran reserva sungrown", "strength": 3, "body": 3,
     "wrapper": "Ecuador Habano", "tags": ["kava", "cedar", "kremasto", "trava-slatka", "zemljano"]},
    {"brand": "PDR", "match": "criollito rosado", "strength": 3, "body": 3,
     "wrapper": "Ecuador Criollo Rosado", "tags": ["cedar", "zemljano", "papar", "zacini-slatki", "kava"]},
    {"brand": "PDR", "match": "criollito", "strength": 3, "body": 3,
     "wrapper": "Ecuador Habano", "tags": ["cedar", "zemljano", "orasasti", "zacini", "kava"]},
    {"brand": "PDR", "match": "flores y rodriguez", "strength": 3, "body": 3,
     "wrapper": "Ecuador Habano", "tags": ["duhan", "kremasto", "papar", "zemljano", "cedar"]},
    {"brand": "PDR", "match": "value line", "strength": 2, "body": 2,
     "wrapper": "Ecuador Connecticut", "tags": ["cedar", "kremasto", "drvo", "trava-slatka", "slatko"]},
    {"brand": "PDR", "match": "rosado infante", "strength": 3, "body": 3,
     "wrapper": "Ecuador Criollo Rosado", "tags": ["cedar", "zemljano", "papar", "zacini-slatki", "kava"]},

    # === Don Kiki (verified: Neptune, Karen Berger official) ===
    {"brand": "Don Kiki", "match": "brown", "strength": 4, "body": 4,
     "wrapper": "Nicaraguan Criollo", "tags": ["kava", "kakao", "zacini", "drvo", "koza"]},
    {"brand": "Don Kiki", "match": "gold", "strength": 5, "body": 5,
     "wrapper": "Nicaraguan Maduro", "tags": ["zacini", "kakao", "koza", "cedar", "papar"]},
    {"brand": "Don Kiki", "match": "platinum", "strength": 4, "body": 4,
     "wrapper": "Nicaraguan Maduro", "tags": ["cedar", "kakao", "zacini", "zemljano", "koza"]},

    # === Liga Privada (verified: halfwheel, Cigar Coop, Blind Man's Puff) ===
    {"brand": "Liga Privada", "match": "seleccion", "strength": 3, "body": 4,
     "wrapper": "Connecticut Criollo Rosado", "tags": ["kava", "cedar", "zemljano", "kremasto", "kakao"]},

    # === Sin Compromiso (verified: Cigar Coop, halfwheel, Stogie Press) ===
    {"brand": "Sin Compromiso", "match": "paladin", "strength": 3, "body": 3,
     "wrapper": "Mexican San Andrés", "tags": ["kava", "kakao", "cedar", "zemljano", "papar", "duhan"]},
    {"brand": "Sin Compromiso", "match": "intrepido", "strength": 3, "body": 4,
     "wrapper": "Mexican San Andrés", "tags": ["kakao", "kava", "zemljano", "koza", "cedar", "papar"]},
    {"brand": "Sin Compromiso", "match": "no.5", "strength": 3, "body": 4,
     "wrapper": "Mexican San Andrés", "tags": ["kakao", "kava", "cedar", "zemljano", "koza", "karamela"]},
    {"brand": "Sin Compromiso", "match": "seleccion", "strength": 3, "body": 4,
     "wrapper": "Mexican San Andrés", "tags": ["kakao", "kava", "zemljano", "koza", "cedar", "papar"]},

    # === La Aroma del Caribe (verified: halfwheel, Cigar Aficionado) ===
    {"brand": "La Aroma del Caribe", "match": "mi amor", "strength": 4, "body": 4,
     "wrapper": "Mexican San Andrés Maduro", "tags": ["kakao", "kava", "papar", "koza", "zemljano"]},
    {"brand": "La Aroma del Caribe", "match": "pasion", "strength": 3, "body": 3,
     "wrapper": "Nicaragua Habano", "tags": ["cedar", "zacini", "kremasto", "kava", "orasasti"]},
    {"brand": "La Aroma del Caribe", "match": "connecticut", "strength": 2, "body": 2,
     "wrapper": "Ecuador Connecticut", "tags": ["kremasto", "cedar", "orasasti", "med", "citrus"]},
    {"brand": "La Aroma del Caribe", "match": "edicion especial", "strength": 3, "body": 4,
     "wrapper": "Nicaragua Habano", "tags": ["cedar", "zacini", "kakao", "koza", "zemljano"]},
    {"brand": "La Aroma del Caribe", "match": "robusto", "strength": 3, "body": 3,
     "wrapper": "Nicaragua Habano", "tags": ["cedar", "zacini", "kava", "orasasti", "zemljano"]},

    # === La Instructora (verified: Cigar Coop, Dunbarton official) ===
    {"brand": "La Instructora", "match": "delicado", "strength": 2, "body": 3,
     "wrapper": "Ecuador Connecticut", "tags": ["kremasto", "cedar", "orasasti", "zacini-slatki", "med"]},
    {"brand": "La Instructora", "match": "perfection", "strength": 4, "body": 4,
     "wrapper": "Nicaragua Habano", "tags": ["kakao", "papar", "koza", "cedar", "dim"]},
    {"brand": "La Instructora", "match": "box pressed", "strength": 3, "body": 4,
     "wrapper": "Nicaragua Habano", "tags": ["cedar", "zacini", "kava", "koza", "zemljano"]},

    # === Omar Ortez (verified: Cigar Coop, Famous Smoke) ===
    {"brand": "Omar Ortez", "match": "connecticut", "strength": 2, "body": 2,
     "wrapper": "Ecuador Connecticut", "tags": ["kremasto", "cedar", "orasasti", "med", "slatko"]},
    {"brand": "Omar Ortez", "match": "maduro", "strength": 3, "body": 4,
     "wrapper": "Mexican San Andrés Maduro", "tags": ["kakao", "kava", "karamela", "zemljano", "koza"]},
    {"brand": "Omar Ortez", "match": "original", "strength": 3, "body": 3,
     "wrapper": "Nicaragua Habano", "tags": ["cedar", "zacini", "kava", "orasasti", "zemljano"]},

    # === Enclave (verified: halfwheel, AJF official) ===
    {"brand": "Enclave", "match": "broadleaf", "strength": 4, "body": 4,
     "wrapper": "Connecticut Broadleaf", "tags": ["kakao", "zemljano", "papar", "koza", "kava"]},
    {"brand": "Enclave", "match": "connecticut", "strength": 2, "body": 2,
     "wrapper": "Ecuador Connecticut", "tags": ["kremasto", "cedar", "orasasti", "med", "citrus"]},
    {"brand": "Enclave", "match": "habano", "strength": 3, "body": 3,
     "wrapper": "Ecuador Habano", "tags": ["cedar", "zacini", "kava", "orasasti", "zemljano"]},

    # === Dunbarton Muestras de Saka ===
    {"brand": "Dunbarton T&T", "match": "bewitched", "strength": 4, "body": 4,
     "wrapper": "Ecuador Habano", "tags": ["kakao", "papar", "koza", "cedar", "dim"]},
]


def main():
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    applied = 0

    for c in cigars:
        if not c.get("profileEstimated"):
            continue

        brand = c["brand"]
        line = norm(c.get("line", ""))

        for r in RESEARCHED:
            if r["brand"] != brand:
                continue
            match_kw = norm(r["match"])
            if match_kw and match_kw not in line:
                continue
            if not match_kw:
                has_specific = any(
                    rr["brand"] == brand and norm(rr["match"]) and norm(rr["match"]) in line
                    for rr in RESEARCHED
                )
                if has_specific:
                    continue

            c["strength"] = r["strength"]
            c["body"] = r["body"]
            c["flavorTags"] = list(r["tags"][:6])
            if r.get("wrapper"):
                c["wrapper"] = r["wrapper"]
            c["profileEstimated"] = True
            applied += 1
            break

    CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=1), encoding="utf-8")

    estimated = sum(1 for c in cigars if c.get("profileEstimated"))
    curated = sum(1 for c in cigars if not c.get("profileEstimated", False))
    print(f"Applied web-researched profiles: {applied}")
    print(f"Total: {len(cigars)} | Curated: {curated} | Estimated: {estimated}")


if __name__ == "__main__":
    main()
