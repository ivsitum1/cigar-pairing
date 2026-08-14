import { describe, expect, it } from "vitest";
import { dedupeCollectionCigarIds } from "./cigarItemId";
import {
  ownedWithoutStockIds,
  shortlistItemIds,
} from "./collectionPanels";
import type { ItemState } from "../store/collection";

const blank = (patch: Partial<ItemState> = {}): ItemState => ({
  owned: false,
  tried: false,
  wishlist: false,
  rating: null,
  note: "",
  ...patch,
});

describe("dedupeCollectionCigarIds", () => {
  it("sakriva goli id linije kad postoji scoped vitola", () => {
    expect(
      dedupeCollectionCigarIds([
        "cig-oliva-serie-v",
        "cig-oliva-serie-v@torpedo",
        "cig-oliva-serie-v-melanio",
      ]),
    ).toEqual(["cig-oliva-serie-v@torpedo", "cig-oliva-serie-v-melanio"]);
  });

  it("zadrzava goli id kad nema scoped siblinga", () => {
    expect(dedupeCollectionCigarIds(["cig-oliva-serie-v", "cig-other"])).toEqual([
      "cig-oliva-serie-v",
      "cig-other",
    ]);
  });
});

describe("collectionPanels filters", () => {
  it("shortlist iskljucuje owned i wishlist", () => {
    const items: Record<string, ItemState> = {
      a: blank({ tried: true }),
      b: blank({ owned: true, tried: true }),
      c: blank({ wishlist: true, tried: true }),
      d: blank({ rating: 8 }),
      e: blank({ note: "ok" }),
    };
    expect(shortlistItemIds(items).sort()).toEqual(["a", "d", "e"]);
  });

  it("ownedWithoutStock gleda zalihu po kljucu", () => {
    const items: Record<string, ItemState> = {
      "cig-x@robusto": blank({ owned: true }),
      "cig-y@churchill": blank({ owned: true }),
      "cig-z": blank({ tried: true }),
    };
    const stock = (id: string) => (id === "cig-x@robusto" ? 2 : 0);
    expect(ownedWithoutStockIds(items, stock)).toEqual(["cig-y@churchill"]);
  });

  it("stavka s racuna (goli id linije) nestaje kad linija dobije zalihu", () => {
    // OCR racuna daje id linije; u humidor stavka ulazi pod vitolom, pa
    // brojac mora biti onaj koji goli kljuc razumije kao „cijela linija"
    const items: Record<string, ItemState> = { "cig-x": blank({ owned: true }) };
    const lineAware = (id: string) => (id === "cig-x" ? 3 : 0);
    const exactOnly = (id: string) => (id === "cig-x@robusto" ? 3 : 0);

    expect(ownedWithoutStockIds(items, lineAware)).toEqual([]);
    // s brojacem koji gleda samo tocan kljuc stavka bi zauvijek ostala na popisu
    expect(ownedWithoutStockIds(items, exactOnly)).toEqual(["cig-x"]);
  });
});
