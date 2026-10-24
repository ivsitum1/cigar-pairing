// Tvoja ocjena nadjacava katalog — i za prikaz i za pairing.
//
// Katalogova snaga, tijelo i intenzitet note su procjena (osim shop mjerenja);
// tvoja je mjerenje. Zato se, kad ocjena postoji, ona upisuje u cigaru prije
// nego sto je pairing uopce vidi, i kartica prestaje pisati "procijenjen profil".
import type { Cigar } from "../types";
import { getTasteProfile, type TasteProfiles } from "../store/tasteProfile";

/** Cigara s tvojom ocjenom umjesto katalogove procjene, ako ocjena postoji. */
export function withTaste(cigar: Cigar, profiles?: TasteProfiles): Cigar {
  const lineId = cigar.id;
  const p = profiles ? profiles[lineId] : getTasteProfile(lineId);
  if (!p) return cigar;

  const nextStrength = p.strength;
  const nextBody = p.body;
  const catalogFlavor = cigar.flavorIntensity ?? cigar.body;
  const nextFlavor =
    typeof p.flavorIntensity === "number" ? p.flavorIntensity : catalogFlavor;

  const same =
    nextStrength === cigar.strength &&
    nextBody === cigar.body &&
    nextFlavor === catalogFlavor &&
    !cigar.profileEstimated;
  if (same) return cigar;

  return {
    ...cigar,
    strength: nextStrength,
    body: nextBody,
    flavorIntensity: nextFlavor,
    profileEstimated: false,
    profileFromUser: true,
  };
}

/** Isto nad popisom — jedno mjesto za sve stranice koje hrane pairing. */
export function withTasteAll(cigars: Cigar[], profiles?: TasteProfiles): Cigar[] {
  if (profiles && Object.keys(profiles).length === 0) return cigars;
  return cigars.map((c) => withTaste(c, profiles));
}
