// Dojmovi iz aplikacije natrag u repo — bez servera i bez tajni u pregledniku.
//
// App je statična stranica na GitHub Pagesu; nema gdje čuvati token, pa ne može
// sama pisati u repo. Ono što MOŽE je pripremiti gotovu prijavu i otvoriti je:
// GitHub prima naslov i tijelo kroz URL, a tko je prijavljen samo pritisne
// "Submit". Zapis time nastaje pod njegovim imenom, ne pod tuđim ključem.
//
// Za onoga tko nema GitHub račun, isti tekst ide u međuspremnik ili dijeljenje
// — `scripts/import-taste-report.py` prima oba oblika jednako.
import type { Cigar } from "../types";
import type { TasteProfiles } from "../store/tasteProfile";

export const REPORT_KIND = "cigar-pairing-taste-report";
export const REPORT_VERSION = 1;

export interface TasteReportEntry {
  cigarId: string;
  /** Ime za ljudsko oko u prijavi; skripta se oslanja na cigarId. */
  label: string;
  strength: number;
  body: number;
  at: string;
}

export interface TasteReport {
  kind: typeof REPORT_KIND;
  v: number;
  by: string;
  /**
   * Stabilan potpis prijavljenog računa (`g_…`, vidi lib/googleIdentity).
   * Kad ga ima, skripte spajaju po njemu umjesto po imenu, pa isti čovjek s
   * dva uređaja više ne ulazi u prosjek dvaput. Izostaje kad prijave nema —
   * stari oblik izvještaja i dalje prolazi kroz cijeli lanac.
   */
  byId?: string;
  at: string;
  reports: TasteReportEntry[];
}

/** Ocjene iz preglednika → izvještaj, poredan po imenu radi čitljivog diffa. */
export function buildTasteReport(
  profiles: TasteProfiles,
  by: string,
  cigarById: (id: string) => Cigar | undefined,
  now: Date = new Date(),
  byId = "",
): TasteReport {
  const reports: TasteReportEntry[] = Object.entries(profiles)
    .map(([cigarId, p]) => {
      const c = cigarById(cigarId);
      return {
        cigarId,
        label: c ? `${c.brand} ${c.line}` : cigarId,
        strength: p.strength,
        body: p.body,
        at: p.at,
      };
    })
    .sort((a, b) => a.label.localeCompare(b.label));
  const signed = byId.trim();
  return {
    kind: REPORT_KIND,
    v: REPORT_VERSION,
    by: by.trim(),
    ...(signed ? { byId: signed } : {}),
    at: now.toISOString(),
    reports,
  };
}

/** Tijelo prijave: tablica za čitanje + blok koji skripta uvozi. */
export function reportMarkdown(report: TasteReport): string {
  const rows = report.reports
    .map((r) => `| ${r.label} | ${r.strength} | ${r.body} |`)
    .join("\n");
  return [
    `Dojmovi nakon pušenja — **${report.by || "bez potpisa"}**, ${report.reports.length} cigara.`,
    "",
    "| Cigara | Snaga | Tijelo |",
    "| --- | --- | --- |",
    rows,
    "",
    "<details><summary>Podaci za uvoz</summary>",
    "",
    "```json",
    JSON.stringify(report, null, 2),
    "```",
    "",
    "</details>",
  ].join("\n");
}

export function reportTitle(report: TasteReport): string {
  const who = report.by || "nepotpisano";
  return `Dojmovi: ${who} — ${report.reports.length} cigara`;
}

/**
 * Predpopunjena prijava na GitHubu. `labels` traži postojeću oznaku; ako je
 * nema, GitHub je jednostavno ignorira i prijava se svejedno otvori.
 */
export function githubIssueUrl(
  report: TasteReport,
  repo = "ivsitum1/cigar-pairing",
): string {
  const params = new URLSearchParams({
    title: reportTitle(report),
    body: reportMarkdown(report),
    labels: "dojmovi",
  });
  return `https://github.com/${repo}/issues/new?${params.toString()}`;
}

/**
 * GitHub odbija predugačak URL (praktična granica je oko 8 kB). Preko toga se
 * nudi samo kopiranje — bolje nego prijava koja se otvori prazna.
 */
export const URL_LIMIT = 7000;

export function issueUrlTooLong(url: string): boolean {
  return url.length > URL_LIMIT;
}
