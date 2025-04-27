# Testing Infrastructure for LevyMaster

This directory contains the testing infrastructure for the LevyMaster application's components using Vitest as the testing framework.

## Structure

The test directory is organized to mirror the structure of the source code:

```
test/
├── utils/                  # Tests for utility functions
│   ├── schemaHelper.test.ts
│   └── handleError.test.ts
├── controllers/            # Tests for API controllers
│   └── LevyController.test.ts
├── mocks/                  # Mock dependencies for testing
│   ├── BaseController.ts
│   ├── db.ts
│   ├── formatResponse.ts
│   ├── handleError.ts
│   ├── mockAuth.ts
│   └── schema.ts
└── README.md               # This file
```

## Mock Strategy

The testing infrastructure uses a robust mocking strategy to isolate the components being tested:

1. **Mock Hoisting**: All `vi.mock()` calls are properly hoisted to avoid "Cannot access before initialization" errors.
2. **Component Isolation**: Each component is tested in isolation with its dependencies mocked.
3. **Request/Response Mocking**: Express request and response objects are mocked to simulate HTTP interactions.
4. **Authentication Mocking**: User authentication and authorization are mocked to test permission scenarios.
5. **Database Mocking**: Database operations are mocked to avoid actual database connections during testing.

## Best Practices

The tests follow these best practices:

1. **Setup/Teardown**: Use `beforeEach` and `afterEach` to set up and clean up test environments.
2. **Clear Mocks**: Use `vi.clearAllMocks()` before each test to ensure a clean state.
3. **Error Handling**: Test both success and error scenarios for comprehensive coverage.
4. **Permissions**: Test different user permissions (admin vs. non-admin) to ensure proper authorization.
5. **Edge Cases**: Include edge cases such as empty results, not found resources, etc.

## Running Tests

Tests can be run using the following commands:

```bash
# Run all tests
npx vitest run

# Run tests in watch mode
npx vitest

# Run tests with coverage
npx vitest run --coverage
```

## Adding New Tests

When adding new tests, follow these guidelines:

1. Create test files with the `.test.ts` extension.
2. Use descriptive test names that clearly indicate what is being tested.
3. Mock external dependencies appropriately.
4. Test both success and error scenarios.
5. Verify correct interactions with dependencies.
6. Verify correct response status codes and data.

## Common Patterns

### Testing Controller Methods

```typescript
describe('methodName', () => {
  it('should do expected behavior when conditions are met', async () => {
    // 1. Reset mocks
    vi.clearAllMocks();
    
    // 2. Setup test data and mock responses
    const mockData = { /* test data */ };
    db.query.someTable.findFirst.mockResolvedValue(mockData);
    
    // 3. Call the method
    await controller.methodName(req as any, res as any);
    
    // 4. Verify database interactions
    expect(db.query.someTable.findFirst).toHaveBeenCalled();
    
    // 5. Verify response
    expect(statusMock).toHaveBeenCalled();
    expect(jsonMock).toHaveBeenCalled();
  });
});
```

### Testing Error Handling

```typescript
it('should handle errors properly', async () => {
  // 1. Reset mocks
  vi.clearAllMocks();
  
  // 2. Setup to trigger an error
  db.query.someTable.findFirst.mockResolvedValue(null);
  
  // 3. Mock error handler
  handleErrorMock.mockImplementation((error, res) => {
    return res.status(404).json({ success: false, message: error.message });
  });
  
  // 4. Call the method
  await controller.methodName(req as any, res as any);
  
  // 5. Verify error handling
  expect(handleErrorMock).toHaveBeenCalled();
  expect(statusMock).toHaveBeenCalledWith(404);
});
```