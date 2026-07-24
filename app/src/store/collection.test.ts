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
