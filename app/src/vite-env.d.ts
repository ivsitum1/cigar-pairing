/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_OCR_API_URL?: string;
  readonly VITE_OCR_API_TOKEN?: string;
  readonly VITE_AGE_GATE?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
