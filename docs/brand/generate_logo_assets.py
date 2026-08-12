#!/usr/bin/env python3
"""Jedini izvor istine za znak Cigar & Drink Pairinga.

Znak je sustav od dvije težine iste geometrije:

  * **Banderola** — linijski znak (prsten cigar-banda = obod čaše, donja
    trećina je razina pića). Ide u zaglavlje, na papir, u dokumente.
  * **Pečat** — ista banderola utisnuta u nepravilnu masu kože. Puna forma,
    pa nosi ikonu na početnom zaslonu i favicon na 16 px.

Skripta ispisuje SVG-ove, PNG-ove i `app/src/components/brandArt.ts` (putanje
koje React komponenta crta inline). Ništa od toga ne uređivati ručno — sve se
mijenja ovdje i ponovno ispiše:

    python docs/brand/generate_logo_assets.py

PNG izlaz traži cairosvg (`pip install cairosvg`).

Skice iz kojih je znak izabran žive u `docs/brand/concepts/`.
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BRAND = ROOT / "docs" / "brand"
PUBLIC = ROOT / "app" / "public"
SRC = ROOT / "app" / "src" / "components"

# --- Paleta -----------------------------------------------------------------
DUHAN = "#241a12"  # najdublja smeđa — podloga ikone
HUMIDOR = "#201812"  # pozadina appa (--color-humidor)
KOZA = "#6b4a31"  # sedlasta koža — masa pečata, linija na papiru
KONJAK = "#a9662f"  # tekućina — jedini topli akcent
ZLATO = "#c9a35c"  # band zlato — linija znaka
PAPIR = "#e8dbc0"

VB = 200  # svi znakovi dijele okvir 200×200
C = VB / 2


def ellipse_path(cx: float, cy: float, rx: float, ry: float) -> str:
    return (
        f"M {cx - rx:.2f} {cy:.2f} "
        f"A {rx:.2f} {ry:.2f} 0 1 0 {cx + rx:.2f} {cy:.2f} "
        f"A {rx:.2f} {ry:.2f} 0 1 0 {cx - rx:.2f} {cy:.2f} Z"
    )


def ring(cx: float, cy: float, rx: float, ry: float, bok: float, vrh: float) -> str:
    """Prsten kao ispuna između dvije elipse, s optičkim ispravkom: potez na
    vrhu i dnu je nijansu deblji od bočnog, inače oval izgleda stisnuto.
    Crta se s `fill-rule="evenodd"`."""
    return f"{ellipse_path(cx, cy, rx, ry)} {ellipse_path(cx, cy, rx - bok, ry - vrh)}"


def wobble(cx: float, cy: float, rx: float, ry: float, lobes: int, amp: float, phase: float, steps: int = 240) -> str:
    """Zatvorena putanja ovala kojemu radijus lagano 'diše' — ručno motan,
    ne strojno savršen."""
    pts = []
    for i in range(steps):
        t = 2 * math.pi * i / steps
        k = 1 + (amp / max(rx, ry)) * math.sin(lobes * t + phase)
        pts.append((cx + rx * k * math.cos(t), cy + ry * k * math.sin(t)))
    return (
        f"M {pts[0][0]:.2f} {pts[0][1]:.2f} "
        + " ".join(f"L {x:.2f} {y:.2f}" for x, y in pts[1:])
        + " Z"
    )


def razina(cx: float, cy: float, rx: float, ry: float, y: float, steps: int = 160) -> str:
    """Zatvoreni oblik pića: dio elipse ispod razine `y`. Jednobojna verzija ne
    može klipati pravokutnik — sve mora stati u jednu putanju s evenodd."""
    dy = (y - cy) / ry
    dy = max(-1.0, min(1.0, dy))
    t0 = math.asin(dy)  # desna strana, y = cy + ry*sin t
    pts = [(cx + rx * math.cos(t0), y)]
    for i in range(1, steps + 1):
        t = t0 + (math.pi - 2 * t0) * i / steps  # preko dna do lijeve strane
        pts.append((cx + rx * math.cos(t), cy + ry * math.sin(t)))
    return (
        f"M {pts[0][0]:.2f} {pts[0][1]:.2f} "
        + " ".join(f"L {x:.2f} {y:.2f}" for x, y in pts[1:])
        + " Z"
    )


# --- Geometrija -------------------------------------------------------------
# Banderola
MARK_RING = ring(C, C, 83, 61, bok=7.0, vrh=7.9)
MARK_KEYLINE = ring(C, C, 70, 49, bok=2.5, vrh=3.0)
MARK_LIQUID_CLIP = ellipse_path(C, C, 67.5, 46.0)
MARK_LIQUID_Y = 117  # razina pića

# Pečat
SEAL_BODY = wobble(C, C, 92, 84, lobes=5, amp=6, phase=1.1)
SEAL_RING = ring(C, C, 55, 41, bok=5.5, vrh=6.2)
SEAL_LIQUID_CLIP = ellipse_path(C, C, 49.5, 34.8)
SEAL_LIQUID_Y = 112

# Jednobojno: jedna boja, sve u jednoj putanji s fill-rule="evenodd".
#
# Banderola u jednoj boji ostaje pozitiv (prsten + keyline + puno piće), a
# pečat se mora obrnuti: masa je tinta, pa banderola u njoj postaje izrez —
# parnost preklapanja radi posao (masa 1× → tinta, prsten 2× → izrez,
# unutrašnjost 3× → tinta, piće 4× → izrez).
MARK_MONO = " ".join(
    [MARK_RING, MARK_KEYLINE, razina(C, C, 67.5, 46.0, MARK_LIQUID_Y)]
)
SEAL_MONO = " ".join(
    [SEAL_BODY, SEAL_RING, razina(C, C, 49.5, 34.8, SEAL_LIQUID_Y)]
)


def svg_open(title: str, size: int = VB) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'role="img" aria-label="{title}">\n'
    )


def mark(linija: str = ZLATO) -> str:
    return (
        svg_open("Cigar &amp; Drink Pairing")
        + f"""  <defs><clipPath id="m-razina"><path d="{MARK_LIQUID_CLIP}"/></clipPath></defs>
  <g clip-path="url(#m-razina)"><rect x="0" y="{MARK_LIQUID_Y}" width="{VB}" height="{VB - MARK_LIQUID_Y}" fill="{KONJAK}"/></g>
  <path d="{MARK_KEYLINE}" fill="{linija}" fill-rule="evenodd" opacity="0.55"/>
  <path d="{MARK_RING}" fill="{linija}" fill-rule="evenodd"/>
