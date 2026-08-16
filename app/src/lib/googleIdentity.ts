// Prijava Google računom — samo zato da potpis dojma bude stabilan.
//
// Zašto uopće: dojmovi se u repou spajaju po ključu (osoba, cigara), a "osoba"
// je dosad bio slobodan nadimak. Isti čovjek s dva uređaja i dva različito
// upisana nadimka broji se kao dvoje ljudi — njegov glas uđe dvaput u prosjek,
// a `strengthFromTasting` slaže o tome koliko je ljudi cigaru stvarno pušilo.
// Google račun daje jedan stabilan `sub` po čovjeku i tu rupu zatvara.
//
// Što ovo NIJE: provjeren identitet. App je statična stranica na GitHub
// Pagesu, nema servera koji bi Googleov token provjerio, pa je potpis ovdje
// pogodnost — ne dokaz. Tko hoće lagati o tome tko je, može ručno urediti
// tijelo prijave i bez ovoga. Trenutak kad potpis postane dokaz je trenutak
// kad `backend/` počne provjeravati token; do tada se prosjeku vjeruje jednako
// koliko i prije.
//
// Privatnost: repo je javan. U prijavu ide SAMO ime i kratki haš `sub`-a.
// E-mail se nikad ne sprema, ne šalje i ne izlazi iz ove datoteke, a ni sam
// `sub` ne ide u repo — haš je jednosmjeran i služi isključivo za spajanje
// dviju prijava iste osobe.

const GIS_SRC = "https://accounts.google.com/gsi/client";

/** Ono malo iz Googleovog tokena što nas zanima. E-mail namjerno ne ulazi. */
export interface GoogleIdentity {
  /** Googleov trajni identifikator korisnika. Ostaje u pregledniku. */
  sub: string;
  /** Ime za prikaz; korisnik ga smije prepisati prije slanja. */
  name: string;
}

/**
 * Client ID dolazi iz okoline, kao i za OCR servis (`VITE_OCR_API_URL`). Bez
 * njega se prijava nigdje ne nudi — build bez postavljenog ID-a izgleda točno
 * kao app prije ove promjene.
 */
export function googleClientId(): string {
  return (import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined)?.trim() ?? "";
}

export function isGoogleConfigured(): boolean {
  return googleClientId().length > 0;
}

/** base64url → tekst, s ispravnim čitanjem dijakritike u imenu. */
function decodeSegment(segment: string): string {
  const padded = segment.replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(padded + "=".repeat((4 - (padded.length % 4)) % 4));
  const bytes = Uint8Array.from(raw, (ch) => ch.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

/**
 * Sadržaj Googleovog ID tokena, bez provjere potpisa — vidi napomenu na vrhu.
 * Vraća null za sve što ne izgleda kao token s upotrebljivim `sub`.
 */
export function decodeIdToken(jwt: string): GoogleIdentity | null {
  const parts = jwt.split(".");
  if (parts.length !== 3) return null;
  try {
    const payload = JSON.parse(decodeSegment(parts[1])) as Record<string, unknown>;
    const sub = typeof payload.sub === "string" ? payload.sub.trim() : "";
    if (!sub) return null;
    const name =
      typeof payload.name === "string" && payload.name.trim()
        ? payload.name.trim()
        : typeof payload.given_name === "string"
          ? payload.given_name.trim()
          : "";
    return { sub, name };
  } catch {
    return null;
  }
}

/**
 * Potpis koji smije u javni repo: `g_` + prvih 12 znakova SHA-256 haša.
 * Dovoljno da se dvije prijave iste osobe spoje, premalo da se iz njega vrati
 * Googleov račun.
 */
export async function tasterIdFromSub(sub: string): Promise<string> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(sub));
  const hex = [...new Uint8Array(digest)]
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
  return `g_${hex.slice(0, 12)}`;
}

interface GoogleAccountsId {
  initialize: (config: {
    client_id: string;
    callback: (response: { credential?: string }) => void;
    auto_select?: boolean;
    cancel_on_tap_outside?: boolean;
  }) => void;
  renderButton: (parent: HTMLElement, options: Record<string, unknown>) => void;
  disableAutoSelect: () => void;
}

declare global {
  interface Window {
    google?: { accounts?: { id?: GoogleAccountsId } };
  }
}

let scriptPromise: Promise<GoogleAccountsId | null> | null = null;

/**
 * Googleova skripta se povlači tek kad je prijava stvarno na ekranu — ne na
 * svakom otvaranju appa. Neuspjeh (offline, blokiran skript) vraća null i
 * ostavlja upisivanje imena rukom kao put koji uvijek radi.
 */
export function loadGoogleIdentity(): Promise<GoogleAccountsId | null> {
  if (!isGoogleConfigured()) return Promise.resolve(null);
  if (window.google?.accounts?.id) return Promise.resolve(window.google.accounts.id);
  if (scriptPromise) return scriptPromise;

  scriptPromise = new Promise<GoogleAccountsId | null>((resolve) => {
    const existing = document.querySelector<HTMLScriptElement>(`script[src="${GIS_SRC}"]`);
    const script = existing ?? document.createElement("script");
    const done = () => resolve(window.google?.accounts?.id ?? null);
    script.addEventListener("load", done);
    script.addEventListener("error", () => resolve(null));
    if (!existing) {
      script.src = GIS_SRC;
      script.async = true;
      script.defer = true;
      document.head.appendChild(script);
    }
  }).then((api) => {
    if (!api) scriptPromise = null; // neuspjeh se smije pokušati ponovno
    return api;
  });
  return scriptPromise;
}

/** Googleov gumb u zadani element; poziva `onIdentity` kad prijava uspije. */
export async function renderGoogleButton(
  parent: HTMLElement,
  onIdentity: (identity: GoogleIdentity) => void,
): Promise<boolean> {
  const api = await loadGoogleIdentity();
  if (!api) return false;
  api.initialize({
    client_id: googleClientId(),
    callback: (response) => {
      const identity = response.credential ? decodeIdToken(response.credential) : null;
      if (identity) onIdentity(identity);
    },
    auto_select: false,
    cancel_on_tap_outside: true,
  });
  api.renderButton(parent, {
    type: "standard",
    theme: "filled_black",
    size: "large",
    text: "signin_with",
    shape: "pill",
  });
  return true;
}

/** Odjava je lokalna — Googleu se ništa ne javlja jer mu ništa nismo ni slali. */
export async function forgetGoogleAutoSelect(): Promise<void> {
  const api = window.google?.accounts?.id;
  api?.disableAutoSelect();
}
