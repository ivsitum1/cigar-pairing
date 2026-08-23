#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rewrite spirit notes/hints so each bottle has a unique, catalog-grounded line.

Avoids shared closings and identical cigarHints. No transcript paste.

    python rewrite-unique-drink-notes.py
    python rewrite-unique-drink-notes.py --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
APP = HERE.parent / "src" / "data"
DATA = HERE / "data" / "youtube"

TAG_HR = {
    "dim": "dim",
    "iodin": "jod",
    "medicinski": "medicinska nota",
    "morski": "morska nota",
    "hrast": "hrast",
    "karamela": "karamela",
    "vanilija": "vanilija",
    "suho-voce": "suho voće",
    "tropsko-voce": "tropsko voće",
    "voce": "voće",
    "tamno-voce": "tamno voće",
    "citrus": "citrus",
    "zacini": "začini",
    "papar": "papar",
    "med": "med",
    "cvjetno": "cvijet",
    "kremasto": "kremastost",
    "kakao": "kakao",
    "orasasti": "orašasti ton",
    "ester-funk": "esterski funk",
    "duhan": "duhan",
    "borovica": "borovica",
    "biljno": "bilje",
    "travnato": "travnato",
    "overproof": "jači alkohol",
}


def hpick(drink_id: str, options: list[str]) -> str:
    digest = hashlib.sha1(drink_id.encode("utf-8")).hexdigest()
    return options[int(digest[:8], 16) % len(options)]


def tags_list(drink: dict, n: int = 3) -> list[str]:
    out: list[str] = []
    for t in drink.get("flavorTags") or []:
        s = TAG_HR.get(str(t), str(t).replace("-", " "))
        if s and s not in out:
            out.append(s)
        if len(out) >= n:
            break
    return out


def tags_join(tags: list[str]) -> str:
    if not tags:
        return "čist bačveni profil"
    if len(tags) == 1:
        return tags[0]
    if len(tags) == 2:
        return f"{tags[0]} i {tags[1]}"
    return f"{tags[0]}, {tags[1]} i {tags[2]}"


def body_word(drink: dict) -> tuple[str, str]:
    try:
        b = int(drink.get("body") or 3)
    except (TypeError, ValueError):
        b = 3
    if b <= 2:
        return "laganije tijelo", "lighter body"
    if b >= 4:
        return "punije tijelo", "fuller body"
    return "srednje tijelo", "medium body"


def abv_s(drink: dict) -> str:
    abv = drink.get("abv")
    if abv is None:
        return ""
    try:
        return f"{float(abv):g} %"
    except (TypeError, ValueError):
        return ""


def age_bit(name: str) -> str:
    m = re.search(r"\b(\d{1,2})\s*YO\b", name, re.I)
    if m:
        return f"{m.group(1)} godina"
    m = re.search(r"\b(\d{1,2})\s*god", name, re.I)
    if m:
        return f"{m.group(1)} godina"
    return ""


def finish_bit(name: str) -> str:
    low = name.lower()
    for needle, label in (
        ("sherry", "sherry finish"),
        ("port", "port finish"),
        ("madeira", "madeira finish"),
        ("oloroso", "oloroso bačva"),
        ("mizunara", "mizunara"),
        ("px", "PX finish"),
        ("bourbon barrel", "bourbon bačva"),
        ("rum cask", "rum cask"),
        ("wine cask", "wine cask"),
    ):
        if needle in low:
            return label
    return ""


def short_name(name: str) -> str:
    # drop gift-box noise
    n = re.sub(r"\s+u poklon.*$", "", name, flags=re.I).strip()
    n = re.sub(r"\s+\d+[.,]?\d*\s*%.*$", "", n).strip()
    # avoid English common noun leaking into HR sentences from product lines
    n = re.sub(r"\bCigar\b", "linija za sparivanje", n)
    n = re.sub(r"\bcigar\b", "linija za sparivanje", n)
    if len(n) > 70:
        n = n[:67].rstrip() + "…"
    return n or name


def botan_label(drink: dict) -> str:
    b = drink.get("botanicalProfile")
    if b is True or str(b).lower() in {"true", "1", "yes"}:
        return "bogata botanika"
    if isinstance(b, str) and b.strip() and b.strip().lower() not in {"true", "false", "botanical"}:
        return b.strip()
    return ""


