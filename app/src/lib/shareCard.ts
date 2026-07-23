// Share-kartica spoja: model (čist, testabilan) + canvas render + dijeljenje.
// Backup/Export ostaje u store/collection.ts — ovo je samo vizualna kartica.

import type { Cigar, Drink, Lang, PairingReason, ServeStyle } from "../types";

export interface ShareCardModel {
  eyebrow: string; // "DOSJE · SPOJ"
  cigarLine: string; // "Padrón 1964 · Robusto"
  drinkLine: string; // "Diplomático Reserva · Kap vode"
  score: number; // 0..100
  reasons: string[]; // do 2 pozitivna razloga, lokalizirano
  footer: string; // URL
}

const SERVE_LABEL: Record<ServeStyle, { hr: string; en: string }> = {
  neat: { hr: "Čisto", en: "Neat" },
  water: { hr: "Kap vode", en: "Splash of water" },
  rocks: { hr: "Na ledu", en: "On the rocks" },
  highball: { hr: "Highball", en: "Highball" },
  cola: { hr: "S colom", en: "With cola" },
};

const FOOTER = "ivsitum1.github.io/cigar-pairing";

/** Sastavi tekstualni model kartice. Čista funkcija — jezgra testova. */
export function buildShareCardModel(
  cigar: Cigar,
  drink: Drink,
  serve: ServeStyle | undefined,
  score: number,
  reasons: PairingReason[],
  lang: Lang,
): ShareCardModel {
  const cigarVitola = cigar.vitola && cigar.vitola !== "—" ? ` · ${cigar.vitola}` : "";
  const serveSuffix =
    serve && serve !== "neat" ? ` · ${SERVE_LABEL[serve][lang]}` : "";
  const topReasons = reasons
    .filter((r) => r.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 2)
    .map((r) => r.text[lang]);

  return {
    eyebrow: lang === "hr" ? "DOSJE · SPOJ" : "DOSSIER · PAIRING",
    cigarLine: `${cigar.brand} ${cigar.line}${cigarVitola}`,
    drinkLine: `${drink.name}${serveSuffix}`,
    score: Math.round(score),
    reasons: topReasons,
    footer: FOOTER,
  };
}

// ── Canvas render (samo u pregledniku) ─────────────────────────────
const PALETTE = {
  bg: "#201812",
  cedar: "#2c211a",
  gold: "#c9a35c",
  goldShine: "#e3c68b",
  paper: "#ede0c8",
  dim: "#a98f72",
};

