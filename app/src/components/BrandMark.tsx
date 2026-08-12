// Znak aplikacije. Dvije težine iste geometrije:
//
//   <BrandMark />   linijska banderola — nasljeđuje boju teksta (currentColor),
//                   pa radi i na tamnoj i na svijetloj podlozi
//   <BrandSeal />   puna forma (pečat) — vlastite boje, za trenutke gdje znak
//                   stoji sam, bez teksta uz sebe
//
// Putanje dolaze iz generiranog `brandArt.ts`; geometrija se mijenja u
// docs/brand/generate_logo_assets.py, nikad ovdje.
import { useId } from "react";
import {
  BRAND_SIZE,
  BRAND_VIEWBOX,
  MARK_KEYLINE,
  MARK_LIQUID_CLIP,
  MARK_LIQUID_Y,
  MARK_RING,
  SEAL_BODY,
  SEAL_LIQUID_CLIP,
  SEAL_LIQUID_Y,
  SEAL_RING,
} from "./brandArt";

type MarkProps = {
  className?: string;
  /** Znak je dekoracija uz ispisano ime; postavi samo ako stoji sam. */
  title?: string;
};

function a11y(title?: string) {
  return title
    ? ({ role: "img", "aria-label": title } as const)
    : ({ "aria-hidden": true, focusable: false } as const);
}

export function BrandMark({ className = "h-8 w-8", title }: MarkProps) {
  const clip = useId();
  return (
    <svg viewBox={BRAND_VIEWBOX} className={className} {...a11y(title)}>
      <defs>
        <clipPath id={clip}>
          <path d={MARK_LIQUID_CLIP} />
        </clipPath>
      </defs>
      <g clipPath={`url(#${clip})`}>
        <rect
          x="0"
          y={MARK_LIQUID_Y}
          width={BRAND_SIZE}
          height={BRAND_SIZE - MARK_LIQUID_Y}
          fill="var(--color-konjak)"
        />
      </g>
      <path d={MARK_KEYLINE} fill="currentColor" fillRule="evenodd" opacity={0.55} />
      <path d={MARK_RING} fill="currentColor" fillRule="evenodd" />
    </svg>
  );
}

export function BrandSeal({ className = "h-16 w-16", title }: MarkProps) {
  const clip = useId();
  return (
    <svg viewBox={BRAND_VIEWBOX} className={className} {...a11y(title)}>
      <defs>
        <clipPath id={clip}>
          <path d={SEAL_LIQUID_CLIP} />
        </clipPath>
      </defs>
      <path d={SEAL_BODY} fill="var(--color-koza)" />
      <g clipPath={`url(#${clip})`}>
        <rect
          x="0"
          y={SEAL_LIQUID_Y}
          width={BRAND_SIZE}
          height={BRAND_SIZE - SEAL_LIQUID_Y}
          fill="var(--color-zlato)"
        />
      </g>
      <path d={SEAL_RING} fill="var(--color-zlato)" fillRule="evenodd" />
    </svg>
  );
}

/** Ime + zlatna linija, bez znaka — ide ispod pečata, gdje bi znak bio dvaput. */
export function BrandWordmark({ className = "" }: { className?: string }) {
  return (
    <div className={className}>
      <div className="font-display text-lg uppercase tracking-[0.25em] text-zlato-2">
        Cigar <span className="text-oxblood">&</span> Pairing
      </div>
      <div className="band-rule mt-1.5" />
    </div>
  );
}

/** Znak uz ime — zaglavlje aplikacije. */
export function BrandLockup({ className = "" }: { className?: string }) {
  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <BrandMark className="h-9 w-9 shrink-0 text-zlato-2" />
      <BrandWordmark />
    </div>
  );
}