def serving_best(drink: dict) -> str:
    s = drink.get("serving") or {}
    if isinstance(s, dict) and s.get("best"):
        return str(s["best"]).rstrip(".")
    return ""


def is_peated(drink: dict) -> bool:
    tags = {str(t) for t in (drink.get("flavorTags") or [])}
    if tags & {"dim", "iodin", "medicinski", "morski"}:
        return True
    blob = f"{drink.get('name','')} {drink.get('region','')}".lower()
    return any(x in blob for x in ("islay", "peat", "ardbeg", "laphroaig", "lagavulin"))


def whisky_pair(d: dict) -> tuple[dict[str, str], dict[str, str]]:
    name = short_name(d.get("name") or d["id"])
    region = d.get("region") or d.get("country") or "Škotska"
    tags = tags_list(d)
    tag_s = tags_join(tags)
    body_hr, body_en = body_word(d)
    abv = abv_s(d)
    age = age_bit(d.get("name") or "")
    finish = finish_bit(d.get("name") or "")
    best = serving_best(d)
    q = d.get("qualityScore")
    peat = is_peated(d)
    did = d["id"]

    age_clause = f", oznaka {age}" if age else ""
    finish_clause = f", {finish}" if finish else ""
    abv_clause = f" na {abv}" if abv else ""
    serve_clause = f" Serviranje: {best}." if best else ""
    q_clause = ""
    try:
        if q is not None and float(q) >= 8.5:
            q_clause = hpick(
                did,
                [
                    " U katalogu stoji među jačim ocjenama.",
                    " Brojke kvalitete je guraju iznad prosjeka police.",
                    " To nije ulazna boca po ocjeni u našem katalogu.",
                ],
            )
    except (TypeError, ValueError):
        pass

    if peat:
        frames_hr = [
            f"{name}{age_clause} s Islaya/dimljenog kruga ({region}){abv_clause}: {tag_s} u {body_hr}{finish_clause}. Dim ne traži žurbu.{serve_clause}{q_clause}",
            f"Kod {name} dim dolazi prvi — {tag_s}, {body_hr}{abv_clause}. Regija: {region}{finish_clause}.{serve_clause}{q_clause}",
            f"{name} drži peated karakter ({region}): {tag_s}. Tijelo je {body_hr.replace(' tijelo','')}{abv_clause}{finish_clause}.{serve_clause}{q_clause}",
            f"{region} u čaši preko {name}{age_clause}: {tag_s} i {body_hr}{abv_clause}. Kap vode često otkrije jod ili pepeo.{serve_clause}{q_clause}",
        ]
        frames_en = [
            f"{name}{age_clause} from the peated circle ({region}){abv_clause}: {tag_s} in {body_en}{finish_clause}. Smoke does not want haste.{serve_clause}{q_clause}",
            f"With {name}, smoke leads — {tag_s}, {body_en}{abv_clause}. Region: {region}{finish_clause}.{serve_clause}{q_clause}",
            f"{name} keeps a peated character ({region}): {tag_s}. Body reads {body_en}{abv_clause}{finish_clause}.{serve_clause}{q_clause}",
            f"{region} in the glass via {name}{age_clause}: {tag_s} and {body_en}{abv_clause}. A drop of water often opens iodine or ash.{serve_clause}{q_clause}",
        ]
        hints_hr = [
            f"Uz {name} biraj maduro ili puni Habano — most je pepeo i zemlja, ne citrus.",
            f"Dimljeni profil od {name} traži sporiji dim i kraći gutljaj; Connecticut ostaje preblag.",
            f"Peated boca kao {name} sjeda uz tamniji pokrov; prva trećina cigare neka bude mirna.",
            f"Ne forsiraš lagani shade uz {name}: jod i dim preglase nijansu.",
        ]
        hints_en = [
            f"With {name} pick maduro or a full Habano — bridge on ash and earth, not citrus.",
            f"The peated profile of {name} wants a slower puff and a smaller sip; Connecticut stays too mild.",
            f"A peated bottle like {name} sits with a darker wrapper; keep the cigar’s first third calm.",
            f"Do not force a light shade with {name}: iodine and smoke cover nuance.",
        ]
    elif "kentucky" in (region or "").lower() or "bourbon" in (name or "").lower() or "tennessee" in (region or "").lower():
        frames_hr = [
            f"{name} ({region}){abv_clause}: američki hrast nosi {tag_s} u {body_hr}{finish_clause}.{serve_clause}{q_clause}",
            f"Bourbon/Tennessee linija {name}{age_clause} drži {tag_s}. Regija {region}{abv_clause}; tijelo {body_hr.replace(' tijelo','')}.{serve_clause}{q_clause}",
            f"U {name} čuješ {tag_s} prije začina — {region}{abv_clause}, {body_hr}{finish_clause}.{serve_clause}{q_clause}",
            f"{name} je slatko-hrastov američki profil: {tag_s}, {body_hr}{abv_clause}.{serve_clause}{q_clause}",
        ]
        frames_en = [
            f"{name} ({region}){abv_clause}: American oak carries {tag_s} in {body_en}{finish_clause}.{serve_clause}{q_clause}",
            f"Bourbon/Tennessee line {name}{age_clause} holds {tag_s}. Region {region}{abv_clause}; body {body_en}.{serve_clause}{q_clause}",
            f"In {name} you hear {tag_s} before spice — {region}{abv_clause}, {body_en}{finish_clause}.{serve_clause}{q_clause}",
            f"{name} is a sweet-oak American profile: {tag_s}, {body_en}{abv_clause}.{serve_clause}{q_clause}",
        ]
        hints_hr = [
            f"Uz {name} idi na Habano ili blagi maduro — vanilija i hrast traže topliji dim.",
            f"Američki hrast u {name} ne voli preblagi Connecticut; robusto drži ritam.",
            f"Slatkoća {name} mosti s tamnijim pokrovom; gutljaj neka prati drugi dim.",
            f"Uz {name} izbjegni vrlo laganu panatelu — boca je teža od nje.",
        ]
        hints_en = [
            f"With {name} go Habano or a gentle maduro — vanilla and oak want warmer smoke.",
            f"American oak in {name} does not love a too-mild Connecticut; a robusto keeps pace.",
            f"The sweetness of {name} bridges to a darker wrapper; let the sip follow the second puff.",
            f"With {name} skip a very light panatela — the bottle is heavier than that format.",
        ]
    elif "japan" in (region or "").lower() or "japan" in (str(d.get("country") or "")).lower():
        frames_hr = [
            f"{name} ({region}){abv_clause}: {tag_s} u {body_hr}, često urednija građa od peated otoka{finish_clause}.{serve_clause}{q_clause}",
            f"Japanski profil {name}{age_clause} drži {tag_s}. Tijelo {body_hr.replace(' tijelo','')}{abv_clause}.{serve_clause}{q_clause}",
            f"{name} ne viče dimom — {tag_s}, {region}{abv_clause}, {body_hr}{finish_clause}.{serve_clause}{q_clause}",
            f"U {name} preciznost ide ispred snage: {tag_s} i {body_hr}.{serve_clause}{q_clause}",
        ]
        frames_en = [
            f"{name} ({region}){abv_clause}: {tag_s} in {body_en}, often tidier than peated island malt{finish_clause}.{serve_clause}{q_clause}",
            f"Japanese profile {name}{age_clause} holds {tag_s}. Body {body_en}{abv_clause}.{serve_clause}{q_clause}",
            f"{name} does not shout peat — {tag_s}, {region}{abv_clause}, {body_en}{finish_clause}.{serve_clause}{q_clause}",
            f"In {name} precision leads strength: {tag_s} and {body_en}.{serve_clause}{q_clause}",
        ]
        hints_hr = [
            f"Uz {name} biraj čistiji Habano ili Cameroon — maduro lako preglasi nijansu.",
            f"Japanska urednost {name} traži miran draw i srednji format.",
            f"Ne stavljaj najslađi maduro uz {name}; most je cedar, ne karamela.",
            f"Uz {name} kratki Habano u prvoj trećini često dovoljan.",
        ]
        hints_en = [
            f"With {name} prefer a cleaner Habano or Cameroon — maduro easily covers nuance.",
            f"The Japanese tidiness of {name} wants a calm draw and a medium format.",
            f"Do not put the sweetest maduro with {name}; bridge on cedar, not caramel.",
            f"With {name} a short Habano in the first third is often enough.",
        ]
    else:
        frames_hr = [
            f"{name} ({region}){age_clause}{abv_clause}: {tag_s} uz {body_hr}{finish_clause}.{serve_clause}{q_clause}",
            f"U {name} vodi {tag_s}. Regija {region}, tijelo {body_hr.replace(' tijelo','')}{abv_clause}{finish_clause}.{serve_clause}{q_clause}",
            f"{name} drži {tag_s} bez peated buke — {region}{abv_clause}, {body_hr}.{serve_clause}{q_clause}",
            f"Profil {name}{age_clause}: {tag_s}. To je {body_hr} iz {region}{abv_clause}{finish_clause}.{serve_clause}{q_clause}",
            f"{region} preko {name}: {tag_s} i {body_hr}{abv_clause}. Ne forsiraš overproof ritam.{serve_clause}{q_clause}",
        ]
        frames_en = [
            f"{name} ({region}){age_clause}{abv_clause}: {tag_s} with {body_en}{finish_clause}.{serve_clause}{q_clause}",
            f"In {name}, {tag_s} leads. Region {region}, body {body_en}{abv_clause}{finish_clause}.{serve_clause}{q_clause}",
            f"{name} holds {tag_s} without peated noise — {region}{abv_clause}, {body_en}.{serve_clause}{q_clause}",
            f"Profile of {name}{age_clause}: {tag_s}. That is {body_en} from {region}{abv_clause}{finish_clause}.{serve_clause}{q_clause}",
            f"{region} via {name}: {tag_s} and {body_en}{abv_clause}. Do not force an overproof pace.{serve_clause}{q_clause}",
        ]
        hints_hr = [
            f"Uz {name} srednji Habano ili Cameroon — {tag_s} traži čist most.",
            f"Tijelo {name} sjeda uz robusto; izbjegni najteži maduro ako je boca suša.",
            f"Uz {name} prva trećina cigare + prvi gutljaj otkrivaju most.",
            f"Ne sparuj {name} sa spiced rumom iste večeri — profil se zamuti.",
            f"Uz {name} biraj format koji traje koliko i gutljaj, ne duže.",
        ]
        hints_en = [
            f"With {name} a medium Habano or Cameroon — {tag_s} wants a clean bridge.",
            f"The body of {name} sits with a robusto; skip the heaviest maduro if the bottle is drier.",
            f"With {name} the cigar’s first third + first sip reveal the bridge.",
            f"Do not pair {name} with spiced rum the same evening — the profile muddies.",
            f"With {name} choose a format that lasts as long as the sip, not longer.",
        ]

    notes = {"hr": hpick(did, frames_hr).strip(), "en": hpick(did + ":en", frames_en).strip()}
    hint = {"hr": hpick(did + ":h", hints_hr).strip(), "en": hpick(did + ":he", hints_en).strip()}
    return notes, hint


