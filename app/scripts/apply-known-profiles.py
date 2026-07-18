# -*- coding: utf-8 -*-
"""Apply known profiles and fix wrappers for newly imported cigars.

Steps:
  1. Fix Cuban wrappers (Natural -> Cuban Habano)
  2. Apply KNOWN profiles from profile-cigars.py lookup table
  3. Apply curated profiles from matching brand+wrapper entries
  4. Report what still needs web research
"""
from __future__ import annotations

import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "data"
CIGARS = DATA / "cigars.json"

CUBAN_BRANDS = {
    "Bolívar", "Cohiba", "Cuaba", "Fonseca", "Guantanamera",
    "H. Upmann", "Hoyo de Monterrey", "José L. Piedra", "Juan López",
    "La Gloria Cubana", "Maestranza", "Montecristo", "Partagás",
    "Por Larrañaga", "Punch", "Quai d'Orsay", "Quintero",
    "Rafael Gonzalez", "Ramón Allones", "Rey del Mundo",
    "Romeo y Julieta", "San Cristóbal de la Habana", "Sancho Panza",
    "Trinidad", "VegaFina", "Vegas Robaina", "Vegueros",
}

KNOWN_PROFILES: dict[tuple[str, str], tuple[int, int, list[str], str]] = {
    # (brand, line_keyword) -> (strength, body, [flavorTags], wrapper)

    # AJ Fernandez / New World
    ("AJ Fernandez", "new world cameroon"): (2, 3, ["cedar", "kremasto", "zacini-slatki", "orasasti"], "Cameroon"),
    ("AJ Fernandez", "new world connecticut"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),
    ("AJ Fernandez", "new world oscuro"): (4, 4, ["kakao", "kava", "papar", "zemljano"], "Maduro"),
    ("AJ Fernandez", "new world dorado"): (3, 4, ["kakao", "karamela", "zacini", "cedar"], "Habano"),
    ("AJ Fernandez", "new world puro especial"): (3, 3, ["cedar", "zacini", "zemljano", "kava"], "Habano"),
    ("AJ Fernandez", "new world decenio"): (3, 4, ["kakao", "kava", "cedar", "karamela"], "Habano"),
    ("AJ Fernandez", "dias de gloria"): (3, 4, ["kakao", "cedar", "zacini", "karamela"], "Habano"),
    ("AJ Fernandez", "dias de gloria brazil"): (3, 4, ["kakao", "zemljano", "kava", "zacini"], "Brazil"),
    ("AJ Fernandez", "20th anniversary"): (4, 5, ["kakao", "kava", "papar", "koza", "zemljano"], "Maduro"),

    # Arturo Fuente
    ("Arturo Fuente", "hemingway"): (2, 3, ["cedar", "zacini-slatki", "karamela", "kava"], "Cameroon"),
    ("Arturo Fuente", "opus"): (4, 4, ["cedar", "kremasto", "zacini", "karamela", "kava"], "Rosado"),
    ("Arturo Fuente", "don carlos"): (3, 4, ["zacini", "cedar", "kakao", "koza"], "Rosado"),

    # Asylum 13
    ("Asylum 13", "insidious"): (2, 2, ["kremasto", "cedar", "med", "orasasti"], "Connecticut"),
    ("Asylum 13", "connecticut"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),
    ("Asylum 13", "medulla"): (4, 4, ["kakao", "papar", "koza", "zemljano"], "Maduro"),
    ("Asylum 13", ""): (3, 3, ["cedar", "zemljano", "zacini", "kava"], "Habano"),

    # Bellas Artes (AJ Fernandez)
    ("Bellas Artes", "hybrid"): (3, 3, ["cedar", "kremasto", "zacini", "orasasti"], "Habano"),
    ("Bellas Artes", "maduro"): (3, 4, ["kakao", "kava", "karamela", "zemljano"], "Maduro"),

    # CLE
    ("CLE", "connecticut"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),
    ("CLE", "corojo"): (3, 4, ["papar", "zacini", "koza", "cedar"], "Corojo"),
    ("CLE", "criollo"): (3, 3, ["zemljano", "cedar", "orasasti", "zacini"], "Criollo"),
    ("CLE", "prieto"): (4, 4, ["kakao", "kava", "papar", "koza"], "Maduro"),
    ("CLE", "25th"): (3, 4, ["kakao", "cedar", "zacini", "karamela"], "Habano"),

    # Drew Estate / Liga Privada / Enclave
    ("Liga Privada", "seleccion"): (4, 5, ["zemljano", "kakao", "papar", "koza", "dim"], "Maduro"),
    ("Enclave", "broadleaf"): (4, 4, ["kakao", "zemljano", "papar", "koza"], "Broadleaf"),
    ("Enclave", "habano"): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),
    ("Enclave", "connecticut"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),

    # H. Upmann (Cuban)
    ("H. Upmann", "connoisseur"): (3, 3, ["kremasto", "cedar", "kava", "med"], "Cuban Habano"),
    ("H. Upmann", "connossieur"): (3, 3, ["kremasto", "cedar", "kava", "med"], "Cuban Habano"),
    ("H. Upmann", "magnum"): (3, 3, ["kremasto", "cedar", "kava", "med"], "Cuban Habano"),
    ("H. Upmann", "half corona"): (2, 2, ["kremasto", "cedar", "med", "orasasti"], "Cuban Habano"),
    ("H. Upmann", "majestic"): (2, 3, ["kremasto", "cedar", "orasasti", "med"], "Cuban Habano"),
    ("H. Upmann", "noellas"): (3, 3, ["kremasto", "cedar", "zacini", "kava"], "Cuban Habano"),
    ("H. Upmann", "regalias"): (2, 3, ["kremasto", "cedar", "orasasti", "trava-slatka"], "Cuban Habano"),

    # Guantanamera
    ("Guantanamera", ""): (2, 2, ["trava-slatka", "cedar", "zemljano", "orasasti"], "Cuban Habano"),

    # José L. Piedra
    ("José L. Piedra", ""): (3, 3, ["zemljano", "cedar", "duhan", "zacini"], "Cuban Habano"),

    # La Gloria Cubana
    ("La Gloria Cubana", ""): (3, 4, ["zacini", "kakao", "cedar", "koza"], "Cuban Habano"),

    # Maestranza
    ("Maestranza", ""): (3, 3, ["cedar", "duhan", "zemljano", "zacini"], "Cuban Habano"),

    # Por Larrañaga
    ("Por Larrañaga", ""): (2, 3, ["kremasto", "cedar", "orasasti", "trava-slatka"], "Cuban Habano"),

    # Quai d'Orsay
    ("Quai d'Orsay", "no. 50"): (2, 3, ["kremasto", "cedar", "citrus", "orasasti"], "Cuban Habano"),

    # Rafael Gonzalez
    ("Rafael Gonzalez", ""): (2, 3, ["kremasto", "cedar", "med", "orasasti"], "Cuban Habano"),

    # Rey del Mundo
    ("Rey del Mundo", ""): (2, 3, ["kremasto", "cedar", "med", "trava-slatka"], "Cuban Habano"),

    # Sancho Panza
    ("Sancho Panza", ""): (2, 3, ["kremasto", "cedar", "duhan", "orasasti"], "Cuban Habano"),

    # Vegueros
    ("Vegueros", ""): (2, 3, ["trava-slatka", "cedar", "zemljano", "orasasti"], "Cuban Habano"),

    # Dunbarton T&T
    ("Dunbarton T&T", "muestras"): (4, 4, ["kakao", "papar", "koza", "cedar", "dim"], "Habano"),
    ("Dunbarton T&T", "bewitched"): (4, 4, ["kakao", "papar", "koza", "cedar", "dim"], "Habano"),
    ("Dunbarton T&T", "sin compromiso"): (5, 5, ["kakao", "papar", "koza", "zemljano", "dim"], "Habano"),

    # Sin Compromiso (Dunbarton)
    ("Sin Compromiso", ""): (5, 5, ["kakao", "papar", "koza", "zemljano", "dim"], "Habano"),

    # JFR (Aganorsa)
    ("JFR", "connecticut"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),
    ("JFR", "corojo"): (4, 4, ["papar", "zacini", "koza", "cedar"], "Corojo"),
    ("JFR", "lunatic maduro"): (4, 4, ["kakao", "papar", "koza", "zemljano"], "Maduro"),
    ("JFR", "lunatic"): (3, 4, ["cedar", "zacini", "koza", "zemljano"], "Habano"),
    ("JFR", ""): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),

    # K by Karen Berger
    ("K by Karen Berger", "cameroon"): (2, 3, ["zacini-slatki", "cedar", "orasasti", "koza"], "Cameroon"),
    ("K by Karen Berger", "connecticut"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),
    ("K by Karen Berger", "habano"): (3, 3, ["cedar", "zacini", "koza", "kava"], "Habano"),
    ("K by Karen Berger", "fire"): (4, 4, ["kakao", "papar", "koza", "dim"], "Maduro"),
    ("K by Karen Berger", ""): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),

    # La Aroma del Caribe
    ("La Aroma del Caribe", "connecticut"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),
    ("La Aroma del Caribe", "mi amor"): (4, 4, ["kakao", "kava", "papar", "koza"], "Maduro"),
    ("La Aroma del Caribe", "pasion"): (3, 3, ["cedar", "zacini", "kremasto", "kava"], "Habano"),
    ("La Aroma del Caribe", "edicion especial"): (3, 4, ["cedar", "zacini", "kakao", "koza"], "Habano"),
    ("La Aroma del Caribe", ""): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),

    # La Instructora (Dunbarton)
    ("La Instructora", "delicado"): (2, 3, ["kremasto", "cedar", "orasasti", "zacini-slatki"], "Connecticut"),
    ("La Instructora", "perfection"): (4, 4, ["kakao", "papar", "koza", "cedar", "dim"], "Habano"),
    ("La Instructora", "box pressed"): (3, 4, ["cedar", "zacini", "kava", "koza"], "Habano"),
    ("La Instructora", ""): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),

    # La Ley (Dunbarton)
    ("La Ley", "reserva"): (4, 4, ["kakao", "koza", "cedar", "zacini", "dim"], "Habano"),
    ("La Ley", ""): (3, 4, ["cedar", "zacini", "kava", "koza"], "Habano"),

    # Last Call (AJ Fernandez)
    ("Last Call", "habano"): (3, 3, ["cedar", "zacini", "koza", "kava"], "Habano"),
    ("Last Call", "maduro"): (3, 4, ["kakao", "kava", "karamela", "zemljano"], "Maduro"),

    # Leaf by Oscar
    ("Leaf by Oscar", "connecticut"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),
    ("Leaf by Oscar", "corojo"): (3, 4, ["papar", "zacini", "koza", "cedar"], "Corojo"),

    # Omar Ortez
    ("Omar Ortez", "connecticut"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),
    ("Omar Ortez", "maduro"): (3, 4, ["kakao", "kava", "karamela", "zemljano"], "Maduro"),
    ("Omar Ortez", "original"): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),
    ("Omar Ortez", ""): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),

    # San Lotano (AJ Fernandez)
    ("San Lotano", "bull"): (4, 4, ["kakao", "papar", "koza", "zemljano"], "Habano"),
    ("San Lotano", "habano"): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),
    ("San Lotano", "oval"): (3, 3, ["cedar", "zacini", "kremasto", "orasasti"], "Habano"),
    ("San Lotano", "requiem connecticut"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),
    ("San Lotano", ""): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),

    # Don Kiki
    ("Don Kiki", "brown"): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),
    ("Don Kiki", "gold"): (3, 4, ["kakao", "kava", "zacini", "cedar"], "Habano"),
    ("Don Kiki", "platinum"): (4, 4, ["kakao", "papar", "koza", "cedar"], "Maduro"),

    # Saga (De los Reyes)
    ("Saga", "short tales"): (3, 3, ["cedar", "zacini", "kremasto", "orasasti"], "Habano"),
    ("Saga", "solaz"): (3, 3, ["cedar", "kremasto", "kava", "orasasti"], "Habano"),
    ("Saga", "golden age"): (4, 4, ["kakao", "zacini", "koza", "cedar"], "Habano"),

    # The Aviator (General Cigar)
    ("The Aviator", ""): (3, 4, ["kakao", "cedar", "zacini", "karamela"], "Habano"),

    # PDR (Pinar del Rio)
    ("PDR", "1878"): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),
    ("PDR", "value line"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),
    ("PDR", "flores y rodriguez"): (3, 4, ["kakao", "cedar", "zacini", "koza"], "Habano"),
    ("PDR", "gran reserva corojo"): (3, 4, ["papar", "zacini", "koza", "cedar"], "Corojo"),
    ("PDR", "gran reserva maduro"): (3, 4, ["kakao", "kava", "karamela", "zemljano"], "Maduro"),
    ("PDR", "gran reserva desflorado"): (2, 3, ["cedar", "kremasto", "orasasti", "med"], "Habano"),
    ("PDR", "gran reserva sungrown"): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),
    ("PDR", "criollito rosado"): (2, 3, ["kremasto", "zacini-slatki", "cedar", "orasasti"], "Rosado"),
    ("PDR", "criollito"): (3, 3, ["cedar", "zemljano", "orasasti", "zacini"], "Habano"),
    ("PDR", ""): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),

    # Blend 15
    ("Blend 15", ""): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),

    # Buffalo Ten
    ("Buffalo Ten", "connecticut"): (2, 2, ["kremasto", "cedar", "orasasti", "med"], "Connecticut"),
    ("Buffalo Ten", "maduro"): (3, 4, ["kakao", "kava", "karamela", "zemljano"], "Maduro"),
    ("Buffalo Ten", "natural"): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),

    # Chateau Diadem
    ("Chateau Diadem", ""): (3, 3, ["cedar", "kremasto", "zacini", "kava"], "Habano"),

    # Accomplice
    ("Accomplice", ""): (3, 3, ["cedar", "zacini", "kremasto", "orasasti"], "Habano"),

    # Aging Room
    ("Aging Room", "quattro"): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),
    ("Aging Room", ""): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),

    # Ambasciator Italico (Italian Toscano-style)
    ("Ambasciator Italico", "maturo"): (3, 4, ["kakao", "kava", "dim", "zemljano"], "Maduro"),
    ("Ambasciator Italico", "nero"): (3, 4, ["kakao", "dim", "kava", "koza"], "Maduro"),
    ("Ambasciator Italico", "torpedo"): (3, 4, ["dim", "zemljano", "kava", "zacini"], "Toscano"),
    ("Ambasciator Italico", "superiore"): (3, 3, ["dim", "zemljano", "cedar", "zacini"], "Toscano"),
    ("Ambasciator Italico", ""): (2, 2, ["dim", "trava-slatka", "cedar", "zemljano"], "Toscano"),

    # Artista
    ("Artista", "harvest"): (3, 3, ["cedar", "kremasto", "zacini", "orasasti"], "Habano"),
    ("Artista", "midnight"): (3, 4, ["kakao", "kava", "zacini", "cedar"], "Maduro"),
    ("Artista", ""): (3, 3, ["cedar", "zacini", "kremasto", "orasasti"], "Habano"),

    # El Vinyet
    ("El Vinyet", ""): (3, 3, ["cedar", "zacini", "kremasto", "orasasti"], "Habano"),

    # Kintsugi
    ("Kintsugi", ""): (3, 3, ["cedar", "kakao", "zacini", "kremasto"], "Habano"),

    # Padilla
    ("Padilla", ""): (3, 4, ["kakao", "cedar", "zacini", "koza"], "Habano"),

    # Paradiso
    ("Paradiso", ""): (3, 3, ["cedar", "kremasto", "kava", "orasasti"], "Habano"),

    # Pulita
    ("Pulita", ""): (3, 3, ["cedar", "zacini", "kava", "orasasti"], "Habano"),

    # Puro Ambar
    ("Puro Ambar", ""): (3, 3, ["cedar", "zacini", "karamela", "kava"], "Habano"),

    # The Oscar
    ("The Oscar", ""): (3, 3, ["cedar", "zacini", "orasasti", "kremasto"], "Habano"),
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.lower().strip())


