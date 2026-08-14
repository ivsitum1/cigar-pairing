// Regresija na stvarnim podacima: humidor, kartica cigare i zapis večeri moraju
// govoriti o istom ključu.
//
// Simptom koji ovo hvata: u humidoru stoji 6 komada linije, otvoriš cigaru,
// izabereš Robusto i dolje uz „Zapiši večer” piše stanje 0 — jer je zaliha
// sjedila na golom ključu linije (`cig-x`), a kartica broji ključ vitole
// (`cig-x@robusto`).
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { cigarById, cigarForItemId } from "../data";
import { cigarItemId } from "../lib/cigarItemId";
import { applyVitola, uniqueVitolas } from "../lib/cigarVitola";
import {
  stockNeedsVitola,
  stockVitolaName,
  vitolaStockId,
} from "../lib/humidorVitola";

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

const load = () => import("./humidor");

// linija s više formata iz živog kataloga
const LINE_ID = "cig-1502-xo";

describe("humidor prati vitole (stvarni katalog)", () => {
  beforeAll(installMemoryStorage);

  beforeEach(() => {
    localStorage.clear();
    vi.resetModules();
  });

  const line = () => {
    const c = cigarById(LINE_ID);
    if (!c) throw new Error(`test traži liniju ${LINE_ID}`);
    return c;
  };

  it("svaka vitola ima svoju zalihu i svoj broj", async () => {
    const h = await load();
    const box = h.addHumidor("Radni stol");
    const [a, b, c] = uniqueVitolas(line());

    h.setStock(box.id, vitolaStockId(line(), a), 3);
    h.setStock(box.id, vitolaStockId(line(), b), 2);
    h.setStock(box.id, vitolaStockId(line(), c), 1);

    expect(h.stockCount(box.id, vitolaStockId(line(), a))).toBe(3);
    expect(h.stockCount(box.id, vitolaStockId(line(), b))).toBe(2);
    expect(h.stockCount(box.id, vitolaStockId(line(), c))).toBe(1);
    expect(h.lineTotalStock(LINE_ID)).toBe(6);
  });

  it("kartica odabrane vitole pokazuje njezino stanje, ne nulu", async () => {
    const h = await load();
    const box = h.addHumidor("Radni stol");
    const vitola = uniqueVitolas(line())[1];

    h.setStock(box.id, vitolaStockId(line(), vitola), 3);

    // ono što DetailSheet drži u rukama nakon odabira vitole
    const shown = applyVitola(line(), vitola);
    const itemId = cigarItemId(shown);

    expect(itemId).toBe(vitolaStockId(line(), vitola));
    expect(h.totalStock(itemId)).toBe(3);
    expect(stockNeedsVitola(shown, itemId)).toBe(false);
  });

  it("zapis večeri skida baš tu vitolu", async () => {
    const h = await load();
    const box = h.addHumidor("Radni stol");
    const [a, b] = uniqueVitolas(line());
    const aId = vitolaStockId(line(), a);
    const bId = vitolaStockId(line(), b);

    h.setStock(box.id, aId, 3);
    h.setStock(box.id, bId, 2);

    expect(h.consumeFromStock(bId)).toEqual({ humidorId: box.id, itemId: bId });
    expect(h.stockCount(box.id, bId)).toBe(1);
    expect(h.stockCount(box.id, aId)).toBe(3);
  });

  it("stara zaliha po liniji se vidi kao neodređena i razrješava se u jednom potezu", async () => {
    const h = await load();
    const box = h.addHumidor("Radni stol");
    h.setStock(box.id, LINE_ID, 3); // zapis iz doba kad se brojala linija

    const shownLine = cigarForItemId(LINE_ID)!;
    expect(stockNeedsVitola(shownLine, LINE_ID)).toBe(true);
    expect(stockVitolaName(shownLine, LINE_ID)).toBeNull();

    const vitola = uniqueVitolas(line())[0];
    h.moveStock(box.id, LINE_ID, vitolaStockId(line(), vitola));

    expect(h.stockCount(box.id, LINE_ID)).toBe(0);
    expect(h.stockCount(box.id, vitolaStockId(line(), vitola))).toBe(3);
    expect(stockVitolaName(shownLine, vitolaStockId(line(), vitola))).toBe(vitola.name);
  });

  it("zaliha jedne vitole ne pokriva drugu vitolu iste linije", async () => {
    const h = await load();
    const box = h.addHumidor("Radni stol");
    const [a, b, c] = uniqueVitolas(line());

    h.setStock(box.id, vitolaStockId(line(), a), 2);
    h.setStock(box.id, vitolaStockId(line(), b), 1);

    // treću nemaš — ni zapis večeri je ne smije skinuti s tuđe police
    expect(h.consumeFromStock(vitolaStockId(line(), c))).toBeNull();
    expect(h.lineTotalStock(LINE_ID)).toBe(3);
  });
});
