// Čuvar hrvatskog teksta: sve što korisnik čita na hrvatskom mora proći ovdje.
// Regeneracija kataloga i novi sadržaj lako vrate anglizme, srbizme i ogoljene
// dijakritike — ovaj test ih hvata prije nego dođu u aplikaciju.
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const DATA = resolve(HERE, "..", "data");

const DATA_FILES = [
  "bonton.json",
  "brandies.json",
  "brands.json",
  "cigars.json",
  "club.json",
  "club101.json",
  "coffees.json",
  "dictionary.json",
  "digestifs.json",
  "eveningArchetypes.json",
  "gins.json",
  "hrGuide.json",
  "lexicon.json",
  "rums.json",
  "shopping.json",
  "tequilas.json",
  "whiskies.json",
  "wines.json",
] as const;

/** Svi hrvatski stringovi: `{ hr: "…" }` u JSON podacima i u i18n tablici. */
function croatianStrings(): { where: string; text: string }[] {
  const out: { where: string; text: string }[] = [];

  // region/country su HR prikaz korisniku (npr. "Jerez, Španjolska") — ne samo .hr
  const HR_KEYS = new Set(["hr", "region", "country"]);

  const walk = (node: unknown, file: string, path: string) => {
    if (Array.isArray(node)) {
      node.forEach((v, i) => walk(v, file, `${path}[${i}]`));
      return;
    }
    if (node && typeof node === "object") {
      for (const [k, v] of Object.entries(node as Record<string, unknown>)) {
        if (HR_KEYS.has(k) && typeof v === "string") {
          out.push({ where: `${file}${path}.${k}`, text: v });
        } else {
          walk(v, file, `${path}.${k}`);
        }
      }
    }
  };

  for (const file of DATA_FILES) {
    walk(JSON.parse(readFileSync(resolve(DATA, file), "utf8")), file, "");
  }

  // i18n tablica je TSX — čitamo je kao tekst
  const i18n = readFileSync(resolve(HERE, "index.tsx"), "utf8");
  const entry = /"([\w.]+)":\s*\{\s*hr:\s*"((?:[^"\\]|\\.)*)"/g;
  for (let m = entry.exec(i18n); m; m = entry.exec(i18n)) {
    out.push({ where: `i18n:${m[1]}`, text: m[2] });
  }

  // hrvatski živi i u kodu (objašnjenja enginea, opisi vitola, note trgovina)
  const SRC = resolve(HERE, "..");
  const TS_SOURCES = [
    "engine/curatedOpinion.ts",
    "engine/occasion.ts",
    "engine/pairing.ts",
    "engine/personal.ts",
    "engine/rules.ts",
    "engine/serve.ts",
    "data/drinkShops.ts",
    "data/shops.ts",
    "lib/geo.ts",
    "lib/shareCard.ts",
    "lib/shoppingPicks.ts",
    "lib/vitolaInfo.ts",
  ];
  // `hr: "…"` i `labelHr: "…"` — oba se prikazuju korisniku
  const inline = /\b(?:hr|labelHr):\s*"((?:[^"\\]|\\.)*)"/g;
  for (const file of TS_SOURCES) {
    const code = readFileSync(resolve(SRC, file), "utf8");
    for (let m = inline.exec(code); m; m = inline.exec(code)) {
      out.push({ where: file, text: m[1] });
    }
  }

  return out;
}

const strings = croatianStrings();

// Ime aplikacije ("Cigar & Drink Pairing") je vlastito ime, ne prijevodna
// riječ. Kraći oblik "Cigar & Pairing" ostaje pokriven zbog starijih nizova.
const APP_NAME = /Cigar\s*&\s*(Drink\s*)?Pairing/i;

/** Prijavi do 5 primjera da poruka o grešci bude upotrebljiva. */
const offenders = (re: RegExp): string[] =>
  strings
    .filter((s) => re.test(s.text.replace(APP_NAME, "")))
    .slice(0, 5)
    .map((s) => `${s.where}: ${s.text.slice(0, 100)}`);

describe("hrvatski tekst", () => {
  it("ima što provjeriti", () => {
    expect(strings.length).toBeGreaterThan(3000);
  });

  it("bez engleskih naziva listova (wrapper / binder / filler)", () => {
    expect(offenders(/\b(wrapper|binder|filler)\w*/i)).toEqual([]);
  });

  it("bez anglizama koji imaju hrvatski ekvivalent", () => {
    // "brendon" je ime, ne anglizam — zato negativni lookahead
    expect(offenders(/\bpairing\w*/i)).toEqual([]);
    expect(offenders(/\bbrend(?!on)\w*/i)).toEqual([]);
    // "Cigar Export" u imenu tvrtke je vlastito ime — gađamo hrvatske rečenice
    expect(offenders(/\b(export|import)\s+podataka\b/i)).toEqual([]);
    expect(offenders(/\b(backup|storage)\b/i)).toEqual([]);
  });

  it("bez srbizama", () => {
    expect(
      offenders(
        /\b(italijansk\w*|historij\w*|hiljad\w*|saradnj\w*|opšt\w*|porodic\w*|fabrik\w*|vazduh\w*|porijekl\w*)/i,
      ),
    ).toEqual([]);
  });

  it("bez ogoljenih dijakritika u čestim riječima", () => {
    expect(
      offenders(
        /\b(voce|secer\w*|zacin\w*|slatkoca|gorcina|cokolad\w*|tresnj\w*|pjenusa\w*|bacv\w*|odlezan\w*|zavrsnic\w*|klasican|klasicn\w*|spanjolsk\w*|skotsk\w*|njemack\w*|madjarsk\w*|grck\w*|peljesac|plesivica|primosten|skriljevac|orasast\w*|dosladj\w*|dopust\w*|grozdj\w*|Dingac\w*)\b/,
      ),
    ).toEqual([]);
  });

  it("bez CP437 mojibakea dijakritika (┼á ≈ Š)", () => {
    // UTF-8 Š (C5 A0) pročitan kao OEM/CP437 daje U+253C U+00E1
    expect(offenders(/[─│┌┐└┘├┤┬┴┼═║╔╗╚╝╠╣╦╩╬]/)).toEqual([]);
  });

  it("ne propušta interne oznake okusa u tekst", () => {
    expect(offenders(/\b(suho-voce|tropsko-voce|zacini-slatki|ester-funk|trava-slatka)\b/)).toEqual(
      [],
    );
  });

  it("koristi hrvatske navodnike, uparene", () => {
    expect(offenders(/[«»]/)).toEqual([]);
    const unbalanced = strings
      .filter((s) => (s.text.match(/„/g) ?? []).length !== (s.text.match(/”/g) ?? []).length)
      .slice(0, 5)
      .map((s) => `${s.where}: ${s.text.slice(0, 100)}`);
    expect(unbalanced).toEqual([]);
  });

  it("bez padežnih grešaka uz 'cigara'", () => {
    expect(offenders(/\b(uz|Uz)\s+cigara\b/)).toEqual([]);
    expect(offenders(/\b(laganu|punu|srednju|blagu|jaku)\s+cigara\b/)).toEqual([]);
  });
});
