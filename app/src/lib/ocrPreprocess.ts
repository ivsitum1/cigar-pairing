// Predobrada fotke za OCR: skaliranje na ~1600px, grayscale s rastegnutim
// kontrastom, te normalna + invertirana varijanta (svijetli tekst na tamnom).

const TARGET_DIM = 1600;
const MAX_UPSCALE = 3;

export async function preprocessImage(file: File): Promise<Blob[]> {
  const bmp = await createImageBitmap(file);
  const factor = Math.min(MAX_UPSCALE, TARGET_DIM / Math.max(bmp.width, bmp.height));
  const w = Math.max(1, Math.round(bmp.width * factor));
  const h = Math.max(1, Math.round(bmp.height * factor));

  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext("2d");
  if (!ctx) throw new Error("canvas 2d context unavailable");
  ctx.imageSmoothingQuality = "high";
  ctx.drawImage(bmp, 0, 0, w, h);
  bmp.close();

  const img = ctx.getImageData(0, 0, w, h);
  const d = img.data;

  // luminancija + histogram za rastezanje kontrasta (5./95. percentil)
  const lum = new Uint8ClampedArray(w * h);
  const hist = new Array<number>(256).fill(0);
  for (let i = 0, p = 0; i < d.length; i += 4, p++) {
    const y = Math.round(0.299 * d[i] + 0.587 * d[i + 1] + 0.114 * d[i + 2]);
    lum[p] = y;
    hist[y]++;
  }
  const total = w * h;
  let lo = 0;
  let hi = 255;
  for (let v = 0, acc = 0; v < 256; v++) {
    acc += hist[v];
    if (acc >= total * 0.05) {
      lo = v;
      break;
    }
  }
  for (let v = 255, acc = 0; v >= 0; v--) {
    acc += hist[v];
    if (acc >= total * 0.05) {
      hi = v;
      break;
    }
  }
  const range = Math.max(1, hi - lo);

  const variants: Blob[] = [];
  for (const invert of [false, true]) {
    for (let p = 0; p < lum.length; p++) {
      let y = Math.round(((lum[p] - lo) / range) * 255);
      y = Math.max(0, Math.min(255, y));
      if (invert) y = 255 - y;
      const i = p * 4;
      d[i] = d[i + 1] = d[i + 2] = y;
      d[i + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    const blob = await new Promise<Blob>((resolve, reject) =>
      canvas.toBlob(
        (b) => (b ? resolve(b) : reject(new Error("toBlob failed"))),
        "image/jpeg",
        0.9,
      ),
    );
    variants.push(blob);
  }
  return variants;
}
