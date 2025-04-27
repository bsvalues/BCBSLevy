import { describe, it, expect } from 'vitest';
import { schemaTypes, schemaPatterns, createBaseEntitySchema, createEntitySchema, createUpdateSchema, pickFields, omitFields } from '../../src/utils/schemaHelper';
import { z } from 'zod';

describe('schemaHelper', () => {
  // Test schema types
  describe('schemaTypes', () => {
    it('validates basic id field', () => {
      const { id } = schemaTypes;
      
      expect(id.safeParse(1).success).toBe(true);
      expect(id.safeParse(0).success).toBe(false);
      expect(id.safeParse(-1).success).toBe(false);
      expect(id.safeParse('1').success).toBe(false);
    });

    it('validates uuid field', () => {
      const { uuid } = schemaTypes;
      const validUuid = '123e4567-e89b-12d3-a456-426614174000';
      
      expect(uuid.safeParse(validUuid).success).toBe(true);
      expect(uuid.safeParse('not-a-uuid').success).toBe(false);
    });

    it('validates email field', () => {
      const { email } = schemaTypes;
      
      expect(email.safeParse('user@example.com').success).toBe(true);
      expect(email.safeParse('invalid-email').success).toBe(false);
    });

    it('validates money field', () => {
      const { money } = schemaTypes;
      
      expect(money.safeParse(10.99).success).toBe(true);
      expect(money.safeParse(0).success).toBe(true);
      expect(money.safeParse(-1).success).toBe(false);
      expect(money.safeParse(10.999).success).toBe(false); // Not multiple of 0.01
    });

    it('validates percentage field', () => {
      const { percentage } = schemaTypes;
      
      expect(percentage.safeParse(50).success).toBe(true);
      expect(percentage.safeParse(0).success).toBe(true);
      expect(percentage.safeParse(100).success).toBe(true);
      expect(percentage.safeParse(-1).success).toBe(false);
      expect(percentage.safeParse(101).success).toBe(false);
    });
  });

  // Test schema patterns
  describe('schemaPatterns', () => {
    it('validates pagination pattern', () => {
      const { pagination } = schemaPatterns;
      
      expect(pagination.safeParse({}).success).toBe(true);
      expect(pagination.safeParse({ page: 2, limit: 50 }).success).toBe(true);
      expect(pagination.safeParse({ page: 0 }).success).toBe(false);
      expect(pagination.safeParse({ limit: 101 }).success).toBe(false);
      
      // Check defaults
      const result = pagination.parse({});
      expect(result.page).toBe(1);
      expect(result.limit).toBe(20);
    });

    it('validates idParam pattern', () => {
      const { idParam } = schemaPatterns;
      
      expect(idParam.safeParse({ id: 1 }).success).toBe(true);
      expect(idParam.safeParse({ id: '1' }).success).toBe(true); // Should coerce
      expect(idParam.safeParse({ id: 0 }).success).toBe(false);
      expect(idParam.safeParse({}).success).toBe(false);
    });
  });

  // Test schema creation helpers
  describe('schema creation helpers', () => {
    const testSchema = z.object({
      name: z.string(),
      value: z.number(),
    });

    it('creates base entity schema', () => {
      const schema = createBaseEntitySchema(testSchema.shape);
      const result = schema.safeParse({
        id: 1,
        name: 'Test',
        value: 100,
        createdAt: new Date(),
        updatedAt: new Date(),
      });
      
      expect(result.success).toBe(true);
    });

    it('creates update schema with all fields optional', () => {
      const schema = createUpdateSchema(testSchema.shape);
      
      expect(schema.safeParse({}).success).toBe(true);
      expect(schema.safeParse({ name: 'New Name' }).success).toBe(true);
      expect(schema.safeParse({ value: 200 }).success).toBe(true);
    });

    it('picks specific fields from schema', () => {
      const fullSchema = z.object({
        id: z.number(),
        name: z.string(),
        email: z.string(),
        role: z.string(),
      });
      
      const pickedSchema = pickFields(fullSchema, ['name', 'email']);
      
      expect(pickedSchema.safeParse({ name: 'Test', email: 'test@example.com' }).success).toBe(true);
      expect(pickedSchema.safeParse({ name: 'Test', role: 'admin' }).success).toBe(false);
    });

    it('omits specific fields from schema', () => {
      const fullSchema = z.object({
        id: z.number(),
        name: z.string(),
        email: z.string(),
        password: z.string(),
      });
      
      const safeSchema = omitFields(fullSchema, ['password']);
      
      const result = safeSchema.safeParse({ id: 1, name: 'Test', email: 'test@example.com' });
      expect(result.success).toBe(true);
      
      // Should fail if password is included
      expect(safeSchema.shape.password).toBeUndefined();
    });
  });
});