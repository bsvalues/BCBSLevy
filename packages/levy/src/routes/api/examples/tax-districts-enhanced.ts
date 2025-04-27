/**
 * Enhanced Tax Districts API Routes with Controller
 * 
 * Example of using the controller pattern with middleware for enhanced API design
 */

import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { TaxDistrictController } from '../../../controllers/TaxDistrictController';
import { validateRequest, commonValidations } from '../../../middleware/validateRequest';
import { requireAuth } from '../../../middleware/mockAuth';

const router = Router();
const controller = new TaxDistrictController();

// Validation schema for tax district queries
const TaxDistrictQuerySchema = z.object({
  ...commonValidations.pagination.shape,
  ...commonValidations.sorting.shape,
  name: z.string().optional(),
  districtType: z.string().optional(),
  countyName: z.string().optional(),
  stateName: z.string().optional(),
  isActive: z.coerce.boolean().optional(),
});

// Get all tax districts with optional filtering
router.get('/', 
  requireAuth,
  validateRequest({ query: TaxDistrictQuerySchema }),
  controller.getList
);

// Get a specific tax district by ID
router.get('/:id', 
  requireAuth,
  validateRequest({ params: commonValidations.idParam }),
  controller.getById
);

// Get tax codes associated with a tax district
router.get('/:id/tax-codes', 
  requireAuth,
  validateRequest({ params: commonValidations.idParam }),
  controller.getTaxCodes
);

// Get levies associated with a tax district
router.get('/:id/levies', 
  requireAuth,
  validateRequest({ params: commonValidations.idParam }),
  controller.getLevies
);

// Get statistics for a tax district
router.get('/:id/statistics',
  requireAuth,
  validateRequest({ params: commonValidations.idParam }),
  controller.getStatistics
);

// Get a list of district types
router.get('/types/list', 
  requireAuth,
  controller.getDistrictTypes
);

// Create schema for tax district create/update
const TaxDistrictSchema = z.object({
  name: z.string().min(3).max(100).trim(),
  districtType: z.string().max(50).trim(),
  countyName: z.string().max(100).trim(),
  stateName: z.string().max(50).trim(),
  taxDistrictId: z.string().max(50).optional(),
  levyCode: z.string().max(50).optional(),
  linkedLevyCode: z.string().max(50).optional(),
  isActive: z.boolean().default(true),
  metadata: z.record(z.any()).optional()
});

// Create a new tax district
router.post('/', 
  requireAuth,
  validateRequest({ body: TaxDistrictSchema }),
  controller.create
);

// Update an existing tax district
router.put('/:id', 
  requireAuth,
  validateRequest({ 
    params: commonValidations.idParam,
    body: TaxDistrictSchema.partial()
  }),
  controller.update
);

// Delete a tax district
router.delete('/:id', 
  requireAuth,
  validateRequest({ params: commonValidations.idParam }),
  controller.delete
);

export default router;