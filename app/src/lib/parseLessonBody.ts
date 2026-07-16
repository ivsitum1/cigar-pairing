/** Parse Club 101 lesson bodies (intro + headed lists) into structured blocks. */

export type LessonListKind = "bullet" | "number";

export type LessonListItem = {
  kind: LessonListKind;
  text: string;
};

export type LessonBlock =
  | { type: "paragraph"; text: string }
  | {
      type: "section";
      title: string;
      lead?: string;
      items: LessonListItem[];
    };

const BULLET = /^•\s*/;
const NUMBER = /^\d+\.\s*/;

function isListLine(line: string): boolean {
  return BULLET.test(line) || NUMBER.test(line);
}

function parseListLine(line: string): LessonListItem {
  if (NUMBER.test(line)) {
    return { kind: "number", text: line.replace(NUMBER, "").trim() };
  }
  return { kind: "bullet", text: line.replace(BULLET, "").trim() };
}

/** Split a catalogue line into emphasis label + rest when " — " / " → " present. */
export function splitItemLabel(item: string): { label: string; rest: string } | null {
  const m = item.match(/^(.*?)\s+[—→]\s+(.*)$/);
  if (!m) return null;
  const label = m[1].trim();
  const rest = m[2].trim();
  if (!label || !rest || label.length > 80) return null;
  return { label, rest };
}

export function parseLessonBody(text: string): LessonBlock[] {
  const chunks = text
    .split(/\n\n+/)
    .map((c) => c.trim())
    .filter(Boolean);

  const blocks: LessonBlock[] = [];

  for (const chunk of chunks) {
    const lines = chunk
      .split("\n")
      .map((l) => l.trimEnd())
      .filter((l) => l.trim().length > 0);

    if (lines.length === 0) continue;

    const listIdx = lines.findIndex(isListLine);
    if (listIdx === -1) {
      blocks.push({ type: "paragraph", text: lines.join(" ").trim() });
      continue;
    }

    const before = lines.slice(0, listIdx).map((l) => l.trim()).filter(Boolean);
    const items = lines.slice(listIdx).filter(isListLine).map(parseListLine);
    const title = before[0] ?? "";
    const lead =
      before.length > 1 ? before.slice(1).join(" ").trim() : undefined;

    blocks.push({
      type: "section",
      title,
      lead: lead || undefined,
      items,
    });
  }

  return blocks;
}
