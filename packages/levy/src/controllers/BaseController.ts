/**
 * Base Controller Class
 * 
 * Provides common functionality for API controllers to standardize
 * route implementations and reduce code duplication.
 */

import { Request, Response } from 'express';
import { ZodSchema } from 'zod';
import { handleError } from '../utils/handleError';
import { createResponseFormatter } from '../utils/formatResponse';
import { validateRequest } from '../middleware/validateRequest';
import { buildQueryParams, applyPagination } from '../utils/buildQueryParams';
import { SQL, eq } from 'drizzle-orm';
import { db } from '../../../shared/db';

export interface ControllerOptions {
  tableName: string;
  primaryKey?: string;
}

/**
 * Base controller class with common CRUD operations
 */
export class BaseController {
  protected tableName: string;
  protected primaryKey: string;
  protected modelName: string;
  
  /**
   * Create a new BaseController
   * @param options - Controller options
   */
  constructor(options: ControllerOptions) {
    this.tableName = options.tableName;
    this.primaryKey = options.primaryKey || 'id';
    
    // Convert table name to model name (e.g., 'tax_districts' -> 'Tax District')
    this.modelName = this.tableName
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    
    // Remove trailing 's' if present
    if (this.modelName.endsWith('s')) {
      this.modelName = this.modelName.slice(0, -1);
    }
  }
  
  /**
   * Get a list of records with filtering, sorting, and pagination
   */
  getList = async (req: Request, res: Response) => {
    try {
      const { pagination, sorting } = buildQueryParams(req);
      const { offset, limit } = applyPagination(pagination);
      
      // Get the table from the schema
      const table = (db._.schema as any)[this.tableName];
      if (!table) {
        throw new Error(`Table ${this.tableName} not found in schema`);
      }
      
      // Execute query with filtering, sorting, and pagination
      const items = await db.query[this.tableName].findMany({
        orderBy: sorting.sortDir === 'asc' 
          ? { [sorting.sortBy]: 'asc' } 
          : { [sorting.sortBy]: 'desc' },
        offset,
        limit,
      });
      
      // Get total count for pagination
      const countResult = await db.select({ count: db.fn.count() }).from(table);
      const totalCount = Number(countResult[0].count);
      const totalPages = Math.ceil(totalCount / limit);
      
      // Format response
      const formatter = createResponseFormatter(res);
      return formatter.paginated(items, {
        page: pagination.page,
        limit: pagination.limit,
        totalItems: totalCount,
        totalPages
      }, `${this.modelName} list retrieved successfully`);
      
    } catch (error) {
      return handleError(error, res, `${this.modelName}:list`);
    }
  };
  
  /**
   * Get a single record by ID
   */
  getById = async (req: Request, res: Response) => {
    try {
      const id = parseInt(req.params.id);
      
      // Get the table from the schema
      const table = (db._.schema as any)[this.tableName];
      if (!table) {
        throw new Error(`Table ${this.tableName} not found in schema`);
      }
      
      // Find the item by ID
      const item = await db.query[this.tableName].findFirst({
        where: eq(table[this.primaryKey], id)
      });
      
      if (!item) {
        const formatter = createResponseFormatter(res);
        return formatter.error(`${this.modelName} not found`, undefined, 404);
      }
      
      // Format response
      const formatter = createResponseFormatter(res);
      return formatter.success(item, `${this.modelName} retrieved successfully`);
      
    } catch (error) {
      return handleError(error, res, `${this.modelName}:getById`);
    }
  };
  
  /**
   * Create a new record
   */
  create = async (req: Request, res: Response) => {
    try {
      const data = req.body;
      
      // Get the table from the schema
      const table = (db._.schema as any)[this.tableName];
      if (!table) {
        throw new Error(`Table ${this.tableName} not found in schema`);
      }
      
      // Add timestamps
      const now = new Date();
      data.createdAt = now;
      data.updatedAt = now;
      
      // Insert the new record
      const result = await db.insert(table).values(data).returning();
      
      // Format response
      const formatter = createResponseFormatter(res);
      return formatter.created(result[0], `${this.modelName} created successfully`);
      
    } catch (error) {
      return handleError(error, res, `${this.modelName}:create`);
    }
  };
  
  /**
   * Update an existing record
   */
  update = async (req: Request, res: Response) => {
    try {
      const id = parseInt(req.params.id);
      const data = req.body;
      
      // Get the table from the schema
      const table = (db._.schema as any)[this.tableName];
      if (!table) {
        throw new Error(`Table ${this.tableName} not found in schema`);
      }
      
      // Check if the record exists
      const existingItem = await db.query[this.tableName].findFirst({
        where: eq(table[this.primaryKey], id)
      });
      
      if (!existingItem) {
        const formatter = createResponseFormatter(res);
        return formatter.error(`${this.modelName} not found`, undefined, 404);
      }
      
      // Update timestamp
      data.updatedAt = new Date();
      
      // Update the record
      await db.update(table)
        .set(data)
        .where(eq(table[this.primaryKey], id));
      
      // Get the updated record
      const updatedItem = await db.query[this.tableName].findFirst({
        where: eq(table[this.primaryKey], id)
      });
      
      // Format response
      const formatter = createResponseFormatter(res);
      return formatter.success(updatedItem, `${this.modelName} updated successfully`);
      
    } catch (error) {
      return handleError(error, res, `${this.modelName}:update`);
    }
  };
  
  /**
   * Delete a record
   */
  delete = async (req: Request, res: Response) => {
    try {
      const id = parseInt(req.params.id);
      
      // Get the table from the schema
      const table = (db._.schema as any)[this.tableName];
      if (!table) {
        throw new Error(`Table ${this.tableName} not found in schema`);
      }
      
      // Check if the record exists
      const existingItem = await db.query[this.tableName].findFirst({
        where: eq(table[this.primaryKey], id)
      });
      
      if (!existingItem) {
        const formatter = createResponseFormatter(res);
        return formatter.error(`${this.modelName} not found`, undefined, 404);
      }
      
      // Delete the record
      await db.delete(table).where(eq(table[this.primaryKey], id));
      
      // Format response
      const formatter = createResponseFormatter(res);
      return formatter.noContent();
      
    } catch (error) {
      return handleError(error, res, `${this.modelName}:delete`);
    }
  };
}

export default BaseController;