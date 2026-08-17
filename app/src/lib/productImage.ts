import manifest from "../data/productImages.json";

/**
 * Fotografije proizvoda — put do slike i njezin oblik.
 *
 * Popis (`productImages.json`) puni `scripts/normalize-product-images.py`. Dok
 * slika nema, popis je prazan i sve ovdje vraca `null` — kartica tada izgleda
 * tocno kao prije. Zato aplikacija nikad ne "ceka" slike i nijedan zaslon ne
 * ovisi o tome je li skripta pokrenuta.
 */

/** Kako je slika obradjena. */
export type ImageTreatment =
  /** Podloga je maknuta — slika sjeda izravno na karticu, bez okvira. */
  | "cutout"
  /** Podloga se nije dala odvojiti (ambijentalna fotografija) — ide u okvir. */
  | "framed";

export type ProductImage = {
  src: string;
  /** Izvorne dimenzije: kartica po njima rezervira prostor prije ucitavanja. */
  width: number;
  height: number;
  treatment: ImageTreatment;
  /** Domena s koje je slika preuzeta (npr. "humidor.hr"), za potpis. */
  source: string;
};

type Unos = { w: number; h: number; t: string; s?: string };
type Popis = Record<string, Unos>;

const POPIS: Record<"cigars" | "drinks", Popis> = {
  cigars: (manifest as { cigars?: Popis }).cigars ?? {},
  drinks: (manifest as { drinks?: Popis }).drinks ?? {},
};

/**
 * Vite servira aplikaciju pod `/cigar-pairing/`, ne pod korijenom. Put do
 * slike zato mora proci kroz BASE_URL — tvrdo upisan `/img/...` radio bi u
 * dev serveru samo slucajno, a na GitHub Pagesu bi dao 404.
 */
function base(): string {
  const b = import.meta.env.BASE_URL || "/";
  return b.endsWith("/") ? b : `${b}/`;
}

function nadji(vrsta: "cigars" | "drinks", id: string | undefined): ProductImage | null {
  if (!id) return null;
  const unos = POPIS[vrsta][id];
  if (!unos) return null;
  return {
    src: `${base()}img/products/${vrsta}/${encodeURIComponent(id)}.webp`,
    width: unos.w,
    height: unos.h,
    treatment: unos.t === "framed" ? "framed" : "cutout",
    source: unos.s ?? "",
  };
}

/**
 * Slika cigare. Trazi se po id-u LINIJE, a ne po odabranoj vitoli: duckani
 * fotografiraju liniju (ista kutija, ista traka), pa bi trazenje po vitoli
 * ostavilo vecinu kartica bez slike bez ijednog dobitka u tocnosti.
 */
export function cigarImage(id: string | undefined): ProductImage | null {
  return nadji("cigars", id);
}

/** Slika boce ili pakiranja pica. */
export function drinkImage(id: string | undefined): ProductImage | null {
  return nadji("drinks", id);
}

/** Ima li aplikacija ijednu sliku (kartica po tome odlucuje crta li pojas). */
export function hasProductImages(): boolean {
  return Object.keys(POPIS.cigars).length > 0 || Object.keys(POPIS.drinks).length > 0;
}
