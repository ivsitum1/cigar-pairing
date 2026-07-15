#!/usr/bin/env python3
"""Pretvara additiveDetail i cigarHint u dvojezicna polja {hr, en}.

Jednokratna migracija + tablice prijevoda. Neutralizira i preostale
"Nije za cigaru" naznake (uredjivacka politika: deklaracija, ne osuda).
"""
import json, sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "data"
SEED = Path(__file__).resolve().parent / "seed" / "whiskies_classics_seed.json"

# neutralizacija prije prijevoda
HINT_FIX = {
    "Nije za cigaru": "Uz koktel ili highball",
    "Nije za cigaru (aromatizirano)": "Uz koktel ili desert",
    "Nije za cigaru (mixing)": "Uz koktel ili highball",
}

DET = {
    "Aroma narance, doslazen": "Orange flavouring, sweetened",
    "Aromatiziran (Inlander stil), 80%": "Flavoured (Inländer style), 80%",
    "Aromatizirana edicija (ananas) uz rum-cask dozrijevanje": "Flavoured release (pineapple) with rum-cask maturation",
    "Bez aditiva": "No additives",
    "Bez aditiva (AOC)": "No additives (AOC)",
    'Bez aditiva (US "straight" pravila ne dopustaju dodatke)': 'No additives (US "straight" rules allow none)',
    "Bez dod. secera": "No added sugar",
    "Bez podataka o dodacima (nije mjereno)": "No additive data (not measured)",
    "Blaga slatkoca": "Light sweetness",
    "Blagi dodatak": "Light addition",
    "Blagi dodatak (sherry)": "Light addition (sherry)",
    "Blagi dodatak (solera)": "Light addition (solera)",
    "Blagi dodatak (spirit drink)": "Light addition (spirit drink)",
    "Blago slazen": "Lightly sweetened",
    "Blago slazen (solera)": "Lightly sweetened (solera)",
    "Cist": "Clean",
    "Cist (bottler)": "Clean (bottler)",
    "Cist (dekl. 0)": "Clean (declared 0)",
    "Cist (mlad)": "Clean (young)",
    "Cist-ish": "Essentially clean",
    "Cist-ish bijeli": "Essentially clean white",
    "Cist/vrlo nizak": "Clean / very low",
    "Dodana aroma narance i secer": "Added orange flavouring and sugar",
    "Dodane arome (klincic, cimet, vanilija) i karamel boja; secer ~26 g/L": "Added flavourings (clove, cinnamon, vanilla) and caramel colour; sugar ~26 g/L",
    "Dodane arome (vanilija, cimet) i secer": "Added flavourings (vanilla, cinnamon) and sugar",
    "Dodane arome (vanilija, zacini)": "Added flavourings (vanilla, spices)",
    "Dodane arome (vanilija, zacini) i secer": "Added flavourings (vanilla, spices) and sugar",
    "Dodane arome i secer": "Added flavourings and sugar",
    "Dodane arome i secer (38%, spirit drink)": "Added flavourings and sugar (38%, spirit drink)",
    "Dodane arome: vanilija, kokos, zacini": "Added flavourings: vanilla, coconut, spices",
    "Dodane vocne arome i secer": "Added fruit flavourings and sugar",
    "Dodani secer (Alko lab; novije boce ispod 20 g/L)": "Added sugar (Alko lab; recent bottlings under 20 g/L)",
    "Dodani secer (hidrometrija)": "Added sugar (hydrometer)",
    "Dodani secer i arome": "Added sugar and flavourings",
    "Dodani secer i suho grozdje (elixir kategorija)": "Added sugar and raisins (elixir category)",
    "Dodani secer ~15-20 g/L": "Added sugar ~15–20 g/L",
    "Dodani secer/arome (kategorija elixir)": "Added sugar/flavourings (elixir category)",
    "Dodani: vanilija, cimet, naranca, klincic, kardamom": "Added: vanilla, cinnamon, orange, clove, cardamom",
    "Dodatak secera": "Added sugar",
    "Doslazen": "Sweetened",
    "Doslazen (solera stil)": "Sweetened (solera style)",
    "Doslazen (~12-20 g/L)": "Sweetened (~12–20 g/L)",
    "Doslazen/aromatiziran (intenzivnije od Don Pape 7)": "Sweetened/flavoured (more intense than Don Papa 7)",
    "Doslazen/aromatiziran (procjena)": "Sweetened/flavoured (estimate)",
    "E150a boja / chill-filtracija nije deklarirana (EU ne zahtijeva)": "E150a colouring / chill filtration undeclared (the EU does not require it)",
    "EU dopusta karamel i dosladjivanje do 20 g/L za grappu; nije deklarirano": "The EU permits caramel and sweetening up to 20 g/L for grappa; undeclared",
    "Filtriran; bez podataka o dodacima": "Filtered; no additive data",
    "Fortificirano vinskim destilatom (77%); slatkoca iz zaustavljene fermentacije": "Fortified with grape spirit (77%); sweetness from arrested fermentation",
    "Fortificirano vinskim destilatom; potpuno suho": "Fortified with grape spirit; fully dry",
    "Fortificirano vinskim destilatom; slatkoca iz zaustavljene fermentacije": "Fortified with grape spirit; sweetness from arrested fermentation",
    "Fortificirano vinskim destilatom; slatkoca ovisi o sorti (Bual/Malmsey)": "Fortified with grape spirit; sweetness depends on the variety (Bual/Malmsey)",
    "Fortificirano vinskim destilatom; suho": "Fortified with grape spirit; dry",
    "Fortificirano; slatkoca iz prosusenog grozdja (PX)": "Fortified; sweetness from sun-dried grapes (PX)",
    "Hidrometrija: ~19 g/L dodataka (znatno manje od Originala)": "Hydrometer: ~19 g/L additives (far less than the Original)",
    "Kokosov liker 21% (secer i aroma kokosa)": "Coconut liqueur, 21% (sugar and coconut flavouring)",
    "Krem liker 15% (mlijecna baza, secer, arome)": "Cream liqueur, 15% (dairy base, sugar, flavourings)",
    "Krem liker: vrhnje, secer i arome na bazi Edradour single malta (17%)": "Cream liqueur: cream, sugar and flavourings on an Edradour single malt base (17%)",
    "Lab: ~29 g/L secera + 2,4 g/L glicerola + vanilin ~360 mg/L": "Lab: ~29 g/L sugar + 2.4 g/L glycerol + vanillin ~360 mg/L",
    "Liker: cognac baza + destilat gorke narance + secer (deklarirano)": "Liqueur: cognac base + bitter-orange distillate + sugar (declared)",
    "Liker: dodana aroma jabuke i secer (35%)": "Liqueur: added apple flavouring and sugar (35%)",
    "Liker: dodani med/aroma i secer (35%)": "Liqueur: added honey/flavouring and sugar (35%)",
    "Mladi/mixing": "Young / for mixing",
    "Nizak (reformuliran)": "Low (reformulated)",
    "Nizak (sherry)": "Low (sherry)",
    "Pravi single malt — dozrijevan u ginger beer bacvama, nista dodano": "A true single malt — matured in ginger beer casks, nothing added",
    "Prirodna boja, bez dosladjivanja (deklaracija destilerije)": "Natural colour, no sweetening (distillery declaration)",
    "Prirodna slatkoca (kasna berba)": "Natural sweetness (late harvest)",
    "Prirodna slatkoca iz botritiziranog grozdja": "Natural sweetness from botrytised grapes",
    "Prirodna slatkoca iz prosusenog grozdja (passito), bez fortifikacije": "Natural sweetness from dried grapes (passito), no fortification",
    "Relativno cisci": "Relatively cleaner",
    "Sastav nepoznat (nije mjereno)": "Composition unknown (not measured)",
    "Standardno vinarstvo (sulfiti)": "Standard winemaking (sulphites)",
    "Standardno vinarstvo (sulfiti); appassimento (prosuseno grozdje)": "Standard winemaking (sulphites); appassimento (dried grapes)",
    "Standardno vinarstvo (sulfiti); barrique dozrijevanje": "Standard winemaking (sulphites); barrique maturation",
    "Standardno vinarstvo (sulfiti); brut dozaza": "Standard winemaking (sulphites); brut dosage",
    "Standardno vinarstvo (sulfiti); brut nature (bez dozaze)": "Standard winemaking (sulphites); brut nature (no dosage)",
    "Standardno vinarstvo (sulfiti); brut/extra dry dozaza": "Standard winemaking (sulphites); brut/extra dry dosage",
    "Standardno vinarstvo (sulfiti); dozaza secera u brut razini (<12 g/L)": "Standard winemaking (sulphites); sugar dosage at brut level (<12 g/L)",
    "Standardno vinarstvo (sulfiti); klasicna metoda": "Standard winemaking (sulphites); classic method",
    "Standardno vinarstvo (sulfiti); klasicna metoda, brut dozaza": "Standard winemaking (sulphites); classic method, brut dosage",
    "Standardno vinarstvo (sulfiti); prirodni zaostali secer": "Standard winemaking (sulphites); natural residual sugar",
    "Standardno vinarstvo (sulfiti); zaostali secer daje mekocu": "Standard winemaking (sulphites); residual sugar lends softness",
    "Systembolaget: ~51 g/L secera; hidrometrija ~40 g/L; arome vanilije/banane": "Systembolaget: ~51 g/L sugar; hydrometer ~40 g/L; vanilla/banana flavourings",
    "Umjeren dodatak": "Moderate addition",
    "Umjereno slazen": "Moderately sweetened",
    "Vrlo nisko/0": "Very low / none",
    "~Bez dodatka": "~No additions",
}

