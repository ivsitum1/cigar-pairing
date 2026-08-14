import { describe, expect, it } from "vitest";
import {
  VITOLA_FAMILY_ORDER,
  vitolaFamily,
  vitolaFamilyLabel,
} from "./vitolaFamily";

describe("vitolaFamily", () => {
  it("prepoznaje osnovne formate", () => {
    expect(vitolaFamily("Robusto")).toBe("robusto");
    expect(vitolaFamily("Toro")).toBe("toro");
    expect(vitolaFamily("Churchill")).toBe("churchill");
    expect(vitolaFamily("Corona")).toBe("corona");
    expect(vitolaFamily("Gordo")).toBe("gordo");
  });

  it("oblik pobjeđuje veličinu — figurado ostaje figurado", () => {
    expect(vitolaFamily("Torpedo")).toBe("figurado");
    expect(vitolaFamily("Belicoso Fino")).toBe("figurado");
    expect(vitolaFamily("Pirámide")).toBe("figurado");
    expect(vitolaFamily("Salomon")).toBe("figurado");
    expect(vitolaFamily("Perfecto No. 2")).toBe("figurado");
  });

  it("uže ime pobjeđuje šire", () => {
    expect(vitolaFamily("Double Corona")).toBe("double-corona");
    expect(vitolaFamily("Petit Corona")).toBe("petit");
    expect(vitolaFamily("Short Robusto")).toBe("petit");
    expect(vitolaFamily("Half Corona")).toBe("petit");
  });

  it("sinonimi kuće idu u istu obitelj", () => {
    expect(vitolaFamily("Epicure No. 2")).toBe("robusto");
    expect(vitolaFamily("Cañonazo")).toBe("toro");
    expect(vitolaFamily("Julieta No. 2")).toBe("churchill");
    expect(vitolaFamily("Laguito No. 1")).toBe("lancero");
    expect(vitolaFamily("Panetela Larga")).toBe("lancero");
  });

  it("„Robusto Gordo” ostaje robusto, goli „Gordo” je gordo", () => {
    expect(vitolaFamily("Robusto Gordo")).toBe("robusto");
    expect(vitolaFamily("Magnum 60")).toBe("gordo");
  });

  it("nepoznato i prazno padaju u ostalo", () => {
    expect(vitolaFamily("Conquistador")).toBe("other");
    expect(vitolaFamily("")).toBe("other");
    expect(vitolaFamily(null)).toBe("other");
    expect(vitolaFamily(undefined)).toBe("other");
  });

  it("svaka obitelj ima mjesto u poretku i naziv na oba jezika", () => {
    const seen = new Set(VITOLA_FAMILY_ORDER);
    expect(seen.size).toBe(VITOLA_FAMILY_ORDER.length);
    for (const family of VITOLA_FAMILY_ORDER) {
      expect(vitolaFamilyLabel(family, "hr")).toBeTruthy();
      expect(vitolaFamilyLabel(family, "en")).toBeTruthy();
    }
    expect(VITOLA_FAMILY_ORDER[VITOLA_FAMILY_ORDER.length - 1]).toBe("other");
  });
});
