import { describe, expect, it } from "vitest";
import type { Drink } from "../types";
import ginsJson from "./gins.json";
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

const GIN_CURATED_IDS = [
  "gin-monkey-47-schwarzwald-dry-gin-47-vol-0-5l",
  "gin-hendrick-s-gin-41-4-vol-0-7l",
  "gin-tanqueray-no-ten-47-3-vol-0-7l",
  "gin-the-botanist-islay-dry-gin-46-vol-0-7l",
  "gin-gin-mare-capri-mediterranean-gin-42-7-vol-0-7l",
  "gin-plymouth-gin",
  "gin-sipsmith-london-dry-gin-41-6-0-7-l",
  "gin-nikka-coffey-gin-47-vol-0-7l",
  "gin-four-pillars-rare-dry-gin-41-8-vol-0-7l",
  "gin-old-pilot-s-dalmatian-dry-gin-45-vol-0-7l",
  "gin-dugave-gin",
  "gin-beefeater-24",
  "gin-aviation-gin-42-0-7-l",
  "gin-roku-japanese-craft-gin-43-0-7-l",
] as const;

const rums = rumsJson as Drink[];
const tequilas = tequilasJson as Drink[];
const gins = ginsJson as Drink[];

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

describe("kurirane biljeske za gin", () => {
  it("referentni set ima dovoljno duge HR+EN biljeske i cigarHint", () => {
    for (const id of GIN_CURATED_IDS) {
      const g = gins.find((item) => item.id === id);

      expect(g, id).toBeDefined();
      expect(g?.notes.hr.length, id).toBeGreaterThanOrEqual(80);
      expect(g?.notes.en.length, id).toBeGreaterThanOrEqual(80);
      expect(g?.cigarHint?.hr?.length ?? 0, id).toBeGreaterThanOrEqual(80);
      expect(g?.cigarHint?.en?.length ?? 0, id).toBeGreaterThanOrEqual(80);
    }
  });
});
