# -*- coding: utf-8 -*-
"""Profesionalni dvojezicni opisi linija cigara (idempotentno).

Zamjenjuje filler biljeske ("Sinkronizirano iz HR trgovina...", "Dostupno u
HR trgovinama...", kratke engleske natuknice) pravim opisima:
  1. KURIRANI opisi za poznate linije (prefiks brand+line)
  2. generator iz profila (wrapper + snaga/tijelo + note okusa) za ostale;
     postojeca engleska natuknica se ugradi u EN opis

Pokreni nakon regeneracije cigars.json (prije dedupe-data.py):
  python scripts/describe-lines.py
"""
import json
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "data"

TAG_EN = {
    "kakao": "cocoa", "kava": "coffee", "zemljano": "earth", "koza": "leather",
    "papar": "pepper", "zacini": "spice", "zacini-slatki": "sweet spice",
    "cedar": "cedar", "drvo": "wood", "med": "honey", "citrus": "citrus",
    "kremasto": "cream", "orasasti": "nuts", "karamela": "caramel",
    "vanilija": "vanilla", "slatko": "sweetness", "suho-voce": "dried fruit",
    "tamno-voce": "dark fruit", "cvjetno": "florals", "trava-slatka": "sweet grass",
    "duhan": "tobacco", "dim": "smoke", "melasa": "molasses",
}

