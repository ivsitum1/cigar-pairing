import { beforeEach, describe, expect, it, vi } from "vitest";

const addJournalEntry = vi.fn();
const getItemState = vi.fn();
const updateItem = vi.fn();

vi.mock("../store/collection", () => ({
  addJournalEntry: (...args: unknown[]) => addJournalEntry(...args),
  getItemState: (...args: unknown[]) => getItemState(...args),
  updateItem: (...args: unknown[]) => updateItem(...args),
}));

describe("logEveningSession", () => {
  beforeEach(() => {
    addJournalEntry.mockReset();
    getItemState.mockReset();
    updateItem.mockReset();
    getItemState.mockReturnValue({
      owned: false,
      tried: false,
      wishlist: false,
      rating: null,
      note: "",
    });
  });

  it("zapisuje dnevnik i oznacava obje stavke kao probane", async () => {
    const { logEveningSession } = await import("./eveningSession");
    logEveningSession({
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
});
