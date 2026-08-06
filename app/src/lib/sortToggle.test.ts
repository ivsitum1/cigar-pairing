import { describe, expect, it } from "vitest";
import { cycleSort, directedComparator, sortArrow } from "./sortToggle";

type Key = "price" | "quality";

describe("cycleSort", () => {
  it("prvi klik uključuje zadani smjer", () => {
    expect(cycleSort<Key>(null, "price", "asc")).toEqual({ key: "price", dir: "asc" });
    expect(cycleSort<Key>(null, "quality", "desc")).toEqual({
      key: "quality",
      dir: "desc",
    });
  });

  it("drugi klik okreće smjer, treći gasi sortiranje", () => {
    const first = cycleSort<Key>(null, "price", "asc");
    const second = cycleSort<Key>(first, "price", "asc");
    expect(second).toEqual({ key: "price", dir: "desc" });
    expect(cycleSort<Key>(second, "price", "asc")).toBeNull();
  });

  it("klik na drugi ključ počinje ispočetka, ne nastavlja ciklus", () => {
    const price = { key: "price", dir: "desc" } as const;
    expect(cycleSort<Key>(price, "quality", "desc")).toEqual({
      key: "quality",
      dir: "desc",
    });
  });
});

describe("sortArrow", () => {
  it("strelicu nosi samo aktivni ključ i prati smjer", () => {
    expect(sortArrow<Key>({ key: "price", dir: "asc" }, "price")).toBe(" ↑");
    expect(sortArrow<Key>({ key: "price", dir: "desc" }, "price")).toBe(" ↓");
    expect(sortArrow<Key>({ key: "price", dir: "asc" }, "quality")).toBe("");
    expect(sortArrow<Key>(null, "price")).toBe("");
  });
});

describe("directedComparator", () => {
  const asc = (a: number, b: number) => a - b;

  it("zadani smjer ostavlja komparator kakav jest", () => {
    expect([3, 1, 2].sort(directedComparator(asc, "asc", "asc"))).toEqual([1, 2, 3]);
  });

  it("suprotan smjer ga obrće", () => {
    expect([3, 1, 2].sort(directedComparator(asc, "asc", "desc"))).toEqual([3, 2, 1]);
  });
});
