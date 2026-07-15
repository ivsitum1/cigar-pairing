// Gradi src/data/world_outline.json iz Natural Earth "land" TopoJSON-a
// (world-atlas@2 land-50m.json — 50m rezolucija drži i manje karipske otoke).
//
//   curl -sL -o /tmp/land-50m.json https://unpkg.com/world-atlas@2.0.2/land-50m.json
//   node scripts/build-world-outline.mjs /tmp/land-50m.json
//
// Izlaz: poligoni kao [[ [lon,lat], ... ], ...] (prsten po poligonu, rupe
// uključene), koordinate zaokružene na 0.1° i deduplicirane — karta koristi
// ekvirektangularnu projekciju pa se lon/lat crta izravno.

import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const OUT = join(dirname(fileURLToPath(import.meta.url)), "..", "src", "data", "world_outline.json");
const MIN_LAT = -45; // viewBox karte pokriva lat -45..75 — Antarktika otpada

const topo = JSON.parse(readFileSync(process.argv[2], "utf8"));
const { scale, translate } = topo.transform;

// TopoJSON arc dekoder: delta-kodirane kvantizirane koordinate
const arcs = topo.arcs.map((arc) => {
  let x = 0, y = 0;
  return arc.map(([dx, dy]) => {
    x += dx; y += dy;
    return [x * scale[0] + translate[0], y * scale[1] + translate[1]];
  });
});

function ringFromArcRefs(arcRefs) {
  const pts = [];
  for (const ref of arcRefs) {
    const idx = ref < 0 ? ~ref : ref;
    const coords = ref < 0 ? [...arcs[idx]].reverse() : arcs[idx];
    // prvi arc ide cijeli; svaki sljedeći bez prve točke (dijele rub)
    pts.push(...(pts.length ? coords.slice(1) : coords));
  }
  return pts;
}

const round1 = (v) => Math.round(v * 10) / 10;
const TOLERANCE = 0.1; // stupnjeva — ispod pixela na world pogledu, a dovoljno
// fino da kontinentalna obala u zoom pogledima (Jadran, Iberija) ne bude kockasta

// Douglas-Peucker po udaljenosti točke od segmenta
function dpSimplify(pts, tol) {
  if (pts.length <= 3) return pts;
  const sqTol = tol * tol;
  const keep = new Uint8Array(pts.length);
  keep[0] = keep[pts.length - 1] = 1;
  const stack = [[0, pts.length - 1]];
  while (stack.length) {
    const [a, b] = stack.pop();
    let maxD = 0, maxI = -1;
    const [ax, ay] = pts[a], [bx, by] = pts[b];
    const dx = bx - ax, dy = by - ay;
    const len2 = dx * dx + dy * dy;
    for (let i = a + 1; i < b; i++) {
      const [px, py] = pts[i];
      let d;
      if (len2 === 0) {
        d = (px - ax) ** 2 + (py - ay) ** 2;
      } else {
        const t = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / len2));
        d = (px - ax - t * dx) ** 2 + (py - ay - t * dy) ** 2;
      }
      if (d > maxD) { maxD = d; maxI = i; }
    }
    if (maxD > sqTol) {
      keep[maxI] = 1;
      stack.push([a, maxI], [maxI, b]);
    }
  }
  return pts.filter((_, i) => keep[i]);
}

// veliki oblici: 0.1° mreža; mali otoci: 0.01° da ne kolabiraju u <3 točke
function dedupeRounded(ring, precision) {
  const f = precision === 2 ? 100 : 10;
  const rnd = (v) => Math.round(v * f) / f;
  const out = [];
  for (const [lon, lat] of ring) {
    const p = [rnd(lon), rnd(lat)];
    const last = out[out.length - 1];
    if (!last || last[0] !== p[0] || last[1] !== p[1]) out.push(p);
  }
  if (out.length > 1) {
    const [first, last] = [out[0], out[out.length - 1]];
    if (first[0] === last[0] && first[1] === last[1]) out.pop();
  }
  return out;
}

