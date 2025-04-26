import { pgTable, serial, varchar, text, integer, numeric, boolean, timestamp } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { taxDistricts } from './taxDistricts';
import { users } from './users';

/**
 * Tax Code schema - represents tax codes
 * Corresponds to the TaxCode model in SQLAlchemy
 */
export const taxCodes = pgTable('tax_code', {
  id: serial('id').primaryKey(),
  code: varchar('code', { length: 20 }).notNull().unique(),
  name: varchar('name', { length: 100 }),
  taxDistrictId: integer('tax_district_id').references(() => taxDistricts.id),
  description: text('description'),
  levyRate: numeric('levy_rate'),
  totalLevyAmount: numeric('total_levy_amount'),
  totalAssessedValue: numeric('total_assessed_value'),
  effectiveTaxRate: numeric('effective_tax_rate'),
  active: boolean('active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow()
});

/**
 * Historical Rate schema - represents historical tax rates
 * Corresponds to the TaxCodeHistoricalRate model in SQLAlchemy
 */
export const taxCodeHistoricalRates = pgTable('tax_code_historical_rate', {
  id: serial('id').primaryKey(),
  taxCodeId: integer('tax_code_id').notNull().references(() => taxCodes.id),
  year: integer('year').notNull(),
  levyRate: numeric('levy_rate').notNull(),
  levyAmount: numeric('levy_amount'),
  totalAssessedValue: numeric('total_assessed_value'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow()
});

/**
 * Levy Scenario schema - represents levy calculation scenarios
 * Corresponds to the LevyScenario model in SQLAlchemy
 */
export const levyScenarios = pgTable('levy_scenario', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 100 }).notNull(),
  description: text('description'),
  taxCodeId: integer('tax_code_id').references(() => taxCodes.id),
  taxDistrictId: integer('tax_district_id').references(() => taxDistricts.id),
  year: integer('year').notNull(),
  baseRate: numeric('base_rate'),
  targetYear: integer('target_year'),
  levyAmount: numeric('levy_amount'),
  assessedValueChange: numeric('assessed_value_change'),
  newConstructionValue: numeric('new_construction_value'),
  annexationValue: numeric('annexation_value'),
  resultLevyRate: numeric('result_levy_rate'),
  resultLevyAmount: numeric('result_levy_amount'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
  userId: integer('user_id').references(() => users.id),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id)
});

// Define relationships
export const taxCodesRelations = relations(taxCodes, ({ one, many }) => ({
  district: one(taxDistricts, {
    fields: [taxCodes.taxDistrictId],
    references: [taxDistricts.id]
  }),
  historicalRates: many(taxCodeHistoricalRates),
  scenarios: many(levyScenarios)
}));

export const taxCodeHistoricalRatesRelations = relations(taxCodeHistoricalRates, ({ one }) => ({
  taxCode: one(taxCodes, {
    fields: [taxCodeHistoricalRates.taxCodeId],
    references: [taxCodes.id]
  })
}));

export const levyScenariosRelations = relations(levyScenarios, ({ one }) => ({
  taxCode: one(taxCodes, {
    fields: [levyScenarios.taxCodeId],
    references: [taxCodes.id]
  }),
  taxDistrict: one(taxDistricts, {
    fields: [levyScenarios.taxDistrictId],
    references: [taxDistricts.id]
  }),
  user: one(users, {
    fields: [levyScenarios.userId],
    references: [users.id]
  }),
  createdBy: one(users, {
    fields: [levyScenarios.createdById],
    references: [users.id]
  }),
  updatedBy: one(users, {
    fields: [levyScenarios.updatedById],
    references: [users.id]
  })
}));