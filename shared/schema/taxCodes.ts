import { pgTable, serial, integer, text, timestamp, boolean, jsonb, varchar, doublePrecision } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { users } from './users';
import { taxDistricts } from './taxDistricts';

/**
 * Tax Codes schema
 * 
 * Stores tax code information including rates and associated districts
 */
export const taxCodes = pgTable('tax_code', {
  id: serial('id').primaryKey(),
  code: varchar('code', { length: 32 }).notNull().unique(),
  description: text('description'),
  countyName: varchar('county_name', { length: 64 }),
  stateName: varchar('state_name', { length: 64 }),
  taxYear: integer('tax_year').notNull(),
  levyRate: doublePrecision('levy_rate').notNull(),
  totalAssessedValue: doublePrecision('total_assessed_value'),
  totalLevyAmount: doublePrecision('total_levy_amount'),
  effectiveTaxRate: doublePrecision('effective_tax_rate'),
  isActive: boolean('is_active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id),
  metadata: jsonb('metadata'),
});

/**
 * Tax Code Historical Rate schema
 * 
 * Stores historical tax rates for each tax code over multiple years
 */
export const taxCodeHistoricalRates = pgTable('tax_code_historical_rate', {
  id: serial('id').primaryKey(),
  taxCodeId: integer('tax_code_id').references(() => taxCodes.id).notNull(),
  year: integer('year').notNull(),
  levyRate: doublePrecision('levy_rate').notNull(),
  levyAmount: doublePrecision('levy_amount'),
  totalAssessedValue: doublePrecision('total_assessed_value'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
});

/**
 * Tax Code to Tax District junction table
 * 
 * Connects tax codes to tax districts with relationship metadata
 */
export const taxCodeToTaxDistrict = pgTable('tax_code_to_tax_district', {
  id: serial('id').primaryKey(),
  taxCodeId: integer('tax_code_id').references(() => taxCodes.id).notNull(),
  taxDistrictId: integer('tax_district_id').references(() => taxDistricts.id).notNull(),
  percentage: doublePrecision('percentage').default(100.0),
  isActive: boolean('is_active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
});

// Define tax code relations
export const taxCodesRelations = relations(taxCodes, ({ one, many }) => ({
  createdBy: one(users, {
    fields: [taxCodes.createdById],
    references: [users.id]
  }),
  updatedBy: one(users, {
    fields: [taxCodes.updatedById],
    references: [users.id]
  }),
  historicalRates: many(taxCodeHistoricalRates),
  districts: many(taxCodeToTaxDistrict)
}));

// Define tax code historical rates relations
export const taxCodeHistoricalRatesRelations = relations(taxCodeHistoricalRates, ({ one }) => ({
  taxCode: one(taxCodes, {
    fields: [taxCodeHistoricalRates.taxCodeId],
    references: [taxCodes.id]
  })
}));

// Define tax code to tax district relations
export const taxCodeToTaxDistrictRelations = relations(taxCodeToTaxDistrict, ({ one }) => ({
  taxCode: one(taxCodes, {
    fields: [taxCodeToTaxDistrict.taxCodeId],
    references: [taxCodes.id]
  }),
  taxDistrict: one(taxDistricts, {
    fields: [taxCodeToTaxDistrict.taxDistrictId],
    references: [taxDistricts.id]
  })
}));