// Prsteni koji prelaze antimeridijan (Čukotka, Fiji) crtali bi horizontalnu
// liniju preko cijele karte — razdvoji ih na lance po strani ±180.
// Svaki lanac počinje/završava na meridijanu pa ga fill ispravno zatvori.
function splitAntimeridian(ring) {
  const chains = [[ring[0]]];
  for (let i = 1; i < ring.length; i++) {
    const prev = ring[i - 1], cur = ring[i];
    if (Math.abs(cur[0] - prev[0]) > 180) chains.push([]);
    chains[chains.length - 1].push(cur);
  }
  if (chains.length === 1) return chains;
  // spoji zadnji lanac s prvim ako se prsten ne lomi između kraja i početka
  const first = chains[0][0], last = ring[ring.length - 1];
  if (Math.abs(first[0] - last[0]) <= 180) {
    chains[0] = [...chains.pop(), ...chains[0]];
  }
  return chains;
}

const bboxOf = (ring) => {
  let minLon = 180, maxLon = -180, minLat = 90, maxLat = -90;
  for (const [lon, lat] of ring) {
    if (lon < minLon) minLon = lon;
    if (lon > maxLon) maxLon = lon;
    if (lat < minLat) minLat = lat;
    if (lat > maxLat) maxLat = lat;
  }
  return { minLon, maxLon, minLat, maxLat };
};

// zoom pogledi: u njima čuvamo i male otoke u finoj rezoluciji
// (Karibi: Sv. Lucija, Barbados...; Europa: Jadran, Balearidi, Egej...)
const ZOOMS = [
  { minLon: -108, maxLon: -50, minLat: 1, maxLat: 37 },  // Karibi
  { minLon: -12, maxLon: 48, minLat: 34, maxLat: 62 },   // Europa
];
const inZoom = (b) =>
  ZOOMS.some(
    (z) =>
      b.maxLon >= z.minLon && b.minLon <= z.maxLon &&
      b.maxLat >= z.minLat && b.minLat <= z.maxLat,
  );

// otoci s markerima na karti izvan Kariba — uvijek ih zadrži
const KEEP_POINTS = [
  [-64.8, 32.3], // Bermuda
  [55.5, -4.7],  // Sejšeli (Mahé)
  [55.5, -21.1], // Réunion
  [57.6, -20.3], // Mauricijus
  [178, -17.8],  // Fiji
];
const nearKeepPoint = (b) =>
  KEEP_POINTS.some(
    ([lon, lat]) =>
      lon >= b.minLon - 0.5 && lon <= b.maxLon + 0.5 &&
      lat >= b.minLat - 0.5 && lat <= b.maxLat + 0.5,
  );

const polygons = [];
for (const geom of topo.objects.land.geometries) {
  const polys = geom.type === "Polygon" ? [geom.arcs] : geom.arcs;
  for (const poly of polys) {
    const rings = [];
    for (const arcRefs of poly) {
      const raw = ringFromArcRefs(arcRefs);
      const b = bboxOf(raw);
      if (b.maxLat < MIN_LAT) continue; // Antarktika
      const size = Math.max(b.maxLon - b.minLon, b.maxLat - b.minLat);
      // sitni otočići bez markera na karti su nevidljivi na world pogledu;
      // otoci s markerima (Bermuda, Sejšeli...) čuvaju se preko KEEP liste
      const kept = inZoom(b) || nearKeepPoint(b);
      if (size < 0.4 && !kept) continue;
      // fina rezolucija samo za otoke u zoom pogledima / s markerom;
      // kontinentalne mase (i kad sijeku zoom bbox) idu grubo
      const fine = kept && size < 12;
      for (const chain of splitAntimeridian(raw)) {
        const ring = dedupeRounded(
          dpSimplify(chain, fine ? 0.02 : TOLERANCE),
          fine ? 2 : 1,
        );
        if (ring.length < 3) continue;
        rings.push(ring);
      }
    }
    if (rings.length) polygons.push(rings);
  }
}

writeFileSync(OUT, JSON.stringify(polygons));
const kb = (JSON.stringify(polygons).length / 1024).toFixed(0);
console.log(`world_outline.json: ${polygons.length} poligona, ${kb} KB`);
