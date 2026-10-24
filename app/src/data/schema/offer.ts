import { z } from "zod";

export const OfferSchema = z.object({
  id: z.string().min(1),
  shopId: z.string().min(1),
  productId: z.string().min(1),
  vitolaId: z.string().nullable().optional(),
  url: z.string().nullable().optional(),
  priceEUR: z.number().nullable().optional(),
  currency: z.string().min(1),
  packSize: z.number().nullable().optional(),
  inStock: z.boolean().nullable().optional(),
  fetchedAt: z.string().nullable(),
  validUntil: z.string(),
  matchConfidence: z.number(),
  checkedStatus: z.union([z.number(), z.string()]).nullable().optional(),
  source: z.string().min(1),
});

export type Offer = z.infer<typeof OfferSchema>;
