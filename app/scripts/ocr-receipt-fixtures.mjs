/**
 * Receipt-oriented OCR: SINGLE_COLUMN (+ AUTO merge) — not SPARSE_TEXT (band mode).
 */
import { createWorker, PSM } from "tesseract.js";
import { writeFileSync, readdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const fixtureDir = join(__dirname, "data/ocr-receipts");
const pngs = readdirSync(fixtureDir).filter((f) => f.endsWith(".png"));

const w = await createWorker(["eng", "spa"]);

for (const name of pngs) {
  const path = join(fixtureDir, name);
  console.log("OCR", name, "...");
  let text = "";
  for (const psm of [PSM.SINGLE_COLUMN, PSM.AUTO]) {
    await w.setParameters({ tessedit_pageseg_mode: psm });
    const { data } = await w.recognize(path);
    text += (data.text || "") + "\n";
  }
  text = text.trim();
  writeFileSync(join(fixtureDir, name.replace(/\.png$/i, ".actual-ocr.txt")), text + "\n", "utf8");
  console.log("---", name, "chars", text.length, "---");
  console.log(text);
  console.log("");
}
await w.terminate();
console.log("DONE");
