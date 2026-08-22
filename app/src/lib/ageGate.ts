// Provjera punoljetnosti — čista logika, odvojena od overlaya radi testova.
//
// `.env.example` je gate opisivao („leave unset (gate ON) or set to 1"), a
// `vite-env.d.ts` deklarirao tip, ali mehanizam nije postojao: prekidač nije
// radio ništa. Ovo je ta obećana strana.

import type { RegionFilter } from "../types";

const KEY = "cigar-pairing-age-ok-v1";

/**
 * Zakonska dob za duhan I alkohol na odabranom tržištu.
 *
 * SAD: savezni Tobacco 21 (2019.) diže duhan na 21, a alkohol je 21 u svim
 * saveznim državama. HR i ostatak EU: 18. Aplikacija je tvrdila 18 svugdje,
 * što je za USA tržište netočno.
 *
 * `ALL` nije zemlja nego „bez filtera" — ostaje na 18 (EU/HR je matično
 * tržište), a gate zato ne barata jednim brojem nego traži punoljetnost
 * *u korisnikovoj zemlji*.
 */
export function legalAgeForMarket(market: RegionFilter): 18 | 21 {
  return market === "USA" ? 21 : 18;
}

/**
 * Je li gate uključen za ovaj build.
 * Zadano UKLJUČEN — QA ga gasi s `VITE_AGE_GATE=0` (ili `off`/`false`),
 * točno kako `.env.example` opisuje.
 */
export function isAgeGateEnabled(
  raw: string | undefined,
): boolean {
  const v = raw?.trim().toLowerCase();
  return !(v === "0" || v === "off" || v === "false" || v === "no");
}

/** Je li gate uključen za ovaj build, prema `VITE_AGE_GATE`. */
export function isAgeGateEnabledFromEnv(): boolean {
  return isAgeGateEnabled(import.meta.env.VITE_AGE_GATE);
}

/** Je li korisnik već potvrdio dob na ovom uređaju. */
export function hasConfirmedAge(): boolean {
  try {
    return localStorage.getItem(KEY) === "1";
  } catch {
    // storage blokiran — ne možemo pamtiti, pa pitamo svaki put
    return false;
  }
}

/** Zapamti potvrdu. Kad storage ne radi, gate vrijedi samo za ovu sesiju. */
export function rememberAgeConfirmed(): void {
  try {
    localStorage.setItem(KEY, "1");
  } catch {
    /* bez pamćenja — pitat ćemo opet pri sljedećem otvaranju */
  }
}

/** Za testove i „odjavu" iz QA alata. */
export function forgetAgeConfirmation(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    /* nema se što obrisati */
  }
}

/** Treba li overlay prikazati na ovom otvaranju. */
export function shouldShowAgeGate(
  enabled: boolean = isAgeGateEnabledFromEnv(),
  confirmed: boolean = hasConfirmedAge(),
): boolean {
  return enabled && !confirmed;
}
