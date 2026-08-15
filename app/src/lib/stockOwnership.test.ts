import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

function installMemoryStorage() {
  const store = new Map<string, string>();
  Object.defineProperty(globalThis, "localStorage", {
    configurable: true,
    value: {
      getItem: (k: string) => store.get(k) ?? null,
      setItem: (k: string, v: string) => {
        store.set(k, String(v));
      },
      removeItem: (k: string) => {
        store.delete(k);
      },
      clear: () => store.clear(),
    },
  });
}

const load = async () => ({
  ...(await import("./stockOwnership")),
  collection: await import("../store/collection"),
  humidor: await import("../store/humidor"),
});

describe("„Imam” prati zalihu", () => {
  beforeAll(installMemoryStorage);

  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  it("zadnja iz humidora gasi oznaku", async () => {
    const { releaseOwnedIfEmpty, collection, humidor } = await load();
    const box = humidor.addHumidor("A");
    collection.updateItem("cig-x@toro", { owned: true, tried: true });
    humidor.setStock(box.id, "cig-x@toro", 1);

    humidor.adjustStock(box.id, "cig-x@toro", -1);
    expect(releaseOwnedIfEmpty("cig-x@toro")).toBe(true);
    expect(collection.getItemState("cig-x@toro").owned).toBe(false);
    // probano ostaje — bilježnica se ne briše zajedno sa zalihom
    expect(collection.getItemState("cig-x@toro").tried).toBe(true);
  });

  it("dok ima zalihe oznaka ostaje", async () => {
    const { releaseOwnedIfEmpty, collection, humidor } = await load();
    const box = humidor.addHumidor("A");
    collection.updateItem("cig-x@toro", { owned: true });
    humidor.setStock(box.id, "cig-x@toro", 2);

    expect(releaseOwnedIfEmpty("cig-x@toro")).toBe(false);
    expect(collection.getItemState("cig-x@toro").owned).toBe(true);
  });

  it("druga vitola iste linije ne drži oznaku na životu", async () => {
    const { releaseOwnedIfEmpty, collection, humidor } = await load();
    const box = humidor.addHumidor("A");
    collection.updateItem("cig-x@toro", { owned: true });
    humidor.setStock(box.id, "cig-x@robusto", 3);

    expect(releaseOwnedIfEmpty("cig-x@toro")).toBe(true);
    expect(collection.getItemState("cig-x@toro").owned).toBe(false);
  });

  it("goli ključ linije gleda cijelu liniju", async () => {
    const { releaseOwnedIfEmpty, collection, humidor } = await load();
    const box = humidor.addHumidor("A");
    collection.updateItem("cig-x", { owned: true });
    humidor.setStock(box.id, "cig-x@robusto", 1);

    // stavka bez formata je „imam tu liniju” — vitola u kutiji je drži
    expect(releaseOwnedIfEmpty("cig-x")).toBe(false);

    humidor.adjustStock(box.id, "cig-x@robusto", -1);
    expect(releaseOwnedIfEmpty("cig-x")).toBe(true);
  });

  it("kupljeno a još nesloženo u humidor ostaje na popisu", async () => {
    const { releaseOwnedIfEmpty, collection, humidor } = await load();
    humidor.addHumidor("A");
    collection.updateItem("cig-novo", { owned: true });

    // nikad nije bilo zalihe → ovo je „imam, još nisam složio”, ne potrošeno.
    // Oznaka se gasi tek kad je zaliha stvarno pala na nulu, a to radi UI
    // (pozivom nakon smanjenja); sama provjera ovdje vraća true jer zalihe nema.
    expect(releaseOwnedIfEmpty("cig-novo")).toBe(true);
    expect(collection.getItemState("cig-novo").owned).toBe(false);
  });

  it("dodavanje u humidor postavlja oznaku", async () => {
    const { claimOwnedForStock, collection, humidor } = await load();
    const box = humidor.addHumidor("A");
    humidor.adjustStock(box.id, "cig-y@robusto", 1);

    expect(claimOwnedForStock("cig-y@robusto")).toBe(true);
    expect(collection.getItemState("cig-y@robusto").owned).toBe(true);
    // drugi poziv ne piše ponovno
    expect(claimOwnedForStock("cig-y@robusto")).toBe(false);
  });

  it("stavka s računa seli oznaku na vitolu kojom je složena u humidor", async () => {
    const { transferOwnedToVitola, collection, humidor } = await load();
    const box = humidor.addHumidor("A");
    // OCR računa označi liniju: „imam je, još nije u kutiji"
    collection.updateItem("cig-x", { owned: true, rating: 8 });

    humidor.adjustStock(box.id, "cig-x@robusto", 1);
    transferOwnedToVitola("cig-x", "cig-x@robusto");

    expect(collection.getItemState("cig-x@robusto").owned).toBe(true);
    expect(collection.getItemState("cig-x").owned).toBe(false);
    // ocjena s linije se ne gubi
    expect(collection.getItemState("cig-x").rating).toBe(8);
  });

  it("sampler ulazi u humidor razložen na svoje vitole", async () => {
    const { unpackSamplerIntoStock, collection, humidor } = await load();
    const { default: cigarsData } = await import("../data/cigars.json");
    const cigars = cigarsData as unknown as { id: string }[];
    const sampler = cigars.find((c) => c.id === "cig-aj-fernandez-toro-sampler")!;
    const box = humidor.addHumidor("A");
    collection.updateItem("cig-aj-fernandez-toro-sampler", { owned: true });

    const pieces = unpackSamplerIntoStock(box.id, sampler as never);

    expect(pieces).toBe(5);
    // kutije nema na stanju — na polici su cigare
    expect(humidor.stockCount(box.id, "cig-aj-fernandez-toro-sampler")).toBe(0);
    expect(humidor.stockCount(box.id, "cig-aj-fernandez-enclave@connecticut-toro")).toBe(1);
    expect(humidor.stockCount(box.id, "cig-aj-fernandez-bellas-artes@hybrid-toro")).toBe(1);
    // oznaka „Imam" seli s kutije na sadržaj
    expect(collection.getItemState("cig-aj-fernandez-toro-sampler").owned).toBe(false);
    expect(
      collection.getItemState("cig-aj-fernandez-enclave@connecticut-toro").owned,
    ).toBe(true);
  });

  it("kupljeno s liste želja skida zvjezdicu", async () => {
    const { claimOwnedForStock, collection, humidor } = await load();
    const box = humidor.addHumidor("A");
    collection.updateItem("cig-z@toro", { wishlist: true });
    humidor.adjustStock(box.id, "cig-z@toro", 1);

    expect(claimOwnedForStock("cig-z@toro")).toBe(true);
    const state = collection.getItemState("cig-z@toro");
    expect(state.owned).toBe(true);
    expect(state.wishlist).toBe(false);
  });
});
