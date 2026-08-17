// Marke pića su IZVEDENE iz imena (pića nemaju `brand` polje), pa moraju
// ostati u skladu s podacima — inače filter po marki prikazuje marke bez boca
// ili gubi boce koje su u međuvremenu dodane.
import { describe, expect, it } from "vitest";
import { ALL_DRINKS, ALL_DRINK_BRANDS, drinkBrand, drinksByBrand } from "./index";

describe("marke pića", () => {
  // Stilska kava (Ristretto, Brazil Santos) nema proizvođača. Imenovane
  // mješavine (Franck, illy…) imaju marku iz overrides.
  const NAMED_COFFEE: Record<string, string> = {
    "cf-franck-bonus-espresso": "Franck",
    "cf-franck-crema": "Franck",
    "cf-franck-espresso": "Franck",
    "cf-franck-jubilarna": "Franck",
    "cf-franck-jubilarna-intense": "Franck",
    "cf-franck-jubilarna-sensual": "Franck",
    "cf-illy-classico": "illy",
    "cf-illy-intenso": "illy",
    "cf-julius-meinl-vienna-espresso": "Julius Meinl",
    "cf-lavazza-qualita-oro": "Lavazza",
    "cf-lavazza-qualita-rossa": "Lavazza",
    "cf-segafredo-intermezzo": "Segafredo",
  };
  const withBrand = ALL_DRINKS.filter(
    (d) => d.category !== "coffee" || d.id in NAMED_COFFEE,
  );

  it("svako piće osim stilske kave ima marku", () => {
    const missing = withBrand.filter((d) => !drinkBrand(d.id)).map((d) => d.id);
    expect(
      missing,
      "Novo piće? Pokreni `python3 scripts/derive-drink-brands.py`.",
    ).toEqual([]);
  });

  it("stilska kava nema marku; imenovane mješavine imaju", () => {
    const coffee = ALL_DRINKS.filter((d) => d.category === "coffee");
    expect(coffee.length).toBeGreaterThan(0);
    const styleBranded = coffee
      .filter((d) => !(d.id in NAMED_COFFEE) && drinkBrand(d.id))
      .map((d) => d.id);
    expect(styleBranded).toEqual([]);
    const wrong: string[] = [];
    for (const [id, brand] of Object.entries(NAMED_COFFEE)) {
      const got = drinkBrand(id);
      if (got !== brand) wrong.push(`${id}: ${got} ≠ ${brand}`);
    }
    expect(wrong).toEqual([]);
  });

  it("svaka marka ima barem jednu bocu", () => {
    const empty = ALL_DRINK_BRANDS.filter((b) => drinksByBrand(b).length === 0);
    expect(empty).toEqual([]);
  });

  it("marka nije prazna ni sam broj", () => {
    const bad = ALL_DRINK_BRANDS.filter((b) => !b.trim() || /^[\d\s.,%]+$/.test(b));
    expect(bad).toEqual([]);
  });

  it("boce marke su poredane po kvaliteti pa imenu", () => {
    const brand = ALL_DRINK_BRANDS.find((b) => drinksByBrand(b).length > 2);
    expect(brand).toBeDefined();
    const list = drinksByBrand(brand!);
    for (let i = 1; i < list.length; i++) {
      const a = list[i - 1].qualityScore ?? 0;
      const b = list[i].qualityScore ?? 0;
      expect(a >= b).toBe(true);
    }
  });

  it("zbroj boca po markama pokriva sva pića koja imaju marku", () => {
    const total = ALL_DRINK_BRANDS.reduce((n, b) => n + drinksByBrand(b).length, 0);
    expect(total).toBe(withBrand.length);
  });

  // Boca koja je jedina s tom prvom rijecju nema s cim usporediti prefiks, pa
  // je heuristika rezala na prvu rijec — "Sailor" umjesto "Sailor Jerry".
  // Vezne rijeci ("&", "de", "y", "of") skripta drzi na okupu sama; ostalo je
  // rijeseno u scripts/data/drink_brand_overrides.json.
  it("dvorječne marke nisu odrezane na prvu riječ", () => {
    const expected: Record<string, string> = {
      "rum-sailor-jerry": "Sailor Jerry",
      "rum-smith-cross": "Smith & Cross",
      "rum-wray-nephew-overproof-63": "Wray & Nephew",
      "rum-sol-tarasco-4-yo-charanda": "Sol Tarasco",
      "rum-captain-morgan-spiced-white-black": "Captain Morgan",
      "rum-gold-of-mauritius-dark-heritage-solera": "Gold of Mauritius",
      "wh-buffalo-trace": "Buffalo Trace",
      "wh-makers-mark": "Maker's Mark",
      "wh-woodford-reserve": "Woodford Reserve",
      "wh-knob-creek-9": "Knob Creek",
      "br-baron-de-sigognac-10-ans": "Baron de Sigognac",
      "br-cardenal-mendoza-solera-gran-reserva": "Cardenal Mendoza",
      "wine-don-melchor": "Concha y Toro",
      "wine-moet-brut-imperial": "Moet & Chandon",
      "wine-veuve-clicquot-yellow": "Veuve Clicquot",
    };
    const wrong: string[] = [];
    for (const [id, brand] of Object.entries(expected)) {
      const got = drinkBrand(id);
      if (got !== brand) wrong.push(`${id}: ${got} ≠ ${brand}`);
    }
    expect(wrong).toEqual([]);
  });

  // Marka je kuca, ne kuca + vrsta pica ("Boulard Calvados", "Berta Grappa").
  it("marka ne nosi vrstu pića u imenu", () => {
    const KIND = /\b(rum|rhum|gin|whisky|whiskey|calvados|grappa|vinjak|armagnac|cognac|tequila|vodka|liqueur|liker)\b/i;
    // Iznimke: vrsta JEST dio registriranog imena marke.
    const OK = new Set([
      "Rhum J.M",
      "Four Monkey's Rum",
      "Gin Mare",
      "The Bush Rum",
      "Rum Exchange",
      "Rum Nation",
      "Hrvatski lozovača / vinjak (craft)", // generički unos, nije marka
    ]);
    const bad = ALL_DRINK_BRANDS.filter(
      (b) => !OK.has(b) && b.split(/\s+/).length > 1 && KIND.test(b),
    );
    expect(bad).toEqual([]);
  });

  // Kad dvije RAZLICITE marke dijele prvu rijec ("Black Tot" i "Black Bottle"),
  // najdulji zajednicki prefiks ispadne goli krnjatak — algoritam ih ne moze
  // razluciti bez znanja o svijetu. Prelazak kategorija je jak signal: isti
  // proizvodac rijetko radi i gin i bourbon.
  //
  // Poznate iznimke su stvarni proizvodaci s vise kategorija.
  it("jednorječna marka ne spaja različite proizvođače", () => {
    const MULTI_CATEGORY_HOUSES = new Set([
      "Nikka", // whisky + Coffey Gin
      "Nonino", // grappa + amaro
      "Antinori", // vino + grappa
      "Gaja", // vino + grappa
      "Ableforth's", // gin + rum
      "AURA", // pelinkovac + gin
    ]);
    const suspects = ALL_DRINK_BRANDS.filter((b) => {
      if (b.split(/\s+/).length !== 1 || MULTI_CATEGORY_HOUSES.has(b)) return false;
      const cats = new Set(drinksByBrand(b).map((d) => d.category));
      return cats.size > 1;
    });
    expect(
      suspects,
      "Marka od jedne riječi s bocama u više kategorija vjerojatno spaja dva proizvođača. " +
        "Razdvoji ih u scripts/data/drink_brand_overrides.json, ili — ako je stvarno " +
        "ista kuća — dopiši je u MULTI_CATEGORY_HOUSES.",
    ).toEqual([]);
  });
});