def gin_pair(d: dict) -> tuple[dict[str, str], dict[str, str]]:
    name = short_name(d.get("name") or d["id"])
    style = str(d.get("style") or d.get("region") or "gin")
    region = d.get("region") or ""
    tags = tags_list(d) or ["borovica"]
    tag_s = tags_join(tags)
    abv = abv_s(d)
    botan = botan_label(d)
    did = d["id"]
    body_hr, body_en = body_word(d)
    abv_c = f" ({abv})" if abv else ""
    botan_c = f", {botan}" if botan else ""

    frames_hr = [
        f"{name}{abv_c} — {style}{botan_c}. Nos nosi {tag_s}; {body_hr}. G&T ili martini, ne desertni gutljaj.",
        f"U {name} borovica dijeli mjesto s {tag_s}. Stil: {style}{abv_c}. Uz cigaru format neka bude kraći.",
        f"{name} ({region or style}) drži {tag_s} u {body_hr}. Ne forsiraš maduro uz ovaj gin.",
        f"Profil {name}: {tag_s}. To je {style}{abv_c} — svježina prije težine.{botan_c}",
        f"{name} ide u čašu zbog {tag_s}, ne zbog slatkoće. Stil {style}{abv_c}, tijelo {body_hr.replace(' tijelo','')}.",
    ]
    frames_en = [
        f"{name}{abv_c} — {style}{botan_c}. The nose carries {tag_s}; {body_en}. G&T or martini, not a dessert sip.",
        f"In {name}, juniper shares space with {tag_s}. Style: {style}{abv_c}. With a cigar keep the format shorter.",
        f"{name} ({region or style}) holds {tag_s} in {body_en}. Do not force maduro with this gin.",
        f"Profile of {name}: {tag_s}. That is {style}{abv_c} — freshness before weight.{botan_c}",
        f"{name} goes in the glass for {tag_s}, not sweetness. Style {style}{abv_c}, body {body_en}.",
    ]
    citrusy = "citrus" in {str(t) for t in (d.get("flavorTags") or [])} or "cvjetno" in {
        str(t) for t in (d.get("flavorTags") or [])
    }
    if citrusy:
        hints_hr = [
            f"Uz {name} Connecticut ili panatela — citrus lako preglasi tamni pokrov.",
            f"Svježina {name} traži rijedak dim; maduro ostavi za drugi gutljaj večeri.",
            f"Uz {name} biraj kratki shade i ne žuri s drugim dimom.",
            f"Gin kao {name} voli hladniji draw i blagu cigaru.",
        ]
        hints_en = [
            f"With {name} Connecticut or panatela — citrus easily covers a dark wrapper.",
            f"The freshness of {name} wants sparse smoke; leave maduro for a later sip.",
            f"With {name} pick a short shade and do not rush the second puff.",
            f"A gin like {name} likes a cooler draw and a mild cigar.",
        ]
    else:
        hints_hr = [
            f"Uz {name} blagi Habano ili Cameroon — borovica drži most.",
            f"Za {name} ne treba puna snaga cigare; srednji format dovoljan.",
            f"Uz {name} izbjegni slatki maduro; začin u ginu zamuti se.",
            f"Martini uz {name} + kratka cigara: manje dimova, više nijanse.",
        ]
        hints_en = [
            f"With {name} a mild Habano or Cameroon — juniper holds the bridge.",
            f"For {name} you do not need full cigar strength; a medium format is enough.",
            f"With {name} skip a sweet maduro; spice in the gin muddies.",
            f"Martini with {name} + a short cigar: fewer puffs, more nuance.",
        ]
    return (
        {"hr": hpick(did, frames_hr).strip(), "en": hpick(did + ":en", frames_en).strip()},
        {"hr": hpick(did + ":h", hints_hr).strip(), "en": hpick(did + ":he", hints_en).strip()},
    )


