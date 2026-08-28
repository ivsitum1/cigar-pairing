// Zajednicki omotac modalnih sheetova (detalj, linija, marka, večer, vitola).
//
// Prije je svaki od pet bio gola <div> s onClick na pozadini: bez role,
// bez Escapea, bez zamke fokusa i bez povrata fokusa. Citac ekrana nije znao
// da je otvoren dijalog, a tipkovnicom se iz njega nije dalo izaci.
// A11y sada zivi na jednom mjestu i svaki novi sheet ga dobiva besplatno.
import { useEffect, useRef, type ReactNode } from "react";

const FOCUSABLE =
  'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

export function SheetShell({
  onClose,
  label,
  scrollKey,
  panelClassName = "max-h-[85vh] w-full max-w-lg overflow-y-auto rounded-t-2xl border border-zlato/25 bg-humidor p-5 pb-8 sm:rounded-2xl",
  children,
}: {
  /** Zatvaranje: pozadina, Escape, gumb. */
  onClose: () => void;
  /** Pristupacno ime dijaloga (citac ekrana ga izgovori pri otvaranju). */
  label: string;
  /** Kad se sadržaj zamijeni bez demontaže — reset scrolla (default: label). */
  scrollKey?: string;
  panelClassName?: string;
  children: ReactNode;
}) {
  const panelRef = useRef<HTMLDivElement>(null);
  const contentKey = scrollKey ?? label;

  // isti panel ostaje montiran kad se sadržaj zamijeni (npr. druga cigara) —
  // bez reseta korisnik ostane na dnu prethodne kartice
  useEffect(() => {
    if (panelRef.current) panelRef.current.scrollTop = 0;
  }, [contentKey]);

  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    const panel = panelRef.current;

    // fokus u dijalog — inace ostaje iza otvorenog sheeta
    const first = panel?.querySelector<HTMLElement>(FOCUSABLE);
    (first ?? panel)?.focus();

    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        onClose();
        return;
      }
      if (e.key !== "Tab" || !panel) return;
      // zamka fokusa: Tab kruzi unutar dijaloga
      const items = [...panel.querySelectorAll<HTMLElement>(FOCUSABLE)].filter(
        (el) => el.offsetParent !== null,
      );
      if (items.length === 0) {
        e.preventDefault();
        panel.focus();
        return;
      }
      const firstEl = items[0];
      const lastEl = items[items.length - 1];
      const active = document.activeElement;
      if (e.shiftKey && (active === firstEl || active === panel)) {
        e.preventDefault();
        lastEl.focus();
      } else if (!e.shiftKey && active === lastEl) {
        e.preventDefault();
        firstEl.focus();
      }
    };

    document.addEventListener("keydown", onKeyDown, true);
    // pozadina ne smije skrolati ispod otvorenog sheeta
    const prevOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", onKeyDown, true);
      document.body.style.overflow = prevOverflow;
      previouslyFocused?.focus?.();
    };
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 sm:items-center"
      onClick={onClose}
    >
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-label={label}
        tabIndex={-1}
        className={panelClassName}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
}
