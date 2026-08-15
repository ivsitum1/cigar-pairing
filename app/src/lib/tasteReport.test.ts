// Izvještaj mora biti čitljiv čovjeku i strojno uvozljiv istim tekstom —
// `scripts/import-taste-report.py` iz njega vadi ```json blok, pa oblik nije
// kozmetika nego sučelje između preglednika i repoa.
import { describe, expect, it } from "vitest";
import type { Cigar } from "../types";
import {
  REPORT_KIND,
  buildTasteReport,
  githubIssueUrl,
  issueUrlTooLong,
  reportMarkdown,
  reportTitle,
} from "./tasteReport";

const cigars: Record<string, Cigar> = {
  "cig-b": { brand: "Bolívar", line: "Belicosos" } as Cigar,
  "cig-a": { brand: "Ashton", line: "Classic" } as Cigar,
};
const lookup = (id: string) => cigars[id];

const profiles = {
  "cig-b": { strength: 5, body: 4, at: "2026-08-01T10:00:00.000Z" },
  "cig-a": { strength: 2, body: 2, at: "2026-08-02T10:00:00.000Z" },
};

describe("izvještaj o dojmovima", () => {
  it("nosi potpis, vrijeme i sve ocjene", () => {
    const r = buildTasteReport(profiles, " Ivan ", lookup, new Date("2026-08-15T12:00:00Z"));
    expect(r.kind).toBe(REPORT_KIND);
    expect(r.by).toBe("Ivan");
    expect(r.at).toBe("2026-08-15T12:00:00.000Z");
    expect(r.reports).toHaveLength(2);
  });

  it("poredan je po imenu — dva slanja daju isti redoslijed", () => {
    const r = buildTasteReport(profiles, "Ivan", lookup);
    expect(r.reports.map((x) => x.label)).toEqual(["Ashton Classic", "Bolívar Belicosos"]);
  });

  it("nepoznata cigara ne ruši izvještaj — ostaje id", () => {
    const r = buildTasteReport(
      { "cig-x": { strength: 3, body: 3, at: "2026-08-01T00:00:00.000Z" } },
      "Ivan",
      lookup,
    );
    expect(r.reports[0].label).toBe("cig-x");
  });

  it("tijelo prijave sadrži blok koji skripta uvozi", () => {
    const md = reportMarkdown(buildTasteReport(profiles, "Ivan", lookup));
    const block = /```json\s*(\{[\s\S]*?\})\s*```/.exec(md);
    expect(block).not.toBeNull();
    const parsed = JSON.parse(block![1]);
    expect(parsed.kind).toBe(REPORT_KIND);
    expect(parsed.by).toBe("Ivan");
    expect(parsed.reports).toHaveLength(2);
  });

  it("tablica je uz blok, za ljudsko oko", () => {
    const md = reportMarkdown(buildTasteReport(profiles, "Ivan", lookup));
    expect(md).toContain("| Ashton Classic | 2 | 2 |");
    expect(md).toContain("| Bolívar Belicosos | 5 | 4 |");
  });

  it("naslov kaže tko i koliko", () => {
    expect(reportTitle(buildTasteReport(profiles, "Ivan", lookup))).toBe("Dojmovi: Ivan — 2 cigara");
    expect(reportTitle(buildTasteReport({}, "", lookup))).toBe("Dojmovi: nepotpisano — 0 cigara");
  });
});

describe("poveznica na GitHub", () => {
  it("vodi u novu prijavu s popunjenim naslovom i tijelom", () => {
    const url = new URL(githubIssueUrl(buildTasteReport(profiles, "Ivan", lookup)));
    expect(url.origin + url.pathname).toBe("https://github.com/ivsitum1/cigar-pairing/issues/new");
    expect(url.searchParams.get("title")).toContain("Ivan");
    expect(url.searchParams.get("body")).toContain(REPORT_KIND);
  });

  it("predugačku poveznicu prepoznaje umjesto da je ponudi slomljenu", () => {
    const many = Object.fromEntries(
      Array.from({ length: 300 }, (_, i) => [
        `cig-${i}`,
        { strength: 3, body: 3, at: "2026-08-01T00:00:00.000Z" },
      ]),
    );
    const url = githubIssueUrl(buildTasteReport(many, "Ivan", lookup));
    expect(issueUrlTooLong(url)).toBe(true);
    expect(issueUrlTooLong(githubIssueUrl(buildTasteReport(profiles, "Ivan", lookup)))).toBe(false);
  });
});
