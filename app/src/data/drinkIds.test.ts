// Čuvar korisničkih podataka: kolekcija i dnevnik žive u localStorageu na
// uređaju i drže ID-jeve pića. Kad se zapis ukloni ili preimenuje bez aliasa,
// korisnikova oznaka Imam / ocjena / bilješka tiho nestane iz Kolekcije, a
// dnevnik umjesto imena pokaže goli ID.
//
// Zato ovdje ne provjeravamo samo trenutne podatke nego i povijesni registar:
// svaki ID koji je ikada isporučen mora se i danas razriješiti.
import { describe, expect, it } from "vitest";
import { ALL_DRINKS, drinkById } from "./index";
import aliasFile from "./drinkIdAliases.json";
import registryFile from "./drinkIdRegistry.json";

const aliases = (aliasFile as { aliases?: Record<string, string> }).aliases ?? {};
const registry = (registryFile as { ids?: string[] }).ids ?? [];

describe("registar ID-jeva pića", () => {
  const live = new Set(ALL_DRINKS.map((d) => d.id));

  it("svaki ID iz registra se razrješava (živ zapis ili alias)", () => {
    const broken = registry.filter((id) => drinkById(id) == null);
    expect(
      broken,
      "Ovi ID-jevi su nekad postojali i mogu biti u korisničkoj kolekciji/dnevniku. " +
        "Dodaj im nasljednika u drinkIdAliases.json umjesto da ih pustiš da propadnu.",
    ).toEqual([]);
  });

  it("svaki živi ID je u registru", () => {
    const missing = [...live].filter((id) => !registry.includes(id));
    expect(
      missing,
      "Novo piće — dopiši ga u drinkIdRegistry.json da ubuduće bude čuvano.",
    ).toEqual([]);
  });

  it("alias targeti postoje", () => {
    const broken = Object.entries(aliases)
      .filter(([, to]) => !live.has(to))
      .map(([from, to]) => `${from} -> ${to}`);
    expect(broken).toEqual([]);
  });

  it("alias ne pokazuje na ID koji je i sam živ zapis", () => {
    // alias za živi ID znači da bi zapis bio dostupan pod dva imena
    const shadowed = Object.keys(aliases).filter((from) => live.has(from));
    expect(shadowed).toEqual([]);
  });

  it("nema ciklusa u aliasima", () => {
    const cyclic: string[] = [];
    for (const start of Object.keys(aliases)) {
      const seen = new Set<string>();
      let cur: string | undefined = start;
      while (cur && !live.has(cur)) {
        if (seen.has(cur)) {
          cyclic.push(start);
          break;
        }
        seen.add(cur);
        cur = aliases[cur];
      }
    }
    expect(cyclic).toEqual([]);
  });
});
