// @vitest-environment jsdom
import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// Service worker nije predmet ovog testa; virtualni modul plugina zamjenjujemo
// mirnom kukom da render ne ovisi o registraciji SW-a.
vi.mock("virtual:pwa-register/react", () => ({
  useRegisterSW: () => ({
    needRefresh: [false, () => {}],
    offlineReady: [false, () => {}],
    updateServiceWorker: () => Promise.resolve(),
  }),
}));

/**
 * Traka mora reagirati na SVAKI store, ne samo na kolekciju: kvota
 * localStoragea je zajednička, pa humidor zna pasti prvi.
 */
describe("SystemBanners — upozorenje o spremanju", () => {
  beforeEach(() => {
    vi.resetModules();
    localStorage.clear();
  });
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  /** Odbij zapis samo za zadani ključ, ostale pusti. */
  const breakKey = (key: string) => {
    const real = Storage.prototype.setItem;
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(function (
      this: Storage,
      k: string,
      v: string,
    ) {
      if (k === key) throw new DOMException("QuotaExceededError");
      return real.call(this, k, v);
    });
  };

  const renderBanners = async () => {
    const { SystemBanners } = await import("./SystemBanners");
    const { I18nProvider } = await import("../i18n");
    render(
      <I18nProvider>
        <SystemBanners />
      </I18nProvider>,
    );
  };

  it("šuti dok su svi zapisi prošli", async () => {
    await renderBanners();
    expect(screen.queryByText(/Spremanje nije uspjelo/)).toBeNull();
  });

  it.each([
    [
      "cigar-pairing-collection-v1",
      "kolekcija",
      async () => (await import("../store/collection")).updateItem("cig-x", { rating: 8 }),
    ],
    [
      "cigar-pairing-humidors-v1",
      "humidor",
      async () => (await import("../store/humidor")).addHumidor("Radni humidor"),
    ],
    [
      "cigar-pairing-favorite-brands-v1",
      "omiljene marke",
      async () =>
        (await import("../store/favorites")).toggleFavoriteBrand("cigar", "Bolivar"),
    ],
    ["market", "regija", async () => (await import("../store/market")).setMarket("EU")],
  ])("podigne se kad padne zapis u %s (%s)", async (key, _label, write) => {
    breakKey(key);
    await renderBanners();
    expect(screen.queryByText(/Spremanje nije uspjelo/)).toBeNull();
    await write();
    expect(await screen.findByText(/Spremanje nije uspjelo/)).toBeTruthy();
  });
});
