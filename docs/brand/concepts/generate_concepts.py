#!/usr/bin/env python3
"""Generira skice logo-koncepata (SVG + PNG preview) za Cigar & Drink Pairing.

Sve skice dijele istu paletu (koža / duhan / konjak / band-zlato) i isti
viewBox 0 0 200 200, pa se mogu izravno usporediti jedna do druge.

    python docs/brand/concepts/generate_concepts.py

PNG preview traži cairosvg (`pip install cairosvg`); ako ga nema, skripta
ispiše upozorenje i svejedno zapiše SVG-ove.
"""

from __future__ import annotations

import math
from pathlib import Path

OUT = Path(__file__).parent

# --- Paleta -----------------------------------------------------------------
# Zemljano/kožno; izvedeno iz postojeće "Humidor" palete u app/src/index.css.
DUHAN = "#241a12"  # najdublja smeđa — pozadina pečata i tamnih podloga
KOZA = "#6b4a31"  # sedlasta koža — masa, tijelo znaka
KONJAK = "#a9662f"  # tekućina u čaši — jedini "topli" akcent
ZLATO = "#c9a35c"  # band zlato — linija, keyline
PAPIR = "#e8dbc0"  # stari label papir — svijetla podloga
ZAR = "#8a3a2a"  # oxblood — žar, koristi se maksimalno jednom po znaku

SIZE = 200
C = SIZE / 2


def wobble_ellipse(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    lobes: int = 5,
    amp: float = 4.0,
    phase: float = 0.0,
    steps: int = 180,
) -> str:
    """Zatvorena putanja ovala kojemu radijus lagano 'diše' — ručno motan,
    ne strojno savršen. Vraća `d` atribut."""
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        k = 1 + (amp / max(rx, ry)) * math.sin(lobes * t + phase)
        pts.append((cx + rx * k * math.cos(t), cy + ry * k * math.sin(t)))
    d = f"M {pts[0][0]:.2f} {pts[0][1]:.2f} " + " ".join(
        f"L {x:.2f} {y:.2f}" for x, y in pts[1:]
    )
    return d + " Z"


def arc(cx: float, cy: float, rx: float, ry: float, a0: float, a1: float) -> str:
    """Luk elipse od kuta a0 do a1 (stupnjevi, matematički smjer, y prema gore)."""
    x0, y0 = cx + rx * math.cos(math.radians(a0)), cy - ry * math.sin(math.radians(a0))
    x1, y1 = cx + rx * math.cos(math.radians(a1)), cy - ry * math.sin(math.radians(a1))
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 0 if a1 > a0 else 1  # y je obrnut, pa je i sweep obrnut
    return f"M {x0:.2f} {y0:.2f} A {rx} {ry} 0 {large} {sweep} {x1:.2f} {y1:.2f}"


def spiral(cx: float, cy: float, r0: float, r1: float, turns: float, steps: int = 400) -> str:
    pts = []
    for i in range(steps + 1):
        u = i / steps
        t = 2 * math.pi * turns * u
        r = r0 + (r1 - r0) * u
        pts.append((cx + r * math.cos(t), cy + r * math.sin(t)))
    return f"M {pts[0][0]:.2f} {pts[0][1]:.2f} " + " ".join(
        f"L {x:.2f} {y:.2f}" for x, y in pts[1:]
    )


def svg(body: str, title: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" '
        f'role="img" aria-label="{title}">\n{body}\n</svg>\n'
    )


# --- 1. BANDEROLA -----------------------------------------------------------
# Prsten cigar-banda je ovalni kartuš; ista ta elipsa gledana odozgo je i obod
# čaše. Puna donja trećina = razina pića. Dva elementa, jedno čitanje po sloju.
def banderola(na_papiru: bool = False) -> str:
    # Zlato na papiru pada ispod čitljivog kontrasta, pa svijetla verzija vodi liniju
    # u koži. Geometrija je identična — mijenja se samo boja poteza.
    linija = KOZA if na_papiru else ZLATO
    body = f"""  <defs>
    <clipPath id="b-unut"><ellipse cx="{C}" cy="{C}" rx="70" ry="49"/></clipPath>
  </defs>
  <g clip-path="url(#b-unut)">
    <rect x="0" y="117" width="200" height="83" fill="{KONJAK}"/>
  </g>
  <ellipse cx="{C}" cy="{C}" rx="70" ry="49" fill="none" stroke="{linija}" stroke-width="2.5" opacity="0.55"/>
  <ellipse cx="{C}" cy="{C}" rx="83" ry="61" fill="none" stroke="{linija}" stroke-width="7"/>"""
    return svg(body, "Banderola")