def find_profile(brand: str, line: str) -> tuple[int, int, list[str], str] | None:
    line_n = norm(line)
    for (b, keyword), profile in KNOWN_PROFILES.items():
        if b != brand:
            continue
        if keyword and keyword in line_n:
            return profile
    for (b, keyword), profile in KNOWN_PROFILES.items():
        if b != brand:
            continue
        if keyword == "":
            return profile
    return None


def main():
    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))

    fixed_wrapper = 0
    applied_profile = 0
    still_needs = 0

    for c in cigars:
        if not c.get("_needsProfile"):
            continue

        if c["brand"] in CUBAN_BRANDS and c.get("wrapper") == "Natural":
            c["wrapper"] = "Cuban Habano"
            fixed_wrapper += 1

        prof = find_profile(c["brand"], c.get("line", ""))
        if prof:
            strength, body, tags, wrapper = prof
            c["strength"] = strength
            c["body"] = body
            c["flavorTags"] = list(tags)
            if c.get("wrapper") in ("Natural", "Cuban Habano") or wrapper != "Natural":
                c["wrapper"] = wrapper
            c["profileEstimated"] = True
            del c["_needsProfile"]
            applied_profile += 1
        else:
            still_needs += 1

    CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Fixed wrappers: {fixed_wrapper}")
    print(f"Applied known profiles: {applied_profile}")
    print(f"Still needs web research: {still_needs}")

    if still_needs:
        print("\nStill needing profiles:")
        for c in cigars:
            if c.get("_needsProfile"):
                print(f"  {c['brand']} | {c['line']} | {c['vitola']} | {c['wrapper']}")


if __name__ == "__main__":
    main()
