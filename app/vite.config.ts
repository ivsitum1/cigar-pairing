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
      },
    }),
  ],
  build: {
    rollupOptions: {
      output: {
        // podaci i vendor odvojeni od app koda: izmjena koda ne rusi kes
        // podataka (i obrnuto); world_outline/club ostaju u lazy Club chunku
        manualChunks(id: string) {
          if (/\/src\/data\/.*\.json$/.test(id)) {
            if (id.includes("world_outline") || id.includes("club.json")) {
              return undefined;
            }
            return "data";
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
