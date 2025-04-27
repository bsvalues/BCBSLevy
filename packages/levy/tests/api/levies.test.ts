import request from 'supertest';
import app from '../../src/index';
import { db } from '../../../../shared/db';
import { levies, taxDistricts, taxCodes } from '../../../../shared/schema';
import { eq } from 'drizzle-orm';

// Mock data for testing
const mockTaxDistrict = {
  name: 'Test District',
  countyName: 'Test County',
  stateName: 'Test State',
  districtType: 'SCHOOL',
  isActive: true
};

const mockTaxCode = {
  code: 'TC1234',
  name: 'Test Tax Code',
  description: 'Test tax code for API tests',
  levyRate: 0.025,
  isActive: true
};

const mockLevy = {
  name: 'Test Levy',
  description: 'Test levy for API tests',
  taxYear: 2025,
  levyAmount: 500000,
  levyRate: 0.025,
  assessedValue: 20000000,
  status: 'draft'
};

// Test suite for levy API routes
describe('Levy API Routes', () => {
  let taxDistrictId: number;
  let taxCodeId: number;
  let levyId: number;

  // Setup test data before running tests
  beforeAll(async () => {
    // Clear any existing test data
    await db.delete(levies).where(eq(levies.name, mockLevy.name));
    await db.delete(taxCodes).where(eq(taxCodes.code, mockTaxCode.code));
    await db.delete(taxDistricts).where(eq(taxDistricts.name, mockTaxDistrict.name));

    // Create test tax district
    const district = await db.insert(taxDistricts).values(mockTaxDistrict).returning();
    taxDistrictId = district[0].id;

    // Create test tax code
    const taxCode = await db.insert(taxCodes).values(mockTaxCode).returning();
    taxCodeId = taxCode[0].id;
  });

  // Clean up test data after all tests
  afterAll(async () => {
    await db.delete(levies).where(eq(levies.name, mockLevy.name));
    await db.delete(taxCodes).where(eq(taxCodes.code, mockTaxCode.code));
    await db.delete(taxDistricts).where(eq(taxDistricts.name, mockTaxDistrict.name));
  });

  // Test creating a levy
  test('POST /api/levies - Create a new levy', async () => {
    const response = await request(app)
      .post('/api/levies')
      .send({
        ...mockLevy,
        taxDistrictId,
        taxCodeId
      });

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.data.name).toBe(mockLevy.name);
    expect(response.body.data.taxDistrictId).toBe(taxDistrictId);
    expect(response.body.data.taxCodeId).toBe(taxCodeId);

    // Save the levy ID for subsequent tests
    levyId = response.body.data.id;
  });

  // Test retrieving all levies
  test('GET /api/levies - Get all levies', async () => {
    const response = await request(app).get('/api/levies');

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(Array.isArray(response.body.data)).toBe(true);
    expect(response.body.data.some((levy: any) => levy.id === levyId)).toBe(true);
  });

  // Test retrieving a specific levy
  test('GET /api/levies/:id - Get a specific levy', async () => {
    const response = await request(app).get(`/api/levies/${levyId}`);

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.id).toBe(levyId);
    expect(response.body.data.name).toBe(mockLevy.name);
    expect(response.body.data.taxDistrict).toBeDefined();
    expect(response.body.data.taxCode).toBeDefined();
  });

  // Test updating a levy
  test('PUT /api/levies/:id - Update a levy', async () => {
    const updatedData = {
      name: 'Updated Test Levy',
      description: 'Updated test levy description',
      status: 'submitted'
    };

    const response = await request(app)
      .put(`/api/levies/${levyId}`)
      .send(updatedData);

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.name).toBe(updatedData.name);
    expect(response.body.data.description).toBe(updatedData.description);
    expect(response.body.data.status).toBe(updatedData.status);
  });

  // Test deleting a levy
  test('DELETE /api/levies/:id - Delete a levy', async () => {
    const response = await request(app).delete(`/api/levies/${levyId}`);

    expect(response.status).toBe(204);

    // Verify levy was deleted
    const verifyResponse = await request(app).get(`/api/levies/${levyId}`);
    expect(verifyResponse.status).toBe(404);
  });

  // Test handling invalid input
  test('POST /api/levies - Handle invalid input', async () => {
    const invalidLevy = {
      name: '', // Invalid: empty name
      taxYear: -2025, // Invalid: negative year
      levyAmount: -100, // Invalid: negative amount
      taxDistrictId: 99999 // Invalid: non-existent district
    };

    const response = await request(app)
      .post('/api/levies')
      .send(invalidLevy);

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.errors).toBeDefined();
  });
});