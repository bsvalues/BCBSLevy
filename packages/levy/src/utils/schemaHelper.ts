/**
 * Schema Helper Utility
 * 
 * Provides helper functions and utilities for working with Zod schemas
 * and validation in a standardized way.
 */

import { z } from 'zod';

/**
 * Common schema types that can be reused across the application
 */
export const schemaTypes = {
  /**
   * Basic ID field (positive integer)
   */
  id: z.number().int().positive(),
  
  /**
   * UUID string
   */
  uuid: z.string().uuid(),
  
  /**
   * Basic string field with trimming
   */
  string: z.string().trim(),
  
  /**
   * Required string field with min/max length and trimming
   */
  requiredString: (minLength = 1, maxLength = 255) => 
    z.string().min(minLength).max(maxLength).trim(),
  
  /**
   * Optional string field with max length and trimming
   */
  optionalString: (maxLength = 255) => 
    z.string().max(maxLength).trim().optional(),
  
  /**
   * Email field
   */
  email: z.string().email().trim().max(255),
  
  /**
   * URL field
   */
  url: z.string().url().trim().max(2048),
  
  /**
   * Date field (ISO string format)
   */
  date: z.string().datetime({ offset: true }),
  
  /**
   * Date field (JavaScript Date object)
   */
  dateObject: z.date(),
  
  /**
   * Money field (positive number with two decimal places)
   */
  money: z.number().nonnegative().multipleOf(0.01),
  
  /**
   * Percentage field (0-100 range)
   */
  percentage: z.number().min(0).max(100),
  
  /**
   * Phone number field (simple format validation)
   */
  phone: z.string().regex(/^\+?[0-9]{10,15}$/, 'Invalid phone number'),
  
  /**
   * Boolean field
   */
  boolean: z.boolean(),
  
  /**
   * JSON object field
   */
  json: z.record(z.any()),
  
  /**
   * Array field
   */
  array: <T extends z.ZodTypeAny>(schema: T) => z.array(schema),
  
  /**
   * Enum field
   */
  enum: <T extends [string, ...string[]]>(values: T) => z.enum(values),
};

/**
 * Common schema patterns that can be reused across the application
 */
export const schemaPatterns = {
  /**
   * Pagination query parameters
   */
  pagination: z.object({
    page: z.coerce.number().int().positive().optional().default(1),
    limit: z.coerce.number().int().positive().max(100).optional().default(20),
  }),
  
  /**
   * Sorting query parameters
   */
  sorting: z.object({
    sortBy: z.string().optional(),
    sortDir: z.enum(['asc', 'desc']).optional().default('asc'),
  }),
  
  /**
   * Basic filter parameters
   */
  filter: z.object({
    filter: z.record(z.string()).optional(),
  }),
  
  /**
   * ID parameter
   */
  idParam: z.object({
    id: z.coerce.number().int().positive(),
  }),
  
  /**
   * UUID parameter
   */
  uuidParam: z.object({
    id: z.string().uuid(),
  }),
  
  /**
   * Audit fields (created/updated)
   */
  auditFields: z.object({
    createdAt: z.date().optional(),
    updatedAt: z.date().optional(),
    createdById: z.number().int().positive().optional(),
    updatedById: z.number().int().positive().optional(),
  }),
  
  /**
   * Generic name/description fields pattern
   */
  nameDescription: z.object({
    name: schemaTypes.requiredString(3, 100),
    description: schemaTypes.optionalString(1000),
  }),
};

/**
 * Helper to create a schema for a basic entity with ID and audit fields
 */
export const createBaseEntitySchema = <T extends z.ZodRawShape>(schema: T) => {
  return z.object({
    id: schemaTypes.id.optional(),
    ...schema,
    ...schemaPatterns.auditFields.shape,
  });
};

/**
 * Helper to create a schema for a basic entity with required create fields
 */
export const createEntitySchema = <T extends z.ZodRawShape>(schema: T) => {
  return createBaseEntitySchema(schema);
};

/**
 * Helper to create an update schema (all fields optional)
 */
export const createUpdateSchema = <T extends z.ZodRawShape>(schema: T) => {
  return createBaseEntitySchema(schema).partial();
};

/**
 * Helper to pick specific fields from a schema
 */
export const pickFields = <T extends z.ZodRawShape, K extends keyof T>(
  schema: z.ZodObject<T>,
  keys: K[]
) => {
  return schema.pick(Object.fromEntries(keys.map(k => [k, true])) as any);
};

/**
 * Helper to omit specific fields from a schema
 */
export const omitFields = <T extends z.ZodRawShape, K extends keyof T>(
  schema: z.ZodObject<T>,
  keys: K[]
) => {
  return schema.omit(Object.fromEntries(keys.map(k => [k, true])) as any);
};

export default {
  types: schemaTypes,
  patterns: schemaPatterns,
  createBaseEntitySchema,
  createEntitySchema,
  createUpdateSchema,
  pickFields,
  omitFields,
};