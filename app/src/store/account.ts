// Prijavljeni račun — ime i potpis, ništa više.
//
// `store/taster` drži ime koje si sam upisao; ovaj store drži ime koje je
// stiglo prijavom i uz njega stabilan potpis (`g_…`, haš Googleovog `sub`).
// Dvije stvari stoje odvojeno namjerno: ime se smije prepisati prije slanja, a
// potpis ne — on je jedino po čemu se dvije prijave iste osobe u repou spoje.
//
// U pregledniku ostaje samo ovo. E-mail ne ulazi ovamo ni u kojem obliku.
import { useSyncExternalStore } from "react";
import { normalizeTasterName } from "./taster";

export interface Account {
  /** Ime za prikaz, iz prijave. */
  name: string;
  /** Potpis koji smije u javni repo — `g_` + 12 znakova haša. */
  tasterId: string;
  /** ISO datum prijave. */
  at: string;
}

const KEY = "cigar-pairing-account-v1";

/** Potpis mora izgledati kao potpis; sve drugo je zapis kojem se ne vjeruje. */
const isTasterId = (value: unknown): value is string =>
  typeof value === "string" && /^g_[0-9a-f]{12}$/.test(value);

export function normalizeAccount(raw: unknown): Account | null {
  if (!raw || typeof raw !== "object") return null;
  const v = raw as Partial<Account>;
  if (!isTasterId(v.tasterId)) return null;
  return {
    name: normalizeTasterName(v.name),
    tasterId: v.tasterId,
    at: typeof v.at === "string" ? v.at : new Date().toISOString(),
  };
}

function read(): Account | null {
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? normalizeAccount(JSON.parse(raw)) : null;
  } catch {
    return null;
  }
}

let cache: Account | null = read();
const listeners = new Set<() => void>();

function emit() {
  for (const fn of listeners) fn();
}

export function useAccount(): Account | null {
  return useSyncExternalStore(
    (fn) => {
      listeners.add(fn);
      return () => listeners.delete(fn);
    },
    () => cache,
    () => cache,
  );
}

export function setAccount(account: Account | null) {
  cache = account ? normalizeAccount(account) : null;
  try {
    if (cache) localStorage.setItem(KEY, JSON.stringify(cache));
    else localStorage.removeItem(KEY);
  } catch {
    // prijava koja se ne uspije zapisati i dalje vrijedi za ovu sesiju
  }
  emit();
}

export function clearAccount() {
  setAccount(null);
}
