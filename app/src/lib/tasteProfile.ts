// Tvoja ocjena nadjacava katalog — i za prikaz i za pairing.
//
// Katalogova snaga i tijelo su procjena; tvoja je mjerenje. Zato se, kad
// ocjena postoji, ona upisuje u cigaru prije nego sto je pairing uopce vidi,
// i kartica prestaje pisati "procijenjen profil".
import type { Cigar } from "../types";
import { getTasteProfile, type TasteProfiles } from "../store/tasteProfile";

/** Cigara s tvojom ocjenom umjesto katalogove procjene, ako ocjena postoji. */
export function withTaste(cigar: Cigar, profiles?: TasteProfiles): Cigar {
  const lineId = cigar.id;
  const p = profiles ? profiles[lineId] : getTasteProfile(lineId);
  if (!p) return cigar;
  if (p.strength === cigar.strength && p.body === cigar.body && !cigar.profileEstimated) {
    return cigar;
  }
  return {
    ...cigar,
    strength: p.strength,
    body: p.body,
    profileEstimated: false,
    profileFromUser: true,
  };
}

/** Isto nad popisom — jedno mjesto za sve stranice koje hrane pairing. */
export function withTasteAll(cigars: Cigar[], profiles?: TasteProfiles): Cigar[] {
  if (profiles && Object.keys(profiles).length === 0) return cigars;
  return cigars.map((c) => withTaste(c, profiles));
}