# kurirani opisi: (prefiks "brand line".lower()) -> (hr, en)
CURATED = {
    "1502 emerald": (
        "Emerald je najpitkiji izraz linije 1502 — nikaragvanski puro s box-pressom i zatvorenom nogom, kremasto-drvenast uz blage začine.",
        "Emerald is 1502's most approachable expression — a box-pressed Nicaraguan puro with a closed foot, creamy-woody with gentle spice."),
    "1502 ruby": (
        "Ruby donosi srednje-puno tijelo i sočniju slatkoću od Emeralda; potpisni box-press i zatvorena noga čuvaju ulja i arome.",
        "Ruby brings medium-full body and juicier sweetness than Emerald; the signature box-press and closed foot lock in oils and aroma."),
    "1502 black gold": (
        "Black Gold je najtamnija redovna 1502 — bogata, čokoladno-zemljana, uz jaču kavu i dulji finiš.",
        "Black Gold is the darkest regular 1502 — rich, chocolate-earthy, with stronger coffee and a longer finish."),
    "1502 nicaragua": (
        "Nicaragua slavi terroir: puro iz tri regije s naglašenim začinima i zemljom, srednje-puno tijelo.",
        "Nicaragua celebrates terroir: a three-region puro with pronounced spice and earth, medium-full in body."),
    "1502 xo": (
        "XO je luksuzni vrh kuće — dodatno odležani duhani, svilenkast dim i profinjena slatkoća kakaa.",
        "XO tops the house range — extra-aged tobaccos, silky smoke and refined cocoa sweetness."),
    "1502 aniversario": (
        "Jubilarno izdanje uz obljetnicu marke — odabrane šarže i zaobljeniji, svečaniji profil.",
        "The anniversary release — selected batches and a rounder, celebratory profile."),
    "aj fernandez enclave": (
        "Enclave je AJ-eva posveta 'enklavi' odanih pušača: broadleaf slatkoća preko nikaragvanske jezgre, kruh s korom, kakao i slatki začini u srednje-punom tijelu.",
        "Enclave is AJ's tribute to the 'enclave' of loyal smokers: broadleaf sweetness over a Nicaraguan core — baked bread, cocoa and sweet spice at medium-full."),
    "aj fernandez san lotano": (
        "San Lotano je obiteljska linija (ime iz duhanskih polja obitelji Fernández) — oval press za ravnomjerno gorenje, uravnotežena začinjenost.",
        "San Lotano is the family line (named for the Fernández tobacco fields) — the oval press burns evenly, with balanced spice."),
    "aganorsa leaf aniversario connecticut": (
        "Jubilarni blend u Connecticut ruhu — najsvjetlija Aganorsa: kremasta, medena, uz prepoznatljivu slatkoću kućnog duhana.",
        "The anniversary blend in Connecticut dress — Aganorsa's brightest: creamy, honeyed, with the house tobacco's signature sweetness."),
    "aganorsa leaf aniversario corojo": (
        "Jubilarni corojo — svilenkast dim, slatki začini i kakao; elegantna demonstracija slavnih Aganorsa polja.",
        "The anniversary corojo — silky smoke, sweet spice and cocoa; an elegant showcase of the famed Aganorsa farms."),
    "aganorsa leaf aniversario maduro": (
        "Jubilarni maduro — tamna čokolada i espresso na kremastoj Aganorsa bazi.",
        "The anniversary maduro — dark chocolate and espresso over the creamy Aganorsa base."),
    "aganorsa leaf la validacion": (
        "La Validación ('potvrda') dokazuje kvalitetu vlastitog duhana — gusti, uljasti dim; svaka verzija (Connecticut, Habano, Corojo, Maduro) nosi isti svilenkasti DNK.",
        "La Validación ('the validation') proves their own leaf — dense oily smoke; each version (Connecticut, Habano, Corojo, Maduro) carries the same silky DNA."),
    "aganorsa leaf rare leaf": (
        "Rare Leaf Reserve koristi rijetke, dodatno odležane šarže — koncentriran okus i dulji finiš za posebne prigode.",
        "Rare Leaf Reserve uses rare, extra-aged batches — concentrated flavour and a longer finish for special occasions."),
    "aganorsa leaf signature": (
        "Signature Selection je potpisni kućni blend — najizravniji uvod u slatko-začinski karakter Aganorsa duhana.",
        "Signature Selection is the house's signature blend — the most direct introduction to Aganorsa's sweet-spiced character."),
    "aganorsa leaf supreme": (
        "Supreme Leaf je punokrvna strana kuće — snažan, zemljano-papren, s karakterističnom slatkoćom u pozadini.",
        "Supreme Leaf is the house at full blood — strong, earthy-peppery, with the trademark sweetness underneath."),
    "casa 1910 cuchillo parado": (
        "Cuchillo Parado nosi ime mjesta gdje je počela meksička revolucija — San Andrés puro: tamno, zemljano, s kakaom i suhim voćem.",
        "Cuchillo Parado is named for the village where the Mexican revolution began — a San Andrés puro: dark, earthy, cocoa and dried fruit."),
    "cohiba robusto": (
        "Robusto Línea Clásice — snažniji od Sigla, s dubinom El Laguito fermentacije: trava, med, kava i fini začini.",
        "The Línea Clásica Robusto — stronger than the Siglos, with El Laguito's depth: grass, honey, coffee and fine spice."),
    "e.p. carrillo inch": (
        "INCH slavi velike prstenove (58–70): puno dima, mekana tekstura; Natural je uglađen, Maduro tamniji i slađi.",
        "INCH celebrates big ring gauges (58–70): huge smoke output, soft texture; Natural is polished, Maduro darker and sweeter."),
    "e.p. carrillo dusk": (
        "Dusk je Ernestova večernja cigara — tamni broadleaf preko nikaragvanske jezgre, kakao i zemlja bez agresije.",
        "Dusk is Ernesto's evening cigar — dark broadleaf over a Nicaraguan core, cocoa and earth without aggression."),
    "e.p. carrillo seleccion oscuro": (
        "Selección Oscuro — najtamniji EPC izraz: gusta slatkoća pečenog kakaa i crne kave, puno tijelo.",
        "Selección Oscuro — EPC's darkest expression: dense baked-cocoa sweetness and black coffee, full body."),
    "eiroa 20 years colorado": (
        "20 Years Colorado obilježava dva desetljeća Christiana Eiroe — colorado wrapper daje karamelu i cedar uz honduraški temperament.",
        "20 Years Colorado marks Christian Eiroa's two decades — the colorado wrapper adds caramel and cedar to Honduran temperament."),
    "eiroa the first 20 years": (
        "The First 20 Years je svečana serija — odležani honduraški duhani u velikim, sporim formatima poput diademe.",
        "The First 20 Years is the celebration series — aged Honduran tobaccos in large, slow formats like the diadema."),
    "joya de nicaragua joya red": (
        "JOYA Red je moderna, pitkija strana najstarije nikaragvanske fabrike — sočni začini, kremasto, bez težine Antaña.",
        "JOYA Red is the modern, sessionable side of Nicaragua's oldest factory — juicy spice, creamy, without Antaño's weight."),
    "joya de nicaragua rosalones": (
        "Rosalones je tradicionalna serija za europsko tržište — pošteni nikaragvanski profil izvrsnog omjera cijene i kvalitete.",
        "Rosalones is the traditional series for Europe — an honest Nicaraguan profile at excellent value."),
    "la galera fresh pack": (
        "Fresh Pack donosi La Galera kvalitetu u pakiranju koje čuva vlagu — ista dominikanska izrada, spremna za put.",
        "Fresh Pack brings La Galera quality in humidity-sealed packs — the same Dominican craft, travel-ready."),
    "oscar valladares connecticut": (
        "Oscarov Connecticut nije tipično blag — kremast, ali s honduraškom jezgrom koja dodaje papar i tijelo.",
        "Oscar's Connecticut isn't typically mild — creamy, but with a Honduran core adding pepper and body."),
    "oscar valladares corojo": (
        "Corojo je Oscarova najjača karta — papreno, zemljano, s tamnom slatkoćom; za iskusne pušače.",
        "The Corojo is Oscar's strongest card — peppery, earthy, darkly sweet; for seasoned smokers."),
    "oscar valladares edition": (
        "Edition serija (boje) istražuje različite wrappere na istoj jezgri — svaka boja nosi svoj karakter, od kremastog do tamnog.",
        "The Edition series (colours) explores different wrappers on one core — each colour has its own character, from creamy to dark."),
    "oscar valladares barber pole": (
        "Barber Pole plete dva wrappera u spiralu — izmjena kremastog i tamnog u svakom dimu.",
        "The Barber Pole braids two wrappers in a spiral — creamy and dark alternating in every puff."),
    "partagás short": (
        "Legendarni Short — puni Partagás karakter (zemlja, papar, kava) sažet u pola sata. Referentna mala kubanka.",
        "The legendary Short — full Partagás character (earth, pepper, coffee) in half an hour. The reference small Cuban."),
    "perdomo 10th anniversary": (
        "10th Anniversary Champagne — kremasti Connecticut odležan u bourbon bačvama: vanilija, med i lagana hrastova slatkoća.",
        "10th Anniversary Champagne — a creamy Connecticut aged in bourbon barrels: vanilla, honey and light oak sweetness."),
    "perdomo 30th anniversary": (
        "30th Anniversary donosi najstarije Perdomo duhane — svilenkast, zaobljen, s bourbon-bačva finišem.",
        "30th Anniversary features Perdomo's oldest tobaccos — silky, rounded, with the bourbon-barrel finish."),
    "plasencia cosecha 146": (
        "Cosecha 146 slavi berbu 2011./12. ('146. žetva obitelji') — voćno-začinski honduraški blend iz jednog uroda.",
        "Cosecha 146 honours the 2011/12 harvest (the family's 146th) — a fruit-and-spice Honduran blend from a single crop."),
    "punch punch": (
        "Punch Punch je istoimeni klasik marke — zemljano-drvenast corona gorda s notom kave; stara škola habanosa.",
        "The eponymous Punch Punch — an earthy-woody corona gorda with a coffee note; old-school habano."),
    "punch triunfos": (
        "Triunfos — pristupačniji Punch format istog rustikalnog, medeno-zemljanog karaktera.",
        "Triunfos — a more accessible Punch format with the same rustic, honey-earth character."),
    "san cristóbal de la habana el principe": (
        "El Príncipe je mala kruna marke — kratka kubanka medene slatkoće i blagih začina, izvrsna uz kavu.",
        "El Príncipe is the marque's little crown — a short Cuban of honeyed sweetness and gentle spice, excellent with coffee."),
    "trinidad esmeralda": (
        "Esmeralda proširuje Trinidad u veći format — ista medeno-cedrasta elegancija, više vremena za razvoj.",
        "Esmeralda extends Trinidad into a larger format — the same honey-cedar elegance with more time to evolve."),
    "vegas robaina famosos": (
        "Famosos je srce marke Robaina — zemljano-slatki hermoso format iz najboljih vega Vuelta Abaja.",
        "Famosos is the heart of the Robaina marque — an earthy-sweet hermoso from Vuelta Abajo's finest vegas."),
    "h. upmann half corona": (
        "Half Corona — savršena 'kava cigara': 25 minuta uglađene kremaste kubanke, referentni mali format.",
        "The Half Corona — the perfect coffee cigar: 25 minutes of polished, creamy Cuban; the reference small format."),
    "aj fernandez dias de gloria": (
        "Días de Gloria ('dani slave') vraća AJ-a korijenima — punokrvni nikaragvanski puro, zemlja, papar i tamni kakao.",
        "Días de Gloria ('days of glory') returns AJ to his roots — a full-blooded Nicaraguan puro of earth, pepper and dark cocoa."),
}

