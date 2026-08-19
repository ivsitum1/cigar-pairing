import { describe, expect, it } from "vitest";
import cigarsData from "../data/cigars.json";
import type { Cigar } from "../types";
import { matchesAnySearch, matchesSearch, searchTokens } from "./searchMatch";

const cigars = cigarsData as Cigar[];

/** Isti opis koji katalog sastavlja za popis cigara. */
const hay = (c: Cigar) =>
  `${c.brand} ${c.line} ${c.vitola} ${c.wrapper} ${c.country} ${(c.vitolas ?? [])
    .map((v) => [v.name, v.shape, v.format].filter(Boolean).join(" "))
    .join(" ")}`;

const findByQuery = (q: string) => cigars.filter((c) => matchesSearch(hay(c), q));

describe("riječi upita", () => {
  it("ispušta riječi s pakiranja, zadržava značajne", () => {
    expect(searchTokens("Flor de Selva Classic Collection Tempo")).toEqual([
      "flor",
      "de",
      "selva",
      "classic",
      "tempo",
    ]);
    expect(searchTokens("Oliva Serie V")).toEqual(["oliva", "serie", "v"]);
    expect(searchTokens("   ")).toEqual([]);
  });

  it("prazan upit ne filtrira ništa", () => {
    expect(matchesSearch("bilo što", "")).toBe(true);
    expect(matchesSearch("bilo što", "   ")).toBe(true);
  });

  it("redoslijed riječi nije bitan", () => {
    expect(matchesSearch("Oliva Serie V Melanio", "melanio oliva")).toBe(true);
    expect(matchesSearch("Oliva Serie V Melanio", "oliva churchill")).toBe(false);
  });

  it("ne mari za dijakritike ni velika slova", () => {
    expect(matchesSearch("Padrón 1964 Anniversary", "PADRON 1964")).toBe(true);
  });

  it("pogađa kroz više izvora", () => {
    expect(matchesAnySearch(["Flor de Selva Classic", "Tempo"], "classic tempo")).toBe(true);
    expect(matchesAnySearch(["Flor de Selva Classic", "Tempo"], "classic robusto")).toBe(false);
  });
});

describe("pretraga nad stvarnim katalogom", () => {
  it("ime s kutije nalazi cigaru koju katalog vodi kraće", () => {
    const hits = findByQuery("Flor de Selva Classic Collection Tempo");
    expect(hits.map((c) => c.id)).toContain("cig-flor-de-selva-tempo");
  });

  it("Oliva Serie O Toro postoji i nalazi se", () => {
    const hits = findByQuery("Oliva Serie O Toro");
    expect(hits.map((c) => c.id)).toContain("cig-oliva-serie-o");
    const serieO = cigars.find((c) => c.id === "cig-oliva-serie-o")!;
    expect(serieO.vitolas.map((v) => v.name)).toContain("Serie O Toro");
  });

  it("Oliva Serie G mali perfecto (Special G) se nalazi po obliku i dimenziji", () => {
    const g = cigars.find((c) => c.id === "cig-oliva-serie-g")!;
    const special = g.vitolas.find((v) => v.name === "Special G")!;
    expect(special.shape).toBe("Perfecto");
    expect(special.ring).toBe(48);
    expect(special.lengthMM).toBe(95);
    expect(findByQuery("oliva serie g perfecto").map((c) => c.id)).toContain(
      "cig-oliva-serie-g",
    );
    expect(findByQuery("oliva special g 48").map((c) => c.id)).toContain(
      "cig-oliva-serie-g",
    );
  });

  it("upit s viškom riječi i dalje pogađa", () => {
    expect(findByQuery("aganorsa aniversario connecticut toro").map((c) => c.id)).toContain(
      "cig-aganorsa-leaf-aniversario",
    );
  });

  it("jednoslovna oznaka serije ne hvata sve redom", () => {
    // „o" kao niz znakova stoji u „Toro" i „Robusto" — kao riječ ne stoji
    const ids = findByQuery("Oliva Serie O Toro").map((c) => c.id);
    expect(ids).toContain("cig-oliva-serie-o");
    expect(ids).not.toContain("cig-oliva-serie-v");
  });

  it("nedovršena riječ i dalje nalazi", () => {
    expect(findByQuery("aganor aniversario").map((c) => c.id)).toContain(
      "cig-aganorsa-leaf-aniversario",
    );
  });

  it("nepostojeća riječ i dalje ne pogađa ništa", () => {
    expect(findByQuery("oliva serie zzzz")).toHaveLength(0);
  });
});
