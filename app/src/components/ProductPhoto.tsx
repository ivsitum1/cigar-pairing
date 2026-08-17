import { useState } from "react";
import { useI18n } from "../i18n";
import type { ProductImage } from "../lib/productImage";

/**
 * Fotografija proizvoda na vrhu kartice.
 *
 * Pojas ima ISTU visinu za sve cigare i istu za sva pica, bez obzira kako je
 * koja slika snimljena. To je druga polovica ujednacavanja: skripta makne
 * podlogu, a ovaj pojas izjednaci prostor koji slika zauzima. Bez toga bi
 * uska boca i siroka kutija razmicale sadrzaj kartice svaka na svoj nacin.
 *
 * Slika koja se ne ucita (datoteka obrisana, popis stariji od mape) ne
 * ostavlja slomljenu ikonu — pojas jednostavno nestane.
 */
export function ProductPhoto({
  image,
  alt,
  kind,
}: {
  image: ProductImage | null;
  alt: string;
  kind: "cigar" | "drink";
}) {
  const { t } = useI18n();
  const [pukla, setPukla] = useState(false);

  if (!image || pukla) return null;

  // Cigara lezi, boca stoji — otud razlicita visina pojasa.
  const visina = kind === "cigar" ? "h-32" : "h-44";

  return (
    <figure className="mb-3">
      <div
        className={`relative flex ${visina} w-full items-center justify-center overflow-hidden rounded-xl`}
        style={{
          // Blagi snop svjetla iza proizvoda — daje dubinu izrezu bez okvira
          // i drzi tamnu cigaru citljivom na tamnoj kartici.
          background:
            "radial-gradient(120% 90% at 50% 45%, rgba(201,163,92,0.13) 0%, rgba(201,163,92,0.04) 45%, transparent 75%)",
        }}
      >
        <img
          src={image.src}
          alt={alt}
          width={image.width}
          height={image.height}
          loading="lazy"
          decoding="async"
          onError={() => setPukla(true)}
          className={
            image.treatment === "framed"
              ? // Ambijentalna fotografija zadrzala je svoju podlogu, pa dobiva
                // okvir — inace bi tudja pozadina curila u karticu.
                "max-h-full max-w-full rounded-lg border border-zlato/25 object-contain"
              : "max-h-full max-w-full object-contain drop-shadow-[0_6px_12px_rgba(0,0,0,0.45)]"
          }
        />
      </div>
      {image.source ? (
        <figcaption className="mt-1 text-right text-micro text-dim/70">
          {t("photo.source")} {image.source}
        </figcaption>
      ) : null}
    </figure>
  );
}
