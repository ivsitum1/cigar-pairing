import { describe, expect, it } from "vitest";
import { isRestockItem, isShoppingWishlistItem } from "./shoppingWishlist";

const base = {
  owned: false,
  tried: false,
  wishlist: true,
  rating: null as number | null,
  note: "",
};

describe("isShoppingWishlistItem", () => {
  it("prikazuje neposedovanu listu zelja", () => {
    expect(isShoppingWishlistItem(base, 0)).toBe(true);
    expect(isShoppingWishlistItem(base, 5)).toBe(true);
  });

  it("prikazuje owned restock kad je zaliha 0", () => {
    expect(isShoppingWishlistItem({ ...base, owned: true }, 0)).toBe(true);
  });

  it("skriva owned kad jos ima zalihe", () => {
    expect(isShoppingWishlistItem({ ...base, owned: true }, 2)).toBe(false);
  });

  it("skriva bez wishlist", () => {
    expect(isShoppingWishlistItem({ ...base, wishlist: false }, 0)).toBe(false);
  });
});

describe("isRestockItem", () => {
  it("dopuna je samo ono sto imas, a zalihe nema", () => {
    expect(isRestockItem({ ...base, owned: true }, 0)).toBe(true);
  });

  it("neposedovana zelja nije dopuna — to je drugi popis", () => {
    expect(isRestockItem(base, 0)).toBe(false);
  });

  it("owned sa zalihom nije ni jedno ni drugo", () => {
    expect(isRestockItem({ ...base, owned: true }, 3)).toBe(false);
  });

  it("dva popisa zajedno daju tocno ono sto ide na Kupovinu", () => {
    const cases = [
      { s: base, stock: 0 },
      { s: base, stock: 4 },
      { s: { ...base, owned: true }, stock: 0 },
      { s: { ...base, owned: true }, stock: 2 },
      { s: { ...base, wishlist: false }, stock: 0 },
      { s: { ...base, wishlist: false, owned: true }, stock: 0 },
    ];
    for (const { s, stock } of cases) {
      const pure = s.wishlist && !s.owned;
      expect(pure || isRestockItem(s, stock)).toBe(isShoppingWishlistItem(s, stock));
    }
  });
});
