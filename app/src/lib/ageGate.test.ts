import { describe, expect, it, beforeEach, vi } from "vitest";
import {
  forgetAgeConfirmation,
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