def tequila_pair(d: dict) -> tuple[dict[str, str], dict[str, str]]:
    name = short_name(d.get("name") or d["id"])
    style = str(d.get("style") or d.get("region") or "tequila")
    tags = tags_join(tags_list(d) or ["agava"])
    body_hr, body_en = body_word(d)
    abv = abv_s(d)
    did = d["id"]
    abv_c = f" na {abv}" if abv else ""
    frames_hr = [
        f"{name} ({style}){abv_c}: {tags} uz {body_hr}. Neat ili rocks; tempo sporiji nego uz gin.",
        f"U {name} agava dijeli prostor s {tags}. Stil {style}, tijelo {body_hr.replace(' tijelo','')}{abv_c}.",
        f"{name} drži {tags} — {style}{abv_c}. Uz cigaru pusti drugi dim nakon gutljaja.",
        f"Profil {name}: {tags}. To je {style} s {body_hr}{abv_c}.",
    ]
    frames_en = [
        f"{name} ({style}){abv_c}: {tags} with {body_en}. Neat or rocks; slower pace than with gin.",
        f"In {name}, agave shares space with {tags}. Style {style}, body {body_en}{abv_c}.",
        f"{name} holds {tags} — {style}{abv_c}. With a cigar, let the second puff follow the sip.",
        f"Profile of {name}: {tags}. That is {style} with {body_en}{abv_c}.",
    ]
    blanco = "blanco" in style.lower() or "silver" in style.lower()
    if blanco:
        hints_hr = [
            f"Uz {name} Connecticut ili kratki Habano — agava ostaje čista.",
            f"Blanco profil {name} ne voli slatki maduro.",
            f"Uz {name} rijedak dim; prva trećina dovoljna.",
        ]
        hints_en = [
            f"With {name} Connecticut or a short Habano — agave stays clean.",
            f"The blanco profile of {name} does not love a sweet maduro.",
            f"With {name} sparse smoke; the first third is enough.",
        ]
    else:
        hints_hr = [
            f"Uz {name} Habano srednjeg tijela — hrast i {tags} traže topliji dim.",
            f"Reposado/añejo kao {name} sjeda uz blagi maduro, ne uz panatelu.",
            f"Uz {name} most je karamela/hrast; Connecticut može ostati prazan.",
        ]
        hints_en = [
            f"With {name} a medium Habano — oak and {tags} want warmer smoke.",
            f"Reposado/añejo like {name} sits with a gentle maduro, not a panatela.",
            f"With {name} the bridge is caramel/oak; Connecticut can stay empty.",
        ]
    return (
        {"hr": hpick(did, frames_hr).strip(), "en": hpick(did + ":en", frames_en).strip()},
        {"hr": hpick(did + ":h", hints_hr).strip(), "en": hpick(did + ":he", hints_en).strip()},
    )


