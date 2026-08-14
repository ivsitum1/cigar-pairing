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

const load = () => import("./humidor");

describe("humidor", () => {
  beforeAll(installMemoryStorage);

  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  it("novi humidor postaje aktivan", async () => {
    const h = await load();
    const first = h.addHumidor("Radni stol");
    expect(h.humidorData().humidors).toHaveLength(1);
    expect(h.humidorData().activeId).toBe(first.id);

    const second = h.addHumidor("Putni");
    expect(h.humidorData().activeId).toBe(second.id);
  });

  it("prazan naziv pada na zadani", async () => {
    const h = await load();
    expect(h.addHumidor("   ").name).toBe("Humidor");
  });

  it("zaliha se broji po humidoru i po vitoli", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    const b = h.addHumidor("B");

    h.setStock(a.id, "cig-x@churchill", 3);
    h.setStock(a.id, "cig-x@corona", 2);
    h.setStock(b.id, "cig-x@churchill", 1);

    expect(h.stockCount(a.id, "cig-x@churchill")).toBe(3);
    expect(h.stockCount(a.id, "cig-x@corona")).toBe(2);
    expect(h.stockCount(b.id, "cig-x@churchill")).toBe(1);
    expect(h.totalStock("cig-x@churchill")).toBe(4);
  });

  it("nula miče zapis umjesto da čuva praznu zalihu", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.setStock(a.id, "cig-x", 2);
    h.setStock(a.id, "cig-x", 0);
    expect(h.humidorData().stock).toHaveLength(0);
  });

  it("adjustStock ne ide ispod nule", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.setStock(a.id, "cig-x", 1);
    h.adjustStock(a.id, "cig-x", -5);
    expect(h.stockCount(a.id, "cig-x")).toBe(0);
  });

  it("brisanje humidora briše i njegovu zalihu", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    const b = h.addHumidor("B");
    h.setStock(a.id, "cig-x", 2);
    h.setStock(b.id, "cig-y", 1);

    h.removeHumidor(a.id);
    expect(h.humidorData().humidors.map((x) => x.id)).toEqual([b.id]);
    expect(h.humidorData().stock.map((s) => s.itemId)).toEqual(["cig-y"]);
    expect(h.humidorData().activeId).toBe(b.id);
  });

  it("consumeFromStock skida jednu iz aktivnog humidora", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    const b = h.addHumidor("B");
    h.setStock(a.id, "cig-x", 2);
    h.setStock(b.id, "cig-x", 5);
    h.setActiveHumidor(b.id);

    expect(h.consumeFromStock("cig-x")).toEqual({ humidorId: b.id, itemId: "cig-x" });
    expect(h.stockCount(b.id, "cig-x")).toBe(4);
    expect(h.stockCount(a.id, "cig-x")).toBe(2);
  });

  it("consumeFromStock poseže za drugim humidorom kad aktivni nema", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    const b = h.addHumidor("B");
    h.setStock(a.id, "cig-x", 1);
    h.setActiveHumidor(b.id);

    expect(h.consumeFromStock("cig-x")).toEqual({ humidorId: a.id, itemId: "cig-x" });
    expect(h.stockCount(a.id, "cig-x")).toBe(0);
  });

  it("consumeFromStock ne mijenja ništa kad cigare nema u zalihi", async () => {
    const h = await load();
    h.addHumidor("A");
    expect(h.consumeFromStock("cig-nema")).toBeNull();
  });

  it("zapis po vitoli skida zalihu vođenu po liniji", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.setStock(a.id, "cig-x", 1);

    expect(h.consumeFromStock("cig-x@churchill")).toEqual({
      humidorId: a.id,
      itemId: "cig-x",
    });
    expect(h.stockCount(a.id, "cig-x")).toBe(0);
  });

  it("zapis po liniji skida jedinu vitolu te linije", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.setStock(a.id, "cig-x@churchill", 2);

    expect(h.consumeFromStock("cig-x")).toEqual({
      humidorId: a.id,
      itemId: "cig-x@churchill",
    });
    expect(h.stockCount(a.id, "cig-x@churchill")).toBe(1);
  });

  it("ne pogađa vitolu kad ih linija ima više u zalihi", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.setStock(a.id, "cig-x@churchill", 2);
    h.setStock(a.id, "cig-x@corona", 2);

    expect(h.consumeFromStock("cig-x@robusto")).toBeNull();
    expect(h.stockCount(a.id, "cig-x@churchill")).toBe(2);
    expect(h.stockCount(a.id, "cig-x@corona")).toBe(2);
  });

  it("popušena vitola ne skida drugu vitolu iste linije", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.setStock(a.id, "cig-x@toro", 2);

    expect(h.consumeFromStock("cig-x@robusto")).toBeNull();
    expect(h.stockCount(a.id, "cig-x@toro")).toBe(2);
  });

  it("točan ključ ima prednost pred zalihom linije", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.setStock(a.id, "cig-x", 3);
    h.setStock(a.id, "cig-x@churchill", 3);

    expect(h.consumeFromStock("cig-x@churchill")?.itemId).toBe("cig-x@churchill");
    expect(h.stockCount(a.id, "cig-x")).toBe(3);
  });

  it("ne dira ključ druge linije s istim prefiksom", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.setStock(a.id, "cig-x-reserva", 2);

    expect(h.consumeFromStock("cig-x@churchill")).toBeNull();
    expect(h.stockCount(a.id, "cig-x-reserva")).toBe(2);
  });

  it("moveStock daje vitolu staroj zalihi vođenoj po liniji", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.setStock(a.id, "cig-x", 3);

    h.moveStock(a.id, "cig-x", "cig-x@robusto");

    expect(h.stockCount(a.id, "cig-x")).toBe(0);
    expect(h.stockCount(a.id, "cig-x@robusto")).toBe(3);
  });

  it("moveStock zbraja kad odredište već postoji", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.setStock(a.id, "cig-x", 2);
    h.setStock(a.id, "cig-x@toro", 1);

    h.moveStock(a.id, "cig-x", "cig-x@toro");

    expect(h.stockCount(a.id, "cig-x@toro")).toBe(3);
    expect(h.humidorData().stock.map((s) => s.itemId)).toEqual(["cig-x@toro"]);
  });

  it("moveStock može prebaciti samo dio zalihe", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.setStock(a.id, "cig-x", 5);

    h.moveStock(a.id, "cig-x", "cig-x@figurado", 2);

    expect(h.stockCount(a.id, "cig-x")).toBe(3);
    expect(h.stockCount(a.id, "cig-x@figurado")).toBe(2);
  });

  it("moveStock ne izmišlja zalihu koje nema", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    h.moveStock(a.id, "cig-x", "cig-x@robusto");
    expect(h.humidorData().stock).toHaveLength(0);
  });

  it("lineStock skuplja sve vitole jedne linije u tom humidoru", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    const b = h.addHumidor("B");
    h.setStock(a.id, "cig-x@robusto", 3);
    h.setStock(a.id, "cig-x@figurado", 2);
    h.setStock(a.id, "cig-x-reserva", 4);
    h.setStock(b.id, "cig-x@toro", 1);

    const rows = h.lineStock(a.id, "cig-x");
    expect(rows.map((s) => s.itemId).sort()).toEqual([
      "cig-x@figurado",
      "cig-x@robusto",
    ]);
    expect(rows.reduce((sum, s) => sum + s.count, 0)).toBe(5);
  });

  it("preživljava ponovno učitavanje", async () => {
    const first = await load();
    const a = first.addHumidor("Radni stol");
    first.setStock(a.id, "cig-x@toro", 4);

    vi.resetModules();
    const again = await load();
    expect(again.humidorData().humidors[0].name).toBe("Radni stol");
    expect(again.stockCount(a.id, "cig-x@toro")).toBe(4);
  });

  it("odbija neupotrebljiv payload, prihvaća valjani", async () => {
    const h = await load();
    expect(h.normalizeHumidorPayload(null)).toBeNull();
    expect(h.normalizeHumidorPayload({ humidors: "ne" })).toBeNull();

    const ok = h.normalizeHumidorPayload({
      humidors: [{ id: "h1", name: "A", createdAt: "2026-01-01T00:00:00.000Z" }],
      stock: [{ humidorId: "h1", itemId: "cig-x", count: 2 }],
      activeId: "h1",
    });
    expect(ok?.humidors).toHaveLength(1);
    expect(ok?.stock[0].count).toBe(2);
  });

  it("odbacuje zalihu bez svog humidora i negativne brojeve", async () => {
    const h = await load();
    const cleaned = h.normalizeHumidorPayload({
      humidors: [{ id: "h1", name: "A" }],
      stock: [
        { humidorId: "h1", itemId: "cig-ok", count: 2 },
        { humidorId: "nepostojeci", itemId: "cig-siroce", count: 9 },
        { humidorId: "h1", itemId: "cig-nula", count: -3 },
      ],
    });
    expect(cleaned?.stock.map((s) => s.itemId)).toEqual(["cig-ok"]);
  });

  it("importHumidors zamjenjuje stanje", async () => {
    const h = await load();
    h.addHumidor("Staro");
    const ok = h.importHumidors({
      humidors: [{ id: "h9", name: "Novo", createdAt: "2026-01-01T00:00:00.000Z" }],
      stock: [{ humidorId: "h9", itemId: "cig-x", count: 7 }],
      activeId: "h9",
    });
    expect(ok).toBe(true);
    expect(h.humidorData().humidors.map((x) => x.name)).toEqual(["Novo"]);
    expect(h.stockCount("h9", "cig-x")).toBe(7);
  });
});

