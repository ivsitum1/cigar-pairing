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
      // prompt: korisnik dobije "nova verzija" traku umjesto tihe zamjene
      // usred koristenja; hashirani asseti cine rucni cacheId bump nepotrebnim
      registerType: "prompt",
      includeAssets: ["icon.svg"],
      manifest: {
        name: "Cigar & Drink Pairing",
        short_name: "Pairing",
        description:
          "Pairing vodič za cigare i pića — rum, whisky, konjak, gin, kava",
        theme_color: "#1a1512",
        background_color: "#1a1512",
        display: "standalone",
        start_url: "/cigar-pairing/",
        icons: [
          {
            src: "icon-192.png",
            sizes: "192x192",
            type: "image/png",
          },
          {
            src: "icon-512.png",
            sizes: "512x512",
            type: "image/png",
            purpose: "any maskable",
          },
        ],
      },
      workbox: {
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
