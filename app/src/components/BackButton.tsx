import type { ReactNode } from "react";

/** Natrag gumb — konzistentan u sheetovima i podstranicama. */
export function BackButton({
  onClick,
  children,
}: {
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="inline-flex items-center gap-1.5 rounded-full border border-zlato/40 px-3 py-1.5 font-display text-xs uppercase tracking-widest text-zlato hover:bg-zlato/10"
    >
      ← {children}
    </button>
  );
}
