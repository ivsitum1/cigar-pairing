import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { VitePWA } from "vite-plugin-pwa";

// Dva build targeta iz istog koda:
//   web    (default)        → GitHub Pages pod /cigar-pairing/, PWA + service worker
//   native (--mode native)  → Capacitor Android WebView (APK), korijenski base, bez SW
export default defineConfig(({ mode }) => {
  // U WebView-u app zivi na capacitor://localhost/ pa nema Pages base patha;
  // relativni base cini bundle prenosivim bez obzira na shemu/host.
  // Service worker je tamo suvisan (sve je u APK-u) i samo uvodi drugi,
  // nevidljivi cache sloj koji se ne moze osvjeziti iz Play/APK updatea.
  const native = mode === "native";

  return {
    base: native ? "./" : "/cigar-pairing/",
    plugins: [
      react(),
      tailwindcss(),
      VitePWA({
        // disable: virtual:pwa-register/react ostaje uvozljiv (no-op stub),
        // pa SystemBanners ne treba granati po targetu
        disable: native,
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
      // odvojeni izlaz da se native bundle (relativni base, bez SW) nikad
      // ne moze slucajno deployati na Pages
      outDir: native ? "dist-native" : "dist",
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
  };
});
