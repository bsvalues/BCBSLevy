import { z } from 'zod';

/**
 * Validation schema for creating a levy
 */
export const LevyCreateSchema = z.object({
  name: z.string().min(3).max(100).trim(),
  description: z.string().max(1000).optional(),
  taxYear: z.number().int().positive(),
  taxDistrictId: z.number().int().positive(),
  taxCodeId: z.number().int().positive(),
  levyAmount: z.number().nonnegative(),
  levyRate: z.number().nonnegative(),
  assessedValue: z.number().nonnegative(),
  newConstructionValue: z.number().nonnegative().optional(),
  annexationValue: z.number().nonnegative().optional(),
  priorYearLevyAmount: z.number().nonnegative().optional(),
  status: z.enum(['draft', 'submitted', 'approved', 'rejected', 'archived']).default('draft'),
  calculationMethod: z.enum(['standard', 'banked', 'custom']).default('standard'),
  isApproved: z.boolean().default(false),
  approvedById: z.number().int().positive().optional(),
  approvedAt: z.date().optional(),
  metadata: z.record(z.any()).optional()
});

/**
 * Validation schema for updating a levy (all fields optional)
 */
export const LevyUpdateSchema = LevyCreateSchema.partial();

/**
 * Type definitions for levy validation
 */
export type LevyCreate = z.infer<typeof LevyCreateSchema>;
export type LevyUpdate = z.infer<typeof LevyUpdateSchema>;