</svg>
"""
    )


def seal(background: str | None = None, pad: float = 0.0) -> str:
    """Pečat. `pad` je udio zraka sa svake strane (maskable ikona traži ~10 %)."""
    scale = 1 - 2 * pad
    off = VB * pad
    podloga = (
        f'  <rect width="{VB}" height="{VB}" fill="{background}"/>\n' if background else ""
    )
    return (
        svg_open("Cigar &amp; Drink Pairing")
        + podloga
        + f"""  <defs><clipPath id="s-razina"><path d="{SEAL_LIQUID_CLIP}"/></clipPath></defs>
  <g transform="translate({off:.2f} {off:.2f}) scale({scale:.4f})">
    <path d="{SEAL_BODY}" fill="{KOZA}"/>
    <g clip-path="url(#s-razina)"><rect x="0" y="{SEAL_LIQUID_Y}" width="{VB}" height="{VB - SEAL_LIQUID_Y}" fill="{ZLATO}"/></g>
    <path d="{SEAL_RING}" fill="{ZLATO}" fill-rule="evenodd"/>
  </g>
</svg>
"""
    )


def mono(putanja: str, tinta: str = "#000000") -> str:
    """Jedna boja, jedna putanja — za tisak u jednoj boji, graviranje, žig,
    faks-kvalitetu i svaku podlogu na kojoj dvije nijanse ne prežive."""
    return (
        svg_open("Cigar &amp; Drink Pairing")
        + f'  <path d="{putanja}" fill="{tinta}" fill-rule="evenodd"/>\n</svg>\n'
    )


MARK_TIGHT = f"{C - 83:.0f} {C - 61:.0f} {2 * 83:.0f} {2 * 61:.0f}"


BRAND_ART_TS = f"""// GENERIRANO — ne uređivati ručno.
// Izvor: docs/brand/generate_logo_assets.py (`python docs/brand/generate_logo_assets.py`)
//
// Putanje znaka koje <BrandMark /> crta inline, da logo u UI-u nasljeđuje
// boju teksta i ostane oštar na svakoj veličini. Prstenovi se ispunjavaju
// s fill-rule="evenodd" jer nose optički ispravak (potez na vrhu i dnu je
// deblji od bočnog) koji obični stroke ne može dati.

export const BRAND_SIZE = {VB};
export const BRAND_VIEWBOX = "0 0 {VB} {VB}";
/** Okvir stisnut na sam prsten banderole — bez zraka oko njega, za lockup
 *  gdje se vrh znaka poravnava s vrhom slova. */
export const MARK_VIEWBOX_TIGHT = "{MARK_TIGHT}";

/** Banderola — vanjski prsten banda. */
export const MARK_RING = "{MARK_RING}";
/** Banderola — unutarnji keyline. */
export const MARK_KEYLINE = "{MARK_KEYLINE}";
/** Oblik unutar kojeg stoji razina pića. */
export const MARK_LIQUID_CLIP = "{MARK_LIQUID_CLIP}";
/** Y na kojem počinje razina pića. */
export const MARK_LIQUID_Y = {MARK_LIQUID_Y};

