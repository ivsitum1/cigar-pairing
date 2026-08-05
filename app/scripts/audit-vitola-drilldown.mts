/**
 * Audit: multi-vitola lines + entry points that open cigars without LineSheet drill-down.
 * Read-only — does not modify cigars.json.
 *
 * Run: npx tsx scripts/audit-vitola-drilldown.mts
 * Out:  scripts/output/vitola-drilldown-audit.json
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const cigarsPath = join(root, "src/data/cigars.json");
const srcRoot = join(root, "src");

type Vitola = { name?: string; url?: string | null; priceEUR?: number | null };
type Cigar = {
  id: string;
  brand: string;
  line: string;
  vitola?: string;
  vitolas?: Vitola[];
};

function uniqueNames(c: Cigar): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const v of c.vitolas ?? []) {
    const n = (v.name ?? "").trim();
    if (!n) continue;
    const k = n.toLowerCase();
    if (seen.has(k)) continue;
    seen.add(k);
    out.push(n);
  }
  return out;
}

const cigars = JSON.parse(readFileSync(cigarsPath, "utf8")) as Cigar[];
const multi = cigars
  .map((c) => {
    const names = uniqueNames(c);
    return { id: c.id, brand: c.brand, line: c.line, defaultVitola: c.vitola ?? null, vitolas: names };
  })
  .filter((c) => c.vitolas.length > 1)
  .sort((a, b) => b.vitolas.length - a.vitolas.length || a.brand.localeCompare(b.brand));

const spotIds = [
  "cig-la-galera-1936-box-pressed",
  "cig-1502-emerald",
];
const spotChecks = spotIds.map((id) => {
  const hit = multi.find((c) => c.id === id) ?? null;
  const raw = cigars.find((c) => c.id === id);
  return {
    id,
    found: Boolean(raw),
    multiVitola: Boolean(hit),
    vitolas: hit?.vitolas ?? uniqueNames(raw ?? { id, brand: "", line: "" }),
  };
});

// Rough scan: setDetail({ kind: "cigar" without going through openCigar / applyVitola / LineSheet
const pageFiles = [
  "pages/ShoppingPage.tsx",
  "pages/ClubPage.tsx",
  "pages/CollectionPage.tsx",
  "pages/PairingPage.tsx",
  "pages/CatalogPage.tsx",
];
const entryPoints = pageFiles.map((rel) => {
  const text = readFileSync(join(srcRoot, rel), "utf8");
  const rawSetDetail = [
    ...text.matchAll(/setDetail\(\{\s*kind:\s*"cigar"/g),
  ].length;
  const usesBrowse =
    text.includes("useCigarBrowseSheets") ||
    text.includes("openCigar(") ||
    text.includes("openLine(") ||
    text.includes("openVitola(");
  const usesApplyVitola = text.includes("applyVitola(");
  return {
    file: rel,
    rawSetDetailCigar: rawSetDetail,
    usesBrowseSheetsOrOpenCigar: usesBrowse,
    usesApplyVitola,
    ok:
      rel.includes("CatalogPage")
        ? usesApplyVitola && text.includes("LineSheet")
        : usesBrowse && rawSetDetail === 0,
  };
});

const out = {
  generatedAt: new Date().toISOString(),
  totals: {
    cigars: cigars.length,
    multiVitolaLines: multi.length,
    maxVitolasOnLine: multi[0]?.vitolas.length ?? 0,
  },
  spotChecks,
  entryPoints,
  multiVitolaLines: multi,
};

const outDir = join(root, "scripts/output");
mkdirSync(outDir, { recursive: true });
const outPath = join(outDir, "vitola-drilldown-audit.json");
writeFileSync(outPath, JSON.stringify(out, null, 2), "utf8");

console.log(
  `multi-vitola lines: ${multi.length} / ${cigars.length}; spot: ${JSON.stringify(spotChecks.map((s) => s.id + "=" + s.multiVitola))}`,
);
console.log(
  `entry points ok: ${entryPoints.filter((e) => e.ok).length}/${entryPoints.length}`,
);
console.log(`wrote ${outPath}`);
