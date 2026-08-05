import { describe, it, expect } from "vitest";
import { bottleLabel, drinkNameLoc, drinkNameHaystack } from "./drinkName";
import { ALL_DRINKS } from "../data";
import displayNamesJson from "../data/drinkDisplayNames.json";
import type { Drink } from "../types";

const DISPLAY = (displayNamesJson as { names: Record<string, string> }).names;

const byName = (frag: string): Drink => {
  const d = ALL_DRINKS.find((x) => x.name.includes(frag));
  if (!d) throw new Error(`missing drink ~ ${frag}`);
  return d;
};

const byId = (id: string): Drink => {
  const d = ALL_DRINKS.find((x) => x.id === id);
  if (!d) throw new Error(`missing drink id ${id}`);
  return d;
};

describe("drinkNameLoc — lokalizacija imena pića", () => {
  it("bez nameLoc i bez display mape: oba jezika padaju na sirovo name", () => {
    const plain = ALL_DRINKS.find((d) => !d.nameLoc && !DISPLAY[d.id])!;
    expect(drinkNameLoc(plain)).toEqual({ hr: plain.name, en: plain.name });
  });

  it("hrvatski opisni nazivi kave prevedeni u EN, HR ostaje", () => {
    const turska = byName("Turska");
    const loc = drinkNameLoc(turska);
    expect(loc.hr).toBe("Turska / domaća kava (džezva)");
    expect(loc.en).toBe("Turkish coffee (džezva)");
    expect(loc.en).toContain("džezva");

    const vijet = byName("Vijetnamska");
    expect(drinkNameLoc(vijet).en).toBe("Vietnamese iced coffee (cà phê sữa đá)");
    expect(drinkNameLoc(vijet).en).toContain("cà phê sữa đá");
  });

  it("EN imena kave ne sadrže hrvatske riječi", () => {
    const HR_WORD = /\b(kava|talijanska|tamna|mješavina|ledena|zaslađeni|duži|prženica|domaća|Turska|Vijetnamska|Etiopija|Kenija|Kolumbija|Gvatemala)\b/;
    for (const d of ALL_DRINKS.filter((x) => x.category === "coffee")) {
      expect(drinkNameLoc(d).en, d.name).not.toMatch(HR_WORD);
    }
  });

  it("haystack sadrži i HR i EN varijantu (pretraga u oba jezika)", () => {
    const turska = byName("Turska");
    const hay = drinkNameHaystack(turska);
    expect(hay).toContain("Turska");
    expect(hay).toContain("Turkish");
  });
});

describe("drinkNameLoc — scrape repovi (W4 display map)", () => {
  const SCRAPE_JUNK = /%\s*Vol|u poklon kutij|&#|\d+[.,]?\d*\s*l\b/i;

  it("nijedno prikazno ime u mapi ne nosi scrape rep", () => {
    for (const [id, label] of Object.entries(DISPLAY)) {
      expect(label, id).not.toMatch(/%\s*Vol|u poklon kutij|&#/i);
    }
  });

  it("boce sa scrape repom u name dobiju očišćen prikaz", () => {
    const tailed = ALL_DRINKS.filter((d) => SCRAPE_JUNK.test(d.name) && !d.nameLoc);
    expect(tailed.length).toBeGreaterThan(0);
    for (const d of tailed) {
      const loc = drinkNameLoc(d);
      expect(loc.hr, d.id).not.toMatch(/%\s*Vol|u poklon kutij|&#/i);
      // sirovi name ostaje za buy-link
      expect(d.name).toMatch(SCRAPE_JUNK);
    }
  });

  it("varijante istog očišćenog imena ostaju razlučive", () => {
    // No. 3 London Dry Gin: standard (0,7 l) vs isti u poklon kutiji sa čašom —
    // oba imaju isti očišćeni naziv ali različite diskriminatore.
    const a = drinkNameLoc(byId("gin-no-3-london-dry-gin-46-vol-0-7l"));
    const b = drinkNameLoc(byId("gin-no-3-london-dry-gin-46-vol-0-7l-u-poklon-kutiji-sa-casom"));
    expect(a.hr).not.toBe(b.hr);
    expect(a.hr).toContain("No. 3 London Dry Gin");
    expect(b.hr).toMatch(/poklon/i);
  });

  it("haystack i dalje sadrži sirovo name (buy-link / pretraga)", () => {
    const d = byId("gin-no-3-london-dry-gin-46-vol-0-7l");
    expect(drinkNameHaystack(d)).toContain(d.name);
    expect(drinkNameHaystack(d)).toContain(drinkNameLoc(d).hr);
  });
});

// U usporednoj tablici marke ime marke se ponavlja u svakom retku, pa ga
// kartica skida. Skidanje ne smije proizvesti prazan naziv.
describe("bottleLabel — naziv boce unutar marke", () => {
  it("skida ime marke s početka", () => {
    expect(bottleLabel("GlenDronach 12", "GlenDronach")).toBe("12");
    expect(bottleLabel("Foursquare Détente", "Foursquare")).toBe("Détente");
  });

  it("ime jednako marki ostaje cijelo", () => {
    expect(bottleLabel("Zacapa", "Zacapa")).toBe("Zacapa");
  });

  it("ime koje ne počinje markom ostaje cijelo", () => {
    expect(bottleLabel("Tokaji Aszú 5", "Royal Tokaji")).toBe("Tokaji Aszú 5");
  });

  it("nikad ne vraća prazan naziv", () => {
    expect(bottleLabel("Nikka  ", "Nikka")).toBe("Nikka  ");
    for (const d of ALL_DRINKS) {
      expect(bottleLabel(d.name, d.name.split(" ")[0]).trim(), d.name).not.toBe("");
    }
  });
});
