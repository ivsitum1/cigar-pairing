"""Generira Android launcher ikone iz istog amblema kao public/icon.svg.

Android res/ nije generiran s `cap sync` — te PNG-ove se commita. Skripta
postoji da ikona ostane reproducibilna i vezana na jedan izvor geometrije
(AMBLEM ispod = 1:1 prijepis public/icon.svg u 512 koordinatama).

    cd app && python scripts/build-android-icons.py

Zahtjeva Pillow (`pip install Pillow`). Splash se ne generira kao raster —
res/drawable/splash.xml slaze boju + ic_launcher_foreground.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

RES = Path(__file__).resolve().parent.parent / "android" / "app" / "src" / "main" / "res"

# public/icon.svg, viewBox 0 0 512 512
TILE = "#201812"  # pozadina plocice (= ic_launcher_background)
ZLATO = "#c9a35c"
OXBLOOD = "#9c4433"
MASLINA = "#6f8757"
CORNER_RADIUS = 96 / 512  # rx u icon.svg, kao udio stranice

# gustoce: mdpi = 1x. Legacy ikona 48dp, adaptive foreground 108dp canvas.
DENSITIES = {
    "mdpi": 1.0,
    "hdpi": 1.5,
    "xhdpi": 2.0,
    "xxhdpi": 3.0,
    "xxxhdpi": 4.0,
}
LEGACY_DP = 48
FOREGROUND_DP = 108

# Adaptive foreground: sustav prikazuje samo sredisnjih 72dp od 108dp, a
# maskira do 66dp. Amblem se skalira na 72/108 legacy velicine da ostane
# unutar safe zone bez obzira na oblik maske launchera.
FOREGROUND_SCALE = 72 / 108

SS = 4  # supersampling faktor (Pillow ne antialiasa crtanje)


def _diamond(draw: ImageDraw.ImageDraw, cx: float, cy: float, side: float, fill: str) -> None:
    """Kvadrat stranice `side` rotiran 45° oko (cx, cy) — kao rect+rotate u SVG-u."""
    half = side * math.sqrt(2) / 2
    draw.polygon(
        [(cx, cy - half), (cx + half, cy), (cx, cy + half), (cx - half, cy)],
        fill=fill,
    )


def _draw_emblem(draw: ImageDraw.ImageDraw, size: float, offset: float = 0.0) -> None:
    """Prstenovi + tri dijamanta, skalirano iz 512 koordinata icon.svg."""
    k = size / 512
    cx = cy = offset + size / 2

    def ring(radius: float, width: float, color: str) -> None:
        r = radius * k
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=color,
            width=max(1, round(width * k)),
        )

    ring(170, 14, ZLATO)
    # unutarnji prsten je u SVG-u opacity .6 — priblizno kao mijesana boja,
    # jer crtamo direktno na neprozirnu plocicu
    ring(140, 4, "#8d7343")

    _diamond(draw, cx, cy, 60 * k, ZLATO)
    _diamond(draw, cx, offset + 144 * k, 28 * k, OXBLOOD)
    _diamond(draw, cx, offset + 368 * k, 28 * k, MASLINA)


def legacy_icon(px: int, *, round_mask: bool) -> Image.Image:
    """Puna plocica (zaobljeni kvadrat ili krug) s amblemom — pre-API 26."""
    s = px * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    if round_mask:
        draw.ellipse([0, 0, s - 1, s - 1], fill=TILE)
    else:
        draw.rounded_rectangle([0, 0, s - 1, s - 1], radius=CORNER_RADIUS * s, fill=TILE)
    _draw_emblem(draw, s)
    return img.resize((px, px), Image.LANCZOS)


def foreground_icon(px: int) -> Image.Image:
    """Amblem na prozirnoj 108dp podlozi (adaptive icon foreground)."""
    s = px * SS
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    emblem = s * FOREGROUND_SCALE
    _draw_emblem(ImageDraw.Draw(img), emblem, offset=(s - emblem) / 2)
    return img.resize((px, px), Image.LANCZOS)


def main() -> None:
    if not RES.is_dir():
        raise SystemExit(f"nema {RES} — pokreni `npx cap add android` prvo")

    for density, scale in DENSITIES.items():
        out = RES / f"mipmap-{density}"
        out.mkdir(parents=True, exist_ok=True)
        legacy_px = round(LEGACY_DP * scale)
        fg_px = round(FOREGROUND_DP * scale)

        legacy_icon(legacy_px, round_mask=False).save(out / "ic_launcher.png")
        legacy_icon(legacy_px, round_mask=True).save(out / "ic_launcher_round.png")
        foreground_icon(fg_px).save(out / "ic_launcher_foreground.png")
        print(f"{out.name}: ic_launcher {legacy_px}px, foreground {fg_px}px")


if __name__ == "__main__":
    main()
