import { describe, expect, it } from "vitest";
import type { Cigar } from "../types";
import cigarsJson from "../data/cigars.json";
import { applyVitola, uniqueVitolas } from "./cigarVitola";
import { cigarItemId, parseCigarItemId, vitolaFromItemId } from "./cigarItemId";

const cigars = cigarsJson as unknown as Cigar[];

const byId = (id: string): Cigar => {
  const hit = cigars.find((c) => c.id === id);
  if (!hit) throw new Error(`missing ${id}`);
  return hit;
};

describe("kljuc stavke po vitoli", () => {
  it("Don Tomas Bundle ima Rothschild i Petit Corona", () => {
    const names = uniqueVitolas(byId("cig-don-tomas-bundle")).map((v) => v.name);
    expect(names).toContain("Rothschild");
    expect(names).toContain("Petit Corona");
    expect(names).toContain("Churchill");
    expect(names).toContain("Corona");
  });

  it("Churchill i Corona iste linije daju razlicite kljuceve", () => {
    const line = byId("cig-don-tomas-bundle");
    const vitolas = uniqueVitolas(line);
    const churchill = vitolas.find((v) => v.name === "Churchill")!;
    const corona = vitolas.find((v) => v.name === "Corona")!;

    const a = cigarItemId(applyVitola(line, churchill));
    const b = cigarItemId(applyVitola(line, corona));

    expect(a).toBe("cig-don-tomas-bundle@churchill");
    expect(b).toBe("cig-don-tomas-bundle@corona");
    expect(a).not.toBe(b);
  });

  it("linija bez izbora ostaje na golom id-u (stara stanja se ne gube)", () => {
    expect(cigarItemId(byId("cig-don-tomas-bundle"))).toBe(
      "cig-don-tomas-bundle",
    );
  });

  it("linija s jednom vitolom ne dobiva sufiks", () => {
    const single = cigars.find((c) => uniqueVitolas(c).length === 1)!;
    const only = uniqueVitolas(single)[0];
    expect(cigarItemId(applyVitola(single, only))).toBe(single.id);
  });

  it("kljuc se rastavlja natrag na liniju i vitolu", () => {
    const line = byId("cig-don-tomas-bundle");
    const rothschild = uniqueVitolas(line).find((v) => v.name === "Rothschild")!;
    const key = cigarItemId(applyVitola(line, rothschild));

    expect(parseCigarItemId(key)).toEqual({
      cigarId: "cig-don-tomas-bundle",
      vitolaSlug: "rothschild",
    });
    expect(vitolaFromItemId(line, key)?.name).toBe("Rothschild");
  });

  it("goli id nema vitola slug", () => {
    expect(parseCigarItemId("cig-don-tomas-bundle")).toEqual({
      cigarId: "cig-don-tomas-bundle",
    });
  });
});
