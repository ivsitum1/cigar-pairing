import { parseLessonBody, splitItemLabel, type LessonBlock } from "../lib/parseLessonBody";

function ItemText({ text }: { text: string }) {
  const parts = splitItemLabel(text);
  if (!parts) {
    return <span className="text-papir/90">{text}</span>;
  }
  return (
    <span className="text-papir/90">
      <span className="font-medium text-papir">{parts.label}</span>
      <span className="text-dim"> — </span>
      <span>{parts.rest}</span>
    </span>
  );
}

function SectionBlock({
  block,
  index,
}: {
  block: Extract<LessonBlock, { type: "section" }>;
  index: number;
}) {
  let numberCounter = 0;

  return (
    <section className={index > 0 ? "mt-5 border-t border-dim/15 pt-4" : "mt-4"}>
      {block.title ? (
        <h3 className="mb-2.5 font-display text-[11px] uppercase tracking-[0.18em] text-zlato">
          {block.title}
        </h3>
      ) : null}
      {block.lead ? (
        <p className="mb-2.5 text-sm leading-relaxed text-papir/75">{block.lead}</p>
      ) : null}
      <ul className="space-y-2.5">
        {block.items.map((item, i) => {
          const marker =
            item.kind === "number" ? (
              <span className="mt-0.5 font-display text-[10px] tabular-nums text-zlato/70">
                {String(++numberCounter).padStart(2, "0")}
              </span>
            ) : (
              <span className="mt-[0.45em] h-1 w-1 shrink-0 rounded-full bg-zlato/55" aria-hidden />
            );
          return (
            <li
              key={i}
              className="grid grid-cols-[1.1rem_1fr] gap-x-2.5 text-sm leading-relaxed"
            >
              {marker}
              <ItemText text={item.text} />
            </li>
          );
        })}
      </ul>
    </section>
  );
}

export function LessonBody({ text }: { text: string }) {
  const blocks = parseLessonBody(text);
  return (
    <div className="lesson-body">
      {blocks.map((block, i) => {
        if (block.type === "paragraph") {
          const isLead = i === 0;
          return (
            <p
              key={i}
              className={`leading-relaxed ${
                isLead ? "text-[15px] text-papir" : "mt-4 text-sm text-papir/80"
              }`}
            >
              {block.text}
            </p>
          );
        }
        return <SectionBlock key={i} block={block} index={i} />;
      })}
    </div>
  );
}
