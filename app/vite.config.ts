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
      registerType: "autoUpdate",
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
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