const wrapLines = (
  ctx: CanvasRenderingContext2D,
  text: string,
  maxWidth: number,
): string[] => {
  const words = text.split(" ");
  const lines: string[] = [];
  let line = "";
  for (const w of words) {
    const test = line ? `${line} ${w}` : w;
    if (ctx.measureText(test).width > maxWidth && line) {
      lines.push(line);
      line = w;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);
  return lines;
};

/** Nacrtaj karticu na canvasu i vrati PNG blob. Baca ako nema canvasa (test env). */
export async function renderShareCardPng(model: ShareCardModel): Promise<Blob> {
  const W = 1080;
  const H = 1350;
  const canvas = document.createElement("canvas");
  canvas.width = W;
  canvas.height = H;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("canvas 2d context unavailable");

  // fontovi (bundlani preko fontsource) — čekaj da budu spremni
  try {
    await Promise.all([
      document.fonts.load('400 64px "Marcellus"'),
      document.fonts.load('400 40px "Marcellus"'),
    ]);
  } catch {
    /* fallback na serif ako font nije dostupan */
  }
  const display = (px: number) => `400 ${px}px "Marcellus", Georgia, serif`;
  const sans = (px: number, weight = 400) =>
    `${weight} ${px}px "Manrope Variable", system-ui, sans-serif`;

  // pozadina + topli sjaj
  ctx.fillStyle = PALETTE.bg;
  ctx.fillRect(0, 0, W, H);
  const glow = ctx.createRadialGradient(W / 2, 0, 0, W / 2, 0, 700);
  glow.addColorStop(0, "rgba(74,51,29,0.55)");
  glow.addColorStop(1, "rgba(74,51,29,0)");
  ctx.fillStyle = glow;
  ctx.fillRect(0, 0, W, H);

  const PAD = 96;
  const cx = W / 2;
  let y = 150;

  const bandRule = (yy: number) => {
    const grad = ctx.createLinearGradient(PAD, 0, W - PAD, 0);
    grad.addColorStop(0, "rgba(201,163,92,0)");
    grad.addColorStop(0.2, PALETTE.gold);
    grad.addColorStop(0.8, PALETTE.gold);
    grad.addColorStop(1, "rgba(201,163,92,0)");
    ctx.fillStyle = grad;
    ctx.fillRect(PAD, yy, W - PAD * 2, 2);
  };

  ctx.textAlign = "center";

  // eyebrow
  ctx.font = sans(26, 600);
  ctx.fillStyle = PALETTE.gold;
  ctx.letterSpacing = "10px";
  ctx.fillText(model.eyebrow, cx, y);
  ctx.letterSpacing = "0px";
  y += 40;
  bandRule(y);
  y += 90;

  // cigara
  ctx.font = display(66);
  ctx.fillStyle = PALETTE.paper;
  for (const line of wrapLines(ctx, model.cigarLine, W - PAD * 2)) {
    ctx.fillText(line, cx, y);
    y += 78;
  }

  // "uz"
  y += 6;
  ctx.font = display(34);
  ctx.fillStyle = PALETTE.dim;
  ctx.fillText("×", cx, y);
  y += 60;

  // piće
  ctx.font = display(60);
  ctx.fillStyle = PALETTE.goldShine;
  for (const line of wrapLines(ctx, model.drinkLine, W - PAD * 2)) {
    ctx.fillText(line, cx, y);
    y += 72;
  }

  // score krug
  y += 70;
  const r = 96;
  ctx.beginPath();
  ctx.arc(cx, y, r, 0, Math.PI * 2);
  ctx.strokeStyle = PALETTE.gold;
  ctx.lineWidth = 3;
  ctx.stroke();
  ctx.font = display(72);
  ctx.fillStyle = PALETTE.goldShine;
  ctx.textBaseline = "middle";
  ctx.fillText(String(model.score), cx, y + 2);
  ctx.textBaseline = "alphabetic";
  ctx.font = sans(22, 600);
  ctx.fillStyle = PALETTE.dim;
  ctx.letterSpacing = "4px";
  ctx.fillText("SLAGANJE", cx, y + r + 44);
  ctx.letterSpacing = "0px";
  y += r + 120;

  // razlozi
  ctx.font = sans(30);
  ctx.fillStyle = PALETTE.paper;
  for (const reason of model.reasons) {
    for (const line of wrapLines(ctx, reason, W - PAD * 2)) {
      ctx.fillText(line, cx, y);
      y += 42;
    }
    y += 10;
  }

  // footer
  bandRule(H - 150);
  ctx.font = sans(26, 600);
  ctx.fillStyle = PALETTE.gold;
  ctx.letterSpacing = "3px";
  ctx.fillText(model.footer, cx, H - 100);
  ctx.letterSpacing = "0px";

  return await new Promise<Blob>((resolve, reject) => {
    canvas.toBlob(
      (b) => (b ? resolve(b) : reject(new Error("toBlob failed"))),
      "image/png",
    );
  });
}

/** Podijeli (Web Share, files) ili preuzmi PNG. Vraća kako je završilo. */
export async function sharePairing(
  model: ShareCardModel,
): Promise<"shared" | "downloaded"> {
  const blob = await renderShareCardPng(model);
  const file = new File([blob], "pairing.png", { type: "image/png" });
  const nav = navigator as Navigator & {
    canShare?: (data?: ShareData) => boolean;
  };
  if (nav.canShare?.({ files: [file] }) && navigator.share) {
    await navigator.share({ files: [file], title: "Cigar & Drink Pairing" });
    return "shared";
  }
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "pairing.png";
  a.click();
  URL.revokeObjectURL(url);
  return "downloaded";
}