/** Pečat — nepravilna masa kože. */
export const SEAL_BODY = "{SEAL_BODY}";
/** Pečat — utisnuta banderola. */
export const SEAL_RING = "{SEAL_RING}";
export const SEAL_LIQUID_CLIP = "{SEAL_LIQUID_CLIP}";
export const SEAL_LIQUID_Y = {SEAL_LIQUID_Y};

// Jednobojne verzije — cijeli znak u jednoj putanji, crta se s
// fill-rule="evenodd". Banderola ostaje pozitiv, pečat je izrez u masi.
/** Banderola u jednoj boji. */
export const MARK_MONO = "{MARK_MONO}";
/** Pečat u jednoj boji. */
export const SEAL_MONO = "{SEAL_MONO}";
"""


FLYER = ROOT / "marketing" / "flyer.html"
FLYER_START = "<!-- LOGO:pecat — sadržaj ispisuje docs/brand/generate_logo_assets.py -->"
FLYER_END = "<!-- /LOGO -->"


def upisi_u_flyer() -> None:
    """Flyer je jedna samostalna datoteka za PDF, pa znak mora biti inline —
    ali ne prepisan rukom. Sadržaj između markera je uvijek ispis ove skripte."""
    if not FLYER.exists():
        return
    html = FLYER.read_text(encoding="utf-8")
    if FLYER_START not in html or FLYER_END not in html:
        print(f"  {FLYER.relative_to(ROOT)} — markeri nedostaju, preskačem")
        return
    znak = seal().replace(
        "<svg ", '<svg class="seal" width="86" height="86" ', 1
    )
    prije, ostatak = html.split(FLYER_START, 1)
    _, poslije = ostatak.split(FLYER_END, 1)
    FLYER.write_text(
        f"{prije}{FLYER_START}\n{znak.rstrip()}\n    {FLYER_END}{poslije}",
        encoding="utf-8",
    )
    print(f"  {FLYER.relative_to(ROOT)}")


def main() -> None:
    BRAND.mkdir(parents=True, exist_ok=True)

    files: dict[Path, str] = {
        # Master brand assets
        BRAND / "logo-mark.svg": mark(),
        BRAND / "logo-mark-papir.svg": mark(linija=KOZA),
        BRAND / "logo-seal.svg": seal(),
        # Jednobojno — crna za svijetlu podlogu, bijela za tamnu
        BRAND / "logo-mark-mono.svg": mono(MARK_MONO),
        BRAND / "logo-mark-mono-invert.svg": mono(MARK_MONO, "#ffffff"),
        BRAND / "logo-seal-mono.svg": mono(SEAL_MONO),
        BRAND / "logo-seal-mono-invert.svg": mono(SEAL_MONO, "#ffffff"),
        # PWA / favicon — ikona je pečat bez podloge; podlogu dobiva samo tamo
        # gdje je platforma traži (maskable, iOS).
        PUBLIC / "icon.svg": seal(),
    }
    for path, markup in files.items():
        path.write_text(markup, encoding="utf-8")
        print(f"  {path.relative_to(ROOT)}")

    SRC.mkdir(parents=True, exist_ok=True)
    (SRC / "brandArt.ts").write_text(BRAND_ART_TS, encoding="utf-8")
    print(f"  {(SRC / 'brandArt.ts').relative_to(ROOT)}")

    upisi_u_flyer()

    try:
        import cairosvg  # noqa: PLC0415
    except ImportError:
        print("cairosvg nije instaliran — PNG-ovi nisu osvježeni.")
        return

    rasters = [
        # (markup, izlaz, veličina, pozadina)
        (seal(), PUBLIC / "icon-192.png", 192, None),
        (seal(), PUBLIC / "icon-512.png", 512, None),
        # Android reže ikonu u krug — maskable verzija ima zrak i punu podlogu
        (seal(background=HUMIDOR, pad=0.16), PUBLIC / "icon-512-maskable.png", 512, None),
        # iOS ne poštuje prozirnost na početnom zaslonu
        (seal(background=HUMIDOR, pad=0.10), PUBLIC / "apple-touch-icon.png", 180, None),
        (mark(), BRAND / "logo-mark-512.png", 512, DUHAN),
        (mark(linija=KOZA), BRAND / "logo-mark-papir-512.png", 512, PAPIR),
        (seal(), BRAND / "logo-seal-512.png", 512, DUHAN),
        (mono(MARK_MONO), BRAND / "logo-mark-mono-512.png", 512, "#ffffff"),
        (mono(SEAL_MONO), BRAND / "logo-seal-mono-512.png", 512, "#ffffff"),
        (mono(MARK_MONO, "#ffffff"), BRAND / "logo-mark-mono-invert-512.png", 512, "#000000"),
        (mono(SEAL_MONO, "#ffffff"), BRAND / "logo-seal-mono-invert-512.png", 512, "#000000"),
    ]
    for markup, out, size, bg in rasters:
        cairosvg.svg2png(
            bytestring=markup.encode("utf-8"),
            write_to=str(out),
            output_width=size,
            output_height=size,
            background_color=bg,
        )
        print(f"  {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
