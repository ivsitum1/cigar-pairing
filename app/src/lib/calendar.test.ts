import { describe, expect, it } from "vitest";
import {
  applyLocalDayToIso,
  groupByDay,
  localDayKey,
  monthGrid,
  shiftMonth,
} from "./calendar";

describe("localDayKey", () => {
  it("koristi lokalni dan, ne UTC", () => {
    // 23:30 lokalno je već sutra po UTC-u u pozitivnim zonama; ključ mora
    // ostati dan koji korisnik vidi
    const late = new Date(2026, 6, 29, 23, 30);
    expect(localDayKey(late)).toBe("2026-07-29");
  });

  it("nadopunjuje nulama", () => {
    expect(localDayKey(new Date(2026, 0, 5))).toBe("2026-01-05");
  });
});

describe("monthGrid", () => {
  it("počinje ponedjeljkom i pokriva pune tjedne", () => {
    const grid = monthGrid(2026, 6, new Date(2026, 6, 29)); // srpanj 2026.
    expect(grid.length % 7).toBe(0);
    expect(grid[0].date.getDay()).toBe(1); // ponedjeljak
    expect(grid[grid.length - 1].date.getDay()).toBe(0); // nedjelja
  });

  it("označava dane susjednih mjeseci", () => {
    const grid = monthGrid(2026, 6, new Date(2026, 6, 29));
    expect(grid.filter((d) => d.inMonth)).toHaveLength(31); // srpanj ima 31 dan
    expect(grid.some((d) => !d.inMonth)).toBe(true);
  });

  it("označava današnji dan", () => {
    const today = new Date(2026, 6, 29);
    const grid = monthGrid(2026, 6, today);
    expect(grid.filter((d) => d.isToday)).toHaveLength(1);
    expect(grid.find((d) => d.isToday)?.dayOfMonth).toBe(29);
  });

  it("veljača u prijestupnoj godini ima 29 dana", () => {
    const grid = monthGrid(2028, 1, new Date(2028, 1, 1));
    expect(grid.filter((d) => d.inMonth)).toHaveLength(29);
  });
});

describe("groupByDay", () => {
  const entries = [
    { id: "a", date: new Date(2026, 6, 29, 20, 0).toISOString() },
    { id: "b", date: new Date(2026, 6, 29, 22, 0).toISOString() },
    { id: "c", date: new Date(2026, 6, 28, 9, 0).toISOString() },
    { id: "bad", date: "nije datum" },
  ];

  it("grupira po lokalnom danu", () => {
    const grouped = groupByDay(entries);
    expect(grouped.get("2026-07-29")).toHaveLength(2);
    expect(grouped.get("2026-07-28")).toHaveLength(1);
  });

  it("preskače neispravne datume", () => {
    const grouped = groupByDay(entries);
    const all = [...grouped.values()].flat();
    expect(all.find((e) => e.id === "bad")).toBeUndefined();
  });

  it("unutar dana ide najnovije prvo", () => {
    const grouped = groupByDay(entries);
    expect(grouped.get("2026-07-29")?.map((e) => e.id)).toEqual(["b", "a"]);
  });
});

describe("shiftMonth", () => {
  it("prelazi godinu unaprijed i unatrag", () => {
    expect(shiftMonth(2026, 11, 1)).toEqual({ year: 2027, month: 0 });
    expect(shiftMonth(2026, 0, -1)).toEqual({ year: 2025, month: 11 });
  });

  it("ostaje u godini kad ne treba prijelaz", () => {
    expect(shiftMonth(2026, 5, 1)).toEqual({ year: 2026, month: 6 });
  });
});

describe("applyLocalDayToIso", () => {
  it("mijenja dan, zadržava sat", () => {
    const iso = new Date(2026, 6, 29, 20, 15, 30).toISOString();
    const next = applyLocalDayToIso(iso, "2026-07-15");
    expect(next).not.toBeNull();
    const d = new Date(next!);
    expect(localDayKey(d)).toBe("2026-07-15");
    expect(d.getHours()).toBe(20);
    expect(d.getMinutes()).toBe(15);
  });

  it("odbija nepostojeći dan", () => {
    const iso = new Date(2026, 0, 15, 12, 0).toISOString();
    expect(applyLocalDayToIso(iso, "2026-02-31")).toBeNull();
  });

  it("odbija loš ključ ili ISO", () => {
    expect(applyLocalDayToIso("nije datum", "2026-07-15")).toBeNull();
    expect(applyLocalDayToIso(new Date().toISOString(), "7/15/2026")).toBeNull();
  });
});