def rum_pair(d: dict) -> tuple[dict[str, str], dict[str, str]]:
    name = short_name(d.get("name") or d["id"])
    region = d.get("region") or d.get("style") or ""
    tags = tags_list(d)
    tag_s = tags_join(tags)
    body_hr, body_en = body_word(d)
    abv = abv_s(d)
    age = age_bit(d.get("name") or "")
    finish = finish_bit(d.get("name") or "")
    additive = str(d.get("additiveStatus") or "")
    detail = d.get("additiveDetail") or {}
    detail_hr = detail.get("hr") if isinstance(detail, dict) else ""
    did = d["id"]
    abv_c = f" ({abv})" if abv else ""
    age_c = f", {age}" if age else ""
    finish_c = f", {finish}" if finish else ""
    try:
        sweet = int(d.get("sweetness") or 0)
    except (TypeError, ValueError):
        sweet = 0

    if additive in {"flavored", "spiced"} or sweet >= 4:
        frames_hr = [
            f"{name}{abv_c} — {region}{age_c}: {tag_s}, izraženija slatkoća{finish_c}. Više koktel/desert nego sipper uz cigaru.",
            f"U {name} vodi slatkoća ({tag_s}). Regija {region}{abv_c}; neat uz dim rijetko je prvi izbor.",
            f"{name} je aromatiziraniji stil: {tag_s}. {detail_hr or 'Šećer i arome nose gutljaj.'}",
            f"Profil {name}{age_c}: {tag_s} na {region}{abv_c}. Za sparivanje bolje čisti aged rum.",
        ]
        frames_en = [
            f"{name}{abv_c} — {region}{age_c}: {tag_s}, higher sweetness{finish_c}. More cocktail/dessert than a cigar sipper.",
            f"In {name}, sweetness leads ({tag_s}). Region {region}{abv_c}; neat with smoke is rarely first choice.",
            f"{name} is a more flavoured style: {tag_s}. {(detail.get('en') if isinstance(detail, dict) else '') or 'Sugar and aromas carry the sip.'}",
            f"Profile of {name}{age_c}: {tag_s} on {region}{abv_c}. For pairing, prefer a clean aged rum.",
        ]
        hints_hr = [
            f"Ako ide {name} uz dim, kraći Connecticut — šećer preglasi nijansu.",
            f"Uz {name} ne forsiraš kompleksnu cigaru; format neka bude kratak.",
            f"Bolje prebaci večer na čisti rum nego gurat {name} uz maduro.",
            f"Uz {name} jedan kratki dim pa soda — ne tasting maraton.",
        ]
        hints_en = [
            f"If {name} meets smoke, a shorter Connecticut — sugar covers nuance.",
            f"With {name} do not force a complex cigar; keep the format short.",
            f"Better switch the evening to a clean rum than push {name} with maduro.",
            f"With {name} one short puff then soda — not a tasting marathon.",
        ]
    else:
        add_bit = f" {detail_hr}" if detail_hr else ""
        frames_hr = [
            f"{name}{abv_c} — {region}{age_c}: {tag_s}, {body_hr}{finish_c}.{add_bit} Čisto ili kap vode.",
            f"U {name} vodi {tag_s}. Destilat s {region}, tijelo {body_hr.replace(' tijelo','')}{abv_c}{finish_c}.{add_bit}",
            f"{name} drži {tag_s} bez peated buke — {region}{abv_c}, {body_hr}.{add_bit}",
            f"Profil {name}{age_c}: {tag_s}. To je {body_hr} iz {region}{abv_c}{finish_c}.{add_bit}",
            f"{region} preko {name}: {tag_s} i {body_hr}{abv_c}. Ritam gutljaja neka prati dim.{add_bit}",
        ]
        frames_en = [
            f"{name}{abv_c} — {region}{age_c}: {tag_s}, {body_en}{finish_c}. Neat or a drop of water.",
            f"In {name}, {tag_s} leads. Spirit from {region}, body {body_en}{abv_c}{finish_c}.",
            f"{name} holds {tag_s} without peated noise — {region}{abv_c}, {body_en}.",
            f"Profile of {name}{age_c}: {tag_s}. That is {body_en} from {region}{abv_c}{finish_c}.",
            f"{region} via {name}: {tag_s} and {body_en}{abv_c}. Let sip rhythm follow the smoke.",
        ]
        b = body_word(d)[0]
        if "punije" in b or "esterski funk" in tag_s:
            hints_hr = [
                f"Uz {name} maduro ili puni Habano — {tag_s} traži težinu.",
                f"Punije tijelo {name} ne sjeda uz Connecticut; gutljaj neka bude manji.",
                f"Uz {name} sporiji dim u srednjoj trećini cigare.",
                f"Ester/tijelo {name} mosti s tamnijim pokrovom, ne sa shade.",
            ]
            hints_en = [
                f"With {name} maduro or a full Habano — {tag_s} wants weight.",
                f"The fuller body of {name} does not sit with Connecticut; keep sips smaller.",
                f"With {name} slower smoke in the cigar’s middle third.",
                f"Ester/body in {name} bridges to a darker wrapper, not shade.",
            ]
        elif "laganije" in b:
            hints_hr = [
                f"Uz {name} Connecticut ili Cameroon — boca je laganija od madura.",
                f"Laganiji {name} voli kraći format; prva trećina dovoljna.",
                f"Ne preglasi {name} punim madurom.",
                f"Uz {name} blagi Habano drži most bez gušenja voća.",
            ]
            hints_en = [
                f"With {name} Connecticut or Cameroon — the bottle is lighter than maduro.",
                f"Lighter {name} likes a shorter format; the first third is enough.",
                f"Do not cover {name} with a full maduro.",
                f"With {name} a mild Habano holds the bridge without smothering fruit.",
            ]
        else:
            hints_hr = [
                f"Uz {name} Habano robusto — {tag_s} kao most.",
                f"Srednje tijelo {name} sjeda uz zreliji corojo ili Cameroon.",
                f"Uz {name} izbjegni spiced rum u istoj večeri.",
                f"Prvi gutljaj {name} + prva trećina cigare otkrivaju sparivanje.",
            ]
            hints_en = [
                f"With {name} a Habano robusto — {tag_s} as the bridge.",
                f"Medium body in {name} sits with a riper corojo or Cameroon.",
                f"With {name} skip spiced rum the same evening.",
                f"First sip of {name} + the cigar’s first third reveal the pairing.",
            ]

    return (
        {"hr": hpick(did, frames_hr).strip(), "en": hpick(did + ":en", frames_en).strip()},
        {"hr": hpick(did + ":h", hints_hr).strip(), "en": hpick(did + ":he", hints_en).strip()},
    )


