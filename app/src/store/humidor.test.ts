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

    expect(h.consumeFromStock("cig-x")).toBe(b.id);
    expect(h.stockCount(b.id, "cig-x")).toBe(4);
    expect(h.stockCount(a.id, "cig-x")).toBe(2);
  });

  it("consumeFromStock poseže za drugim humidorom kad aktivni nema", async () => {
    const h = await load();
    const a = h.addHumidor("A");
    const b = h.addHumidor("B");
    h.setStock(a.id, "cig-x", 1);
    h.setActiveHumidor(b.id);

    expect(h.consumeFromStock("cig-x")).toBe(a.id);
    expect(h.stockCount(a.id, "cig-x")).toBe(0);
  });

  it("consumeFromStock ne mijenja ništa kad cigare nema u zalihi", async () => {
    const h = await load();
    h.addHumidor("A");
    expect(h.consumeFromStock("cig-nema")).toBeNull();
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
