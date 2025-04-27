import { checkDatabaseConnection } from '../../shared/db';

// Increase timeout for tests
jest.setTimeout(30000);

// Setup global variables and mocks
beforeAll(async () => {
  // Verify database connection is working
  const dbConnected = await checkDatabaseConnection();
  
  if (!dbConnected) {
    throw new Error('Database connection failed in test setup');
  }
  
  console.log('✅ Database connection verified for tests');
  
  // Set up any necessary mocks
  process.env.NODE_ENV = 'test';
});

// Cleanup after all tests
afterAll(async () => {
  // Any global cleanup code
});