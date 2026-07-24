import { describe, it, expect } from "vitest";
import { drinkNameLoc, drinkNameHaystack } from "./drinkName";
import { ALL_DRINKS } from "../data";
import type { Drink } from "../types";

const byName = (frag: string): Drink => {
  const d = ALL_DRINKS.find((x) => x.name.includes(frag));
  if (!d) throw new Error(`missing drink ~ ${frag}`);
  return d;
};

describe("drinkNameLoc — lokalizacija imena pića", () => {
  it("bez nameLoc: oba jezika padaju na sirovo name", () => {
    const plain = ALL_DRINKS.find((d) => !d.nameLoc)!;
    expect(drinkNameLoc(plain)).toEqual({ hr: plain.name, en: plain.name });
  });

  it("hrvatski opisni nazivi kave prevedeni u EN, HR ostaje", () => {
    const turska = byName("Turska");
    const loc = drinkNameLoc(turska);
    expect(loc.hr).toBe("Turska / domaća kava (džezva)");
    expect(loc.en).toBe("Turkish coffee (džezva)");
    // vlastiti pojam se ne prevodi
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
