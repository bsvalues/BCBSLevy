import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Request, Response } from 'express';

// vi.mock statements are hoisted, so these need to be defined first
vi.mock('../../../shared/db', () => {
  const mockDb = {
    query: {
      levies: { findFirst: vi.fn(), findMany: vi.fn() },
      taxDistricts: { findFirst: vi.fn(), findMany: vi.fn() },
      taxCodes: { findFirst: vi.fn(), findMany: vi.fn() },
      users: { findFirst: vi.fn(), findMany: vi.fn() }
    },
    insert: vi.fn(() => ({
      values: vi.fn(() => ({
        returning: vi.fn()
      }))
    })),
    update: vi.fn(() => ({
      set: vi.fn(() => ({
        where: vi.fn()
      }))
    })),
    delete: vi.fn(() => ({
      where: vi.fn()
    })),
    and: vi.fn(),
    not: vi.fn(),
    eq: vi.fn(),
    inArray: vi.fn(),
    desc: vi.fn()
  };
  
  // Setup default mock implementations
  mockDb.query.levies.findFirst.mockResolvedValue(null);
  mockDb.query.levies.findMany.mockResolvedValue([]);
  mockDb.query.taxDistricts.findFirst.mockResolvedValue(null);
  mockDb.query.taxDistricts.findMany.mockResolvedValue([]);
  mockDb.query.taxCodes.findFirst.mockResolvedValue(null);
  mockDb.query.taxCodes.findMany.mockResolvedValue([]);
  mockDb.query.users.findFirst.mockResolvedValue(null);
  mockDb.query.users.findMany.mockResolvedValue([]);
  mockDb.insert().values().returning.mockResolvedValue([{ id: 1 }]);
  mockDb.update().set().where.mockResolvedValue([{ id: 1 }]);
  mockDb.delete().where.mockResolvedValue({ count: 1 });
  
  return { db: mockDb };
});

vi.mock('../../../shared/schema', () => {
  return {
    levies: {
      id: 'levies.id',
      taxDistrictId: 'levies.taxDistrictId',
      taxCodeId: 'levies.taxCodeId',
      taxYear: 'levies.taxYear',
      status: 'levies.status'
    },
    taxDistricts: {
      id: 'taxDistricts.id',
      name: 'taxDistricts.name'
    },
    taxCodes: {
      id: 'taxCodes.id',
      code: 'taxCodes.code'
    },
    users: {
      id: 'users.id',
      username: 'users.username'
    }
  };
});

vi.mock('../../src/utils/handleError', () => {
  const NotFoundError = class extends Error {
    constructor(message: string) {
      super(message);
      this.name = 'NotFoundError';
    }
  };
  
  const ValidationError = class extends Error {
    constructor(message: string) {
      super(message);
      this.name = 'ValidationError';
    }
  };
  
  const AuthorizationError = class extends Error {
    constructor(message: string) {
      super(message);
      this.name = 'AuthorizationError';
    }
  };
  
  return {
    handleError: vi.fn((error, res) => res.status(500).json({ success: false })),
    NotFoundError,
    ValidationError,
    AuthorizationError
  };
});

vi.mock('../../src/utils/formatResponse', () => {
  return {
    createResponseFormatter: vi.fn(() => ({
      success: vi.fn((data, message) => ({ status: 200, data, message })),
      created: vi.fn((data, message) => ({ status: 201, data, message })),
      noContent: vi.fn(() => ({ status: 204 })),
      notFound: vi.fn((message) => ({ status: 404, message })),
      badRequest: vi.fn((message) => ({ status: 400, message }))
    }))
  };
});

vi.mock('../../src/controllers/BaseController', () => {
  return {
    BaseController: class {
      protected tableName: string;
      protected primaryKey: string;
      
      constructor(options: { tableName: string; primaryKey: string }) {
        this.tableName = options.tableName;
        this.primaryKey = options.primaryKey;
      }
      
      create = vi.fn();
      get = vi.fn();
      update = vi.fn();
      delete = vi.fn();
      list = vi.fn();
    }
  };
});

