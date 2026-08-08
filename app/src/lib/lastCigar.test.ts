import { beforeEach, describe, expect, it, vi } from "vitest";

const getItemState = vi.fn();
const lineTotalStock = vi.fn();
const totalStock = vi.fn();

vi.mock("../store/collection", () => ({
  getItemState: (...args: unknown[]) => getItemState(...args),
}));

vi.mock("../store/humidor", () => ({
  lineTotalStock: (...args: unknown[]) => lineTotalStock(...args),
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
    lineTotalStock.mockReset();
    totalStock.mockReset();
    getItemState.mockReturnValue(state());
    lineTotalStock.mockReturnValue(0);
    totalStock.mockReturnValue(0);
  });

  it("nudi listu zelja kad je zaliha vitole pala na nulu", async () => {
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-1@churchill")).toBe(true);
    expect(totalStock).toHaveBeenCalledWith("cig-1@churchill");
  });

  it("nudi listu zelja i kad druga vitola iste linije jos stoji u humidoru", async () => {
    // serija Cusano: Figurado potrosen, Robusto ostao — to su dva proizvoda
    totalStock.mockReturnValue(0);
    lineTotalStock.mockReturnValue(4);
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-cusano@figurado")).toBe(true);
    expect(lineTotalStock).not.toHaveBeenCalled();
  });

  it("goli kljuc linije gleda cijelu liniju", async () => {
    lineTotalStock.mockReturnValue(3);
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-1")).toBe(false);
    expect(lineTotalStock).toHaveBeenCalledWith("cig-1");
  });

  it("suti kad je jos ima tog formata", async () => {
    totalStock.mockReturnValue(2);
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-1@churchill")).toBe(false);
  });

  it("suti kad je vitola vec na listi zelja", async () => {
    getItemState.mockImplementation((id: string) =>
      state({ wishlist: id === "cig-1@churchill" }),
    );
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-1@churchill")).toBe(false);
  });

  it("suti kad je cijela linija vec na listi zelja", async () => {
    getItemState.mockImplementation((id: string) => state({ wishlist: id === "cig-1" }));
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist("cig-1@churchill")).toBe(false);
  });

  it("suti kad nista nije skinuto iz humidora", async () => {
    const { shouldOfferWishlist } = await import("./lastCigar");
    expect(shouldOfferWishlist(null)).toBe(false);
    expect(totalStock).not.toHaveBeenCalled();
    expect(lineTotalStock).not.toHaveBeenCalled();
  });
});