STRENGTH_HR = {1: "blaga i glatka", 2: "blaga prema srednjoj", 3: "uravnotežena, srednje snage",
               4: "punija i izražajna", 5: "snažna, za iskusne pušače"}
STRENGTH_EN = {1: "mild and smooth", 2: "mild-to-medium", 3: "balanced, medium in strength",
               4: "fuller and expressive", 5: "powerful, for seasoned smokers"}

FILLER = re.compile(r"^(Sinkronizirano iz HR trgovina|Dostupno u HR trgovinama)|^$")
SHORT_EN = re.compile(r"^[A-Za-z0-9 ,;.'&()/-]+$")


def curated_for(c):
    key = f"{c['brand']} {c['line']}".lower()
    for prefix, txt in CURATED.items():
        if key.startswith(prefix):
            return txt
    return None


def generate(c):
    tags = c.get("flavorTags", [])[:3]
    tags_hr = ", ".join(tags)
    tags_en = ", ".join(TAG_EN.get(t, t) for t in tags)
    wrapper = c.get("wrapper", "").strip()
    country = c.get("country", "")
    s = c.get("strength", 3)
    hr = f"{wrapper} wrapper ({country}); {STRENGTH_HR.get(s, STRENGTH_HR[3])}."
    en = f"{wrapper} wrapper ({country}); {STRENGTH_EN.get(s, STRENGTH_EN[3])}."
    if tags_hr:
        hr += f" Note: {tags_hr}."
        en += f" Notes of {tags_en}."
    return hr, en


def main():
    p = DATA / "cigars.json"
    cigars = json.loads(p.read_text(encoding="utf-8"))
    n_cur = n_gen = 0
    for c in cigars:
        note_hr = (c.get("notes", {}).get("hr") or "").strip()
        is_filler = bool(FILLER.match(note_hr))
        is_short_en = bool(SHORT_EN.match(note_hr)) and len(note_hr) < 70
        cur = curated_for(c)
        if cur:
            c["notes"] = {"hr": cur[0], "en": cur[1]}
            n_cur += 1
        elif is_filler or is_short_en:
            hr, en = generate(c)
            # postojecu englesku natuknicu ugradi u EN opis
            if is_short_en and note_hr:
                en = f"{en} {note_hr.rstrip('.')}."
            c["notes"] = {"hr": hr, "en": en}
            n_gen += 1
        elif not (c.get("notes", {}).get("en") or "").strip():
            # HR opis postoji, EN prazan -> generiraj EN
            _, en = generate(c)
            c["notes"]["en"] = en
            n_gen += 1
    p.write_text(json.dumps(cigars, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"kurirano: {n_cur} | generirano: {n_gen} | ukupno: {len(cigars)}")


if __name__ == "__main__":
    main()