// Import after mocks are set up
import { LevyController } from '../../src/controllers/LevyController';

// Define interfaces for tests
interface AuthenticatedRequest extends Request {
  user?: {
    id: number;
    username: string;
    email: string;
    isAdmin: boolean;
    firstName?: string;
    lastName?: string;
    roles: string[];
  };
}

describe('LevyController', () => {
  let controller: LevyController;
  let req: Partial<AuthenticatedRequest>;
  let res: Partial<Response>;
  let jsonMock: any;
  let statusMock: any;
  
  beforeEach(() => {
    // Clear any previous mock calls
    vi.clearAllMocks();
    
    // Create fresh mocks for each test
    jsonMock = vi.fn().mockReturnThis();
    statusMock = vi.fn().mockReturnValue({ json: jsonMock });
    
    controller = new LevyController();
    
    req = {
      params: {},
      body: {},
      user: {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        isAdmin: false,
        firstName: 'Test',
        lastName: 'User',
        roles: ['user']
      }
    };
    
    res = {
      status: statusMock,
      json: jsonMock
    };
    
    // Important: We need to mock format response to use our mock status and json
    // This is crucial for allowing our tests to verify that response methods are called
    vi.mock('../../src/utils/formatResponse', () => ({
      createResponseFormatter: vi.fn(() => ({
        success: vi.fn((data, message) => res.status(200).json({ success: true, data, message })),
        created: vi.fn((data, message) => res.status(201).json({ success: true, data, message })),
        noContent: vi.fn(() => res.status(204).json()),
        notFound: vi.fn((message) => res.status(404).json({ success: false, message })),
        badRequest: vi.fn((message) => res.status(400).json({ success: false, message })),
        unauthorized: vi.fn((message) => res.status(401).json({ success: false, message })),
        forbidden: vi.fn((message) => res.status(403).json({ success: false, message })),
        serverError: vi.fn((message) => res.status(500).json({ success: false, message }))
      }))
    }));
  });
  
  it('should have required CRUD methods defined', () => {
    expect(controller.createLevy).toBeDefined();
    expect(controller.updateLevy).toBeDefined();
    expect(controller.deleteLevy).toBeDefined();
    expect(controller.bulkApprove).toBeDefined();
    expect(controller.getLevyHistory).toBeDefined();
  });
  
  describe('createLevy', () => {
    it('should create a new levy when valid data is provided', async () => {
      // Set up mocks for database calls
      const mockTaxDistrict = { id: 1, name: 'Test District' };
      const mockTaxCode = { id: 2, code: 'TC001' };
      const mockLevy = { id: 3, taxDistrictId: 1, taxCodeId: 2, taxYear: 2025 };
      
      // Setup request body
      req.body = {
        taxDistrictId: 1,
        taxCodeId: 2,
        taxYear: 2025,
        levyAmount: 1000.00,
        notes: 'Test levy'
      };
      
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Setup mock database responses using directly imported functions
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      db.query.taxDistricts.findFirst.mockResolvedValue(mockTaxDistrict);
      db.query.taxCodes.findFirst.mockResolvedValue(mockTaxCode);
      db.insert().values().returning.mockResolvedValue([mockLevy]);
      
      // Call the controller method
      await controller.createLevy(req as any, res as any);
      
      // Verify the results
      expect(db.query.taxDistricts.findFirst).toHaveBeenCalled();
      expect(db.query.taxCodes.findFirst).toHaveBeenCalled();
      expect(db.insert).toHaveBeenCalled();
      
      // Our test is just checking if methods were called, without verifying exact responses
      // since actual implementation may change
      expect(statusMock).toHaveBeenCalled();
      expect(jsonMock).toHaveBeenCalled();
    });
    
    it('should return an error when tax district is not found', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Setup request body
      req.body = {
        taxDistrictId: 999, // Non-existent ID
        taxCodeId: 2,
        taxYear: 2025,
        levyAmount: 1000.00
      };
      
      // Setup mock database responses
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      // Return null to simulate not finding a tax district
      db.query.taxDistricts.findFirst.mockResolvedValue(null);
      
      // Setup error handler mock
      const errorModule = await import('../../src/utils/handleError');
      const handleErrorMock = errorModule.handleError;
      
      // Create a NotFoundError instance to check later
      const NotFoundError = errorModule.NotFoundError;
      const mockError = new NotFoundError('Tax district not found');
      
      // We need to inject our error for testing since the controller will create its own
      // This is a common pattern in Jest/Vitest testing
      handleErrorMock.mockImplementation((error, res) => {
        return res.status(404).json({ success: false, message: error.message });
      });
      
      // Call the controller method
      await controller.createLevy(req as any, res as any);
      
      // Verify the database was queried
      expect(db.query.taxDistricts.findFirst).toHaveBeenCalled();
      
      // Verify handleError was called
      expect(handleErrorMock).toHaveBeenCalled();
      
      // Verify a 404 response was sent
      expect(statusMock).toHaveBeenCalledWith(404);
    });
  });
  
  describe('updateLevy', () => {
    it('should update a levy when valid data is provided', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Set up mocks for database calls
      const mockLevy = { 
        id: 3, 
        taxDistrictId: 1, 
        taxCodeId: 2, 
        taxYear: 2025, 
        levyAmount: 1000.00,
        status: 'draft',
        isApproved: false
      };
      
      // Setup request parameters and body
      req.params = { id: '3' };
      req.body = {
        levyAmount: 1500.00,
        notes: 'Updated test levy'
      };
      
      // Setup mock database responses
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      db.query.levies.findFirst.mockResolvedValue(mockLevy);
      db.update().set().where.mockResolvedValue([{ ...mockLevy, levyAmount: 1500.00 }]);
      
      // Call the controller method
      await controller.updateLevy(req as any, res as any);
      
      // Verify the results
      expect(db.query.levies.findFirst).toHaveBeenCalled();
      expect(db.update).toHaveBeenCalled();
      
      // Verify the response was successful
      expect(statusMock).toHaveBeenCalled();
      expect(jsonMock).toHaveBeenCalled();
    });
    
    it('should prevent non-admin users from updating approved levies', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Set up mocks for database calls - this time with an approved levy
      const mockLevy = { 
        id: 4, 
        taxDistrictId: 1, 
        taxCodeId: 2, 
        taxYear: 2025, 
        levyAmount: 2000.00,
        status: 'approved',
        isApproved: true
      };
      
      // Setup request parameters and body
      req.params = { id: '4' };
      req.body = {
        levyAmount: 2500.00,
        notes: 'Trying to update approved levy'
      };
      
      // Setup non-admin user
      req.user = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        isAdmin: false, // Non-admin user
        firstName: 'Test',
        lastName: 'User',
        roles: ['user']
      };
      
      // Setup mock database responses
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      db.query.levies.findFirst.mockResolvedValue(mockLevy);
      
      // Setup error handler mock
      const errorModule = await import('../../src/utils/handleError');
      const handleErrorMock = errorModule.handleError;
      
      // Create an AuthorizationError instance and mock implementation
      const AuthorizationError = errorModule.AuthorizationError;
      
      // Mock the implementation of handleError
      handleErrorMock.mockImplementation((error, res) => {
        return res.status(403).json({ success: false, message: error.message });
      });
      
      // Call the controller method
      await controller.updateLevy(req as any, res as any);
      
      // Verify the database was queried
      expect(db.query.levies.findFirst).toHaveBeenCalled();
      
      // Verify handleError was called
      expect(handleErrorMock).toHaveBeenCalled();
      
      // Verify a 403 response was sent
      expect(statusMock).toHaveBeenCalledWith(403);
      
      // Update should not have been called
      expect(db.update).not.toHaveBeenCalled();
    });
    
    it('should allow admin users to update approved levies', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Set up mocks for database calls - with an approved levy
      const mockLevy = { 
        id: 5, 
        taxDistrictId: 1, 
        taxCodeId: 2, 
        taxYear: 2025, 
        levyAmount: 3000.00,
        status: 'approved',
        isApproved: true
      };
      
      // Setup request parameters and body
      req.params = { id: '5' };
      req.body = {
        levyAmount: 3500.00,
        notes: 'Admin updating approved levy'
      };
      
      // Setup admin user
      req.user = {
        id: 2,
        username: 'adminuser',
        email: 'admin@example.com',
        isAdmin: true, // Admin user
        firstName: 'Admin',
        lastName: 'User',
        roles: ['admin', 'user']
      };
      
      // Setup mock database responses
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      db.query.levies.findFirst.mockResolvedValue(mockLevy);
      db.update().set().where.mockResolvedValue([{ ...mockLevy, levyAmount: 3500.00 }]);
      
      // Call the controller method
      await controller.updateLevy(req as any, res as any);
      
      // Verify the results
      expect(db.query.levies.findFirst).toHaveBeenCalled();
      expect(db.update).toHaveBeenCalled();
      
      // Verify the response was successful
      expect(statusMock).toHaveBeenCalled();
      expect(jsonMock).toHaveBeenCalled();
    });
  });
  
  describe('deleteLevy', () => {
    it('should delete a levy when authorized', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Setup request parameters
      req.params = { id: '3' };
      
      // Set up a non-approved levy
      const mockLevy = { 
        id: 3, 
        taxDistrictId: 1, 
        taxCodeId: 2, 
        taxYear: 2025, 
        levyAmount: 1000.00,
        status: 'draft',
        isApproved: false
      };
      
      // Setup mock database responses
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      db.query.levies.findFirst.mockResolvedValue(mockLevy);
      db.delete().where.mockResolvedValue([mockLevy]);
      
      // Call the controller method
      await controller.deleteLevy(req as any, res as any);
      
      // Verify the database queries were made
      expect(db.query.levies.findFirst).toHaveBeenCalled();
      expect(db.delete).toHaveBeenCalled();
      
      // Verify successful response (typically 204 No Content for DELETE)
      expect(statusMock).toHaveBeenCalled();
    });
    
    it('should prevent non-admin users from deleting approved levies', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Setup request parameters
      req.params = { id: '4' };
      
      // Setup non-admin user
      req.user = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        isAdmin: false, // Non-admin user
        firstName: 'Test',
        lastName: 'User',
        roles: ['user']
      };
      
      // Set up an approved levy
      const mockLevy = { 
        id: 4, 
        taxDistrictId: 1, 
        taxCodeId: 2, 
        taxYear: 2025, 
        levyAmount: 2000.00,
        status: 'approved',
        isApproved: true
      };
      
      // Setup mock database responses
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      db.query.levies.findFirst.mockResolvedValue(mockLevy);
      
      // Setup error handler mock
      const errorModule = await import('../../src/utils/handleError');
      const handleErrorMock = errorModule.handleError;
      
      // Create an AuthorizationError instance and mock implementation
      const AuthorizationError = errorModule.AuthorizationError;
      
      // Mock handleError implementation
      handleErrorMock.mockImplementation((error, res) => {
        return res.status(403).json({ success: false, message: error.message });
      });
      
      // Call the controller method
      await controller.deleteLevy(req as any, res as any);
      
      // Verify the database was queried
      expect(db.query.levies.findFirst).toHaveBeenCalled();
      
      // Verify handleError was called
      expect(handleErrorMock).toHaveBeenCalled();
      
      // Verify a 403 Forbidden response
      expect(statusMock).toHaveBeenCalledWith(403);
      
      // Delete should not have been called
      expect(db.delete).not.toHaveBeenCalled();
    });
    
    it('should allow admin users to delete approved levies', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Setup request parameters
      req.params = { id: '5' };
      
      // Setup admin user
      req.user = {
        id: 2,
        username: 'adminuser',
        email: 'admin@example.com',
        isAdmin: true, // Admin user
        firstName: 'Admin',
        lastName: 'User',
        roles: ['admin', 'user']
      };
      
      // Set up an approved levy
      const mockLevy = { 
        id: 5, 
        taxDistrictId: 1, 
        taxCodeId: 2, 
        taxYear: 2025, 
        levyAmount: 3000.00,
        status: 'approved',
        isApproved: true
      };
      
      // Setup mock database responses
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      db.query.levies.findFirst.mockResolvedValue(mockLevy);
      db.delete().where.mockResolvedValue([mockLevy]);
      
      // Call the controller method
      await controller.deleteLevy(req as any, res as any);
      
      // Verify the database queries were made
      expect(db.query.levies.findFirst).toHaveBeenCalled();
      expect(db.delete).toHaveBeenCalled();
      
      // Verify successful response (typically 204 No Content for DELETE)
      expect(statusMock).toHaveBeenCalled();
    });
  });
  
  describe('bulkApprove', () => {
    it('should approve multiple levies when user is admin', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Setup admin user
      req.user = {
        id: 2,
        username: 'adminuser',
        email: 'admin@example.com',
        isAdmin: true, // Admin user
        firstName: 'Admin',
        lastName: 'User',
        roles: ['admin', 'user']
      };
      
      // Setup request body with array of levy IDs to approve
      req.body = {
        levyIds: [1, 2, 3]
      };
      
      // Mock levies to be approved
      const mockLevies = [
        { id: 1, taxDistrictId: 1, taxCodeId: 1, taxYear: 2025, status: 'draft', isApproved: false },
        { id: 2, taxDistrictId: 1, taxCodeId: 2, taxYear: 2025, status: 'draft', isApproved: false },
        { id: 3, taxDistrictId: 1, taxCodeId: 3, taxYear: 2025, status: 'draft', isApproved: false }
      ];
      
      // Setup mock database responses
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      // Set up findMany mock to return the levies
      db.query.levies.findMany.mockResolvedValue(mockLevies);
      
      // Set up update mock for approving levies
      db.update().set().where.mockResolvedValue(
        mockLevies.map(levy => ({ ...levy, status: 'approved', isApproved: true }))
      );
      
      // Call the controller method
      await controller.bulkApprove(req as any, res as any);
      
      // Verify the database operations
      expect(db.query.levies.findMany).toHaveBeenCalled();
      expect(db.update).toHaveBeenCalled();
      
      // Verify successful response
      expect(statusMock).toHaveBeenCalled();
      expect(jsonMock).toHaveBeenCalled();
    });
    
    it('should prevent non-admin users from bulk approving levies', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Setup non-admin user
      req.user = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        isAdmin: false, // Non-admin user
        firstName: 'Test',
        lastName: 'User',
        roles: ['user']
      };
      
      // Setup request body with array of levy IDs to approve
      req.body = {
        levyIds: [1, 2, 3]
      };
      
      // Setup error handler mock
      const errorModule = await import('../../src/utils/handleError');
      const handleErrorMock = errorModule.handleError;
      const AuthorizationError = errorModule.AuthorizationError;
      
      // Mock handleError implementation
      handleErrorMock.mockImplementation((error, res) => {
        return res.status(403).json({ success: false, message: error.message });
      });
      
      // Call the controller method
      await controller.bulkApprove(req as any, res as any);
      
      // Verify handleError was called
      expect(handleErrorMock).toHaveBeenCalled();
      
      // Verify a 403 Forbidden response
      expect(statusMock).toHaveBeenCalledWith(403);
      
      // Setup mock database responses - these should not get called
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      // Verify database operations were NOT performed
      expect(db.query.levies.findMany).not.toHaveBeenCalled();
      expect(db.update).not.toHaveBeenCalled();
    });
    
    it('should return an error if no levies are found to approve', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Setup admin user
      req.user = {
        id: 2,
        username: 'adminuser',
        email: 'admin@example.com',
        isAdmin: true, // Admin user
        firstName: 'Admin',
        lastName: 'User',
        roles: ['admin', 'user']
      };
      
      // Setup request body with array of levy IDs to approve
      req.body = {
        levyIds: [999, 998] // Non-existent IDs
      };
      
      // Setup mock database responses
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      // Set up findMany mock to return empty array (no levies found)
      db.query.levies.findMany.mockResolvedValue([]);
      
      // Setup error handler mock
      const errorModule = await import('../../src/utils/handleError');
      const handleErrorMock = errorModule.handleError;
      
      // Mock handleError implementation
      handleErrorMock.mockImplementation((error, res) => {
        return res.status(404).json({ success: false, message: error.message });
      });
      
      // Call the controller method
      await controller.bulkApprove(req as any, res as any);
      
      // Verify the database query was made
      expect(db.query.levies.findMany).toHaveBeenCalled();
      
      // Verify the error handling
      expect(handleErrorMock).toHaveBeenCalled();
      
      // Verify a 404 Not Found response
      expect(statusMock).toHaveBeenCalledWith(404);
      
      // Verify update was NOT called
      expect(db.update).not.toHaveBeenCalled();
    });
  });
  
  describe('getLevyHistory', () => {
    it('should retrieve levy history grouped by year', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Setup request parameters
      req.params = { districtId: '1' };
      
      // Setup mock database responses
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      // Mock the tax district to exist
      const mockTaxDistrict = { id: 1, name: 'Test District' };
      db.query.taxDistricts.findFirst.mockResolvedValue(mockTaxDistrict);
      
      // Mock the historical levy data
      const mockHistoricalRates = [
        { 
          taxYear: 2024, 
          levyAmount: 10000, 
          taxCodeId: 1, 
          taxCode: { code: 'TC001', id: 1 },
          district: { name: 'Test District', id: 1 }
        },
        { 
          taxYear: 2023, 
          levyAmount: 9500, 
          taxCodeId: 1, 
          taxCode: { code: 'TC001', id: 1 },
          district: { name: 'Test District', id: 1 }
        },
        { 
          taxYear: 2022, 
          levyAmount: 9000, 
          taxCodeId: 1, 
          taxCode: { code: 'TC001', id: 1 },
          district: { name: 'Test District', id: 1 }
        }
      ];
      
      db.query.levies.findMany.mockResolvedValue(mockHistoricalRates);
      
      // Call the controller method
      await controller.getLevyHistory(req as any, res as any);
      
      // Verify the database queries were made
      expect(db.query.taxDistricts.findFirst).toHaveBeenCalled();
      expect(db.query.levies.findMany).toHaveBeenCalled();
      
      // Verify response
      expect(statusMock).toHaveBeenCalled();
      expect(jsonMock).toHaveBeenCalled();
    });
    
    it('should return a 404 error when tax district does not exist', async () => {
      // Reset mock functions before test
      vi.clearAllMocks();
      
      // Setup request parameters with non-existent district ID
      req.params = { districtId: '999' };
      
      // Setup mock database responses
      const dbModule = await import('../../../shared/db');
      const db = dbModule.db;
      
      // Mock the tax district to NOT exist
      db.query.taxDistricts.findFirst.mockResolvedValue(null);
      
      // Setup error handler mock
      const errorModule = await import('../../src/utils/handleError');
      const handleErrorMock = errorModule.handleError;
      const NotFoundError = errorModule.NotFoundError;
      
      // Mock handleError implementation
      handleErrorMock.mockImplementation((error, res) => {
        return res.status(404).json({ success: false, message: error.message });
      });
      
      // Call the controller method
      await controller.getLevyHistory(req as any, res as any);
      
      // Verify the database was queried
      expect(db.query.taxDistricts.findFirst).toHaveBeenCalled();
      
      // Verify handleError was called
      expect(handleErrorMock).toHaveBeenCalled();
      
      // Verify the 404 response
      expect(statusMock).toHaveBeenCalledWith(404);
      expect(jsonMock).toHaveBeenCalled();
    });
  });
});