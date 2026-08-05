import { beforeEach, describe, expect, it, vi } from "vitest";

const lineState = vi.fn();
const lineTotalStock = vi.fn();

vi.mock("../store/collection", () => ({
  lineState: (...args: unknown[]) => lineState(...args),
}));

vi.mock("../store/humidor", () => ({
  lineTotalStock: (...args: unknown[]) => lineTotalStock(...args),
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
    lineState.mockReset();
    lineTotalStock.mockReset();
    lineState.mockReturnValue(state());
    lineTotalStock.mockReturnValue(0);
  });

  it("nudi listu zelja kad je zaliha pala na nulu", async () => {
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-1@churchill")).toBe(true);
    expect(lineTotalStock).toHaveBeenCalledWith("cig-1");
  });

  it("suti kad je jos ima u nekom humidoru", async () => {
    lineTotalStock.mockReturnValue(3);
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-1")).toBe(false);
  });

  it("suti kad je vec na listi zelja", async () => {
    lineState.mockReturnValue(state({ wishlist: true }));
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-1")).toBe(false);
  });

  it("suti kad nista nije skinuto iz humidora", async () => {
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist(null)).toBe(false);
    expect(lineTotalStock).not.toHaveBeenCalled();
  });
});
