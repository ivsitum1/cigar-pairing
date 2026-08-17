#!/usr/bin/env python3
"""Vezni list i punjenje iz scrape-a -> cigars.json.

STANJE PRIJE. Katalog zna pokrov za sve cigare, ali vezni list samo za 530 od
3315 i punjenje za 450. Dva vec preuzeta izvora o tome govore, a nijedan se
dosad nije citao do kraja:

  * `neptune_raw.json` — polja "Cigar Binder" / "Cigar Filler" sa stranice
    proizvoda. `merge-neptune-profiles.py` iz njih vadi SAMO zemlju, pa je
    "Ecuador Sumatra" ostavljalo Ekvador, a Sumatra se gubila.
  * `cigarworld_flavor_raw.json` — CigarWorld drzi podrijetlo i sortu u
    odvojenim poljima ("binder origin": Mexico, "binder variety": San Andrés).
    Iz te datoteke se dosad citao samo opis.

STO SE UPISUJE. `binder` i `filler` (sorta lista, kako ju kartica i prikazuje
uz zemlju) i `binderOrigin` / `fillerOrigin` / `wrapperOrigin` gdje ih nema.

CETIRI PRAVILA, i sva cetiri postoje zbog konkretne stete koju sprjecavaju:

1. Prazno se popunjava, upisano se ne dira. Kurirani podatak uvijek pobjedjuje
   duckanski.
2. Sorta koja je zapravo zemlja se odbacuje. CigarWorld pod "binder variety"
   zna staviti "Indonesia"; upisano, kartica bi pisala "Indonezija · Indonesia".
3. Visestruko podrijetlo ("Dominican Republic, Nicaragua") ne upisuje se u
   `fillerOrigin`. To polje po dogovoru nosi jednu zemlju — mjesavina se ostavlja
   praznom umjesto da se izabere jedna od dvije i time slaze.
4. Zemlja se prevodi preko istog rjecnika kojim se sluzi neptune-merge. Nova
   engleska imena se NE pogadjaju — sto rjecnik ne zna, ostaje neupisano.

Idempotentno; `--check` ne mijenja nista (za CI).

Pokreni iz app/:
    python3 scripts/merge-leaf-details.py
    python3 scripts/merge-leaf-details.py --check
    python3 scripts/merge-leaf-details.py --dry-run   # ispisi sto bi upisao
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "src" / "data"
CIGARS = DATA / "cigars.json"
NEPTUNE = HERE / "output" / "neptune_raw.json"
CIGARWORLD = HERE / "output" / "cigarworld_flavor_raw.json"

PRAZNO = {
    "",
    "—",
    "-",
    "–",
    "n/a",
    "na",
    "unknown",
    # CigarWorld je njemacki duckan i "ne zna se" pise na njemackom. Bez ovih
    # tri niski "unbekannt / geheim" prolazi kroz kosu crtu kao da su dvije
    # zemlje, a zapravo je izricito "nepoznato".
    "keine angabe",
    "unbekannt",
    "geheim",
    "unbekannt / geheim",
}

# Vrijednosti koje duckan upise kad NE ZNA ili ne zeli reci. Upisane u katalog
# citale bi se kao podatak ("Vezni list: Undisclosed"), a prazno polje barem
# posteno kaze da se ne zna.
NIJE_SORTA = {
    "undisclosed",
    "not disclosed",
    "mixed",
    "various",
    "assorted",
    "proprietary",
    "secret",
    "blend",
    "n/a",
}

# Zemlje i regije koje rjecnik zemalja ne poznaje, pa bi prosle kao "sorta".
# Toscano je pravi primjer: punjenje mu pise "Italy" — to je zemlja, ne sorta.
# CigarWorld je njemacki duckan, pa uz engleska imena stoje i njemacka
# ("Kolumbien", "Mexiko") i pokoja pogresno napisana ("Columbia").
NIJE_SORTA_NEGO_MJESTO = {
    "italy",
    "italien",
    "cyprus",
    "zypern",
    "central america",
    "america",
    "europe",
    "africa",
    "germany",
    "deutschland",
    "brasil",
    "brasilien",
    "columbia",
    "kolumbien",
    "mexiko",
    "paraguay",
    "turkey",
    "tuerkei",
    "zimbabwe",
    "simbabwe",
    "canary islands",
    "kanarische inseln",
    "dominikanische republik",
    "nikaragua",
    "kuba",
}

# Imena koja su I mjesto I sorta. Rjecnik zemalja ih zna kao mjesto (Sumatra i
# Java -> Indonezija, Connecticut -> SAD), pa bi ih provjera "je li ovo zemlja"
# bacila — a bas to su najcesce sorte veznog lista u katalogu (Sumatra stoji
# uz 30 cigara). Kad dodju kao sorta, sorta i ostaju.
SORTA_I_MJESTO = {"sumatra", "java", "connecticut", "java besuki"}


def _load(filename: str):
    spec = importlib.util.spec_from_file_location(
        filename.replace("-", "_").removesuffix(".py"), HERE / filename
    )
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


_neptune = _load("merge-neptune-profiles.py")


def prazno(v) -> bool:
    return v is None or str(v).strip().lower() in PRAZNO


def zemlja_hr(tekst: str) -> str | None:
    """Englesko ime zemlje -> hrvatsko, preko rjecnika neptune-mergea."""
    return _neptune._to_hr_country(tekst)


def je_zemlja(tekst: str) -> bool:
    """Je li cijeli tekst samo ime zemlje (ili njezin pridjev)?"""
    ociscen = re.sub(r"[^a-z ]", " ", (tekst or "").lower()).strip()
    ociscen = re.sub(r"\s+", " ", ociscen)
    return ociscen in _neptune.COUNTRY_HR


def sjeme_a_ne_zemlja(tekst: str) -> bool:
    """Govori li vodeca zemlja o SJEMENU umjesto o mjestu uzgoja?

    "Cuban Seed" je duhan kubanskog sjemena uzgojen bilo gdje — najcesce bas
    ne na Kubi. Da se ta rijec citala kao zemlja, katalog bi Nikaragvi upisao
    kubansko podrijetlo, a to je tvrdnja koju izvor nigdje ne postavlja.
    """
    return bool(re.match(r"^\s*[a-z]+\s+seed\b", (tekst or ""), re.I))


def sorta_iz_teksta(tekst: str) -> str | None:
    """Iz "Ecuador Sumatra" izvuci "Sumatra"; iz "Nicaragua" nista.

    Duckanski zapis lijepi zemlju i sortu u jedan redak. Zemlja ide u svoje
    polje, a ono sto ostane je sorta — ako ista ostane. Iznimka je sjeme:
    kod "Cuban Seed Nicaraguan" sorta je "Cuban Seed", a Nikaragva je mjesto.
    """
    if prazno(tekst):
        return None
    ostatak = tekst.strip()
    if je_zemlja(ostatak):
        return None

    if sjeme_a_ne_zemlja(ostatak):
        # zadrzi "<Zemlja> Seed", odbaci zemlju uzgoja koja stoji iza
        m = re.match(r"^\s*([a-z]+\s+seed)\b(.*)$", ostatak, re.I)
        if m:
            return m.group(1).strip()
        return ostatak

    # Makni vodece ime zemlje ili njezin pridjev ("Ecuadorian Habano").
    for kljuc in sorted(_neptune.COUNTRY_HR, key=len, reverse=True):
        uzorak = rf"^{re.escape(kljuc)}\b[\s,-]*"
        novi = re.sub(uzorak, "", ostatak, flags=re.I)
        if novi != ostatak:
            ostatak = novi.strip()
            break
    ostatak = ostatak.strip(" ,-–—")
    if not ostatak:
        return None
    if je_zemlja(ostatak) and ostatak.lower() not in SORTA_I_MJESTO:
        return None
    return ostatak


def vise_od_jednog_imena(tekst: str) -> bool:
    """Nosi li polje popis umjesto jedne sorte?

    CigarWorld u polje SORTE zna upisati mjesavinu zemalja ("Kolumbien,
    Nicaragua") ili popis regija ("Condega, Criollo, Esteli"). Provjerava se
    OBLIK, ne sadrzaj: sorta lista je jedno ime, pa je zarez ili kosa crta
    dovoljan znak da ovo nije sorta. Provjera po rjecniku zemalja tu ne bi
    valjala — duckan je njemacki i pise "Kolumbien", a rjecnik zna "Colombia";
    ovako popis pada bez obzira na jezik i na pravopis.
    """
    return bool(re.search(r"[,/;]| and | und ", tekst or "", re.I))


def sorta_smije(sorta: str | None, podrijetlo: str | None) -> str | None:
    """Odbaci sortu koja samo ponavlja zemlju ili ne govori nista (pravilo 2)."""
    if not sorta:
        return None
    if vise_od_jednog_imena(sorta):
        return None
    niska = sorta.strip().lower()
    if niska in NIJE_SORTA or niska in NIJE_SORTA_NEGO_MJESTO:
        return None
    if je_zemlja(sorta) and niska not in SORTA_I_MJESTO:
        return None
    if podrijetlo and niska == str(podrijetlo).strip().lower():
        return None
    return sorta


def vodeca_zemlja(tekst: str) -> str | None:
    """Zemlja s pocetka retka — duckani pisu "<gdje je raslo> <sorta>".

    Treba jer rjecnik odustaje kad u retku prepozna dva mjesta: "Ecuadorian
    Connecticut" je connecticutska sorta uzgojena u Ekvadoru, a ne duhan iz
    dvije zemlje. Redoslijed rijeci to razrjesava — prva je mjesto.
    """
    prva = re.match(r"^\s*([a-z]+(?:\s+[a-z]+)?)\b", (tekst or ""), re.I)
    if not prva:
        return None
    for kandidat in (prva.group(1), prva.group(1).split()[0]):
        ime = kandidat.lower().strip()
        if ime in _neptune.COUNTRY_HR:
            return _neptune.COUNTRY_HR[ime]
    return None


def jedno_podrijetlo(tekst: str) -> str | None:
    """Zemlja iz teksta, ali samo ako je jedna (pravilo 3)."""
    if prazno(tekst):
        return None
    if "," in tekst or "/" in tekst or re.search(r"\band\b|\bund\b", tekst, re.I):
        return None
    if sjeme_a_ne_zemlja(tekst):
        # "Cuban Seed" ne govori gdje je duhan rastao; ostatak retka mozda da
        ostatak = re.sub(r"^\s*[a-z]+\s+seed\b", "", tekst, flags=re.I).strip()
        return zemlja_hr(ostatak) if ostatak else None
    return zemlja_hr(tekst) or vodeca_zemlja(tekst)


def izvori_se_ne_slazu(cw_tekst: str | None, nep_tekst: str | None) -> bool:
    """Kaze li jedan izvor "mjesavina zemalja", a drugi jednu zemlju?

    CigarWorld za CAO Bones pise punjenje "Honduras, Nicaragua", Neptune
    "Dominican Republic Piloto Cubano". Pravilo o jednoj zemlji odbacilo bi
    CigarWorldov redak kao mjesavinu i onda mirno upisalo Neptuneovu
    Dominikansku — kao da druge tvrdnje nema. Kad se izvori ovako razilaze,
    polje ostaje prazno; nesigurnost je podatak, izmisljena sigurnost nije.
    """
    if prazno(cw_tekst) or prazno(nep_tekst):
        return False
    cw_visestruko = bool(re.search(r",|/|\band\b|\bund\b", cw_tekst or "", re.I))
    if not cw_visestruko:
        return False
    return jedno_podrijetlo(nep_tekst or "") is not None


def prijedlozi(cigar: dict, nep: dict | None, cw: dict | None) -> dict[str, str]:
    """Sto bi se upisalo u ovu cigaru. Prazno = nista za upisati."""
    facts = (cw or {}).get("facts") or {}
    izmjene: dict[str, str] = {}

    for polje, cw_origin, cw_variety, nep_kljuc in (
        ("wrapper", "wrapper origin", "wrapper variety", "wrapper"),
        ("binder", "binder origin", "binder variety", "binder"),
        ("filler", "filler origin", "filler variety", "filler"),
    ):
        polje_origin = f"{polje}Origin"

        # ── podrijetlo ────────────────────────────────────────────────────────
        podrijetlo = cigar.get(polje_origin)
        if prazno(podrijetlo) and not izvori_se_ne_slazu(facts.get(cw_origin), (nep or {}).get(nep_kljuc)):
            nova = jedno_podrijetlo(facts.get(cw_origin) or "") or jedno_podrijetlo(
                (nep or {}).get(nep_kljuc) or ""
            )
            if nova:
                izmjene[polje_origin] = nova
                podrijetlo = nova

        # ── sorta ─────────────────────────────────────────────────────────────
        # Pokrov je vec popunjen u cijelom katalogu, pa mu se sorta ne dira.
        if polje == "wrapper":
            continue
        if not prazno(cigar.get(polje)):
            continue
        # Treci izvor: duckan koji je sortu upisao u polje podrijetla
        # ("filler origin: Corojo"). Corojo nije zemlja, pa to polje ocito
        # govori o listu — cita se kao sorta umjesto da se baci.
        sorta = (
            sorta_smije(facts.get(cw_variety), podrijetlo)
            or sorta_smije(sorta_iz_teksta((nep or {}).get(nep_kljuc) or ""), podrijetlo)
            or sorta_smije(sorta_iz_teksta(facts.get(cw_origin) or ""), podrijetlo)
        )
        if sorta:
            izmjene[polje] = sorta

    return izmjene


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="ne piši, samo provjeri (za CI)")
    ap.add_argument("--dry-run", action="store_true", help="ispiši što bi upisao")
    args = ap.parse_args()

    cigars = json.loads(CIGARS.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in cigars}
    aliases = json.loads((DATA / "cigarIdAliases.json").read_text(encoding="utf-8"))["aliases"]

    def resolve(cid: str) -> str | None:
        seen: set[str] = set()
        while cid not in by_id:
            if cid in seen or cid not in aliases:
                return None
            seen.add(cid)
            cid = aliases[cid]
        return cid

    nep_po_id: dict[str, dict] = {}
    if NEPTUNE.exists():
        for row in json.loads(NEPTUNE.read_text(encoding="utf-8")):
            cid = resolve(row.get("id") or "")
            if cid:
                nep_po_id.setdefault(cid, row)

    cw_po_id: dict[str, dict] = {}
    if CIGARWORLD.exists():
        for row in json.loads(CIGARWORLD.read_text(encoding="utf-8")):
            cid = resolve(row.get("id") or "")
            if cid and row.get("ok"):
                cw_po_id.setdefault(cid, row)

    promjene: list[tuple[str, dict[str, str]]] = []
    for cigar in cigars:
        izmjene = prijedlozi(cigar, nep_po_id.get(cigar["id"]), cw_po_id.get(cigar["id"]))
        if izmjene:
            promjene.append((cigar["id"], izmjene))
            if not (args.check or args.dry_run):
                cigar.update(izmjene)

    po_polju: dict[str, int] = {}
    for _, izmjene in promjene:
        for k in izmjene:
            po_polju[k] = po_polju.get(k, 0) + 1

    if args.check:
        if promjene:
            for cid, izmjene in promjene[:20]:
                print(f"  {cid}: {izmjene}", file=sys.stderr)
            print(
                f"--check: {len(promjene)} cigara ima nepopunjene podatke koje scrape nosi",
                file=sys.stderr,
            )
            return 1
        print("--check: list i punjenje su popunjeni svime što scrape nosi")
        return 0

    if args.dry_run:
        for cid, izmjene in promjene[:40]:
            print(f"  {cid}: {izmjene}")
        print(f"\n(dry-run) {len(promjene)} cigara, po polju: {po_polju}")
        return 0

    if promjene:
        CIGARS.write_text(json.dumps(cigars, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Popunjeno {len(promjene)} cigara — po polju: {po_polju}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
