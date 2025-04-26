import { pgTable, serial, varchar, text, timestamp, integer, doublePrecision, boolean, pgEnum } from 'drizzle-orm/pg-core';
import { InferSelectModel, InferInsertModel } from 'drizzle-orm';
import { users } from './users';
import { taxCodes } from './taxCodes';

/**
 * Property type enum for classification
 */
export const propertyTypeEnum = pgEnum('property_type', [
  'RESIDENTIAL',
  'COMMERCIAL',
  'INDUSTRIAL',
  'AGRICULTURAL',
  'PUBLIC',
  'OTHER'
]);

/**
 * Property model representing individual taxable properties.
 */
export const properties = pgTable('property', {
  id: serial('id').primaryKey(),
  propertyId: varchar('property_id', { length: 64 }).notNull(),
  taxCodeId: integer('tax_code_id').notNull().references(() => taxCodes.id),
  ownerName: varchar('owner_name', { length: 128 }),
  propertyAddress: varchar('property_address', { length: 256 }),
  city: varchar('city', { length: 64 }),
  state: varchar('state', { length: 2 }),
  zipCode: varchar('zip_code', { length: 10 }),
  propertyType: propertyTypeEnum('property_type'),
  assessedValue: doublePrecision('assessed_value').default(0.0),
  marketValue: doublePrecision('market_value'),
  landValue: doublePrecision('land_value'),
  buildingValue: doublePrecision('building_value'),
  taxExempt: boolean('tax_exempt').default(false),
  exemptionAmount: doublePrecision('exemption_amount').default(0.0),
  taxableValue: doublePrecision('taxable_value').default(0.0),
  taxAmount: doublePrecision('tax_amount').default(0.0),
  longitude: doublePrecision('longitude'),
  latitude: doublePrecision('latitude'),
  year: integer('year').notNull(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id)
});

// Types for TypeScript type safety
export type Property = InferSelectModel<typeof properties>;
export type NewProperty = InferInsertModel<typeof properties>;