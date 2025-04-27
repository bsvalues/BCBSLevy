/**
 * Query Builder Utility
 * 
 * Helps build database queries with filtering, sorting, and pagination
 * from standardized request query parameters.
 */

import { Request } from 'express';
import { SQL, sql } from 'drizzle-orm';
import { asc, desc, eq, ilike, and, or, inArray } from 'drizzle-orm';

/**
 * Interface for pagination parameters
 */
export interface PaginationParams {
  page: number;
  limit: number;
}

/**
 * Interface for sorting parameters
 */
export interface SortingParams {
  sortBy: string;
  sortDir: 'asc' | 'desc';
}

/**
 * Interface for filter parameters
 * Represents filters as key-value pairs
 */
export interface FilterParams {
  [key: string]: string | number | boolean | string[] | number[] | null;
}

/**
 * Interface for query parameters combining pagination, sorting, and filtering
 */
export interface QueryParams {
  pagination: PaginationParams;
  sorting: SortingParams;
  filters: FilterParams;
}

/**
 * Extracts and normalizes pagination parameters from request
 */
export const extractPaginationParams = (req: Request): PaginationParams => {
  const page = Number(req.query.page) || 1;
  const limit = Number(req.query.limit) || 20;
  
  return {
    page: Math.max(1, page), // Ensure page is at least 1
    limit: Math.min(Math.max(1, limit), 100) // Ensure limit is between 1 and 100
  };
};

/**
 * Extracts and normalizes sorting parameters from request
 */
export const extractSortingParams = (req: Request, defaultSort: string = 'id'): SortingParams => {
  const sortBy = req.query.sortBy?.toString() || defaultSort;
  const sortDir = (req.query.sortDir?.toString()?.toLowerCase() === 'desc') ? 'desc' : 'asc';
  
  return { sortBy, sortDir };
};

/**
 * Extracts filter parameters from request query
 * Supports filter[fieldName]=value format
 */
export const extractFilterParams = (req: Request): FilterParams => {
  const filters: FilterParams = {};
  
  Object.keys(req.query).forEach(key => {
    // Check if key matches filter[fieldName] pattern
    const match = key.match(/^filter\[(.*)\]$/);
    if (match && match[1]) {
      const fieldName = match[1];
      const value = req.query[key];
      
      // Handle array values (comma-separated)
      if (typeof value === 'string' && value.includes(',')) {
        filters[fieldName] = value.split(',');
      } else {
        filters[fieldName] = value as string | number | boolean | null;
      }
    }
  });
  
  return filters;
};

/**
 * Builds complete query parameters object from request
 */
export const buildQueryParams = (req: Request, defaultSort: string = 'id'): QueryParams => {
  return {
    pagination: extractPaginationParams(req),
    sorting: extractSortingParams(req, defaultSort),
    filters: extractFilterParams(req)
  };
};

/**
 * Applies pagination to a query
 * Returns offset and limit values
 */
export const applyPagination = (pagination: PaginationParams) => {
  const { page, limit } = pagination;
  const offset = (page - 1) * limit;
  
  return { offset, limit };
};

/**
 * Creates a sorting SQL clause based on sorting parameters
 */
export const applySorting = <T extends Record<string, any>>(
  table: T,
  sorting: SortingParams
): SQL => {
  const { sortBy, sortDir } = sorting;
  
  // Ensure the sortBy field exists in the table
  if (sortBy in table) {
    const column = table[sortBy as keyof typeof table];
    return sortDir === 'asc' ? asc(column) : desc(column);
  }
  
  // Fallback to id sorting if sortBy field doesn't exist
  return sortDir === 'asc' ? asc(table.id) : desc(table.id);
};

/**
 * Creates filter conditions from filter parameters
 */
export const applyFilters = <T extends Record<string, any>>(
  table: T,
  filters: FilterParams
): SQL | undefined => {
  const conditions: SQL[] = [];
  
  Object.entries(filters).forEach(([field, value]) => {
    // Skip if field doesn't exist in table
    if (!(field in table)) return;
    
    const column = table[field as keyof typeof table];
    
    if (value === null) {
      conditions.push(sql`${column} IS NULL`);
    } else if (Array.isArray(value)) {
      conditions.push(inArray(column, value));
    } else if (typeof value === 'string') {
      // Use ILIKE for string values (case-insensitive partial match)
      conditions.push(ilike(column, `%${value}%`));
    } else {
      // Exact match for numbers and booleans
      conditions.push(eq(column, value));
    }
  });
  
  if (conditions.length === 0) {
    return undefined;
  }
  
  return and(...conditions);
};

export default buildQueryParams;