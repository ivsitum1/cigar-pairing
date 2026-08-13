import { describe, expect, it, beforeEach, vi } from "vitest";

function fakeStorage(seed?: Record<string, string>) {
  const map = new Map<string, string>(Object.entries(seed ?? {}));
  return {
    getItem: (k: string) => map.get(k) ?? null,
    setItem: (k: string, v: string) => void map.set(k, v),
    removeItem: (k: string) => void map.delete(k),
  };
}

beforeEach(() => {
  vi.resetModules();
  vi.stubGlobal("localStorage", fakeStorage());
});

const load = () => import("./market");

describe("market — zadano tržište", () => {
  it("bez spremljene vrijednosti zadaje HR, ne cijeli katalog", async () => {
    const { parseMarket } = await load();
    expect(parseMarket(null)).toBe("HR");
    expect(parseMarket("WW")).toBe("HR");
    expect(parseMarket("smeće")).toBe("HR");
  });

  it("pamti izričit odabir ALL / EU / USA", async () => {
    const { parseMarket } = await load();
    expect(parseMarket("ALL")).toBe("ALL");
    expect(parseMarket("EU")).toBe("EU");
    expect(parseMarket("USA")).toBe("USA");
    expect(parseMarket("HR")).toBe("HR");
  });

  it("setMarket piše u storage", async () => {
    const { setMarket, parseMarket } = await load();
    setMarket("USA");
    expect(localStorage.getItem("market")).toBe("USA");
    expect(parseMarket(localStorage.getItem("market"))).toBe("USA");
  });
});
