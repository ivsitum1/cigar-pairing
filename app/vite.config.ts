import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { VitePWA } from "vite-plugin-pwa";

// base path odgovara GitHub Pages repo imenu
export default defineConfig({
  base: "/cigar-pairing/",
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      // autoUpdate: nova verzija se preuzme i primijeni sama.
      //
      // Ranije je stajao "prompt", pa je uredaj servirao staru verziju sve dok
      // korisnik ne bi kliknuo traku "nova verzija" — a traka se pojavljivala
      // samo pri ucitavanju stranice, sto kod instaliranog PWA-a zna znaciti
      // danima. Objavljena promjena tada naprosto "nije live".
      // Hashirani asseti cine rucni cacheId bump nepotrebnim.
      registerType: "autoUpdate",
      includeAssets: ["icon.svg", "apple-touch-icon.png"],
      manifest: {
        name: "Cigar & Drink Pairing",
        // Nije drugo ime nego isto ime, rezano tamo gdje mi želimo: launcher
        // kratku oznaku reže na ~12 znakova, pa bi puno ime dalo "Cigar &
        // Drink…". Ovako rez pada na granici riječi, bez trotočja.
        short_name: "Cigar & Drink",
        description:
          "Pairing vodič za cigare i pića — rum, whisky, konjak, gin, kava",
        // ista boja kao --color-humidor u index.css: traka preglednika i
        // splash se nastavljaju na pozadinu appa umjesto da je gase
        theme_color: "#201812",
        background_color: "#201812",
        display: "standalone",
        start_url: "/cigar-pairing/",
        // "any" i "maskable" su NAMJERNO odvojene datoteke: maskable ikonu
        // Android reže u krug, pa pečat u njoj ima 16 % zraka i punu podlogu.
        // Ista slika u obje uloge znači ili odrezan znak ili znak koji pluta
        // premalen u kvadratu.
        icons: [
          {
            src: "icon-192.png",
            sizes: "192x192",
            type: "image/png",
            purpose: "any",
          },
          {
            src: "icon-512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any",
          },
          {
            src: "icon-512-maskable.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "maskable",
          },
          {
            src: "icon.svg",
            sizes: "any",
            type: "image/svg+xml",
            purpose: "any",
          },
        ],
      },
      workbox: {
        // novi service worker preuzima kontrolu odmah, bez cekanja da se
        // zatvore sve kartice — inace autoUpdate ceka isto sto i prompt
        clientsClaim: true,
        skipWaiting: true,
        globPatterns: ["**/*.{js,css,html,svg,png,json,woff2}"],
        // PaddleOCR / ORT worker chunks are 10–27 MB — load on demand, not SW precache
        globIgnores: [
          "**/ocr-paddle-*.js",
          "**/worker-entry-*.js",
          "**/*ort-wasm*.js",
          "**/*ort-wasm*.wasm",
        ],
        // data-cigars (~3 MB) still fits; OCR assets ignored above
        maximumFileSizeToCacheInBytes: 8 * 1024 * 1024,
        runtimeCaching: [
          {
            // PaddleOCR / ORT wasm + model assets (first OCR use)
            urlPattern: ({ url }) =>
              url.hostname.includes("jsdelivr.net") ||
              url.hostname.includes("huggingface.co") ||
              url.hostname.includes("modelscope.cn") ||
              url.pathname.includes("onnxruntime") ||
              url.pathname.endsWith(".wasm") ||
              url.pathname.endsWith(".onnx"),
            handler: "CacheFirst",
            options: {
              cacheName: "ocr-models",
              expiration: { maxEntries: 40, maxAgeSeconds: 60 * 60 * 24 * 30 },
            },
          },
        ],
      },
    }),
  ],
  optimizeDeps: {
    exclude: ["@paddleocr/paddleocr-js"],
  },
  worker: {
    format: "es",
  },
  build: {
    rollupOptions: {
      output: {
        // Lazy OCR chunk zadrzava stabilno ime da ga workbox globIgnores i
        // dalje prepozna — ime se dodjeljuje OVDJE, ne u manualChunks, jer
        // manualChunks bi ga povukao u staticni graf entryja.
        chunkFileNames(info) {
          const ocr = (info.moduleIds ?? []).some(
            (m) => m.includes("@paddleocr/paddleocr-js") || m.includes("onnxruntime"),
          );
          return ocr ? "assets/ocr-paddle-[hash].js" : "assets/[name]-[hash].js";
        },
        // Indeksi po kategoriji (paralelni download + granularni cache).
        // Club atlas / club.json / 101 / bonton ostaju uz svoje lazy stranice.
        manualChunks(id: string) {
          // PaddleOCR/ORT NAMJERNO nema manualChunks ime: imenovani chunk
          // rastopi granicu dinamickog importa, pa entry dobije statican
          // import i <link modulepreload> na 10,9 MB (3,5 MB gzip) — svakom
          // posjetitelju, i onom koji OCR nikad ne dotakne. Bez imena ostaje
          // pravi lazy chunk iza `await import()` u lib/ocrEngine.ts.
          if (/\/src\/data\/.*\.json$/.test(id)) {
            if (
              id.includes("world_outline") ||
              id.includes("club.json") ||
              id.includes("club101") ||
              id.includes("bonton")
            ) {
              return undefined;
            }
            if (id.includes("cigars.json")) return "data-cigars";
            if (id.includes("whiskies.json")) return "data-whiskies";
            if (id.includes("rums.json")) return "data-rums";
            if (id.includes("brandies.json")) return "data-brandies";
            if (
              id.includes("wines.json") ||
              id.includes("gins.json") ||
              id.includes("coffees.json")
            ) {
              return "data-drinks-small";
            }
            // digestifs + aliasi/registar su u eager grafu (data/index.ts).
            // Sve ostalo (dictionary, lexicon, hrGuide, archetypes,
            // clubSources) cita samo lazy Club stranica — bez imena ostaje
            // uz nju umjesto da jedan eager import povuce ~96 kB gzip
            // klupskog teksta u prvo ucitavanje.
            if (
              id.includes("shopping.json") ||
              id.includes("brands.json") ||
              id.includes("cigarIdAliases") ||
              id.includes("drinkIdAliases") ||
              id.includes("drinkIdRegistry") ||
              id.includes("drinkBrands") ||
              id.includes("digestifs.json")
            ) {
              return "data-meta";
            }
            return undefined;
          }
          if (/node_modules\/(react|react-dom|scheduler)\//.test(id)) {
            return "vendor";
          }
          return undefined;
        },
      },
    },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
