import { beforeEach, describe, expect, it } from "vitest";
import {
  normalizeCollectionPayload,
  readJsonStringArray,
  resolveLang,
} from "./safeStorage";

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

describe("readJsonStringArray", () => {
  beforeEach(() => {
    installMemoryStorage();
  });

  it("vraca prazan niz kad kljuc ne postoji", () => {
    expect(readJsonStringArray("prefs-x")).toEqual([]);
  });

  it("cita valjani niz stringova", () => {
    localStorage.setItem("prefs-x", JSON.stringify(["Cuba", "Nicaragua"]));
    expect(readJsonStringArray("prefs-x")).toEqual(["Cuba", "Nicaragua"]);
  });

  it("ignorira pokvaren JSON", () => {
    localStorage.setItem("prefs-x", "{not-json");
    expect(readJsonStringArray("prefs-x")).toEqual([]);
  });

  it("ignorira JSON koji nije niz", () => {
    localStorage.setItem("prefs-x", JSON.stringify({ a: 1 }));
    expect(readJsonStringArray("prefs-x")).toEqual([]);
  });

  it("izbacuje ne-string clanove", () => {
    localStorage.setItem("prefs-x", JSON.stringify(["ok", 2, null, "yes"]));
    expect(readJsonStringArray("prefs-x")).toEqual(["ok", "yes"]);
  });
});

describe("resolveLang", () => {
  it("prihvaca hr i en", () => {
    expect(resolveLang("hr")).toBe("hr");
    expect(resolveLang("en")).toBe("en");
  });

  it("pada na hr za null, prazno i nepoznato", () => {
    expect(resolveLang(null)).toBe("hr");
    expect(resolveLang("")).toBe("hr");
    expect(resolveLang("de")).toBe("hr");
    expect(resolveLang("HR")).toBe("hr");
  });
});

describe("normalizeCollectionPayload", () => {
  it("odbija null i ne-objekt", () => {
    expect(normalizeCollectionPayload(null)).toBeNull();
    expect(normalizeCollectionPayload("x")).toBeNull();
    expect(normalizeCollectionPayload(1)).toBeNull();
  });

  it("prihvaca prazan valjani oblik", () => {
    expect(normalizeCollectionPayload({})).toEqual({ items: {}, journal: [] });
  });

  it("odbija items koji nisu objekt-zapis", () => {
    expect(normalizeCollectionPayload({ items: [], journal: [] })).toBeNull();
    expect(normalizeCollectionPayload({ items: "x", journal: [] })).toBeNull();
  });

  it("odbija journal koji nije niz", () => {
    expect(normalizeCollectionPayload({ items: {}, journal: {} })).toBeNull();
  });

  it("normalizira stavke i odbacuje neispravne kljuceve journala", () => {
    const out = normalizeCollectionPayload({
      items: {
        "cig-1": {
          owned: true,
          tried: "yes",
          wishlist: 1,
          rating: 8,
          note: "  ok  ",
        },
        bad: "nope",
      },
      journal: [
        {
          id: "j1",
          date: "2026-01-01",
          cigarId: "cig-1",
          drinkId: "rum-1",
          rating: 7,
          note: "fine",
        },
        { id: 1, date: "x", cigarId: "a", drinkId: "b" },
        "trash",
      ],
    });
    expect(out).toEqual({
      items: {
        "cig-1": {
          owned: true,
          tried: false,
          wishlist: false,
          rating: 8,
          note: "ok",
        },
      },
      journal: [
        {
          id: "j1",
          date: "2026-01-01",
          cigarId: "cig-1",
          drinkId: "rum-1",
          rating: 7,
          note: "fine",
        },
      ],
    });
  });

  it("odbija rating izvan 1-10", () => {
    const out = normalizeCollectionPayload({
      items: { a: { owned: true, tried: false, wishlist: false, rating: 99, note: "" } },
      journal: [],
    });
    expect(out?.items.a.rating).toBeNull();
  });

  it("prihvaca solo zapis (drinkId null ili nedostaje)", () => {
    const out = normalizeCollectionPayload({
      items: {},
      journal: [
        {
          id: "j-solo",
          date: "2026-07-30",
          cigarId: "cig-1",
          drinkId: null,
          rating: 8,
          note: "solo",
        },
        {
          id: "j-missing",
          date: "2026-07-30",
          cigarId: "cig-2",
          rating: null,
          note: "",
        },
      ],
    });
    expect(out?.journal).toEqual([
      {
        id: "j-solo",
        date: "2026-07-30",
        cigarId: "cig-1",
        drinkId: null,
        rating: 8,
        note: "solo",
      },
      {
        id: "j-missing",
        date: "2026-07-30",
        cigarId: "cig-2",
        drinkId: null,
        rating: null,
        note: "",
      },
    ]);
  });
});
