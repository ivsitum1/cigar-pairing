import { describe, expect, it, beforeEach, vi } from "vitest";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  forgetAgeConfirmation,
  legalAgeForMarket,
  hasConfirmedAge,
  isAgeGateEnabled,
  rememberAgeConfirmed,
  shouldShowAgeGate,
} from "./ageGate";

function fakeStorage() {
  const map = new Map<string, string>();
  return {
    getItem: (k: string) => map.get(k) ?? null,
    setItem: (k: string, v: string) => void map.set(k, v),
    removeItem: (k: string) => void map.delete(k),
  };
}

beforeEach(() => {
  vi.stubGlobal("localStorage", fakeStorage());
});

describe("age gate — prekidač", () => {
  // .env.example: "leave unset (gate ON) or set to 1"; "set to 0 or off" gasi
  it("zadano je UKLJUČEN kad varijabla nije postavljena", () => {
    expect(isAgeGateEnabled(undefined)).toBe(true);
    expect(isAgeGateEnabled("")).toBe(true);
  });

  it("gasi se s 0 / off / false / no, neosjetljivo na velika slova i razmake", () => {
    for (const v of ["0", "off", "false", "no", " OFF ", "False"]) {
      expect(isAgeGateEnabled(v), v).toBe(false);
    }
  });

  it("ostaje uključen za 1 i sve ostalo", () => {
    for (const v of ["1", "on", "true", "yes", "cokolada"]) {
      expect(isAgeGateEnabled(v), v).toBe(true);
    }
  });
});

describe("age gate — pamćenje potvrde", () => {
  it("prije potvrde nije potvrđeno", () => {
    expect(hasConfirmedAge()).toBe(false);
  });

  it("potvrda preživi i čita se natrag", () => {
    rememberAgeConfirmed();
    expect(hasConfirmedAge()).toBe(true);
  });

  it("zaboravljanje vraća na nulu", () => {
    rememberAgeConfirmed();
    forgetAgeConfirmation();
    expect(hasConfirmedAge()).toBe(false);
  });

  it("blokiran storage ne ruši ništa — pita se opet", () => {
    vi.stubGlobal("localStorage", {
      getItem: () => {
        throw new Error("SecurityError");
      },
      setItem: () => {
        throw new Error("SecurityError");
      },
      removeItem: () => {
        throw new Error("SecurityError");
      },
    });
    expect(() => rememberAgeConfirmed()).not.toThrow();
    expect(() => forgetAgeConfirmation()).not.toThrow();
    expect(hasConfirmedAge()).toBe(false);
    expect(shouldShowAgeGate(true)).toBe(true);
  });
});

describe("age gate — treba li prikazati", () => {
  it("prikazuje se kad je uključen a nije potvrđeno", () => {
    expect(shouldShowAgeGate(true, false)).toBe(true);
  });

  it("ne prikazuje se nakon potvrde", () => {
    expect(shouldShowAgeGate(true, true)).toBe(false);
  });

  it("ne prikazuje se kad je isključen — i onda kad nije potvrđeno (QA)", () => {
    expect(shouldShowAgeGate(false, false)).toBe(false);
    expect(shouldShowAgeGate(false, true)).toBe(false);
  });
});

describe("dobna granica po tržištu", () => {
  // SAD: savezni Tobacco 21 (2019.) + alkohol 21 u svim državama.
  // Aplikacija je ranije tvrdila 18 svugdje.
  it("SAD je 21", () => {
    expect(legalAgeForMarket("USA")).toBe(21);
  });

  it("HR i EU su 18", () => {
    expect(legalAgeForMarket("HR")).toBe(18);
    expect(legalAgeForMarket("EU")).toBe(18);
  });

  it("ALL (bez filtera) pada na 18 — matično tržište", () => {
    expect(legalAgeForMarket("ALL")).toBe(18);
  });
});

describe("tekstovi ne tvrde fiksnu dob", () => {
  const i18n = readFileSync(
    resolve(dirname(fileURLToPath(import.meta.url)), "..", "i18n", "index.tsx"),
    "utf8",
  );
  const block = (key: string) => {
    const i = i18n.indexOf(`"${key}"`);
    return i === -1 ? "" : i18n.slice(i, i18n.indexOf("},", i));
  };

  it("gate ne navodi jedan broj kao univerzalnu granicu", () => {
    // Granica ovisi o zemlji; gate traži punoljetnost "u svojoj zemlji",
    // a oba praga stoje odvojeno u age.thresholds.
    for (const key of ["age.body", "age.deniedBody"]) {
      expect(block(key), key).not.toMatch(/\b(18|21)\b/);
    }
    expect(block("age.thresholds")).toMatch(/18/);
    expect(block("age.thresholds")).toMatch(/21/);
  });

  it("footer disclaimeri koriste {age}, ne tvrdu vrijednost", () => {
    for (const key of ["footer.tobacco", "footer.alcohol"]) {
      expect(block(key), key).toContain("{age}");
      expect(block(key), key).not.toMatch(/\b18\b/);
    }
  });
});