# Excel-ostaci -> smisleni tekst (hr, en)
DET_NORMALIZE = {
    "clean / unknown": ("Bez poznatih dodataka", "No known additives"),
    "clean / vs": ("Bez poznatih dodataka", "No known additives"),
    "clean / vsop": ("Bez poznatih dodataka", "No known additives"),
    "clean / xo": ("Bez poznatih dodataka", "No known additives"),
    "natural / unknown": ("Prirodna boja; ostalo nepoznato", "Natural colour; otherwise unknown"),
    "e150 / unknown": ("E150a karamel boja moguca", "E150a caramel colouring possible"),
    "sweetened / unknown": ("Doslazen (unutar dopustene obskuracije)", "Sweetened (within permitted obscuration)"),
    "sweetened / vsop": ("Doslazen (unutar dopustene obskuracije)", "Sweetened (within permitted obscuration)"),
    "sweetened / xo": ("Doslazen (unutar dopustene obskuracije)", "Sweetened (within permitted obscuration)"),
    "unknown / unknown": ("Nije deklarirano", "Not declared"),
    "unknown / vsop": ("Nije deklarirano", "Not declared"),
    "unknown / xo": ("Nije deklarirano", "Not declared"),
}

HINT = {
    "Blaga Connecticut cigara": "A mild Connecticut cigar",
    "Blaga cigara": "A mild cigar",
    "Blaga-srednja Connecticut cigara": "A mild-to-medium Connecticut cigar",
    "Blaga-srednja cigara": "A mild-to-medium cigar",
    "Connecticut do Habano blage — juniper nosi blažu cigaru": "Connecticut to mild Habano — juniper suits a milder cigar",
    "Connecticut do Habano blage-srednje": "Connecticut to mild-medium Habano",
    "Connecticut do Habano mediteranskog profila": "Connecticut to Habano with a Mediterranean profile",
    "Connecticut do Habano srednje snage": "Connecticut to medium-strength Habano",
    "Connecticut do srednje Habano — blaži konjak": "Connecticut to medium Habano — a gentler cognac",
    "Connecticut srednje snage": "A medium-strength Connecticut",
    "Connecticut — med i začini": "Connecticut — honey and spice",
    "Connecticut/claro — cvjetni profil": "Connecticut/claro — a floral profile",
    "Connecticut/claro — elegantno": "Connecticut/claro — elegant",
    "Connecticut/claro — jabuka + blaža cigara": "Connecticut/claro — apple with a milder cigar",
    "Habano srednje snage": "A medium-strength Habano",
    "Habano srednje-jake": "A medium-to-strong Habano",
    "Habano/maduro — rustikalniji profil": "Habano/maduro — a more rustic profile",
    "Habano/oscuro — XO nosi jaču cigaru": "Habano/oscuro — an XO carries a stronger cigar",
    "Jaca Habano ili maduro": "A stronger Habano or maduro",
    "Jaka Habano/corojo — dim nosi dim": "A strong Habano/corojo — smoke carries smoke",
    "Jaka, robusna; ili koktel": "Strong and robust; or a cocktail",
    "Jača, full-bodied, maduro/oscuro": "Stronger, full-bodied, maduro/oscuro",
    "Laganija, Connecticut shade": "Lighter, Connecticut shade",
    "Laganija-srednja, Connecticut - vanilija/duhan": "Light-to-medium, Connecticut — vanilla/tobacco",
    "Laganija; kuriozitet": "Lighter; a curiosity",
    "Maduro srednje snage": "A medium-strength maduro",
    "Maduro/broadleaf — karamela i vanilija": "Maduro/broadleaf — caramel and vanilla",
    "Maduro/oscuro — orah i karamela": "Maduro/oscuro — walnut and caramel",
    "Maduro/oscuro — sherry + kakao": "Maduro/oscuro — sherry and cocoa",
    "Najpunije cigare — maduro/oscuro": "The fullest cigars — maduro/oscuro",
    "Najpunije cigare — nosi i oscuro": "The fullest cigars — carries even an oscuro",
    "Najpunije maduro/oscuro cigare": "The fullest maduro/oscuro cigars",
    "Uz koktel ili highball": "With a cocktail or highball",
    "Uz koktel ili desert": "With a cocktail or dessert",
    "Puna Habano cigara": "A full Habano cigar",
    "Puna Habano/maduro cigara": "A full Habano/maduro cigar",
    "Puna cigara, cedar note": "A full cigar with cedar notes",
    "Puna maduro cigara": "A full maduro cigar",
    "Puna maduro cigara za kontrast slatkoci": "A full maduro cigar to contrast the sweetness",
    "Puna maduro cigara — klasika": "A full maduro cigar — a classic",
    "Puna maduro cigara — sladak kontrast": "A full maduro cigar — a sweet contrast",
    "Puna, zacinska cigara": "A full, spicy cigar",
    "Slatko; gusi finije cigare": "Sweet; smothers finer cigars",
    "Srednja Habano cigara": "A medium Habano cigar",
    "Srednja cigara": "A medium cigar",
    "Srednja cigara, Habano": "A medium cigar, Habano",
    "Srednja cigara, Habano ili blazi maduro": "A medium cigar, Habano or a milder maduro",
    "Srednja cigara, balans snage": "A medium cigar, balanced strength",
    "Srednja cigara, maduro": "A medium cigar, maduro",
    "Srednja cigara, zacinska": "A medium, spicy cigar",
    "Srednja cigara; odlezana grappa podnosi i puniju": "A medium cigar; aged grappa can take a fuller one",
    "Srednja do puna cigara, maduro": "A medium-to-full cigar, maduro",
    "Srednja maduro": "A medium maduro",
    "Srednja maduro - dodaje tijelo cigari": "A medium maduro — adds body to the cigar",
    "Srednja maduro, glađi solera": "A medium maduro; a smoother solera",
    "Srednja maduro, kao Doorly's": "A medium maduro, as with Doorly's",
    "Srednja maduro, ugodna": "A medium, pleasant maduro",
    "Srednja suha; Connecticut ili sredni maduro": "Medium and dry; Connecticut or a medium maduro",
    "Srednja, Barbados/Dom., natural wrapper": "Medium; Barbados/Dominican, natural wrapper",
    "Srednja, blaža": "Medium, on the milder side",
    "Srednja, elegantna": "Medium and elegant",
    "Srednja, suh-ish": "Medium, dry-leaning",
    "Srednja, suha": "Medium and dry",
    "Srednja-jaka maduro": "A medium-strong maduro",
    "Srednja-jaka maduro (slatkoca presiječe gorčinu)": "A medium-strong maduro (sweetness cuts the bitterness)",
    "Srednja-jaka maduro, zemljana": "A medium-strong, earthy maduro",
    "Srednja-jaka, Habano": "Medium-strong, Habano",
    "Srednja-jaka, Habano wrapper": "Medium-strong, Habano wrapper",
    "Srednja-puna Habano cigara": "A medium-to-full Habano cigar",
    "Srednja-puna cigara": "A medium-to-full cigar",
    "Srednja-puna cigara, Habano": "A medium-to-full cigar, Habano",
    "Srednja-puna cigara, maduro ili Habano": "A medium-to-full cigar, maduro or Habano",
    "Srednja-puna cigara, maduro kontrast": "A medium-to-full cigar, a maduro contrast",
    "Srednja-puna maduro cigara": "A medium-to-full maduro cigar",
    "Srednja; mlad ali čist": "Medium; young but clean",
    "Sve wrapper tipovi srednje snage": "Any medium-strength wrapper type",
    "Vrlo blaga cigara": "A very mild cigar",
}

def convert(path: Path) -> None:
    items = json.loads(path.read_text(encoding="utf-8"))
    missing = set()
    for d in items:
        det = d.get("additiveDetail")
        if isinstance(det, str):
            if det in DET_NORMALIZE:
                hr, en = DET_NORMALIZE[det]
                d["additiveDetail"] = {"hr": hr, "en": en}
            elif det in DET:
                d["additiveDetail"] = {"hr": det, "en": DET[det]}
            else:
                missing.add(("det", det))
        hint = d.get("cigarHint")
        if isinstance(hint, str) and hint:
            hint = HINT_FIX.get(hint, hint)
            if hint in HINT:
                d["cigarHint"] = {"hr": hint, "en": HINT[hint]}
            else:
                missing.add(("hint", hint))
    if missing:
        for m in sorted(missing):
            print("NEDOSTAJE:", m)
        sys.exit(1)
    path.write_text(json.dumps(items, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{path.name}: OK")

if __name__ == "__main__":
    for name in ["rums", "whiskies", "brandies", "gins", "wines", "coffees"]:
        convert(DATA / f"{name}.json")
    convert(SEED)
