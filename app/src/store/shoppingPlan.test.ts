import { describe, expect, it, beforeEach, vi } from "vitest";

function fakeStorage() {
  const map = new Map<string, string>();
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

const load = () => import("./shoppingPlan");

describe("moj plan (shopping)", () => {
  it("bez spremljenog stanja sjeme iz shopping.json (owned: true)", async () => {
    const { isPlanRowOwned, exportShoppingPlan } = await load();
    expect(isPlanRowOwned("S", "Foursquare Doorly's XO / ECS")).toBe(true);
    expect(isPlanRowOwned("S", "Hampden Estate 8")).toBe(false);
    expect(exportShoppingPlan().length).toBeGreaterThan(0);
  });

  it("toggle ukljucuje pa iskljucuje i pamti", async () => {
    const { togglePlanRow, isPlanRowOwned } = await load();
    expect(togglePlanRow("S", "Hampden Estate 8")).toBe(true);
    expect(isPlanRowOwned("S", "Hampden Estate 8")).toBe(true);
    expect(togglePlanRow("S", "Hampden Estate 8")).toBe(false);
    expect(isPlanRowOwned("S", "Hampden Estate 8")).toBe(false);

    vi.resetModules();
    const again = await load();
    expect(again.isPlanRowOwned("S", "Hampden Estate 8")).toBe(false);
  });

  it("maknuti seed i dalje ostaje maknut nakon reloada", async () => {
    const { togglePlanRow, isPlanRowOwned } = await load();
    expect(isPlanRowOwned("S", "Foursquare Doorly's XO / ECS")).toBe(true);
    togglePlanRow("S", "Foursquare Doorly's XO / ECS");
    expect(isPlanRowOwned("S", "Foursquare Doorly's XO / ECS")).toBe(false);

    vi.resetModules();
    const again = await load();
    expect(again.isPlanRowOwned("S", "Foursquare Doorly's XO / ECS")).toBe(false);
  });

  it("prazan niz u storageu = sve odkvaceno (nije ponovno sjeme)", async () => {
    localStorage.setItem("cigar-pairing-shopping-plan-v1", "[]");
    const { exportShoppingPlan, isPlanRowOwned } = await load();
    expect(exportShoppingPlan()).toEqual([]);
    expect(isPlanRowOwned("S", "Foursquare Doorly's XO / ECS")).toBe(false);
  });

  it("import odbija smece, prihvaca ispravne kljuceve", async () => {
    const { importShoppingPlan, exportShoppingPlan } = await load();
    expect(importShoppingPlan("nije niz")).toBe(false);
    expect(importShoppingPlan(["S::Hampden Estate 8", 42, "bez-separatora"])).toBe(true);
    expect(exportShoppingPlan()).toEqual(["S::Hampden Estate 8"]);
  });

  it("import ne brise plan kad su svi kljucevi nevaljani", async () => {
    const { importShoppingPlan, togglePlanRow, isPlanRowOwned } = await load();
    togglePlanRow("S", "Hampden Estate 8");
    expect(importShoppingPlan(["bez-separatora", 42, ""])).toBe(false);
    expect(isPlanRowOwned("S", "Hampden Estate 8")).toBe(true);
  });
});
