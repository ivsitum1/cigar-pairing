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

describe("clearItem", () => {
  beforeAll(() => {
    installMemoryStorage();
  });

  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  it("brise cijelo stanje stavke odjednom", async () => {
    const { updateItem, clearItem, getItemState, exportData } = await import(
      "./collection"
    );
    updateItem("cig-a", { owned: true, tried: true, rating: 8, note: "bilo" });
    clearItem("cig-a");
    expect(getItemState("cig-a")).toEqual({
      owned: false,
      tried: false,
      wishlist: false,
      rating: null,
      note: "",
    });
    expect(JSON.parse(exportData()).items["cig-a"]).toBeUndefined();
  });

  it("ne dira dnevnik ni druge stavke", async () => {
    const { updateItem, clearItem, addJournalEntry, getItemState, exportData } =
      await import("./collection");
    updateItem("cig-a", { owned: true });
    updateItem("cig-b", { owned: true });
    addJournalEntry({ cigarId: "cig-a", drinkId: null, rating: 9, note: "" });
    clearItem("cig-a");
    expect(getItemState("cig-b").owned).toBe(true);
    expect(JSON.parse(exportData()).journal).toHaveLength(1);
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

  // Sirotani: kljuc koji kartica cigare nikad ne napise, pa ga se s popisa
  // Kolekcije nije moglo ni odznaciti (vitola izbacena iz linije, ili linija
  // svedena na jednu vitolu). Migracija ih vraca na kljuc koji kartica pise.
  it("spusta kljuc s nepostojecom vitolom na razinu linije", async () => {
    const { remapCollectionAliases } = await import("./collection");
    const out = remapCollectionAliases({
      items: {
        "cig-1502-ruby@nepostojeca-vitola": {
          owned: true,
          tried: false,
          wishlist: false,
          rating: null,
          note: "sirotan",
        },
      },
      journal: [],
    });
    expect(out.items["cig-1502-ruby@nepostojeca-vitola"]).toBeUndefined();
    expect(out.items["cig-1502-ruby"]?.note).toBe("sirotan");
  });

  it("spusta vitola-kljuc na liniju koja ima samo jednu vitolu", async () => {
    const { remapCollectionAliases } = await import("./collection");
    const out = remapCollectionAliases({
      items: {
        "cig-cao-60-torque@robusto": {
          owned: false,
          tried: true,
          wishlist: false,
          rating: 7,
          note: "",
        },
      },
      journal: [],
    });
    expect(out.items["cig-cao-60-torque@robusto"]).toBeUndefined();
    expect(out.items["cig-cao-60-torque"]?.rating).toBe(7);
  });

  it("ziva vitola multi-vitola linije ostaje na svom kljucu", async () => {
    const { remapCollectionAliases } = await import("./collection");
    const out = remapCollectionAliases({
      items: {
        "cig-1502-ruby@torpedo": {
          owned: true,
          tried: false,
          wishlist: false,
          rating: null,
          note: "",
        },
      },
      journal: [],
    });
    expect(Object.keys(out.items)).toEqual(["cig-1502-ruby@torpedo"]);
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

describe("dnevnik i datumi", () => {
  beforeAll(() => {
    installMemoryStorage();
  });

  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  const entry = (over: Record<string, unknown> = {}) => ({
    cigarId: "cig-a",
    drinkId: null,
    rating: null,
    note: "",
    ...over,
  });

  it("bez datuma zapisuje trenutak unosa", async () => {
    const { addJournalEntry, exportData } = await import("./collection");
    const before = Date.now();
    addJournalEntry(entry());
    const [saved] = JSON.parse(exportData()).journal;
    expect(new Date(saved.date).getTime()).toBeGreaterThanOrEqual(before - 1000);
  });

  it("prima zadani datum — jucerasnja cigara unesena danas", async () => {
    const { addJournalEntry, exportData } = await import("./collection");
    const yesterday = new Date(2026, 7, 7, 21, 15).toISOString();
    addJournalEntry(entry({ date: yesterday }));
    expect(JSON.parse(exportData()).journal[0].date).toBe(yesterday);
  });

  it("neispravan datum pada na sada, ne kvari zapis", async () => {
    const { addJournalEntry, exportData } = await import("./collection");
    addJournalEntry(entry({ date: "nije datum" }));
    const [saved] = JSON.parse(exportData()).journal;
    expect(Number.isNaN(new Date(saved.date).getTime())).toBe(false);
  });

  it("drzi dnevnik poredan najnoviji prvi i kad je unos naknadan", async () => {
    const { addJournalEntry, exportData } = await import("./collection");
    addJournalEntry(entry({ cigarId: "cig-novi", date: new Date(2026, 7, 8, 20, 0).toISOString() }));
    addJournalEntry(entry({ cigarId: "cig-stari", date: new Date(2026, 7, 1, 20, 0).toISOString() }));
    expect(JSON.parse(exportData()).journal.map((j: { cigarId: string }) => j.cigarId)).toEqual([
      "cig-novi",
      "cig-stari",
    ]);
  });

  it("updateJournalEntry premjesta zapis na drugi dan", async () => {
    const { addJournalEntry, updateJournalEntry, exportData } = await import("./collection");
    addJournalEntry(entry({ date: new Date(2026, 7, 8, 12, 0).toISOString() }));
    const id = JSON.parse(exportData()).journal[0].id;
    const moved = new Date(2026, 7, 7, 21, 15).toISOString();
    updateJournalEntry(id, { date: moved });
    const [saved] = JSON.parse(exportData()).journal;
    expect(saved.date).toBe(moved);
    expect(saved.cigarId).toBe("cig-a");
  });

  it("updateJournalEntry ignorira neispravan datum i nepoznat id", async () => {
    const { addJournalEntry, updateJournalEntry, exportData } = await import("./collection");
    const original = new Date(2026, 7, 8, 12, 0).toISOString();
    addJournalEntry(entry({ date: original }));
    const id = JSON.parse(exportData()).journal[0].id;
    updateJournalEntry(id, { date: "nije datum" });
    updateJournalEntry("j-nepostojeci", { date: new Date(2026, 0, 1).toISOString() });
    const journal = JSON.parse(exportData()).journal;
    expect(journal).toHaveLength(1);
    expect(journal[0].date).toBe(original);
  });
});
