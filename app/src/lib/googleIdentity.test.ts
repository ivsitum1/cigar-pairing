// Potpis prijave je jedino što iz Googleovog tokena ide dalje — i jedino što
// smije završiti u javnom repou. Zato se ovdje čuvaju dvije stvari: da se iz
// tokena čita ono što treba (i ništa više), i da haš ostane stabilan.
import { describe, expect, it } from "vitest";
import { decodeIdToken, tasterIdFromSub } from "./googleIdentity";

/** Token bez potpisa — dekoder ga i ne provjerava, vidi napomenu u modulu. */
function fakeIdToken(payload: Record<string, unknown>): string {
  const b64 = (obj: unknown) =>
    btoa(String.fromCharCode(...new TextEncoder().encode(JSON.stringify(obj))))
      .replace(/\+/g, "-")
      .replace(/\//g, "_")
      .replace(/=+$/, "");
  return `${b64({ alg: "RS256" })}.${b64(payload)}.potpis`;
}

describe("čitanje Googleovog tokena", () => {
  it("uzima sub i ime", () => {
    const out = decodeIdToken(fakeIdToken({ sub: "123456789", name: "Ivan Šitum" }));
    expect(out).toEqual({ sub: "123456789", name: "Ivan Šitum" });
  });

  it("e-mail ne izlazi iz tokena", () => {
    const out = decodeIdToken(
      fakeIdToken({ sub: "1", name: "Ivan", email: "ivan@example.com" }),
    );
    expect(JSON.stringify(out)).not.toContain("example.com");
  });

  it("pada na given_name kad punog imena nema", () => {
    expect(decodeIdToken(fakeIdToken({ sub: "1", given_name: "Ivan" }))?.name).toBe("Ivan");
  });

  it("bez imena ostaje prazno ime, ali potpis vrijedi", () => {
    expect(decodeIdToken(fakeIdToken({ sub: "1" }))).toEqual({ sub: "1", name: "" });
  });

  it("smeće nije token", () => {
    expect(decodeIdToken("")).toBeNull();
    expect(decodeIdToken("a.b")).toBeNull();
    expect(decodeIdToken("a.b.c")).toBeNull();
    expect(decodeIdToken(fakeIdToken({ name: "bez suba" }))).toBeNull();
    expect(decodeIdToken(fakeIdToken({ sub: "   " }))).toBeNull();
  });
});

describe("potpis za javni repo", () => {
  it("isti račun daje isti potpis", async () => {
    expect(await tasterIdFromSub("123456789")).toBe(await tasterIdFromSub("123456789"));
  });

  it("različiti računi daju različit potpis", async () => {
    expect(await tasterIdFromSub("1")).not.toBe(await tasterIdFromSub("2"));
  });

  it("oblik je g_ + 12 heksadekadskih znakova i ne sadrži sam sub", async () => {
    const id = await tasterIdFromSub("123456789");
    expect(id).toMatch(/^g_[0-9a-f]{12}$/);
    expect(id).not.toContain("123456789");
  });
});
