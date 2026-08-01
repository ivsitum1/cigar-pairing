// Provjera punoljetnosti — čista logika, odvojena od overlaya radi testova.
//
// `.env.example` je gate opisivao („leave unset (gate ON) or set to 1"), a
// `vite-env.d.ts` deklarirao tip, ali mehanizam nije postojao: prekidač nije
// radio ništa. Ovo je ta obećana strana.

const KEY = "cigar-pairing-age-ok-v1";

/**
 * Je li gate uključen za ovaj build.
 * Zadano UKLJUČEN — QA ga gasi s `VITE_AGE_GATE=0` (ili `off`/`false`),
 * točno kako `.env.example` opisuje.
 */
export function isAgeGateEnabled(
  raw: string | undefined = import.meta.env.VITE_AGE_GATE,
): boolean {
  const v = raw?.trim().toLowerCase();
  return !(v === "0" || v === "off" || v === "false" || v === "no");
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
  enabled: boolean = isAgeGateEnabled(),
  confirmed: boolean = hasConfirmedAge(),
): boolean {
  return enabled && !confirmed;
}
