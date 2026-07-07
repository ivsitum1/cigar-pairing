import type { ReactNode } from "react";

// Signature element: red rombova 1-5 (tijelo/snaga/slatkoca)
export function Meter({
  value,
  max = 5,
  label,
  accent = "var(--color-zlato)",
}: {
  value: number;
  max?: number;
  label?: string;
  accent?: string;
}) {
  return (
    <span className="inline-flex items-center gap-1.5">
      {label && (
        <span className="text-[10px] uppercase tracking-widest text-dim">
          {label}
        </span>
      )}
      <span className="inline-flex items-center gap-[3px]">
        {Array.from({ length: max }, (_, i) => (
          <span
            key={i}
            className="inline-block h-[7px] w-[7px] rotate-45"
            style={{
              background: i < value ? accent : "transparent",
              border: `1px solid ${i < value ? accent : "#a98f7255"}`,
            }}
          />
        ))}
      </span>
    </span>
  );
}

// Score medaljon u stilu cigar banda — prikazuje % SLAGANJA (ne ocjenu kvalitete)
export function ScoreBand({ score, title }: { score: number; title?: string }) {
  const tone =
    score >= 75
      ? "var(--color-zlato-2)"
      : score >= 55
        ? "var(--color-zlato)"
        : "var(--color-dim)";
  return (
    <div
      title={title}
      className="relative flex h-12 w-12 shrink-0 flex-col items-center justify-center rounded-full"
      style={{
        border: `1.5px solid ${tone}`,
        boxShadow: `inset 0 0 0 3px var(--color-humidor), inset 0 0 0 4px ${tone}44`,
      }}
    >
      <span className="font-display text-base leading-none" style={{ color: tone }}>
        {score}
      </span>
      <span className="text-[7px] uppercase tracking-wider text-dim">%</span>
    </div>
  );
}

export function Chip({
  children,
  active = false,
  onClick,
}: {
  children: ReactNode;
  active?: boolean;
  onClick?: () => void;
}) {
  const Tag = onClick ? "button" : "span";
  return (
    <Tag
      onClick={onClick}
      className={`inline-flex shrink-0 items-center rounded-full border px-2.5 py-1 text-xs transition-colors ${
        active
          ? "border-zlato bg-zlato/15 text-zlato-2"
          : "border-dim/30 text-dim"
      } ${onClick ? "cursor-pointer hover:border-zlato/60" : ""}`}
    >
      {children}
    </Tag>
  );
}

export function SectionTitle({ children }: { children: ReactNode }) {
  return (
    <div className="mb-3 mt-6 flex items-center gap-3">
      <h2 className="font-display text-sm uppercase tracking-[0.2em] text-zlato">
        {children}
      </h2>
      <div className="band-rule flex-1" />
    </div>
  );
}

export function SearchInput({
  value,
  onChange,
  placeholder,
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
}) {
  return (
    <input
      type="search"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
      className="w-full rounded-lg border border-dim/25 bg-cedar px-3 py-2.5 text-sm text-papir placeholder:text-dim/60 focus:border-zlato/60 focus:outline-none"
    />
  );
}
