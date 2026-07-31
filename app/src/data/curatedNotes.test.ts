import { describe, expect, it } from "vitest";
import type { Drink } from "../types";
import rumsJson from "./rums.json";

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

const rums = rumsJson as Drink[];

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
