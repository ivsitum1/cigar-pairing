#!/usr/bin/env python3
"""Replace catalogue-placeholder brand blurbs with one accurate bilingual sentence each."""
from __future__ import annotations

import json
from pathlib import Path

BLURBS = {
  "Accomplice": {
    "hr": "Accomplice — dominikanska linija (tabacalera partnerstva) iz kataloga premium trgovina; fokus na pristupačne handmade vitole.",
    "en": "Accomplice — a Dominican line (tabacalera partnerships) from premium shop catalogues; focused on approachable handmade vitolas.",
  },
  "Buffalo": {
    "hr": "Buffalo — dominikanska marka iz maloprodajnih kataloga; jednostavnije linije za svakodnevno pušenje.",
    "en": "Buffalo — a Dominican brand from retail catalogues; simpler lines for everyday smoking.",
  },
  "Don Kiki": {
    "hr": "Don Kiki — nikaragvanska marka povezana s A.J. Fernandez proizvodnjom; pune, začinske mješavine.",
    "en": "Don Kiki — a Nicaraguan brand linked to A.J. Fernandez production; full, spicy blends.",
  },
  "El Vinyet": {
    "hr": "El Vinyet — dominikanska marka iz europskih/HR kataloga; klasične vitole srednje snage.",
    "en": "El Vinyet — a Dominican brand from EU/HR catalogues; classic medium-strength vitolas.",
  },
  "Guantanamera": {
    "hr": "Guantanamera — kubanska Habanos marka (maquina i handmade linije) namijenjena pristupačnijem ulazu u cubanske cigare.",
    "en": "Guantanamera — a Cuban Habanos brand (machine-made and handmade lines) aimed at a more accessible entry to Cuban cigars.",
  },
  "K. Fire": {
    "hr": "K. Fire — nikaragvanska marka iz boutique/katalog ponude; kraće linije s naglaskom na snagu i začin.",
    "en": "K. Fire — a Nicaraguan brand from boutique/catalogue lists; shorter lines emphasising strength and spice.",
  },
  "La Instructora": {
    "hr": "La Instructora — dominikanska marka iz specialty kataloga; manje poznata linija uz klasične formate.",
    "en": "La Instructora — a Dominican brand from specialty catalogues; a lesser-known line in classic formats.",
  },
  "Leaf by Oscar": {
    "hr": "Leaf by Oscar — honduraška marka Oscara Vallade (Leaf/Oscar Valladares); širok raspon wrappera i svakodnevnih vitola.",
    "en": "Leaf by Oscar — Oscar Valladares’ Honduran brand (Leaf/Oscar Valladares); a wide range of wrappers and everyday vitolas.",
  },
  "Maestranza": {
    "hr": "Maestranza — honduraška marka iz maloprodajnih kataloga; fokus na punije, zemljane profile.",
    "en": "Maestranza — a Honduran brand from retail catalogues; focused on fuller, earthy profiles.",
  },
  "Pulita": {
    "hr": "Pulita — dominikanska marka iz HR/EU kataloga; jednostavne handmade linije za svakodnevni dim.",
    "en": "Pulita — a Dominican brand from HR/EU catalogues; simple handmade lines for everyday smoke.",
  },
  "Puro": {
    "hr": "Puro — dominikanska katalog-marka; naziv označava čistu duhansku mješavinu bez aromatičnih dodataka u tipičnoj ponudi.",
    "en": "Puro — a Dominican catalogue brand; the name signals a straight tobacco blend without flavoured additives in typical listings.",
  },
  "Rafael Gonzalez": {
    "hr": "Rafael González — povijesna kubanska Habanos marka (danas uglavnom strojne i polu-handmade linije) s blagim do srednjim profilom.",
    "en": "Rafael González — a historic Cuban Habanos brand (today mostly machine and semi-handmade lines) with a mild-to-medium profile.",
  },
  "Tailgate": {
    "hr": "Tailgate — nikaragvanska marka iz američkih/EU kataloga; ležernije linije srednje snage.",
    "en": "Tailgate — a Nicaraguan brand from US/EU catalogues; casual medium-strength lines.",
  },
  "The Aviator": {
    "hr": "The Aviator — dominikanska marka iz specialty kataloga; tematske linije u klasičnim formatima.",
    "en": "The Aviator — a Dominican brand from specialty catalogues; themed lines in classic formats.",
  },
  "The Oscar": {
    "hr": "The Oscar — linija Oscara Vallade (Honduras), povezana s Leaf by Oscar portfeljem; boutique handmade vitole.",
    "en": "The Oscar — an Oscar Valladares line (Honduras), related to the Leaf by Oscar portfolio; boutique handmade vitolas.",
  },
  "JFR": {
    "hr": "JFR — Aganorsa Leaf (Nikaragva); Connecticut i druge linije iz iste kuće polja i tvornice.",
    "en": "JFR — Aganorsa Leaf (Nicaragua); Connecticut and other lines from the same farm-and-factory house.",
  },
}

path = Path("app/src/data/brands.json")
brands = json.loads(path.read_text(encoding="utf-8"))
n = 0
for key, blurb in BLURBS.items():
    if key not in brands:
        print("MISSING", key)
        continue
    brands[key]["blurb"] = blurb
    n += 1
path.write_text(json.dumps(brands, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"updated={n}")
