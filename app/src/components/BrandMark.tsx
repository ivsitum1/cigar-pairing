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
  MARK_MONO,
  MARK_VIEWBOX_TIGHT,
  MARK_RING,
  SEAL_BODY,
  SEAL_MONO,
  SEAL_LIQUID_CLIP,
  SEAL_LIQUID_Y,
  SEAL_RING,
} from "./brandArt";

type MarkProps = {
  className?: string;
  /** Znak je dekoracija uz ispisano ime; postavi samo ako stoji sam. */
  title?: string;
  /** Jedna boja (currentColor), bez tekućine u drugoj nijansi — tisak, žig. */
  mono?: boolean;
  /**
   * Okvir stisnut na sam prsten, bez zraka oko njega. Znak tada ispunjava
   * svoju kutiju, pa se u lockupu može poravnati s vrhom slova; kvadratni
   * okvir bi za istu vidljivu visinu tražio osjetno širu kutiju.
   */
  tight?: boolean;
};

function a11y(title?: string) {
  return title
    ? ({ role: "img", "aria-label": title } as const)
    : ({ "aria-hidden": true, focusable: false } as const);
}

export function BrandMark({ className = "h-8 w-8", title, mono, tight }: MarkProps) {
  const clip = useId();
  const box = tight ? MARK_VIEWBOX_TIGHT : BRAND_VIEWBOX;
  if (mono) {
    return (
      <svg viewBox={box} className={className} {...a11y(title)}>
        <path d={MARK_MONO} fill="currentColor" fillRule="evenodd" />
      </svg>
    );
  }
  return (
    <svg viewBox={box} className={className} {...a11y(title)}>
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

export function BrandSeal({ className = "h-16 w-16", title, mono }: MarkProps) {
  const clip = useId();
  if (mono) {
    // U jednoj boji masa je tinta, pa banderola u njoj postaje izrez.
    return (
      <svg viewBox={BRAND_VIEWBOX} className={className} {...a11y(title)}>
        <path d={SEAL_MONO} fill="currentColor" fillRule="evenodd" />
      </svg>
    );
  }
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

/**
 * Ime + zlatna linija, bez znaka — ide ispod pečata, gdje bi znak bio dvaput.
 *
 * Dva reda, jer par nose "Cigar & Drink": `&` obećava dvije stvari, a pairing
 * je radnja, ne druga stvar. "Pairing" zato stoji ispod, kao opis — i vidljivo
 * ime tako ostaje podskup punog imena iz manifesta i naslova.
 */
export function BrandWordmark({ className = "" }: { className?: string }) {
  return (
    <div className={className}>
      <div className="font-display text-lg uppercase leading-none tracking-[0.25em] text-zlato-2">
        Cigar <span className="text-oxblood">&</span> Drink
      </div>
      <div className="mt-1 font-display text-micro uppercase tracking-[0.42em] text-zlato">
        Pairing
      </div>
      <div className="band-rule mt-1.5" />
    </div>
  );
}

/** Znak uz ime — zaglavlje aplikacije. */
export function BrandLockup({ className = "" }: { className?: string }) {
  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      {/* vrh znaka stoji na istoj liniji kao vrh slova C */}
      <BrandMark tight className="mt-[2px] h-[34px] w-auto shrink-0 self-start text-zlato-2" />
      <BrandWordmark />
    </div>
  );
}
