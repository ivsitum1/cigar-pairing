import type { CapacitorConfig } from "@capacitor/cli";

// Android shell oko istog Vite bundlea koji ide na GitHub Pages.
// webDir je namjerno dist-native (vite build --mode native): taj build ima
// relativni base i nema service workera — vidi vite.config.ts.
const config: CapacitorConfig = {
  appId: "io.github.ivsitum1.cigarpairing",
  appName: "Cigar Pairing",
  webDir: "dist-native",
  android: {
    // sve (indeksi, fontovi, glazba) je u APK-u; nista se ne dohvaca preko
    // http-a pri startu pa mixed content nije potreban
    allowMixedContent: false,
    // WebView pozadina prije prvog paint-a — bez ovoga app bljesne bijelo
    // izmedju splasha i prve React renderirane slike
    backgroundColor: "#1a1512",
  },
};

export default config;
