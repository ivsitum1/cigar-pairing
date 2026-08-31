import type { Lang, LocalizedText } from "../types";
import raw from "../data/ratingPrompts.json";

export type NotePromptContext = "pairing" | "cigar" | "drink";

export interface RatingPromptQuestion {
  id: string;
  label: LocalizedText;
  hint: LocalizedText;
  starter: LocalizedText;
  suggestions: LocalizedText[];
}

export interface RatingScaleBand {
  min: number;
  max: number;
  label: LocalizedText;
}

interface ContextBlock {
  questions: RatingPromptQuestion[];
  skeleton: LocalizedText;
}

const contexts = raw.contexts as Record<NotePromptContext, ContextBlock>;

export const RATING_SCALE: RatingScaleBand[] = raw.ratingScale as RatingScaleBand[];

export function promptsFor(context: NotePromptContext): RatingPromptQuestion[] {
  return contexts[context].questions;
}

export function skeletonFor(context: NotePromptContext, lang: Lang): string {
  return contexts[context].skeleton[lang];
}

/** Prvi dio startera do dvotočke — za prepoznavanje već umetnute linije. */
export function starterKey(starter: string): string {
  const cut = starter.indexOf(":");
  return (cut >= 0 ? starter.slice(0, cut) : starter).trim().toLowerCase();
}

/** Nakon dvotočke: prazno, izbornik s „ / ”, ili samo crtica. */
export function isBlankOrTemplateAfterColon(after: string): boolean {
  const t = after.trim();
  if (!t) return true;
  if (/^[—–-]\s*$/.test(t)) return true;
  if (t.includes(" / ")) return true;
  return false;
}

/**
 * Umeće starter u bilješku ako ta linija još nije tu.
 * Prazan tekst → starter; inače novi red + starter.
 */
export function appendPromptStarter(note: string, starter: string): string {
  const key = starterKey(starter);
  const lines = note.split(/\r?\n/);
  const already = lines.some((line) => starterKey(line) === key && key.length > 0);
  if (already) return note;
  const trimmed = note.replace(/\s+$/, "");
  if (!trimmed) return starter;
  return `${trimmed}\n${starter}`;
}

/**
 * Dodaje prijedlog na liniju pitanja (nakon dvotočke).
 * Više prijedloga na most/notu idu zarezom; jednokratni izbori zamjenjuju predložak.
 */
export function appendSuggestion(
  note: string,
  starter: string,
  suggestion: string,
): string {
  const word = suggestion.trim();
  if (!word) return note;

  const withLine = appendPromptStarter(note, starter);
  const key = starterKey(starter);
  const lines = withLine.split(/\r?\n/);
  const idx = lines.findIndex((line) => starterKey(line) === key);
  if (idx < 0) return withLine;

  const line = lines[idx];
  const colon = line.indexOf(":");
  const prefix = colon >= 0 ? line.slice(0, colon + 1) : `${starterKey(starter)}:`;
  const after = colon >= 0 ? line.slice(colon + 1) : "";

  if (isBlankOrTemplateAfterColon(after)) {
    lines[idx] = `${prefix} ${word}`;
    return lines.join("\n");
  }

  const existing = after.trim();
  const parts = existing.split(/\s*,\s*/).map((p) => p.toLowerCase());
  if (parts.includes(word.toLowerCase())) return withLine;

  lines[idx] = `${prefix} ${existing}, ${word}`;
  return lines.join("\n");
}

/** Punjenje praznog (ili samo-razmak) polja predloškom. */
export function applySkeleton(note: string, skeleton: string): string {
  if (note.trim()) return note;
  return skeleton;
}

export function ratingScaleSummary(lang: Lang): string {
  return RATING_SCALE.map((b) => b.label[lang]).join(" · ");
}
