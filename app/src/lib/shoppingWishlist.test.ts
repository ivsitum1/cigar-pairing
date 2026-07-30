import { describe, expect, it } from "vitest";
import { isShoppingWishlistItem } from "./shoppingWishlist";

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
