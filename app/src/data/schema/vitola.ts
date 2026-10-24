import { z } from "zod";

export const VitolaSchema = z.object({
  id: z.string().min(1),
  productId: z.string().min(1),
  name: z.string().min(1),
  ring: z.number().nullable().optional(),
  lengthMM: z.number().nullable().optional(),
  shape: z.string().nullable().optional(),
  smokeTimeMin: z.number().nullable().optional(),
});

export type VitolaV1 = z.infer<typeof VitolaSchema>;
