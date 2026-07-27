import { readFileSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { describe, expect, it } from "vitest";
import { parseHash } from "../store/route";

const here = dirname(fileURLToPath(import.meta.url));

describe("dictionary alphabet rail", () => {
  it("must not use #letter-* hash hrefs (hash router treats them as pairing)", () => {
    // Evidence: #letter-A is not a club/dictionary route — it falls through to pairing.
    expect(parseHash("#letter-A")).toEqual({ page: "pairing" });

    const src = readFileSync(resolve(here, "./DictionaryPage.tsx"), "utf8");
    expect(src).not.toMatch(/href=\{`#letter-/);
    expect(src).toMatch(/dict-letter-/);
  });
});
