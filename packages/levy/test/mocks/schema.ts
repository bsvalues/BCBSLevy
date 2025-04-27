/**
 * Mock schema for testing LevyController and other components
 * 
 * This mock provides the necessary schema objects and relations
 * required by the controllers and other components during testing.
 */

import { z } from 'zod';

// Mock table objects
export const levies = {
  id: 'levies.id',
  taxDistrictId: 'levies.taxDistrictId',
  taxCodeId: 'levies.taxCodeId',
  taxYear: 'levies.taxYear',
  status: 'levies.status',
  levyAmount: 'levies.levyAmount',
  isApproved: 'levies.isApproved',
  createdById: 'levies.createdById',
  updatedById: 'levies.updatedById',
  approvedById: 'levies.approvedById',
  createdAt: 'levies.createdAt',
  updatedAt: 'levies.updatedAt',
  approvedAt: 'levies.approvedAt'
};

export const taxDistricts = {
  id: 'taxDistricts.id',
  name: 'taxDistricts.name',
  code: 'taxDistricts.code',
  countyId: 'taxDistricts.countyId'
};

export const taxCodes = {
  id: 'taxCodes.id',
  code: 'taxCodes.code',
  name: 'taxCodes.name',
  countyId: 'taxCodes.countyId',
  levyRate: 'taxCodes.levyRate',
  totalLevyAmount: 'taxCodes.totalLevyAmount' 
};

export const users = {
  id: 'users.id',
  username: 'users.username',
  firstName: 'users.firstName',
  lastName: 'users.lastName',
  email: 'users.email',
  isAdmin: 'users.isAdmin',
  active: 'users.active'
};

// Levy schema
export const levySchema = z.object({
  id: z.number().int().positive().optional(),
  taxDistrictId: z.number().int().positive(),
  taxCodeId: z.number().int().positive(),
  taxYear: z.number().int().min(2000).max(2100),
  levyAmount: z.number().nonnegative().multipleOf(0.01),
  status: z.enum(['draft', 'pending', 'approved', 'rejected']).default('draft'),
  isApproved: z.boolean().default(false),
  notes: z.string().optional(),
  createdById: z.number().int().positive().optional(),
  updatedById: z.number().int().positive().optional(),
  approvedById: z.number().int().positive().optional(),
  createdAt: z.date().optional(),
  updatedAt: z.date().optional(),
  approvedAt: z.date().optional()
});

// Export all schemas to match the real schema module
export default {
  levies,
  taxDistricts,
  taxCodes,
  users,
  levySchema
};