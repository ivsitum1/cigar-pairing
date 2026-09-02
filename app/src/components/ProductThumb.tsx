import { useState } from "react";
import type { ImageTreatment } from "../lib/productImage";

/**
 * Fotografija proizvoda uz naziv na kartici.
 *
 * Ploha iza slike ovisi o tome je li slika prošla obradu:
 *
 *  * `cutout` — podloga je maknuta, slika je prozirna i sjeda izravno na
 *    karticu. Ploha bi joj ovdje samo vratila okvir koji je upravo maknut, pa
 *    je nema; sjena daje dubinu.
 *  * `framed` / `remote` — slika još nosi svoju podlogu (bijelu, crnu, drvo).
 *    Tamna ploha i zaobljeni rub drže te razlike unutar jednog oblika, da tuđa
 *    pozadina ne curi u karticu.
 *
 * Okvir je jednake veličine u sva tri slučaja — visina slike ne smije ovisiti
 * o tome je li obrada pokrenuta.
 */
export function ProductThumb({
  src,
  alt,
  treatment = "remote",
  width,
  height,
}: {
  src: string;
  alt: string;
  treatment?: ImageTreatment;
  /** Izvorne dimenzije obrađene slike; kod dućanskih se ne znaju. */
  width?: number;
  height?: number;
}) {
  const [failed, setFailed] = useState(false);
  if (failed) return null;
  const izrezana = treatment === "cutout";
  return (
    <img
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={
        izrezana
          ? "h-28 w-[4.5rem] shrink-0 object-contain drop-shadow-[0_4px_10px_rgba(0,0,0,0.5)]"
          : "h-28 w-[4.5rem] shrink-0 rounded-md bg-black/25 object-contain"
      }
      loading="lazy"
      referrerPolicy="no-referrer"
      onError={() => setFailed(true)}
    />
  );
}
