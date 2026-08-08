import { describe, expect, it } from "vitest";
import {
  isShoppingWishlistItem,
  shoppingWishlistLineIds,
} from "./shoppingWishlist";

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

describe("shoppingWishlistLineIds", () => {
  const item = (over: Partial<typeof base> = {}) => ({ ...base, ...over });
  const noStock = { item: () => 0, line: () => 0 };

  it("vraca liniju kljuca vitole", () => {
    const ids = shoppingWishlistLineIds({ "cig-1@churchill": item() }, noStock);
    expect([...ids]).toEqual(["cig-1"]);
  });

  it("drzi na popisu potrosenu vitolu dok druga iz linije jos ima zalihu", () => {
    // Cusano: Figurado potrosen (owned), Robusto ostao u humidoru
    const ids = shoppingWishlistLineIds(
      {
        "cig-cusano@figurado": item({ owned: true }),
        "cig-cusano@robusto": item({ owned: true, wishlist: false }),
      },
      {
        item: (id) => (id === "cig-cusano@robusto" ? 5 : 0),
        line: () => 5,
      },
    );
    expect([...ids]).toEqual(["cig-cusano"]);
  });

  it("skriva vitolu koja jos ima svoju zalihu", () => {
    const ids = shoppingWishlistLineIds(
      { "cig-1@churchill": item({ owned: true }) },
      { item: () => 2, line: () => 2 },
    );
    expect(ids.size).toBe(0);
  });

  it("„Imam” s druge vitole vrijedi za cijelu liniju", () => {
    // zelja na goloj liniji + zaliha te linije = nije restock
    const ids = shoppingWishlistLineIds(
      {
        "cig-1": item(),
        "cig-1@robusto": item({ owned: true, wishlist: false }),
      },
      { item: () => 3, line: () => 3 },
    );
    expect(ids.size).toBe(0);
  });

  it("preskace stavke bez liste zelja", () => {
    const ids = shoppingWishlistLineIds(
      { "cig-1@churchill": item({ wishlist: false }) },
      noStock,
    );
    expect(ids.size).toBe(0);
  });
});
