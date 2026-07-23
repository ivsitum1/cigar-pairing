/**
 * List NotebookLM notebooks via notebooklm-mcp chrome profile (browser session).
 * Usage: node 40_operations/scripts/notebooklm_list_notebooks.mjs [title_filter]
 */
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import os from "node:os";
import { pathToFileURL } from "node:url";
import { fileURLToPath } from "node:url";

const filter = (process.argv[2] || "").toLowerCase();
const require = createRequire(import.meta.url);

function findPkg() {
  try {
    return path.dirname(require.resolve("notebooklm-mcp/package.json"));
  } catch {
    /* */
  }
  const npxRoot = path.join(os.homedir(), "AppData", "Local", "npm-cache", "_npx");
  if (!fs.existsSync(npxRoot)) return null;
  for (const d of fs.readdirSync(npxRoot)) {
    const p = path.join(npxRoot, d, "node_modules", "notebooklm-mcp");
    if (fs.existsSync(path.join(p, "dist/config.js"))) return p;
  }
  return null;
}

const pkgRoot = findPkg();
if (!pkgRoot) {
  console.error(JSON.stringify({ error: "notebooklm-mcp not found; run: npx -y notebooklm-mcp@latest" }));
  process.exit(2);
}

process.chdir(pkgRoot);
const { CONFIG } = await import(pathToFileURL(path.join(pkgRoot, "dist/config.js")).href);
const { chromium } = await import(pathToFileURL(path.join(pkgRoot, "node_modules/patchright/index.mjs")).href);

const context = await chromium.launchPersistentContext(CONFIG.chromeProfileDir, {
  headless: true,
  channel: "chrome",
});
try {
  const page = context.pages()[0] || (await context.newPage());
  await page.goto("https://notebooklm.google.com/", {
    waitUntil: "domcontentloaded",
    timeout: 120000,
  });
  await page.waitForTimeout(6000);

  const notebooks = await page.evaluate(() => {
    const out = [];
    for (const a of document.querySelectorAll('a[href*="/notebook/"]')) {
      const text = (a.textContent || "").trim();
      const href = a.href || "";
      const m = href.match(/\/notebook\/([a-f0-9-]+)/i);
      if (!m) continue;
      out.push({ title: text, url: href, notebook_id: m[1] });
    }
    const seen = new Set();
    return out.filter((x) => {
      const k = x.notebook_id;
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    });
  });

  const filtered = filter
    ? notebooks.filter(
        (n) =>
          n.title.toLowerCase().includes(filter) ||
          filter.split(/\s+/).every((w) => n.title.toLowerCase().includes(w)),
      )
    : notebooks;

  console.log(JSON.stringify({ profile: CONFIG.chromeProfileDir, notebooks, filtered }, null, 2));
  process.exit(filtered.length ? 0 : notebooks.length ? 0 : 1);
} finally {
  await context.close();
}
