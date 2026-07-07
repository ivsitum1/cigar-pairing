// Kratki opis karaktera vitole izveden iz imena formata.
// Format oblikuje iskustvo: omjer wrappera i punila, temperatura, trajanje.
import type { Lang } from "../types";

const FORMATS: { match: RegExp; hr: string; en: string }[] = [
  { match: /culebra/i,
    hr: "Tri prepletene panatele — kuriozitet za dijeljenje s društvom.",
    en: "Three braided panetelas — a curiosity to share among friends." },
  { match: /diadema|salomon/i,
    hr: "Svečani dvostruko šiljasti div — okus se otvara u valovima, za dugu večer.",
    en: "A ceremonial double-tapered giant — flavour unfolds in waves over a long evening." },
  { match: /perfecto/i,
    hr: "Šiljast na oba kraja — počinje koncentrirano, zatim se širi; format stare škole.",
    en: "Tapered at both ends — starts concentrated then opens up; an old-school shape." },
  { match: /belicoso|torpedo|pir[aá]mide|piramide|pyramid/i,
    hr: "Šiljasta glava usmjerava dim i pojačava okus; rez određuje snagu poteza.",
    en: "The tapered head focuses the smoke and intensifies flavour; the cut sets the draw." },
  { match: /lancero|panatela|laguito/i,
    hr: "Dug i tanak — wrapper dominira okusom; elegantan, traži polagano pušenje.",
    en: "Long and slim — the wrapper leads the flavour; elegant, demands a slow pace." },
  { match: /double corona|prominente/i,
    hr: "Kraljevski format od skoro dva sata — maksimalna kompleksnost i hladnoća dima.",
    en: "The regal near-two-hour format — maximum complexity and the coolest smoke." },
  { match: /churchill|julieta/i,
    hr: "Dugačak i svečan (~7 inča) — hladniji dim i postupni razvoj kroz sat i pol.",
    en: "Long and stately (~7 inches) — cooler smoke and a gradual evolution over ninety minutes." },
  { match: /gran corona|corona gorda|grand corona/i,
    hr: "Deblja corona — više dima uz zadržanu eleganciju klasičnog formata.",
    en: "A thicker corona — more smoke while keeping the classic format's elegance." },
  { match: /half corona|petit corona|mareva|minuto|perla|cadete|short corona/i,
    hr: "Mala klasika za 25–40 minuta — koncentriran okus bez obveze dugog sjedenja.",
    en: "The small classic for 25–40 minutes — concentrated flavour without the long sit." },
  { match: /\bcorona\b/i,
    hr: "Mjera svih formata (42 RG) — savršen omjer wrappera i punila, referentan okus.",
    en: "The benchmark format (42 RG) — the perfect wrapper-to-filler ratio, reference flavour." },
  { match: /gordo|gigante|magnum 60|\b60\b.*RG|grande extra/i,
    hr: "Vrlo debeo (58–60+ RG) — obilje mekog, hladnog dima; punilo vodi okus.",
    en: "Very thick (58–60+ RG) — masses of soft, cool smoke; the filler leads." },
  { match: /toro grande|gran toro|double toro/i,
    hr: "Veći toro — sat i pol punog, mekog dima.",
    en: "A larger toro — ninety minutes of full, soft smoke." },
  { match: /\btoro\b|cañonazo|canonazo/i,
    hr: "Moderni standard (~6 × 50–54) — uravnotežen omjer i sat vremena razvoja.",
    en: "The modern standard (~6 × 50–54) — balanced ratio and an hour of development." },
  { match: /robusto grande|doble robusto|double robusto/i,
    hr: "Produženi robusto — ista koncentracija okusa, nešto više vremena.",
    en: "An extended robusto — the same flavour concentration with extra time." },
  { match: /petit robusto|short robusto|rothschild|epicure no\.?\s?2/i,
    hr: "Kratak i širok — odmah u srž okusa; idealan kad je vrijeme ograničeno.",
    en: "Short and wide — straight to the heart of the flavour; ideal when time is short." },
  { match: /robusto/i,
    hr: "Najpopularniji format današnjice (~5 × 50) — pun okus u 45–60 minuta.",
    en: "Today's most popular format (~5 × 50) — full flavour in 45–60 minutes." },
  { match: /petit|demi|chiquito|puritos|mini/i,
    hr: "Džepni format za 15–25 minuta — brza, koncentrirana pauza.",
    en: "A pocket format for 15–25 minutes — a quick, concentrated break." },
  { match: /tubos|tubo/i,
    hr: "U aluminijskoj tubi — zaštićena i spremna za put ili poklon.",
    en: "In an aluminium tube — protected, travel- and gift-ready." },
];

export function vitolaBlurb(name: string, lang: Lang): string | null {
  for (const f of FORMATS) {
    if (f.match.test(name)) return lang === "en" ? f.en : f.hr;
  }
  return null;
}
