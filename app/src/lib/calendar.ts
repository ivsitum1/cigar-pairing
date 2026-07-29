// Kalendar dnevnika: mjesečna mreža + grupiranje zapisa po danu.
// Čista logika, bez Reacta — da se može testirati bez DOM-a.

export interface CalendarDay {
  /** `YYYY-MM-DD` u lokalnoj zoni (dan kakav korisnik vidi, ne UTC). */
  key: string;
  date: Date;
  dayOfMonth: number;
  /** false = dan iz susjednog mjeseca, prikazan samo da mreža bude puna. */
  inMonth: boolean;
  isToday: boolean;
}

/** Lokalni ključ dana — `toISOString()` bi za HR zonu navečer vratio sutra. */
export function localDayKey(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

/** Ponedjeljak = 0 (hrvatski tjedan počinje ponedjeljkom). */
const mondayIndex = (date: Date): number => (date.getDay() + 6) % 7;

/**
 * Mreža za mjesec: uvijek pune tjedne od ponedjeljka do nedjelje, pa se dani
 * susjednih mjeseca uključuju i označe s `inMonth: false`.
 */
export function monthGrid(year: number, month: number, today = new Date()): CalendarDay[] {
  const first = new Date(year, month, 1);
  const start = new Date(year, month, 1 - mondayIndex(first));

  const last = new Date(year, month + 1, 0);
  const trailing = 6 - mondayIndex(last);
  const totalDays = mondayIndex(first) + last.getDate() + trailing;

  const todayKey = localDayKey(today);
  const days: CalendarDay[] = [];
  for (let i = 0; i < totalDays; i++) {
    const date = new Date(start.getFullYear(), start.getMonth(), start.getDate() + i);
    const key = localDayKey(date);
    days.push({
      key,
      date,
      dayOfMonth: date.getDate(),
      inMonth: date.getMonth() === month,
      isToday: key === todayKey,
    });
  }
  return days;
}

/** Zapisi grupirani po lokalnom danu, najnoviji prvi unutar dana. */
export function groupByDay<T extends { date: string }>(
  entries: T[],
): Map<string, T[]> {
  const out = new Map<string, T[]>();
  for (const entry of entries) {
    const parsed = new Date(entry.date);
    if (Number.isNaN(parsed.getTime())) continue;
    const key = localDayKey(parsed);
    const list = out.get(key);
    if (list) list.push(entry);
    else out.set(key, [entry]);
  }
  for (const list of out.values()) {
    list.sort((a, b) => b.date.localeCompare(a.date));
  }
  return out;
}

/** Pomak mjeseca uz prelazak godine. */
export function shiftMonth(
  year: number,
  month: number,
  delta: number,
): { year: number; month: number } {
  const d = new Date(year, month + delta, 1);
  return { year: d.getFullYear(), month: d.getMonth() };
}

export const MONTH_NAMES_HR = [
  "siječanj",
  "veljača",
  "ožujak",
  "travanj",
  "svibanj",
  "lipanj",
  "srpanj",
  "kolovoz",
  "rujan",
  "listopad",
  "studeni",
  "prosinac",
] as const;

export const MONTH_NAMES_EN = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
] as const;

export const WEEKDAY_SHORT_HR = ["pon", "uto", "sri", "čet", "pet", "sub", "ned"] as const;
export const WEEKDAY_SHORT_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] as const;