# --- 2. MENISKUS ------------------------------------------------------------
# Čaša odozgo: obod + razina pića, a u praznini iznad razine lebdi kolut dima.
def meniskus() -> str:
    body = f"""  <defs>
    <clipPath id="m-casa"><ellipse cx="{C}" cy="108" rx="70" ry="62"/></clipPath>
  </defs>
  <g clip-path="url(#m-casa)">
    <rect x="0" y="122" width="200" height="78" fill="{KONJAK}"/>
  </g>
  <ellipse cx="{C}" cy="108" rx="70" ry="62" fill="none" stroke="{ZLATO}" stroke-width="7"/>
  <ellipse cx="{C}" cy="72" rx="31" ry="11" fill="none" stroke="{ZLATO}" stroke-width="3.5" opacity="0.6"/>"""
    return svg(body, "Meniskus")


# --- 3. PRESJEK -------------------------------------------------------------
# Cigara s glave: nepravilan krug ručno motanog omota, unutra jedan potez
# smotanog uloška, u sredini žar.
def presjek() -> str:
    body = f"""  <path d="{wobble_ellipse(C, C, 74, 74, lobes=6, amp=2.4, phase=0.7)}" fill="none" stroke="{KOZA}" stroke-width="12"/>
  <path d="{spiral(C, C, 16, 52, 1.6)}" fill="none" stroke="{ZLATO}" stroke-width="7" stroke-linecap="round"/>
  <circle cx="{C}" cy="{C}" r="11" fill="{ZAR}"/>"""
    return svg(body, "Presjek")


# --- 4. SPOJ ----------------------------------------------------------------
# Dvije elipse — jedna cigara, jedna piće — a presjek je ono što app radi.
def spoj() -> str:
    body = f"""  <defs>
    <clipPath id="s-a"><ellipse cx="{C}" cy="{C}" rx="80" ry="43" transform="rotate(-27 {C} {C})"/></clipPath>
  </defs>
  <g clip-path="url(#s-a)">
    <ellipse cx="{C}" cy="{C}" rx="80" ry="43" transform="rotate(27 {C} {C})" fill="{KONJAK}"/>
  </g>
  <ellipse cx="{C}" cy="{C}" rx="80" ry="43" transform="rotate(-27 {C} {C})" fill="none" stroke="{ZLATO}" stroke-width="6"/>
  <ellipse cx="{C}" cy="{C}" rx="80" ry="43" transform="rotate(27 {C} {C})" fill="none" stroke="{ZLATO}" stroke-width="6"/>"""
    return svg(body, "Spoj")


# --- 5. PEČAT ---------------------------------------------------------------
# Banderola utisnuta u nepravilan pečat od voska/kože — puna forma, jedina
# skica koja sama nosi app ikonu bez dodatne podloge.
def pecat() -> str:
    body = f"""  <defs>
    <clipPath id="p-unut"><ellipse cx="{C}" cy="{C}" rx="55" ry="41" /></clipPath>
  </defs>
  <path d="{wobble_ellipse(C, C, 92, 84, lobes=5, amp=6, phase=1.1)}" fill="{KOZA}"/>
  <g clip-path="url(#p-unut)">
    <rect x="0" y="112" width="200" height="88" fill="{ZLATO}"/>
  </g>
  <ellipse cx="{C}" cy="{C}" rx="55" ry="41" fill="none" stroke="{ZLATO}" stroke-width="5.5"/>"""
    return svg(body, "Pečat")


# --- 6. LUK -----------------------------------------------------------------
# Jedan oval razlomljen na dva luka: tanki gornji (dim) i teški donji (piće).
# Debljina poteza nosi značenje — praznina sa strane je spoj.
def luk() -> str:
    body = f"""  <path d="{arc(C, C, 76, 66, 158, 22)}" fill="none" stroke="{ZLATO}" stroke-width="4.5" stroke-linecap="round" opacity="0.75"/>
  <path d="{arc(C, C, 76, 66, 202, 338)}" fill="none" stroke="{KONJAK}" stroke-width="14" stroke-linecap="round"/>"""
    return svg(body, "Luk")


CONCEPTS = {
    "01-banderola": banderola,
    "02-meniskus": meniskus,
    "03-presjek": presjek,
    "04-spoj": spoj,
    "05-pecat": pecat,
    "06-luk": luk,
    "01-banderola-papir": lambda: banderola(na_papiru=True),
}

# Skice koje se preview-aju samo na svojoj podlozi.
SAMO_SVIJETLO = {"01-banderola-papir"}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in CONCEPTS.items():
        markup = fn()
        (OUT / f"{name}.svg").write_text(markup, encoding="utf-8")
        print(f"  {name}.svg")

    try:
        import cairosvg  # noqa: PLC0415
    except ImportError:
        print("cairosvg nije instaliran — preskačem PNG preview.")
        return

    for name in CONCEPTS:
        podloge = ((PAPIR, "svijetlo"),) if name in SAMO_SVIJETLO else ((DUHAN, "tamno"), (PAPIR, "svijetlo"))
        for bg, suffix in podloge:
            cairosvg.svg2png(
                url=str(OUT / f"{name}.svg"),
                write_to=str(OUT / f"{name}-{suffix}.png"),
                output_width=384,
                output_height=384,
                background_color=bg,
            )
        print(f"  {name}-*.png")


if __name__ == "__main__":
    main()
