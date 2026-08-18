import { describe, expect, it } from "vitest";
import type { Drink } from "../types";
import rumsJson from "./rums.json";
import tequilasJson from "./tequilas.json";

const CURATED_RUM_NOTE_IDS = [
  "rum-foursquare-ecs-detente-2005",
  "rum-foursquare-sovereignty",
  "rum-covenant",
  "rum-eminente-gran-reserva-10",
  "rum-foursquare-detente-10-yo",
  "rum-foursquare-nobiliary",
  "rum-sagacity",
  "rum-hampden-estate-8",
  "rum-hampden-hlcf-classic-60",
  "rum-havana-club-tributo",
  "rum-mount-gay-1703",
  "rum-admiral-rodney-hms-formidable",
  "rum-appleton-estate-15-black-river",
  "rum-appleton-estate-21",
  "rum-chairman-s-reserve-1931",
  "rum-clement-vsop-agricole",
  "rum-neisson-agricole",
  "rum-doorly-s-12-foursquare",
  "rum-doorly-s-14-foursquare",
  "rum-doorly-s-xo-foursquare",
  "rum-eminente-reserva-7",
  "rum-havana-club-seleccion-maestros",
  "rum-mount-gay-xo",
  "rum-worthy-park-109",
] as const;

const TEQUILA_CURATED_IDS = [
  "tq-don-julio-blanco",
  "tq-don-julio-reposado",
  "tq-don-julio-anejo",
  "tq-don-julio-1942",
  "tq-patron-silver",
  "tq-patron-reposado",
  "tq-patron-anejo",
  "tq-casamigos-reposado",
  "tq-casamigos-anejo",
  "tq-casamigos-mezcal",
  "tq-espolon-blanco",
  "tq-clase-azul-reposado",
] as const;

const rums = rumsJson as Drink[];
const tequilas = tequilasJson as Drink[];

describe("kurirane biljeske za rumove", () => {
  it("val 1 ima dovoljno duge HR biljeske i HR cigarHint", () => {
    expect(CURATED_RUM_NOTE_IDS.length).toBeGreaterThanOrEqual(15);
    expect(CURATED_RUM_NOTE_IDS.length).toBeLessThanOrEqual(25);

    for (const id of CURATED_RUM_NOTE_IDS) {
      const rum = rums.find((item) => item.id === id);

      expect(rum, id).toBeDefined();
      expect(rum?.notes.hr.length, id).toBeGreaterThanOrEqual(80);
      expect(rum?.cigarHint?.hr?.length, id).toBeGreaterThan(0);
    }
  });
});

describe("kurirane biljeske za tequilu", () => {
  it("referentni set ima dovoljno duge HR+EN biljeske i cigarHint", () => {
    for (const id of TEQUILA_CURATED_IDS) {
      const t = tequilas.find((item) => item.id === id);

      expect(t, id).toBeDefined();
      expect(t?.notes.hr.length, id).toBeGreaterThanOrEqual(80);
      expect(t?.notes.en.length, id).toBeGreaterThanOrEqual(80);
      expect(t?.cigarHint?.hr?.length ?? 0, id).toBeGreaterThanOrEqual(80);
      expect(t?.cigarHint?.en?.length ?? 0, id).toBeGreaterThanOrEqual(80);
    }
  });
});
