import images from "../data/productImages.json";

type ImageMaps = {
  cigars: Record<string, string>;
  drinks: Record<string, string>;
};

const MAPS = images as ImageMaps;

export function productImageUrl(
  kind: "cigar" | "drink",
  id: string,
): string | null {
  const map = kind === "cigar" ? MAPS.cigars : MAPS.drinks;
  const url = map[id];
  return typeof url === "string" && url.startsWith("http") ? url : null;
}
