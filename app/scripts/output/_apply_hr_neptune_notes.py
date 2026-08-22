# -*- coding: utf-8 -*-
"""Apply hand HR rewrites for top Neptune-filled cigar notes."""
from __future__ import annotations

import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[2] / "src" / "data" / "cigars.json"

# Paraphrase shop EN into short editorial HR (cigara, pepeo, finite verbs).
HR: dict[str, str] = {
    "cig-a-flores-gran-reserva-desflorado": (
        "Kremasta i cvjetna Desflorado linija: sijeno, bilje, orasi i blagi citrus "
        "preko glatke teksture. Trešnja, koža i kakao dolaze u valovima, a profil "
        "ostaje uravnotežen do kraja, bez pritiska."
    ),
    "cig-camacho-triple-maduro": (
        "Srednje do pune snage: sav maduro list u punjenju, vezivu i pokrovu. "
        "Vanilija i kakao nose kompleksnost, a završetak je dug i slankast."
    ),
    "cig-cain-daytona": (
        "Puna snaga u robustu: cedar, hrast, kakao i začin. Nikaragvanski puro s "
        "crvenkastim maduro pokrovom i listom iz Jalape, pa je dojam snage "
        "malo mekši nego što brojka sugerira. Ručno u Olivinoj tvornici."
    ),
    "cig-cle-corojo": (
        "Srednje tijelo, honduraški puro: tamnocrveni Corojo pokrov, zemlja i papar "
        "s notom kave. Završetak je gladak i dug. Christian Eiroa, CLE."
    ),
    "cig-alec-bradley-kintsugi": (
        "Zemlja, cedar, slatki začin i kakao u srednjem do malo punijem toru "
        "(AJ Fernandez, Estelí). Ekvadorski Habano pokrov, meksičko vezivo, "
        "nikaragvansko punjenje; linija se poziva na wabi-sabi — ljepotu u "
        "nesavršenosti."
    ),
    "cig-la-galera-1936": (
        "Srednja snaga iz Tabacalere Palma: ekvadorski Habano nad dominikanskim "
        "Criollom i Pilotom Cubano. Koža, kava i papar u box-press formatu, "
        "u čast osnutka tvornice 1936."
    ),
    "cig-la-galera-anemoi": (
        "Srednje tijelo: topla kava, orasi i koža. Connecticut Broadleaf pokrov, "
        "dominikanski Corojo i Piloto/Criollo 98. Ručno u Palmi; ime od grčkih "
        "bogova vjetra — vjetar u uzgoju duhana nije sitnica."
    ),
    "cig-perdomo-20th-anniversary": (
        "Srednje do punog tijela, zemljani profil s hrastom i cedrom. Nikaragvanski "
        "puro: sun-grown pokrov odležan osam godina, zatim još deset mjeseci u "
        "bačvi bourbona. Jubilarna linija za dvadesetu Perdomovu godinu."
    ),
    "cig-macanudo-cafe": (
        "Blaga, kremasta jutarnja cigara: Connecticut Shade, meksičko vezivo, "
        "dominikansko i meksičko punjenje. Drvo, orasi i blaga slatkoća, bez "
        "napora. Ručno u Dominikanskoj Republici."
    ),
    "cig-joya-de-nicaragua-antano": (
        "Bez uvijanja: puna snaga, stari duhan, cedar, orasi i začin. Rosado "
        "Habano Criollo pokrov, nikaragvanski puro. Za pušača koji traži jaku "
        "i izravnu cigaru — Antaño 1970."
    ),
    "cig-joya-de-nicaragua-cuatro-cinco": (
        "Puno tijelo uz 45. obljetnicu marke: koža, zemlja i začin. Nikaragvanski "
        "Habano pokrov, dominikansko vezivo, posebno odležano nikaragvansko "
        "punjenje. Ručno u Nikaragvi."
    ),
    "cig-aj-fernandez-20th-anniversary": (
        "Puna snaga s kontroliranom složenošću: tamni maduro pokrov nad listom s "
        "AJ Fernandezovih farmi. Ručno u Tabacaleri AJ Fernandez — jubilej koji "
        "ne gura samo snagu, nego i gustoću okusa."
    ),
    "cig-davidoff-royal-release": (
        "Srednje tijelo: drvo, koža, začin i blaga slatkoća. Dominikanski "
        "Aromatica pokrov, ekvadorski Habano vezivo, Criollo Ligero i San Vicente. "
        "Listovi birani i odležani osam godina; vuku ih iskusni valjatelji."
    ),
    "cig-davidoff-maduro": (
        "Mala panatela Primeros: kratko punjenje dominikanskog duhana, peruansko "
        "vezivo, Yamasa pokrov. Srednje tijelo, gust okus u kratkom formatu."
    ),
}


def main() -> None:
    cigars = json.loads(DATA.read_text(encoding="utf-8"))
    n = 0
    for c in cigars:
        hr = HR.get(c["id"])
        if not hr:
            continue
        notes = dict(c.get("notes") or {})
        if notes.get("hr") == hr:
            continue
        notes["hr"] = hr
        c["notes"] = notes
        n += 1
    DATA.write_text(json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"updated {n} HR notes -> {DATA.name}")


if __name__ == "__main__":
    main()
