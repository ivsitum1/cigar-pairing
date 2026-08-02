import { beforeEach, describe, expect, it, vi } from "vitest";

const getItemState = vi.fn();
const totalStock = vi.fn();

vi.mock("../store/collection", () => ({
  getItemState: (...args: unknown[]) => getItemState(...args),
}));

vi.mock("../store/humidor", () => ({
  totalStock: (...args: unknown[]) => totalStock(...args),
}));

const state = (over: Partial<{ wishlist: boolean }> = {}) => ({
  owned: false,
  tried: false,
  wishlist: false,
  rating: null,
  note: "",
  ...over,
});

describe("shouldOfferWishlist", () => {
  beforeEach(() => {
    getItemState.mockReset();
    totalStock.mockReset();
    getItemState.mockReturnValue(state());
    totalStock.mockReturnValue(0);
  });

  it("nudi listu zelja kad je zaliha pala na nulu", async () => {
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-1@churchill")).toBe(true);
    expect(totalStock).toHaveBeenCalledWith("cig-1@churchill");
  });

  it("suti kad je jos ima u nekom humidoru", async () => {
    totalStock.mockReturnValue(3);
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-1")).toBe(false);
  });

  it("suti kad je vec na listi zelja", async () => {
    getItemState.mockReturnValue(state({ wishlist: true }));
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-1")).toBe(false);
  });

  it("suti kad nista nije skinuto iz humidora", async () => {
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist(null)).toBe(false);
    expect(totalStock).not.toHaveBeenCalled();
  });
});
