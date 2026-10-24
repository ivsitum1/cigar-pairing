import { z } from "zod";

export const ShopRegionSchema = z.enum(["HR", "EU", "USA"]);
export const ShopTypeSchema = z.enum(["online", "walkIn", "both"]);
export const ShopSourceSchema = z.enum(["scraper", "feed", "manual"]);

export const ShopSchema = z.object({
  id: z.string().min(1),
  name: z.string().min(1),
  region: ShopRegionSchema,
  city: z.string().nullable().optional(),
  type: ShopTypeSchema,
  source: ShopSourceSchema,
  adapter: z.string().min(1),
  home: z.string().min(1),
  productHost: z.string().nullable().optional(),
});

export type ShopV1 = z.infer<typeof ShopSchema>;
