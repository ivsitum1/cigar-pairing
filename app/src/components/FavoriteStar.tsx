// Zvjezdica za omiljenu marku. Namjerno je zaseban gumb, a ne dio kartice:
// kartica vodi u marku, zvjezdica samo prebacuje oznaku — kad bi bila ugniježđena
// u gumb kartice, HTML bi bio neispravan i klik bi otvarao marku umjesto oznake.
import { useI18n } from "../i18n";
import {
  favoriteKey,
  toggleFavoriteBrand,
  useFavoriteBrands,
  type FavoriteKind,
} from "../store/favorites";

export function FavoriteStar({
  kind,
  brand,
  size = "sm",
}: {
  kind: FavoriteKind;
  brand: string;
  size?: "sm" | "lg";
}) {
  const { t } = useI18n();
  const favorites = useFavoriteBrands();
  const on = favorites.has(favoriteKey(kind, brand));
  return (
    <button
      type="button"
      aria-pressed={on}
      aria-label={`${on ? t("fav.remove") : t("fav.add")}: ${brand}`}
      title={on ? t("fav.remove") : t("fav.add")}
      onClick={(e) => {
        e.stopPropagation();
        toggleFavoriteBrand(kind, brand);
      }}
      className={`flex shrink-0 items-center justify-center rounded-full border transition-colors ${
        size === "lg" ? "h-9 w-9 text-lg" : "h-7 w-7 text-sm"
      } ${
        on
          ? "border-zlato/60 bg-zlato/15 text-zlato-2"
          : "border-dim/25 text-dim/60 hover:border-zlato/40 hover:text-zlato"
      }`}
    >
      <span aria-hidden="true">{on ? "★" : "☆"}</span>
    </button>
  );
}
