// Ime pića je jedino mjesto na kojem korisnik vidi marku — pića nemaju
// zasebno `brand` polje. Kad se kombinirani unos („La Hechicera SE No.1 / No.2")
// razdvoji, druga polovica zna ostati bez marke: goli „No.2" u katalogu i u
// pretrazi, bez načina da se poveže s ostatkom serije.
//
// Isti splitter ostavljao je i svoju mehaniku u tekstu koji korisnik čita
// („Druga boca iz kombiniranog unosa"), što ne govori ništa o samom piću.
import { describe, expect, it } from "vitest";
import { ALL_DRINKS } from "./index";

describe("imena pića nose marku", () => {
  // Vlastite marke koje SU jednorječne — nisu sirotani.
  const SINGLE_WORD_BRANDS = new Set([
    "malibu",
    "pitú (cachaça)",
    "becherovka",
    "jägermeister",
    "sipsmith",
    "beefeater",
    "citadelle",
    "aviation",
    "paddy",
    "alkkemist",
    "amazzoni",
    "bathtub",
    "brooklyn",
    "broker's",
    "brockman's",
    "bulldog",
  ]);

  // Prave marke koje pocinju brojem — nisu fragmenti.
  const NUMERIC_BRANDS = /^No\. 3 London Dry Gin|^No\. 209 Gin/;

  it("nijedno ime ne počinje golim brojem ili 'No.'", () => {
    const bad = ALL_DRINKS.filter((d) => /^(No\.?\s*\d|\d)/.test(d.name.trim()))
      // kava/vino smiju imati godine i postotke u imenu
      .filter((d) => d.category !== "coffee" && d.category !== "wine")
      .filter((d) => !NUMERIC_BRANDS.test(d.name.trim()))
      .map((d) => `${d.id}: ${d.name}`);
    expect(
      bad,
      "Ime koje počinje brojem obično je fragment razdvojenog kombiniranog unosa — dopiši marku.",
    ).toEqual([]);
  });

  it("jednorječna imena su poznate marke, ne fragmenti", () => {
    const bad = ALL_DRINKS.filter((d) => {
      const n = d.name.trim();
      if (n.split(/\s+/).length > 1) return false;
      return !SINGLE_WORD_BRANDS.has(n.toLowerCase());
    })
      .filter((d) => d.category !== "coffee")
      .map((d) => `${d.id}: ${d.name}`);
    expect(
      bad,
      "Nova jednorječna marka? Dopiši je u SINGLE_WORD_BRANDS. Inače je fragment — dopiši marku u ime.",
    ).toEqual([]);
  });

  it("bilješke ne otkrivaju mehaniku pipelinea", () => {
    const leak =
      /kombiniranog unosa|combined entry|ekspresija u paru|expression in the pair|Starija\/punija ekspresija|older\/fuller expression/i;
    const bad = ALL_DRINKS.filter(
      (d) => leak.test(d.notes?.hr ?? "") || leak.test(d.notes?.en ?? ""),
    ).map((d) => `${d.id}: ${(d.notes?.hr ?? "").slice(0, 60)}`);
    expect(
      bad,
      "Tekst iz splittera ne govori ništa o piću — opiši bocu, ne kako je nastao zapis.",
    ).toEqual([]);
  });
});