describe("brzi unos iz kolekcije", () => {
  beforeAll(installMemoryStorage);

  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  /** Ista logika kao QuickAdd u HumidorPage: sto se nudi za dodavanje. */
  const quickAddIds = (
    items: Record<string, { owned: boolean }>,
    stock: { humidorId: string; itemId: string }[],
    humidorId: string,
    isCigar: (id: string) => boolean,
  ) => {
    const inHumidor = new Set(
      stock.filter((s) => s.humidorId === humidorId).map((s) => s.itemId),
    );
    return Object.entries(items)
      .filter(([id, s]) => s.owned && !inHumidor.has(id) && isCigar(id))
      .map(([id]) => id)
      .sort();
  };

  const isCigar = (id: string) => id.startsWith("cig-");

  it("nudi samo posjedovane cigare kojih jos nema u humidoru", () => {
    const ids = quickAddIds(
      {
        "cig-a@churchill": { owned: true },
        "cig-a@corona": { owned: true },
        "cig-b": { owned: true },
        "cig-c": { owned: false }, // samo probano
        "rum-x": { owned: true }, // pice ne ide u humidor
      },
      [{ humidorId: "h1", itemId: "cig-b" }],
      "h1",
      isCigar,
    );
    expect(ids).toEqual(["cig-a@churchill", "cig-a@corona"]);
  });

  it("zaliha u DRUGOM humidoru ne skriva prijedlog", () => {
    const ids = quickAddIds(
      { "cig-a": { owned: true } },
      [{ humidorId: "h2", itemId: "cig-a" }],
      "h1",
      isCigar,
    );
    expect(ids).toEqual(["cig-a"]);
  });

  it("dodavanje iz brzog unosa mice stavku s popisa", async () => {
    const h = await load();
    const box = h.addHumidor("Radni stol");
    const items = { "cig-a@churchill": { owned: true }, "cig-b": { owned: true } };

    expect(quickAddIds(items, h.humidorData().stock, box.id, isCigar)).toEqual([
      "cig-a@churchill",
      "cig-b",
    ]);

    h.adjustStock(box.id, "cig-a@churchill", 1);

    expect(h.stockCount(box.id, "cig-a@churchill")).toBe(1);
    expect(quickAddIds(items, h.humidorData().stock, box.id, isCigar)).toEqual([
      "cig-b",
    ]);
  });

  it("„Dodaj sve” stavi po jedan komad svake", async () => {
    const h = await load();
    const box = h.addHumidor("Radni stol");
    for (const id of ["cig-a", "cig-b", "cig-c"]) h.adjustStock(box.id, id, 1);

    expect(h.humidorData().stock).toHaveLength(3);
    expect(h.humidorData().stock.every((s) => s.count === 1)).toBe(true);
  });
});

describe("remapHumidorAliases", () => {
  it("spaja alias zalihu na kanonski itemId", async () => {
    const { remapHumidorAliases } = await load();
    const out = remapHumidorAliases({
      humidors: [{ id: "h1", name: "Kuća", createdAt: "2026-01-01T00:00:00.000Z" }],
      activeId: "h1",
      stock: [
        {
          humidorId: "h1",
          itemId: "cig-oliva-oliva-serie-v",
          count: 2,
          updatedAt: "2026-01-01T00:00:00.000Z",
        },
        {
          humidorId: "h1",
          itemId: "cig-oliva-serie-v",
          count: 1,
          updatedAt: "2026-01-02T00:00:00.000Z",
        },
      ],
    });
    expect(out.stock).toHaveLength(1);
    expect(out.stock[0].itemId).toBe("cig-oliva-serie-v");
    expect(out.stock[0].count).toBe(3);
  });
});
