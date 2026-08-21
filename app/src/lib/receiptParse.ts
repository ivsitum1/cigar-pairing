/** Heuristic receipt line parsing → catalog matches (HR shop formats). */
import { matchOcrText, tokenize, STOP, type OcrCandidate } from "./ocrMatch";
import { lookupBarcodeInText, type BarcodeHit } from "./ocrBarcode";

export interface ReceiptLineMatch {
  raw: string;
  candidate: OcrCandidate | null;
  score: number;
  qty: number;
  selected: boolean;
  barcode: BarcodeHit | null;
  barcodeCandidate: OcrCandidate | null;
}

const BOILERPLATE =
  /^(racun|račun|mp\s*račun|receipt|total|suma|porez|pdv|eur|kn|hrk|visa|mastercard|gotovina|hvala|thank|shop|store|adresa|oib|datum|vrijeme|kolicina|količina|cijena|price|subtotal|promo|rabat|popust|ukupno|osnovica|za\s*platiti|sredstvo|kartice|kartica|operator|blagajna|prodavac|prodavač|naziv|artikla|robe|usluge|iznos|stavke|tgr|jm|kom|zki|jir|camelot|tobacco|petica|agram|frankopanska|branimirova|havana|slovima|dospije|mjesto|izdavanja|obracun|obrada|wand|monri|thor)\b/i;

const PRICE_ONLY = /^[\d\s.,€$%]+\s*(eur|kn|hrk|€|kom)?$/i;

/** Non-cigar noise often on tobacco-shop receipts. */
const NON_CIGAR =
  /\b(cedevita|bomboni|chicken|candy|bonbon|upaljac|upaljač|cutter|humidor\s*gel|fluid|benzin)\b/i;

const QTY_KOM =
  /(\d+)(?:[,.]\d+)?\s*(?:kom|kom\.|pcs|x)\b/i;

/** Box-count suffix on shop labels: Torpedo/24, Robusto/10 */
const BOX_SUFFIX = /\/\d{1,3}\b/g;

/** POS SKU / barcode crumbs */
const SKU_TOKEN = /\b(?:cr|sku|ean)?\s?\d{6,}\b/gi;

const TAX_CRUFT = /\b(?:r\s*25|r25|25\s*%|pdv)\b/gi;

/** Shop abbreviations seen on HR tobacco receipts. */
const ABBREV: Array<[RegExp, string]> = [
  [/\bconn\.?/gi, "connecticut "],
  [/\breserv\b/gi, "reserve"],
  [/\b20th\s*an\.?\b/gi, "20th anniversary"],
  [/\bsungrown\b/gi, "sun grown"],
  [/\bnic\b/gi, ""], // "BUNDLE NIC" = Nicaragua filler noise
  // typical tesseract garble on HR thermal receipts
  [/\bdontomas\b/gi, "don tomas"],
  [/\bdontolia\w*/gi, "don tomas"],
  [/\bdontoli\w*/gi, "don tomas"],
  [/\bdon\s*tovias\b/gi, "don tomas"],
  [/\br?cths?chi[dl]\b/gi, "rothschild"],
  [/\broh?sch[il][dl]\b/gi, "rothschild"],
  [/\bestrela\b/gi, "estrella"],
  [/\bperoond\b/gi, "perdomo"],
  [/\bserie\s*0\b/gi, "serie o"], // zero misread as O
  [/\bserie\s*32\b/gi, "serie o"],
  [/\bserie\s*6\b/gi, "serie g"],
];

const BRAND_RESCUE: Array<[RegExp, string]> = [
  [/\b(?:dov?t(?:om|ol|on)[a-z]{1,6}|dontolias?|dontolia>?|dontomas|don\s*tovias)\b/gi, "don tomas"],
  [/\b(?:r[oa]?ths?[cg]h?[il]{1,2}d|roh?s?ch[il]{1,2}d|rothsghld)\b/gi, "rothschild"],
  [/\b(?:church|chrchll|churc?hill?)\b/gi, "churchill"],
  [/\b(?:peroond|perdom0)\b/gi, "perdomo"],
  [/\b(?:estrela|estrelaa?)\b/gi, "estrella"],
];

function extractQty(line: string): { qty: number; rest: string } {
  const kom = line.match(QTY_KOM);
  if (kom) {
    const qty = Math.max(1, parseInt(kom[1], 10));
    const rest = line.replace(kom[0], " ").replace(/\s+/g, " ").trim();
    return { qty, rest };
  }
  const m =
    line.match(/^\s*(\d+)\s*[x×*]\s*(.+)$/i) ||
    line.match(/^(.+?)\s+[x×*]\s*(\d+)\s*$/i);
  if (m) {
    if (/^\d+$/.test(m[1])) return { qty: Math.max(1, parseInt(m[1], 10)), rest: m[2].trim() };
    return { qty: Math.max(1, parseInt(m[2], 10)), rest: m[1].trim() };
  }
  return { qty: 1, rest: line.trim() };
}

