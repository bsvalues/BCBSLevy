/**
 * Mock database for testing
 * 
 * This mock provides an interface similar to the Drizzle ORM
 * to allow testing controllers and utilities without accessing
 * the actual database.
 */

import { vi } from 'vitest';

// Mock query builder with basic functionality
export const db = {
  // Query builder
  query: {
    levies: {
      findFirst: vi.fn(),
      findMany: vi.fn()
    },
    taxDistricts: {
      findFirst: vi.fn(),
      findMany: vi.fn()
    },
    taxCodes: {
      findFirst: vi.fn(),
      findMany: vi.fn()
    },
    users: {
      findFirst: vi.fn(),
      findMany: vi.fn()
    }
  },
  
  // Mock insert operations
  insert: vi.fn().mockReturnValue({
    values: vi.fn().mockReturnValue({
      returning: vi.fn().mockResolvedValue([{ id: 1 }])
    })
  }),
  
  // Mock update operations
  update: vi.fn().mockReturnValue({
    set: vi.fn().mockReturnValue({
      where: vi.fn().mockResolvedValue([{ id: 1 }])
    })
  }),
  
  // Mock delete operations
  delete: vi.fn().mockReturnValue({
    where: vi.fn().mockResolvedValue({ count: 1 })
  }),
  
  // Condition helpers
  and: vi.fn(),
  or: vi.fn(),
  not: vi.fn(),
  eq: vi.fn(),
  ne: vi.fn(),
  gt: vi.fn(),
  gte: vi.fn(),
  lt: vi.fn(),
  lte: vi.fn(),
  like: vi.fn(),
  ilike: vi.fn(),
  inArray: vi.fn(),
  notInArray: vi.fn(),
  desc: vi.fn(),
  asc: vi.fn()
};

// Helper functions to manipulate mock data for tests
export const mockDataHelpers = {
  reset: () => {
    // Reset all mock functions
    vi.clearAllMocks();
  },
  
  setMockData: (entity: string, data: any[]) => {
    if (!db.query[entity]) {
      throw new Error(`Mock entity "${entity}" not found`);
    }
    
    // Setup findFirst to return the first matching item
    db.query[entity].findFirst.mockImplementation((options: any) => {
      if (!options || !options.where) {
        return Promise.resolve(data[0] || null);
      }
      
      // Simple where implementation for tests
      const result = data.find(item => {
        // For now, just assume the where clause is using eq
        const whereKey = Object.keys(options.where)[0];
        return item[whereKey] === options.where[whereKey];
      });
      
      return Promise.resolve(result || null);
    });
    
    // Setup findMany to return filtered data
    db.query[entity].findMany.mockImplementation((options: any) => {
      if (!options || !options.where) {
        return Promise.resolve(data);
      }
      
      // Simple where implementation for tests
      const result = data.filter(item => {
        // For now, just assume the where clause is using eq
        const whereKey = Object.keys(options.where)[0];
        return item[whereKey] === options.where[whereKey];
      });
      
      return Promise.resolve(result);
    });
  }
};

export default db;