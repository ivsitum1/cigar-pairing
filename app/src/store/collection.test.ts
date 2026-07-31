import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

function installMemoryStorage() {
  const store = new Map<string, string>();
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    value: {
      getItem: (k: string) => store.get(k) ?? null,
      setItem: (k: string, v: string) => {
        store.set(k, String(v));
      },
      removeItem: (k: string) => {
        store.delete(k);
      },
      clear: () => store.clear(),
    },
  });
}

describe("importData", () => {
  beforeAll(() => {
    installMemoryStorage();
  });

  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  it("odbija payload s items kao nizom", async () => {
    const { importData, exportData } = await import("./collection");
    const before = exportData();
    expect(importData(JSON.stringify({ items: [], journal: [] }))).toBe(false);
    expect(exportData()).toBe(before);
  });

  it("prihvaca valjani backup i zapisuje ga", async () => {
    const { importData, exportData } = await import("./collection");
    const ok = importData(
      JSON.stringify({
        items: {
          "cig-1": {
            owned: true,
            tried: false,
            wishlist: false,
            rating: 9,
            note: "top",
          },
        },
        journal: [],
      }),
    );
    expect(ok).toBe(true);
    const parsed = JSON.parse(exportData());
    expect(parsed.items["cig-1"].rating).toBe(9);
    expect(parsed.items["cig-1"].note).toBe("top");
  });
});

describe("markOwnedBatch", () => {
  beforeAll(() => {
    installMemoryStorage();
  });

  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  it("oznacava vise cigara kao Imam bez wishlist", async () => {
    const { markOwnedBatch, getItemState } = await import("./collection");
    markOwnedBatch(["cig-a", "cig-b", "cig-a"]);
    expect(getItemState("cig-a").owned).toBe(true);
    expect(getItemState("cig-a").wishlist).toBe(false);
    expect(getItemState("cig-b").owned).toBe(true);
  });
});

describe("remapCollectionAliases", () => {
  it("spaja alias i kanonski kljuc Oliva Serie V", async () => {
    const { remapCollectionAliases } = await import("./collection");
    const out = remapCollectionAliases({
      items: {
        "cig-oliva-oliva-serie-v": {
          owned: true,
          tried: false,
          wishlist: false,
          rating: 7,
          note: "alias",
        },
        "cig-oliva-serie-v": {
          owned: false,
          tried: true,
          wishlist: false,
          rating: 9,
          note: "",
        },
        "cig-oliva-serie-v@torpedo": {
          owned: true,
          tried: false,
          wishlist: false,
          rating: null,
          note: "vitola",
        },
      },
      journal: [
        {
          id: "j1",
          date: "2026-01-01",
          cigarId: "cig-oliva-oliva-serie-v",
          drinkId: null,
          rating: null,
          note: "",
        },
      ],
    });
    expect(out.items["cig-oliva-oliva-serie-v"]).toBeUndefined();
    expect(out.items["cig-oliva-serie-v"]).toEqual({
      owned: true,
      tried: true,
      wishlist: false,
      rating: 9,
      note: "alias",
    });
    expect(out.items["cig-oliva-serie-v@torpedo"].owned).toBe(true);
    expect(out.journal[0].cigarId).toBe("cig-oliva-serie-v");
  });

  // Kombinirani unosi pića ("Flor de Cana 12/18") razdvojeni su u zasebne boce.
  // Korisnikova oznaka na starom ID-u mora preživjeti selidbu.
  it("seli ocjenu i biljesku sa starog ID-a pica na nasljednika", async () => {
    const { remapCollectionAliases } = await import("./collection");
    const out = remapCollectionAliases({
      items: {
        "rum-flor-de-cana-12-18": {
          owned: true,
          tried: true,
          wishlist: false,
          rating: 8,
          note: "kupljeno u Vrutku",
        },
      },
      journal: [
        {
          id: "j1",
          date: "2026-01-01",
          cigarId: "cig-oliva-serie-v",
          drinkId: "rum-flor-de-cana-12-18",
          rating: 9,
          note: "",
        },
      ],
    });
    expect(out.items["rum-flor-de-cana-12-18"]).toBeUndefined();
    expect(out.items["rum-flor-de-cana-12"]).toEqual({
      owned: true,
      tried: true,
      wishlist: false,
      rating: 8,
      note: "kupljeno u Vrutku",
    });
    expect(out.journal[0].drinkId).toBe("rum-flor-de-cana-12");
  });

  it("spaja stari i novi ID pica bez gubitka (ocjena = visa, biljeska ostaje)", async () => {
    const { remapCollectionAliases } = await import("./collection");
    const out = remapCollectionAliases({
      items: {
        "rum-flor-de-cana-12-18": {
          owned: false,
          tried: true,
          wishlist: false,
          rating: 9,
          note: "stara biljeska",
        },
        "rum-flor-de-cana-12": {
          owned: true,
          tried: false,
          wishlist: false,
          rating: 6,
          note: "",
        },
      },
      journal: [],
    });
    expect(Object.keys(out.items)).toEqual(["rum-flor-de-cana-12"]);
    expect(out.items["rum-flor-de-cana-12"]).toEqual({
      owned: true,
      tried: true,
      wishlist: false,
      rating: 9,
      note: "stara biljeska",
    });
  });

  it("solo zapis (drinkId null) ostaje solo", async () => {
    const { remapCollectionAliases } = await import("./collection");
    const out = remapCollectionAliases({
      items: {},
      journal: [
        {
          id: "j1",
          date: "2026-01-01",
          cigarId: "cig-oliva-serie-v",
          drinkId: null,
          rating: null,
          note: "",
        },
      ],
    });
    expect(out.journal[0].drinkId).toBeNull();
  });

  it("nepoznat ID pica ostaje netaknut (ne brisemo sto ne razumijemo)", async () => {
    const { remapCollectionAliases } = await import("./collection");
    const out = remapCollectionAliases({
      items: {
        "rum-nepoznato-nesto": {
          owned: true,
          tried: false,
          wishlist: false,
          rating: 5,
          note: "moje",
        },
      },
      journal: [],
    });
    expect(out.items["rum-nepoznato-nesto"]?.rating).toBe(5);
  });
});
