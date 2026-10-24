import { z } from "zod";

export const ProductKindSchema = z.enum([
  "cigar",
  "rum",
  "whisky",
  "brandy",
  "wine",
  "coffee",
  "tequila",
  "gin",
  "digestif",
]);

export const ProfileSourceSchema = z.enum([
  "measured",
  "curated",
  "estimated",
]);

export const ProductDescriptionSchema = z.object({
  hr: z.string().min(1),
  en: z.string().nullable().optional(),
  reviewedAt: z.string().nullable().optional(),
});

export const ProductSchema = z.object({
  id: z.string().min(1),
  kind: ProductKindSchema,
  brand: z.string(),
  line: z.string(),
  country: z.string().nullable().optional(),
  strength: z.number().nullable().optional(),
  body: z.number().nullable().optional(),
  sweetness: z.number().nullable().optional(),
  flavorTags: z.array(z.string()).default([]),
  profileSource: ProfileSourceSchema,
  description: ProductDescriptionSchema,
});

export type Product = z.infer<typeof ProductSchema>;
export type ProductKind = z.infer<typeof ProductKindSchema>;