/** Strip prices, tax codes, box counts, SKUs — leave brand/line text for matching. */
export function cleanReceiptProductName(line: string): string {
  let s = line;
  s = s.replace(TAX_CRUFT, " ");
  s = s.replace(SKU_TOKEN, " ");
  s = s.replace(BOX_SUFFIX, " ");
  // trailing money columns: 15,85 15,85 or 5.80
  s = s.replace(/(?:^|\s)\d{1,4}[,.]\d{2}(?:\s|$)/g, " ");
  s = s.replace(/\b\d{1,3}\s*%/g, " ");
  for (const [re, repl] of BRAND_RESCUE) s = s.replace(re, repl);
  for (const [re, repl] of ABBREV) s = s.replace(re, repl);
  s = s.replace(/\s+/g, " ").trim();
  // "by Cusano" → keep Cusano tokens
  s = s.replace(/\bby\b/gi, " ");
  return s.replace(/\s+/g, " ").trim();
}

function isNoise(line: string): boolean {
  const t = line.trim();
  if (t.length < 4) return true;
  if (BOILERPLATE.test(t)) return true;
  if (PRICE_ONLY.test(t)) return true;
  if (NON_CIGAR.test(t)) return true;
  // fiscal hashes / long hex
  if (/^[0-9a-f-]{20,}$/i.test(t.replace(/\s/g, ""))) return true;
  const tokens = tokenize(t).filter((w) => !STOP.has(w));
  if (tokens.length === 0) return true;
  return false;
}

/** Split OCR blob into candidate product lines and match each against catalog. */
export function parseReceiptText(
  text: string,
  candidates: OcrCandidate[],
): ReceiptLineMatch[] {
  const candidateById = new Map(candidates.map((c) => [c.id, c]));
  const rawLines = text
    .split(/\n+/)
    .map((l) => l.replace(/\s+/g, " ").trim())
    .filter(Boolean);

  const out: ReceiptLineMatch[] = [];
  const seen = new Set<string>();

  for (const raw of rawLines) {
    if (isNoise(raw)) continue;
    const { qty, rest } = extractQty(raw);
    const barcode = lookupBarcodeInText(raw);
    const barcodeCandidate = barcode ? (candidateById.get(barcode.itemId) ?? null) : null;
    const cleaned = cleanReceiptProductName(rest);
    if ((!cleaned || isNoise(cleaned)) && !barcodeCandidate) continue;
    // need at least one “product-like” token after cleaning
    if (
      tokenize(cleaned).filter((w) => !STOP.has(w)).length < 2 &&
      !barcodeCandidate
    ) continue;

    const hit = cleaned ? matchOcrText(cleaned, candidates) : null;
    const chosen = hit?.candidate ?? barcodeCandidate;
    if (!chosen) continue;
    const sameAsBarcode = barcodeCandidate && hit?.candidate
      ? barcodeCandidate.id === hit.candidate.id
      : false;
    const selected = barcodeCandidate
      ? sameAsBarcode || !hit
      : Boolean(hit && hit.score >= 2);
    const effectiveScore = hit?.score ?? (barcodeCandidate ? 1.5 : 0);
    if (seen.has(chosen.id)) {
      const prev = out.find((x) => x.candidate?.id === chosen.id);
      if (prev) {
        prev.qty += qty;
        prev.selected ||= selected;
        prev.score = Math.max(prev.score, effectiveScore);

        // Prefer barcode evidence that matches the chosen (OCR-selected) candidate.
        // This avoids a scenario where the first occurrence shows "EAN hint" but later
        // lines confirm the same cigar id with a matching barcode.
        if (selected && barcodeCandidate?.id === chosen.id) {
          prev.barcode = barcode;
          prev.barcodeCandidate = barcodeCandidate;
        } else if (!prev.barcodeCandidate && barcodeCandidate) {
          prev.barcodeCandidate = barcodeCandidate;
          prev.barcode = barcode;
        }
      }
      continue;
    }
    seen.add(chosen.id);
    out.push({
      raw: cleaned || raw,
      candidate: chosen,
      score: effectiveScore,
      qty,
      selected,
      barcode,
      barcodeCandidate,
    });
  }

  if (out.length === 0) {
    const hit = matchOcrText(text, candidates);
    if (hit) {
      out.push({
        raw: hit.candidate.label,
        candidate: hit.candidate,
        score: hit.score,
        qty: 1,
        selected: true,
        barcode: null,
        barcodeCandidate: null,
      });
    }
  }

  return out.sort((a, b) => b.score - a.score);
}
