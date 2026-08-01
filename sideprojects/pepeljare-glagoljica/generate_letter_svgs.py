# -*- coding: utf-8 -*-
"""Generate top-view ashtray SVGs for uglata Glagolitic letter candidates."""
from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parent / "slova"
OUT.mkdir(parents=True, exist_ok=True)

BG = "#1a1612"
GOLD = "#c9a66b"
FLOOR = "#2a241c"
MUTED = "#8a8074"
LABEL = "#c4b8a4"
DIM = "#6e6558"

# Suitability for ashtray-as-letter body (not engraving)
# A = strong closed contour + rests, B = workable, C = stretch / sculptural
LETTERS: list[dict] = [
    {
        "id": "01-az",
        "name": "Az",
        "latin": "a",
        "tier": "A",
        "note": "Krug + križ — default pepeljara",
        "body": """
  <circle cx="200" cy="200" r="118" fill="none" stroke="{gold}" stroke-width="14"/>
  <circle cx="200" cy="200" r="104" fill="{floor}"/>
  <rect x="188" y="92" width="24" height="216" rx="2" fill="{gold}"/>
  <rect x="92" y="188" width="216" height="24" rx="2" fill="{gold}"/>
  <ellipse cx="200" cy="100" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="200" cy="300" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="100" cy="200" rx="7" ry="11" fill="{bg}"/>
  <ellipse cx="300" cy="200" rx="7" ry="11" fill="{bg}"/>
""",
    },
    {
        "id": "02-trokutasti-az",
        "name": "Trokutasto az",
        "latin": "a (Baška)",
        "tier": "A",
        "note": "Trokut — epigrafski / kamen",
        "body": """
  <polygon points="200,78 328,320 72,320" fill="{floor}" stroke="{gold}" stroke-width="14" stroke-linejoin="round"/>
  <rect x="188" y="155" width="24" height="100" rx="2" fill="{gold}"/>
  <rect x="118" y="230" width="164" height="22" rx="2" fill="{gold}"/>
  <ellipse cx="200" cy="92" rx="12" ry="7" fill="{bg}"/>
  <ellipse cx="108" cy="278" rx="8" ry="11" fill="{bg}" transform="rotate(-55 108 278)"/>
  <ellipse cx="292" cy="278" rx="8" ry="11" fill="{bg}" transform="rotate(55 292 278)"/>
""",
    },
    {
        "id": "03-slovo",
        "name": "Slovo",
        "latin": "s",
        "tier": "A",
        "note": "Krug + križ s okom — razgovor",
        "body": """
  <circle cx="200" cy="200" r="118" fill="none" stroke="{gold}" stroke-width="14"/>
  <circle cx="200" cy="200" r="104" fill="{floor}"/>
  <rect x="190" y="95" width="20" height="210" rx="2" fill="{gold}"/>
  <rect x="100" y="190" width="200" height="20" rx="2" fill="{gold}"/>
  <rect x="185" y="185" width="30" height="30" fill="{floor}" stroke="{gold}" stroke-width="3"/>
  <ellipse cx="200" cy="104" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="200" cy="296" rx="11" ry="7" fill="{bg}"/>
""",
    },
    {
        "id": "04-on",
        "name": "On",
        "latin": "o",
        "tier": "A",
        "note": "Čista zdjelica — slabo 'slovo', jaka funkcija",
        "body": """
  <circle cx="200" cy="200" r="118" fill="none" stroke="{gold}" stroke-width="16"/>
  <circle cx="200" cy="200" r="100" fill="{floor}"/>
  <!-- two cigar rests as short inner chords -->
  <rect x="120" y="118" width="160" height="16" rx="2" fill="{gold}" opacity="0.95"/>
  <rect x="120" y="266" width="160" height="16" rx="2" fill="{gold}" opacity="0.95"/>
  <ellipse cx="200" cy="126" rx="11" ry="6" fill="{bg}"/>
  <ellipse cx="200" cy="274" rx="11" ry="6" fill="{bg}"/>
""",
    },
    {
        "id": "05-ot",
        "name": "Ot (omega)",
        "latin": "ot / o",
        "tier": "A",
        "note": "Dvostruki krug — prstenasta pepeljara",
        "body": """
  <circle cx="200" cy="200" r="118" fill="none" stroke="{gold}" stroke-width="14"/>
  <circle cx="200" cy="200" r="104" fill="{floor}"/>
  <circle cx="200" cy="200" r="52" fill="none" stroke="{gold}" stroke-width="12"/>
  <circle cx="200" cy="200" r="38" fill="{bg}"/>
  <ellipse cx="200" cy="100" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="200" cy="300" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="100" cy="200" rx="7" ry="11" fill="{bg}"/>
  <ellipse cx="300" cy="200" rx="7" ry="11" fill="{bg}"/>
""",
    },
    {
        "id": "06-frt",
        "name": "Frt (fert)",
        "latin": "f",
        "tier": "A",
        "note": "Krug + okomica — phi-oblika, 2–4 ureza",
        "body": """
  <circle cx="200" cy="200" r="100" fill="none" stroke="{gold}" stroke-width="14"/>
  <circle cx="200" cy="200" r="86" fill="{floor}"/>
  <rect x="188" y="70" width="24" height="260" rx="2" fill="{gold}"/>
  <ellipse cx="200" cy="82" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="200" cy="318" rx="11" ry="7" fill="{bg}"/>
""",
    },
    {
        "id": "07-dobro",
        "name": "Dobro",
        "latin": "d",
        "tier": "B",
        "note": "Trokut / delta — slično B, drugačiji ductus",
        "body": """
  <polygon points="200,85 325,310 75,310" fill="{floor}" stroke="{gold}" stroke-width="14" stroke-linejoin="round"/>
  <!-- inner triangle eye -->
  <polygon points="200,155 260,270 140,270" fill="{bg}" stroke="{gold}" stroke-width="8" stroke-linejoin="round"/>
  <ellipse cx="200" cy="98" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="110" cy="275" rx="8" ry="11" fill="{bg}" transform="rotate(-50 110 275)"/>
  <ellipse cx="290" cy="275" rx="8" ry="11" fill="{bg}" transform="rotate(50 290 275)"/>
""",
    },
    {
        "id": "08-pokoj",
        "name": "Pokoj",
        "latin": "p",
        "tier": "B",
        "note": "Zatvoreni 'P' volumen — mir / počinak",
        "body": """
  <!-- stem -->
  <rect x="95" y="80" width="28" height="240" rx="3" fill="{gold}"/>
  <!-- bowl loop as closed D -->
  <path d="M123 100 H210 A90 90 0 1 1 210 300 H123 Z" fill="{floor}" stroke="{gold}" stroke-width="14"/>
  <ellipse cx="109" cy="110" rx="8" ry="11" fill="{bg}"/>
  <ellipse cx="109" cy="290" rx="8" ry="11" fill="{bg}"/>
  <ellipse cx="280" cy="200" rx="7" ry="11" fill="{bg}"/>
""",
    },
    {
        "id": "09-sa",
        "name": "Ša",
        "latin": "š",
        "tier": "B",
        "note": "Tri zuba u okviru — 3 ureza, lounge tišina",
        "body": """
  <rect x="78" y="90" width="244" height="220" rx="8" fill="{floor}" stroke="{gold}" stroke-width="14"/>
  <rect x="110" y="110" width="22" height="180" rx="2" fill="{gold}"/>
  <rect x="189" y="110" width="22" height="180" rx="2" fill="{gold}"/>
  <rect x="268" y="110" width="22" height="180" rx="2" fill="{gold}"/>
  <ellipse cx="121" cy="118" rx="10" ry="6" fill="{bg}"/>
  <ellipse cx="200" cy="118" rx="10" ry="6" fill="{bg}"/>
  <ellipse cx="279" cy="118" rx="10" ry="6" fill="{bg}"/>
""",
    },
    {
        "id": "10-i",
        "name": "I (ižei)",
        "latin": "i",
        "tier": "B",
        "note": "Kružni / riblji obris — 2 ureza",
        "body": """
  <ellipse cx="200" cy="200" r="0" />
  <path d="M95 200
           C95 110 140 85 200 85
           C260 85 305 110 305 200
           C305 290 260 315 200 315
           C140 315 95 290 95 200 Z"
        fill="{floor}" stroke="{gold}" stroke-width="14"/>
  <rect x="188" y="120" width="24" height="160" rx="2" fill="{gold}"/>
  <ellipse cx="200" cy="100" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="200" cy="300" rx="11" ry="7" fill="{bg}"/>
""",
    },
    {
        "id": "11-tvrdo",
        "name": "Tvrdo",
        "latin": "t",
        "tier": "B",
        "note": "Okvir + prečka — čvrst geometrijski stol",
        "body": """
  <rect x="85" y="95" width="230" height="210" rx="6" fill="{floor}" stroke="{gold}" stroke-width="14"/>
  <rect x="100" y="188" width="200" height="24" rx="2" fill="{gold}"/>
  <rect x="188" y="110" width="24" height="180" rx="2" fill="{gold}"/>
  <ellipse cx="200" cy="118" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="112" cy="200" rx="7" ry="11" fill="{bg}"/>
  <ellipse cx="288" cy="200" rx="7" ry="11" fill="{bg}"/>
""",
    },
    {
        "id": "12-zemlja",
        "name": "Zemlja",
        "latin": "z",
        "tier": "B",
        "note": "Zatvoreni krug s unutarnjim trokutom — tlo / pepeo",
        "body": """
  <circle cx="200" cy="200" r="118" fill="none" stroke="{gold}" stroke-width="14"/>
  <circle cx="200" cy="200" r="104" fill="{floor}"/>
  <polygon points="200,120 275,260 125,260" fill="{bg}" stroke="{gold}" stroke-width="10" stroke-linejoin="round"/>
  <ellipse cx="200" cy="100" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="100" cy="200" rx="7" ry="11" fill="{bg}"/>
  <ellipse cx="300" cy="200" rx="7" ry="11" fill="{bg}"/>
""",
    },
    {
        "id": "13-jest",
        "name": "Jest",
        "latin": "e",
        "tier": "C",
        "note": "Složeni obris — teže čitljiv kao pepeljara",
        "body": """
  <path d="M110 100 H250
           A70 70 0 0 1 250 300
           H110 V260 H230
           A30 30 0 0 0 230 140
           H110 Z"
        fill="{floor}" stroke="{gold}" stroke-width="12" stroke-linejoin="round"/>
  <ellipse cx="120" cy="120" rx="8" ry="11" fill="{bg}"/>
  <ellipse cx="120" cy="280" rx="8" ry="11" fill="{bg}"/>
  <ellipse cx="290" cy="200" rx="7" ry="11" fill="{bg}"/>
""",
    },
    {
        "id": "14-ziveti",
        "name": "Živjeti",
        "latin": "ž",
        "tier": "C",
        "note": "Simetrična 'riblja' silueta — skulpturalno",
        "body": """
  <path d="M200 85
           L255 140 L300 200 L255 260 L200 315
           L145 260 L100 200 L145 140 Z"
        fill="{floor}" stroke="{gold}" stroke-width="12" stroke-linejoin="round"/>
  <rect x="188" y="150" width="24" height="100" rx="2" fill="{gold}"/>
  <ellipse cx="200" cy="100" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="200" cy="300" rx="11" ry="7" fill="{bg}"/>
""",
    },
    {
        "id": "15-derv",
        "name": "Đerv",
        "latin": "ć/đ",
        "tier": "C",
        "note": "Drvo — bolje za kutiju; pepeljara rastezljiva",
        "body": """
  <rect x="175" y="75" width="50" height="250" rx="4" fill="{gold}"/>
  <ellipse cx="200" cy="130" rx="95" ry="45" fill="{floor}" stroke="{gold}" stroke-width="10"/>
  <ellipse cx="200" cy="210" rx="80" ry="38" fill="{floor}" stroke="{gold}" stroke-width="10"/>
  <ellipse cx="200" cy="280" rx="60" ry="30" fill="{floor}" stroke="{gold}" stroke-width="10"/>
  <ellipse cx="200" cy="95" rx="11" ry="7" fill="{bg}"/>
""",
    },
    {
        "id": "16-kako",
        "name": "Kako",
        "latin": "k",
        "tier": "C",
        "note": "Kružni okvir + kuka — moguće, manje ikonično",
        "body": """
  <circle cx="200" cy="200" r="118" fill="none" stroke="{gold}" stroke-width="14"/>
  <circle cx="200" cy="200" r="104" fill="{floor}"/>
  <path d="M150 120 L200 200 L150 280" fill="none" stroke="{gold}" stroke-width="16" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="188" y="110" width="22" height="180" rx="2" fill="{gold}"/>
  <ellipse cx="200" cy="100" rx="11" ry="7" fill="{bg}"/>
  <ellipse cx="200" cy="300" rx="11" ry="7" fill="{bg}"/>
""",
    },
]


