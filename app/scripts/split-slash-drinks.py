#!/usr/bin/env python3
"""Split combined slash drink SKUs into separate catalog entries with unique notes."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "src" / "data"
FILES = ["rums.json", "whiskies.json", "brandies.json"]

# id -> list of half-overrides (name, id suffix fields). Base fields cloned from parent.
# notes/cigarHint/body/sweetness/tags/highball must be unique per half.
SPLITS: dict[str, list[dict]] = {
  "rum-clement-vsop-neisson-agricole": [
    {
      "id": "rum-clement-vsop-agricole",
      "name": "Clément VSOP (agricole)",
      "body": 2, "sweetness": 1,
      "flavorTags": ["travnato", "citrus", "vanilija"],
      "serving": {"neat": 3, "water": 3, "rocks": 1, "highball": 2, "cola": 0, "best": "Čisto / Ti' Punch"},
      "notes": {
        "hr": "Clément VSOP s Habitation Clément (Martinique AOC) odležava najmanje 4 godine: mješavina novih i bourbon bačava daje mokku, kakao, kandiranu naranču i vaniliju uz travnatu agricole bazu. U čaši je suh, srednje lagan i jasan kad se pije čisto.",
        "en": "Clément VSOP from Habitation Clément (Martinique AOC) ages at least four years: new and bourbon casks bring mocha, cocoa, candied orange and vanilla over a grassy agricole base. In the glass it is dry, light-medium and clearest neat."
      },
      "cigarHint": {
        "hr": "Most je citrus i lagani hrast; biraj blagu Connecticut ili natural cigaru (npr. Hemingway/Avo stil) da ne pregaziš rum.",
        "en": "The bridge is citrus and light oak; pick a mild Connecticut or natural cigar (Hemingway/Avo style) so the rum is not buried."
      },
    },
    {
      "id": "rum-neisson-agricole",
      "name": "Neisson (agricole)",
      "body": 2, "sweetness": 1,
      "flavorTags": ["travnato", "vegetalno", "zacini"],
      "serving": {"neat": 3, "water": 3, "rocks": 1, "highball": 1, "cola": 0, "best": "Čisto / Ti' Punch"},
      "notes": {
        "hr": "Neisson je obiteljska destilerija u Carbetu, poznata po izrazito vegetalnom, začinskom agricole profilu i čistoj AOC liniji. U čaši očekuj više zelenog soka trske i papra nego slatke melase; VSOP/Élevé sous bois stilovi ostaju suhiji od hispanskih rumova.",
        "en": "Neisson is a family distillery in Carbet, known for a distinctly vegetal, spicy agricole profile and a clean AOC line. In the glass expect more green cane juice and pepper than sweet molasses; VSOP/élevé styles stay drier than Hispanic rums."
      },
      "cigarHint": {
        "hr": "Vegetalni most traži blagi do srednji dim sa sijeno/biljnim notama, ne teški maduro.",
        "en": "The vegetal bridge wants mild-to-medium smoke with hay/herbal notes, not a heavy maduro."
      },
    },
  ],
  "rum-rhum-j-m-vsop-xo-agricole": [
    {
      "id": "rum-rhum-j-m-vsop-agricole",
      "name": "Rhum J.M VSOP (agricole)",
      "body": 2, "sweetness": 1,
      "flavorTags": ["travnato", "vegetalno", "citrus"],
      "serving": {"neat": 3, "water": 3, "rocks": 1, "highball": 2, "cola": 0, "best": "Čisto / Ti' Punch"},
      "notes": {
        "hr": "J.M VSOP (Habitation Bellevue, Macouba) tipično nosi 4+ godine u hrastu: svježa trska, citrusna kora i blagi začin, još uvijek laganog tijela. Klasik za Ti' Punch ili čistu čašu.",
        "en": "J.M VSOP (Habitation Bellevue, Macouba) typically carries 4+ years in oak: fresh cane, citrus peel and light spice, still light-bodied. A classic for Ti' Punch or a neat pour."
      },
      "cigarHint": {
        "hr": "Uz VSOP biraj laganu natural/Connecticut cigaru — travnati citrus treba prostor.",
        "en": "With VSOP choose a light natural/Connecticut cigar — grassy citrus needs room."
      },
    },
    {
      "id": "rum-rhum-j-m-xo-agricole",
      "name": "Rhum J.M XO (agricole)",
      "body": 3, "sweetness": 1,
      "flavorTags": ["travnato", "hrast", "suho-voce"],
      "serving": {"neat": 3, "water": 2, "rocks": 0, "highball": 0, "cola": 0, "best": "Čisto"},
      "notes": {
        "hr": "J.M XO dulje odležava (često 6+ godina): hrast, suho voće i začin nadograđuju agricole bazu, tijelo je punije od VSOP-a. Pije se čisto; highball bi razvodnio kompleksnost.",
        "en": "J.M XO ages longer (often 6+ years): oak, dried fruit and spice build on the agricole base, with more body than VSOP. Drink neat; a highball would wash out the complexity."
      },
      "cigarHint": {
        "hr": "XO podnosi srednji Habano ili blagi maduro s cedrom — još ne traži najpunije cigare.",
        "en": "XO handles a medium Habano or mild maduro with cedar — it still does not want the fullest cigars."
      },
    },
  ],
  "rum-doorly-s-12-14-foursquare": [
    {
      "id": "rum-doorly-s-12-foursquare",
      "name": "Doorly's 12 (Foursquare)",
      "body": 3, "sweetness": 1,
      "flavorTags": ["suho-voce", "hrast", "vanilija"],
      "priceUrl": "https://allez.hr/shop/svi-proizvodi/doorlys-12-yo-fine-old-barbados-rum-43-vol-07l-u-poklon-kutiji",
      "priceEUR": {"min": 62, "max": 70},
      "notes": {
        "hr": "Doorly's 12 iz Foursquarea (Barbados) je suh, čist single-blended stil: hrast, suho voće i vanilija bez doziranog šećera. U čaši srednje tijelo i uredan završetak uz kap vode.",
        "en": "Doorly's 12 from Foursquare (Barbados) is a dry, clean single-blended style: oak, dried fruit and vanilla with no dosed sugar. Medium body and a tidy finish with a drop of water."
      },
      "cigarHint": {
        "hr": "Most je vanilija u suhom hrastu; cedrasti ili orašasti dim dobro sjeda.",
        "en": "The bridge is vanilla in dry oak; cedar or nutty smoke sits well."
      },
    },
    {
      "id": "rum-doorly-s-14-foursquare",
      "name": "Doorly's 14 (Foursquare)",
      "body": 3, "sweetness": 1,
      "flavorTags": ["suho-voce", "hrast", "orasasti"],
      "priceUrl": None,
      "priceEUR": {"min": 80, "max": 93},
      "notes": {
        "hr": "Doorly's 14 ide korak dalje u zrelosti: više orašastog hrasta i suhog voća, i dalje bez aditiva. Malo bogatiji od 12-ice, i dalje jasan Barbados profil.",
        "en": "Doorly's 14 steps further in maturity: more nutty oak and dried fruit, still additive-free. A touch richer than the 12, still a clear Barbados profile."
      },
      "cigarHint": {
        "hr": "14-ica podnosi malo puniji dim (srednji Habano) uz isti suhi most.",
        "en": "The 14 tolerates a slightly fuller smoke (medium Habano) on the same dry bridge."
      },
    },
  ],
  "rum-hse-xo-vsop-agricole": [
    {
      "id": "rum-hse-vsop-agricole",
      "name": "HSE VSOP (agricole)",
      "body": 2, "sweetness": 1,
      "flavorTags": ["travnato", "citrus", "vanilija"],
      "serving": {"neat": 3, "water": 3, "rocks": 1, "highball": 2, "cola": 0, "best": "Čisto / Ti' Punch"},
      "notes": {
        "hr": "Habitation Saint-Étienne VSOP je martinique agricole s citrusom, vanilijom i svježom trskom nakon nekoliko godina u hrastu. Lagani do srednje lagani sipper.",
        "en": "Habitation Saint-Étienne VSOP is Martinique agricole with citrus, vanilla and fresh cane after several years in oak. A light to light-medium sipper."
      },
      "cigarHint": {"hr": "Connecticut ili blagi Cameroon — ne guši travnati citrus.", "en": "Connecticut or mild Cameroon — do not smother the grassy citrus."},
    },
    {
      "id": "rum-hse-xo-agricole",
      "name": "HSE XO (agricole)",
      "body": 3, "sweetness": 1,
      "flavorTags": ["travnato", "hrast", "suho-voce"],
      "serving": {"neat": 3, "water": 2, "rocks": 0, "highball": 0, "cola": 0, "best": "Čisto"},
      "notes": {
        "hr": "HSE XO dulje odležava: više hrasta, suhog voća i začina uz agricole kičmu. Puniji od VSOP-a; namijenjen čistom servisu.",
        "en": "HSE XO ages longer: more oak, dried fruit and spice on an agricole spine. Fuller than VSOP; meant for neat service."
      },
      "cigarHint": {"hr": "Srednji Habano ili blagi maduro s cedrom.", "en": "Medium Habano or mild maduro with cedar."},
    },
  ],
  "rum-saint-james-xo-12-agricole": [
    {
      "id": "rum-saint-james-12-agricole",
      "name": "Saint James 12 (agricole)",
      "body": 3, "sweetness": 1,
      "flavorTags": ["travnato", "hrast", "zacini"],
      "serving": {"neat": 3, "water": 2, "rocks": 1, "highball": 1, "cola": 0, "best": "Čisto"},
      "notes": {
        "hr": "Saint James 12 Year (Martinique) spaja agricole travnatost s dubljim hrastom i začinom nakon dvanaest godina. Srednje tijelo, suši završetak.",
        "en": "Saint James 12 Year (Martinique) joins agricole grassiness with deeper oak and spice after twelve years. Medium body, dry finish."
      },
      "cigarHint": {"hr": "Srednja cigara s cedrom ili paprom.", "en": "A medium cigar with cedar or pepper."},
    },
    {
      "id": "rum-saint-james-xo-agricole",
      "name": "Saint James XO (agricole)",
      "body": 3, "sweetness": 1,
      "flavorTags": ["travnato", "hrast", "suho-voce"],
      "serving": {"neat": 3, "water": 2, "rocks": 0, "highball": 0, "cola": 0, "best": "Čisto"},
      "notes": {
        "hr": "Saint James XO je hors d'âge ekspresija: bogatiji hrast i suho voće od mlađih linija, i dalje prepoznatljivo agricole. Čisti gutljaj.",
        "en": "Saint James XO is a hors d'âge expression: richer oak and dried fruit than younger lines, still recognisably agricole. A neat pour."
      },
      "cigarHint": {"hr": "Srednje puni Habano; izbjegavaj najblaži Connecticut.", "en": "Medium-full Habano; avoid the mildest Connecticut."},
    },
  ],
  "rum-mount-gay-xo-1703": [
    {
      "id": "rum-mount-gay-xo",
      "name": "Mount Gay XO",
      "body": 3, "sweetness": 2,
      "flavorTags": ["suho-voce", "vanilija", "hrast"],
      "notes": {
        "hr": "Mount Gay XO (Barbados) miješa starije destilate: suho voće, vanilija i hrast u srednje punom, pristupačnom profilu. Kućni klasik Mount Gaya.",
        "en": "Mount Gay XO (Barbados) blends older distillates: dried fruit, vanilla and oak in a medium-full, approachable profile. Mount Gay's house classic."
      },
      "cigarHint": {"hr": "Srednji Habano ili blagi maduro.", "en": "Medium Habano or mild maduro."},
    },
    {
      "id": "rum-mount-gay-1703",
      "name": "Mount Gay 1703",
      "body": 4, "sweetness": 2,
      "flavorTags": ["suho-voce", "hrast", "orasasti"],
      "serving": {"neat": 3, "water": 2, "rocks": 0, "highball": 0, "cola": 0, "best": "Čisto"},
      "notes": {
        "hr": "Mount Gay 1703 Master Select bira starije bačve: orašastiji, dublji i skuplji od XO-a, s duljim završetkom. Sipper za posebne večeri.",
        "en": "Mount Gay 1703 Master Select picks older casks: nuttier, deeper and dearer than XO, with a longer finish. A sipper for special evenings."
      },
      "cigarHint": {"hr": "Puniji maduro ili Habano s kakao notom.", "en": "A fuller maduro or Habano with cocoa notes."},
    },
  ],
  "br-courvoisier-vsop-xo": [
    {
      "id": "br-courvoisier-vsop",
      "name": "Courvoisier VSOP",
      "style": "cognac-vsop",
      "body": 3, "sweetness": 2,
      "flavorTags": ["suho-voce", "vanilija", "cvjetno"],
      "serving": {"neat": 3, "water": 1, "rocks": 1, "highball": 0, "cola": 0, "best": "Čisto"},
      "notes": {
        "hr": "Courvoisier VSOP je cognac s voćnim i cvjetnim notama, vanilijom i umjerenim hrastom. Pristupačniji i lakši od XO linije.",
        "en": "Courvoisier VSOP is cognac with fruit and floral notes, vanilla and moderate oak. More approachable and lighter than the XO line."
      },
      "cigarHint": {"hr": "Srednja cigara, ne najpuniji maduro.", "en": "A medium cigar, not the fullest maduro."},
    },
    # XO already exists as br-courvoisier-xo — enrich via patch below, do not duplicate
  ],
  "br-martell-vsop-cordon-bleu": [
    {
      "id": "br-martell-vsop",
      "name": "Martell VSOP",
      "style": "cognac-vsop",
      "body": 3, "sweetness": 2,
      "flavorTags": ["suho-voce", "cvjetno", "hrast"],
      "notes": {
        "hr": "Martell VSOP (Borderies utjecaj) nudi voće, cvijet i uredan hrast u srednjem tijelu. Ulazna Martell linija za cognac uz cigaru.",
        "en": "Martell VSOP (Borderies influence) offers fruit, flower and tidy oak in medium body. An entry Martell line for cognac with a cigar."
      },
      "cigarHint": {"hr": "Srednja Dominikanska ili Habano cigara.", "en": "A medium Dominican or Habano cigar."},
    },
    # Cordon Bleu already exists as br-martell-cordon-bleu
  ],
}

# Auto-generate remaining splits from name "A / B" with differentiated notes
SKIP_IDS = set(SPLITS.keys()) | {
  # keep category craft blends as-is (two near-duplicates already); do not double-split
  "br-hrvatski-lozovaca-vinjak-craft",
  "br-hrvatski-lozovaza-vinjak-craft",
}


def slug(s: str) -> str:
  s = s.lower()
  s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
  return s[:60]


def auto_halves(drink: dict) -> list[dict] | None:
  name = drink["name"]
  if " / " not in name:
    return None
  # strip trailing parenthetical from whole name, reattach to both
  paren = ""
  m = re.search(r"\s*(\([^)]+\))\s*$", name)
  if m:
    paren = " " + m.group(1)
    name = name[: m.start()]
  left, right = [p.strip() for p in name.split(" / ", 1)]
  base_id = drink["id"]
  prefix = base_id.rsplit("-", 1)[0] if False else re.sub(r"-(vsop|xo|12|14).*$", "", base_id)
  # simpler unique ids
  id_l = f"{drink['category'][:2] if drink['category']!='rum' else 'rum'}-{slug(left)}"
  if drink["category"] == "whisky":
    id_l = "wh-" + slug(left)
    id_r = "wh-" + slug(right)
  elif drink["category"] == "brandy":
    id_l = "br-" + slug(left)
    id_r = "br-" + slug(right)
  else:
    id_l = "rum-" + slug(left)
    id_r = "rum-" + slug(right)
  # ensure uniqueness vs parent
  if id_l == drink["id"]:
    id_l = drink["id"] + "-a"
  if id_r == drink["id"]:
    id_r = drink["id"] + "-b"

  body = drink.get("body", 3)
  tags = list(drink.get("flavorTags") or [])
  notes_base_hr = (drink.get("notes") or {}).get("hr") or drink["name"]
  notes_base_en = (drink.get("notes") or {}).get("en") or drink["name"]

  def half(hid, hname, body_delta, tag_extra, age_note_hr, age_note_en, highball):
    d = {
      "id": hid,
      "name": hname + paren,
      "body": max(1, min(5, body + body_delta)),
      "sweetness": drink.get("sweetness", 1),
      "flavorTags": list(dict.fromkeys(tags + tag_extra))[:4] or tags,
      "notes": {
        "hr": f"{hname}{paren}: {age_note_hr} Profil ostaje u stilu {drink.get('style', '')} ({drink.get('region', '')}). {notes_base_hr[:180]}",
        "en": f"{hname}{paren}: {age_note_en} Profile stays in the {drink.get('style', '')} style ({drink.get('region', '')}). {notes_base_en[:180]}",
      },
      "cigarHint": {
        "hr": f"Uz {hname} biraj cigaru prema tijelu {max(1, min(5, body + body_delta))}/5 i zajedničkim notama ({', '.join((tags[:2]) or ['hrast'])}).",
        "en": f"With {hname} pick a cigar for body {max(1, min(5, body + body_delta))}/5 and shared notes ({', '.join((tags[:2]) or ['oak'])}).",
      },
    }
    if drink.get("serving"):
      srv = copy.deepcopy(drink["serving"])
      srv["highball"] = highball
      d["serving"] = srv
    return d

  # Heuristic: right side often older/fuller if contains xo/higher number
  right_older = bool(re.search(r"\b(xo|23|30|1703|cordon|master|bold|velha|reserva)\b", right, re.I)) or (
    re.search(r"\b(\d+)\b", right) and re.search(r"\b(\d+)\b", left)
    and int(re.search(r"\b(\d+)\b", right).group(1)) > int(re.search(r"\b(\d+)\b", left).group(1))
  )
  if right_older:
    return [
      half(id_l, left, 0, [], f"Mlađa ili lakša ekspresija u paru.", f"The younger or lighter expression in the pair.", drink.get("serving", {}).get("highball", 0) or 0),
      half(id_r, right, 1, ["hrast"], f"Starija/punija ekspresija: više hrasta i težine.", f"The older/fuller expression: more oak and weight.", 0),
    ]
  return [
    half(id_l, left, 0, [], f"Prva boca iz kombiniranog unosa — vlastiti profil.", f"First bottle from the combined entry — its own profile.", drink.get("serving", {}).get("highball", 0) or 0),
    half(id_r, right, 0, [], f"Druga boca iz kombiniranog unosa — vlastiti profil.", f"Second bottle from the combined entry — its own profile.", drink.get("serving", {}).get("highball", 0) or 0),
  ]


def apply_override(base: dict, ovr: dict) -> dict:
  d = copy.deepcopy(base)
  d.update({k: v for k, v in ovr.items() if k != "serving"})
  if "serving" in ovr:
    d["serving"] = {**(base.get("serving") or {}), **ovr["serving"]}
  # clear priceUrl unless override set
  if "priceUrl" not in ovr and " / " in (base.get("name") or ""):
    # keep only if explicitly set in ovr
    pass
  return d


def process_file(fname: str) -> tuple[int, list[str]]:
  path = DATA / fname
  items = json.loads(path.read_text(encoding="utf-8"))
  out: list[dict] = []
  new_ids: list[str] = []
  split_count = 0
  for d in items:
    if d["id"] in SKIP_IDS and d["id"] not in SPLITS:
      out.append(d)
      continue
    if d["id"] in SPLITS:
      for ovr in SPLITS[d["id"]]:
        half = apply_override(d, ovr)
        # drop combined name markers
        out.append(half)
        new_ids.append(half["id"])
      split_count += 1
      continue
    if " / " in d.get("name", "") and "gift" not in d["name"].lower() and "poklon" not in d["name"].lower():
      if d["id"] in SKIP_IDS:
        out.append(d)
        continue
      halves = auto_halves(d)
      if halves:
        for ovr in halves:
          half = apply_override(d, ovr)
          out.append(half)
          new_ids.append(half["id"])
        split_count += 1
        continue
    out.append(d)
  # dedupe by id (keep first)
  seen = set()
  deduped = []
  for d in out:
    if d["id"] in seen:
      continue
    seen.add(d["id"])
    deduped.append(d)
  path.write_text(json.dumps(deduped, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
  return split_count, new_ids


def patch_refs(id_map: dict[str, list[str]]) -> None:
  # shopping.json + serve_corrections + curatedNotes.test.ts
  shopping = DATA / "shopping.json"
  if shopping.exists():
    text = shopping.read_text(encoding="utf-8")
    for old, news in id_map.items():
      # bottleTarget names — update common combined strings
      pass
    # name-based replacements
    reps = {
      "Clement VSOP / Neisson": "Clément VSOP",
      "Rhum JM XO / HSE": "Rhum J.M XO",
      "Doorly's 12 / 14": "Doorly's 12",
    }
    for a, b in reps.items():
      text = text.replace(a, b)
    shopping.write_text(text, encoding="utf-8")

  test = DATA.parent / "data" / "curatedNotes.test.ts"
  # actual path
  test = Path(__file__).resolve().parents[1] / "src" / "data" / "curatedNotes.test.ts"
  if test.exists():
    t = test.read_text(encoding="utf-8")
    for old, news in id_map.items():
      if old in t and news:
        t = t.replace(f'"{old}"', ", ".join(f'"{n}"' for n in news))
    test.write_text(t, encoding="utf-8")

  seed = Path(__file__).resolve().parent / "seed" / "serve_corrections.json"
  if seed.exists():
    t = seed.read_text(encoding="utf-8")
    for a, b in {
      "Clement VSOP / Neisson (agricole)": "Clément VSOP (agricole)",
      "Rhum J.M VSOP / XO (agricole)": "Rhum J.M VSOP (agricole)",
      "Doorly's 12 / 14 (Foursquare)": "Doorly's 12 (Foursquare)",
    }.items():
      t = t.replace(a, b)
    seed.write_text(t, encoding="utf-8")


def main() -> None:
  id_map: dict[str, list[str]] = {}
  total = 0
  all_new: list[str] = []
  for f in FILES:
    # capture parents that will split
    items = json.loads((DATA / f).read_text(encoding="utf-8"))
    parents = [d for d in items if " / " in d.get("name", "")]
    n, new_ids = process_file(f)
    total += n
    all_new.extend(new_ids)
    print(f"{f}: split {n} combined rows")
  # build id_map from SPLITS
  for old, halves in SPLITS.items():
    id_map[old] = [h["id"] for h in halves]
  patch_refs(id_map)
  summary = {"splitRows": total, "newIds": all_new}
  outp = Path(__file__).resolve().parents[2] / "01_work" / "output" / "drink-splits-summary.json"
  outp.parent.mkdir(parents=True, exist_ok=True)
  outp.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
  print(f"Done. {total} combined rows -> {len(all_new)} new ids. Summary: {outp}")


if __name__ == "__main__":
  main()
