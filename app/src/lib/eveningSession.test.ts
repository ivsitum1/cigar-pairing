import { beforeEach, describe, expect, it, vi } from "vitest";

const addJournalEntry = vi.fn();
const getItemState = vi.fn();
const updateItem = vi.fn();
const consumeFromStock = vi.fn();
const totalStock = vi.fn();
const stockForItemKey = vi.fn();

vi.mock("../store/collection", () => ({
  addJournalEntry: (...args: unknown[]) => addJournalEntry(...args),
  getItemState: (...args: unknown[]) => getItemState(...args),
  updateItem: (...args: unknown[]) => updateItem(...args),
}));

vi.mock("../store/humidor", () => ({
  consumeFromStock: (...args: unknown[]) => consumeFromStock(...args),
  totalStock: (...args: unknown[]) => totalStock(...args),
  stockForItemKey: (...args: unknown[]) => stockForItemKey(...args),
}));

describe("logEveningSession", () => {
  beforeEach(() => {
    addJournalEntry.mockReset();
    getItemState.mockReset();
    updateItem.mockReset();
    consumeFromStock.mockReset();
    totalStock.mockReset();
    stockForItemKey.mockReset();
    stockForItemKey.mockReturnValue(0);
    getItemState.mockReturnValue({
      owned: false,
      tried: false,
      wishlist: false,
      rating: null,
      note: "",
    });
    consumeFromStock.mockReturnValue({ humidorId: "hum-1", itemId: "cig-1" });
    totalStock.mockReturnValue(0);
  });

  it("zapisuje dnevnik i oznacava obje stavke kao probane", async () => {
    const { logEveningSession } = await import("./eveningSession");
    const result = logEveningSession({
      cigarId: "cig-1",
      drinkId: "rum-1",
      rating: 8,
      note: "  lijepa vecer  ",
    });
    expect(addJournalEntry).toHaveBeenCalledWith({
      cigarId: "cig-1",
      drinkId: "rum-1",
      rating: 8,
      note: "lijepa vecer",
    });
    expect(updateItem).toHaveBeenCalledWith("cig-1", { tried: true });
    expect(updateItem).toHaveBeenCalledWith("rum-1", { tried: true });
    expect(result).toEqual({
      consumed: true,
      consumedItemId: "cig-1",
      stockAfter: 0,
      releasedOwned: false,
    });
  });

  it("solo: drinkId null, ne oznacava pice", async () => {
    const { logEveningSession } = await import("./eveningSession");
    logEveningSession({
      cigarId: "cig-1",
      drinkId: null,
      rating: 7,
      note: "solo",
    });
    expect(addJournalEntry).toHaveBeenCalledWith({
      cigarId: "cig-1",
      drinkId: null,
      rating: 7,
      note: "solo",
    });
    expect(updateItem).toHaveBeenCalledWith("cig-1", { tried: true });
    expect(updateItem).not.toHaveBeenCalledWith("rum-1", expect.anything());
    expect(updateItem).toHaveBeenCalledTimes(1);
  });

  it("ne dira tried kad je markTried false", async () => {
    const { logEveningSession } = await import("./eveningSession");
    logEveningSession({
      cigarId: "cig-1",
      drinkId: "rum-1",
      rating: null,
      note: "",
      markTried: false,
    });
    expect(addJournalEntry).toHaveBeenCalled();
    expect(updateItem).not.toHaveBeenCalled();
  });

  it("ne ponavlja updateItem ako je vec tried", async () => {
    getItemState.mockImplementation((id: string) => ({
      owned: false,
      tried: id === "cig-1",
      wishlist: false,
      rating: null,
      note: "",
    }));
    const { logEveningSession } = await import("./eveningSession");
    logEveningSession({
      cigarId: "cig-1",
      drinkId: "rum-1",
      rating: 7,
      note: "ok",
    });
    expect(updateItem).toHaveBeenCalledTimes(1);
    expect(updateItem).toHaveBeenCalledWith("rum-1", { tried: true });
  });

  it("skida popusenu cigaru iz zalihe humidora", async () => {
    const { logEveningSession } = await import("./eveningSession");
    logEveningSession({
      cigarId: "cig-1@churchill",
      drinkId: "rum-1",
      rating: 9,
      note: "",
    });
    expect(consumeFromStock).toHaveBeenCalledWith("cig-1@churchill");
  });

  it("zaliha se broji na kljucu koji je stvarno skinut", async () => {
    // zapis nosi vitolu, humidor zalihu vodi po liniji
    consumeFromStock.mockReturnValue({ humidorId: "hum-1", itemId: "cig-1" });
    totalStock.mockImplementation((id: string) => (id === "cig-1" ? 2 : 0));
    const { logEveningSession } = await import("./eveningSession");
    const result = logEveningSession({
      cigarId: "cig-1@churchill",
      drinkId: null,
      rating: null,
      note: "",
    });
    expect(totalStock).toHaveBeenCalledWith("cig-1");
    expect(result).toEqual({
      consumed: true,
      consumedItemId: "cig-1",
      stockAfter: 2,
      releasedOwned: false,
    });
  });

  it("ne dira zalihu kad consumeStock nije trazen", async () => {
    consumeFromStock.mockReturnValue(null);
    totalStock.mockReturnValue(3);
    const { logEveningSession } = await import("./eveningSession");
    const result = logEveningSession({
      cigarId: "cig-1",
      drinkId: "rum-1",
      rating: null,
      note: "",
      consumeStock: false,
    });
    expect(consumeFromStock).not.toHaveBeenCalled();
    expect(result).toEqual({
      consumed: false,
      consumedItemId: null,
      stockAfter: 3,
      releasedOwned: false,
    });
  });

  it("vraca consumed false kad nema zalihe", async () => {
    consumeFromStock.mockReturnValue(null);
    totalStock.mockReturnValue(0);
    const { logEveningSession } = await import("./eveningSession");
    const result = logEveningSession({
      cigarId: "cig-1",
      drinkId: null,
      rating: null,
      note: "",
    });
    expect(result).toEqual({
      consumed: false,
      consumedItemId: null,
      stockAfter: 0,
      releasedOwned: false,
    });
  });

  it("popusena zadnja gasi oznaku „Imam”", async () => {
    getItemState.mockReturnValue({
      owned: true,
      tried: true,
      wishlist: false,
      rating: null,
      note: "",
    });
    stockForItemKey.mockReturnValue(0);
    const { logEveningSession } = await import("./eveningSession");
    const result = logEveningSession({
      cigarId: "cig-1@toro",
      drinkId: null,
      rating: null,
      note: "",
    });
    expect(result.releasedOwned).toBe(true);
    expect(updateItem).toHaveBeenCalledWith("cig-1", { owned: false });
  });

  it("dok jos ima zalihe „Imam” ostaje", async () => {
    getItemState.mockReturnValue({
      owned: true,
      tried: true,
      wishlist: false,
      rating: null,
      note: "",
    });
    stockForItemKey.mockReturnValue(2);
    const { logEveningSession } = await import("./eveningSession");
    const result = logEveningSession({
      cigarId: "cig-1@toro",
      drinkId: null,
      rating: null,
      note: "",
    });
    expect(result.releasedOwned).toBe(false);
    expect(updateItem).not.toHaveBeenCalledWith("cig-1", { owned: false });
  });
});