def card(letter: dict) -> str:
    body = letter["body"].format(gold=GOLD, floor=FLOOR, bg=BG)
    tier = letter["tier"]
    tier_color = {"A": "#7d9b6a", "B": "#c9a66b", "C": "#a06a5a"}[tier]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 460" role="img">
  <rect width="400" height="460" fill="{BG}"/>
  <text x="200" y="34" fill="{LABEL}" font-family="Georgia, serif" font-size="18" text-anchor="middle">{letter["name"]}</text>
  <text x="200" y="54" fill="{MUTED}" font-family="Georgia, serif" font-size="12" text-anchor="middle">uglata · {letter["latin"]} · razred {tier}</text>
  <g transform="translate(0,20)">{body}
  </g>
  <rect x="28" y="390" width="22" height="14" rx="2" fill="{tier_color}"/>
  <text x="58" y="402" fill="{LABEL}" font-family="Georgia, serif" font-size="12">{letter["note"]}</text>
  <text x="200" y="440" fill="{DIM}" font-family="Georgia, serif" font-size="11" text-anchor="middle">tlocrt pepeljare · ne paleografski faksimil</text>
</svg>
"""


def gallery(letters: list[dict]) -> str:
    cols = 4
    cell_w, cell_h = 220, 250
    pad = 24
    rows = (len(letters) + cols - 1) // cols
    width = pad * 2 + cols * cell_w
    height = 90 + rows * cell_h + 40
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        f'<text x="{width/2}" y="36" fill="{LABEL}" font-family="Georgia, serif" font-size="22" text-anchor="middle">Pepeljara = uglato slovo · svi kandidati</text>',
        f'<text x="{width/2}" y="58" fill="{MUTED}" font-family="Georgia, serif" font-size="13" text-anchor="middle">A jak · B upotrebljiv · C rastezljiv / skulpturalan</text>',
    ]
    for i, letter in enumerate(letters):
        r, c = divmod(i, cols)
        x = pad + c * cell_w
        y = 80 + r * cell_h
        body = letter["body"].format(gold=GOLD, floor=FLOOR, bg=BG)
        # scale letter art from 400x340-ish into cell
        scale = 0.42
        parts.append(f'<g transform="translate({x},{y})">')
        parts.append(
            f'<rect width="{cell_w - 12}" height="{cell_h - 16}" rx="8" fill="#221c16" stroke="#3a3228"/>'
        )
        tier_color = {"A": "#7d9b6a", "B": "#c9a66b", "C": "#a06a5a"}[letter["tier"]]
        parts.append(
            f'<text x="12" y="22" fill="{LABEL}" font-family="Georgia, serif" font-size="13">{letter["name"]}</text>'
        )
        parts.append(
            f'<circle cx="{cell_w - 28}" cy="16" r="7" fill="{tier_color}"/>'
        )
        parts.append(
            f'<g transform="translate(8,28) scale({scale})">{body}</g>'
        )
        parts.append("</g>")
    parts.append(
        f'<text x="{width/2}" y="{height - 16}" fill="{DIM}" font-family="Georgia, serif" font-size="11" text-anchor="middle">sideprojects/pepeljare-glagoljica/slova/</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def main() -> None:
    for letter in LETTERS:
        path = OUT / f"{letter['id']}.svg"
        path.write_text(card(letter), encoding="utf-8")
        print("wrote", path.name)
    gal = Path(__file__).resolve().parent / "GALERIJA-sva-slova.svg"
    gal.write_text(gallery(LETTERS), encoding="utf-8")
    print("wrote", gal.name)

    index = OUT / "INDEX.md"
    lines = [
        "# Slova za pepeljaru (tlocrti)",
        "",
        "Razredi: **A** jak · **B** upotrebljiv · **C** rastezljiv.",
        "",
        "| Razred | Datoteka | Slovo | Napomena |",
        "|--------|----------|-------|----------|",
    ]
    for letter in LETTERS:
        lines.append(
            f"| {letter['tier']} | [{letter['id']}.svg](./{letter['id']}.svg) | {letter['name']} | {letter['note']} |"
        )
    lines.append("")
    lines.append("Pregled: [../GALERIJA-sva-slova.svg](../GALERIJA-sva-slova.svg)")
    index.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("wrote INDEX.md")


if __name__ == "__main__":
    main()
