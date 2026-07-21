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
        // data-cigars chunk narastao s market katalogom (>2 MiB uncompressed,
        // ~240 kB gzip na wire) — podigni limit da PWA i dalje radi offline
        maximumFileSizeToCacheInBytes: 5 * 1024 * 1024,
      },
    }),
  ],
  build: {
    rollupOptions: {
      output: {
        // Indeksi po kategoriji (paralelni download + granularni cache).
        // Club atlas / club.json / 101 / bonton ostaju uz svoje lazy stranice.
        manualChunks(id: string) {
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
            if (id.includes("shopping.json") || id.includes("brands.json")) {
              return "data-meta";
            }
            return "data-misc";
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