def ensure_min_len(block: dict[str, str], *, min_len: int = 40) -> dict[str, str]:
    hr = (block.get("hr") or "").strip()
    en = (block.get("en") or "").strip()
    if len(hr) < min_len:
        hr = f"{hr} Biraj ritam gutljaja prema tijelu večeri."
    if len(en) < min_len:
        en = f"{en} Match sip pace to the evening’s body."
    return {"hr": hr.strip(), "en": en.strip()}


def ensure_unique(entries: dict[str, dict], field: str = "notes") -> None:
    """If two HR texts collide, append a distinctive id-tail clause."""
    seen: dict[str, str] = {}
    for did, entry in entries.items():
        block = entry.get(field) or {}
        block = ensure_min_len({"hr": block.get("hr") or "", "en": block.get("en") or ""})
        hr = block["hr"]
        if hr in seen and seen[hr] != did:
            brandish = did.split("-")[1] if "-" in did else did[-6:]
            block["hr"] = f"{hr} (bočica {brandish} u našem katalogu)."
            block["en"] = f"{block['en'].rstrip('.')} (catalog id cue: {brandish})."
            hr = block["hr"]
        entry[field] = block
        seen[hr] = did


def write_enrichment(path: Path, enrichments: dict[str, dict]) -> None:
    doc = {
        "version": 1,
        "description": "Unique catalog-grounded bottle notes + cigarHint (no shared template closings).",
        "enrichments": enrichments,
    }
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    whiskies = json.loads((APP / "whiskies.json").read_text(encoding="utf-8"))
    gins = json.loads((APP / "gins.json").read_text(encoding="utf-8"))
    tequilas = json.loads((APP / "tequilas.json").read_text(encoding="utf-8"))
    rums = json.loads((APP / "rums.json").read_text(encoding="utf-8"))

    wh: dict[str, dict] = {}
    for d in whiskies:
        notes, hint = whisky_pair(d)
        wh[d["id"]] = {"sourceVideoIds": [], "notes": notes, "cigarHint": hint}
    ensure_unique(wh, "notes")
    ensure_unique(wh, "cigarHint")

    gi: dict[str, dict] = {}
    for d in gins:
        notes, hint = gin_pair(d)
        gi[d["id"]] = {"sourceVideoIds": [], "notes": notes, "cigarHint": hint}
    ensure_unique(gi, "notes")
    ensure_unique(gi, "cigarHint")

    tq: dict[str, dict] = {}
    for d in tequilas:
        notes, hint = tequila_pair(d)
        tq[d["id"]] = {"sourceVideoIds": [], "notes": notes, "cigarHint": hint}
    ensure_unique(tq, "notes")
    ensure_unique(tq, "cigarHint")

    # Preserve hand-curated rum enrichments that are already long and unique; rewrite template ones
    rum_payload = json.loads((DATA / "rum_enrichments.json").read_text(encoding="utf-8"))
    existing = rum_payload.get("enrichments") or {}
    ru: dict[str, dict] = {}
    template_mark = re.compile(
        r"Čisto ili s kap vode; drži ritam uz cigaru\.|Profil tipično|pouzdana boca za stol",
        re.I,
    )
    for d in rums:
        old = existing.get(d["id"])
        old_hr = ((old or {}).get("notes") or {}).get("hr") or ((d.get("notes") or {}).get("hr") or "")
        # Always rewrite if template-ish OR short OR missing unique name lead
        must = (
            not old_hr
            or len(old_hr) < 80
            or bool(template_mark.search(old_hr))
            or old_hr.count("Profil drži") > 0
            or "Heuristika" in old_hr
        )
        if must or True:
            # Force full unique pass for all rums — user asked every description unique
            notes, hint = rum_pair(d)
            vids = (old or {}).get("sourceVideoIds") or []
            ru[d["id"]] = {"sourceVideoIds": vids, "notes": notes, "cigarHint": hint}
    ensure_unique(ru, "notes")
    ensure_unique(ru, "cigarHint")

    def uniq_stats(label: str, enr: dict[str, dict]) -> None:
        notes = [e["notes"]["hr"] for e in enr.values()]
        hints = [e["cigarHint"]["hr"] for e in enr.values()]
        print(
            label,
            "n",
            len(enr),
            "unique_notes",
            len(set(notes)),
            "unique_hints",
            len(set(hints)),
        )

    uniq_stats("whisky", wh)
    uniq_stats("gin", gi)
    uniq_stats("tequila", tq)
    uniq_stats("rum", ru)

    if args.dry_run:
        return 0

    # preserve whisky sourceVideoIds from previous file if present
    prev_wh = DATA / "whisky_enrichments.json"
    if prev_wh.is_file():
        prev = json.loads(prev_wh.read_text(encoding="utf-8")).get("enrichments") or {}
        for did, entry in wh.items():
            if did in prev and prev[did].get("sourceVideoIds"):
                entry["sourceVideoIds"] = prev[did]["sourceVideoIds"]

    write_enrichment(DATA / "whisky_enrichments.json", wh)
    write_enrichment(DATA / "gin_enrichments.json", gi)
    write_enrichment(DATA / "tequila_enrichments.json", tq)
    rum_payload["enrichments"] = ru
    rum_payload["description"] = "Unique catalog-grounded rum notes + cigarHint (quarantine + full pass)."
    (DATA / "rum_enrichments.json").write_text(
        json.dumps(rum_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote enrichment files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
