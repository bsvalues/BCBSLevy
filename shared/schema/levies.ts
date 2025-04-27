import { pgTable, serial, integer, text, timestamp, boolean, jsonb, varchar, doublePrecision } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { users } from './users';
import { taxDistricts } from './taxDistricts';
import { taxCodes } from './taxCodes';

/**
 * Levies schema
 * 
 * Stores levy information including rates, calculations, and associated tax districts/codes
 */
export const levies = pgTable('levy', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 128 }).notNull(),
  description: text('description'),
  taxYear: integer('tax_year').notNull(),
  taxDistrictId: integer('tax_district_id').references(() => taxDistricts.id).notNull(),
  taxCodeId: integer('tax_code_id').references(() => taxCodes.id),
  levyAmount: doublePrecision('levy_amount').notNull(),
  levyRate: doublePrecision('levy_rate').notNull(),
  assessedValue: doublePrecision('assessed_value'),
  newConstructionValue: doublePrecision('new_construction_value'),
  annexationValue: doublePrecision('annexation_value'),
  priorYearLevyAmount: doublePrecision('prior_year_levy_amount'),
  status: varchar('status', { length: 32 }).default('draft').notNull(),
  calculationMethod: varchar('calculation_method', { length: 64 }),
  isApproved: boolean('is_approved').default(false),
  approvedById: integer('approved_by_id').references(() => users.id),
  approvedAt: timestamp('approved_at'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id),
  metadata: jsonb('metadata'),
});

/**
 * Levy Scenarios schema
 * 
 * Stores levy calculation scenarios for simulation and forecasting
 */
export const levyScenarios = pgTable('levy_scenario', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 128 }).notNull(),
  description: text('description'),
  taxDistrictId: integer('tax_district_id').references(() => taxDistricts.id).notNull(),
  taxCodeId: integer('tax_code_id').references(() => taxCodes.id),
  year: integer('year').notNull(),
  baseAssessedValue: doublePrecision('base_assessed_value').notNull(),
  assessedValueChange: doublePrecision('assessed_value_change'),
  newConstructionValue: doublePrecision('new_construction_value'),
  annexationValue: doublePrecision('annexation_value'),
  levyAmount: doublePrecision('levy_amount'),
  resultLevyRate: doublePrecision('result_levy_rate'),
  resultLevyAmount: doublePrecision('result_levy_amount'),
  isActive: boolean('is_active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id),
  userId: integer('user_id').references(() => users.id),
});

/**
 * Levy Scenario Results schema
 * 
 * Stores detailed calculation results for levy scenarios
 */
export const levyScenarioResults = pgTable('levy_scenario_result', {
  id: serial('id').primaryKey(),
  scenarioId: integer('scenario_id').references(() => levyScenarios.id).notNull(),
  calculationDate: timestamp('calculation_date').defaultNow(),
  initialLevyRate: doublePrecision('initial_levy_rate'),
  initialLevyAmount: doublePrecision('initial_levy_amount'),
  finalLevyRate: doublePrecision('final_levy_rate'),
  finalLevyAmount: doublePrecision('final_levy_amount'),
  complianceStatus: varchar('compliance_status', { length: 32 }),
  calculationDetails: jsonb('calculation_details'),
  createdAt: timestamp('created_at').defaultNow(),
});

// Define levy relations
export const leviesRelations = relations(levies, ({ one }) => ({
  taxDistrict: one(taxDistricts, {
    fields: [levies.taxDistrictId],
    references: [taxDistricts.id]
  }),
  taxCode: one(taxCodes, {
    fields: [levies.taxCodeId],
    references: [taxCodes.id]
  }),
  createdBy: one(users, {
    fields: [levies.createdById],
    references: [users.id]
  }),
  updatedBy: one(users, {
    fields: [levies.updatedById],
    references: [users.id]
  }),
  approvedBy: one(users, {
    fields: [levies.approvedById],
    references: [users.id]
  })
}));

// Define levy scenario relations
export const levyScenariosRelations = relations(levyScenarios, ({ one, many }) => ({
  taxDistrict: one(taxDistricts, {
    fields: [levyScenarios.taxDistrictId],
    references: [taxDistricts.id]
  }),
  taxCode: one(taxCodes, {
    fields: [levyScenarios.taxCodeId],
    references: [taxCodes.id]
  }),
  createdBy: one(users, {
    fields: [levyScenarios.createdById],
    references: [users.id]
  }),
  updatedBy: one(users, {
    fields: [levyScenarios.updatedById],
    references: [users.id]
  }),
  user: one(users, {
    fields: [levyScenarios.userId],
    references: [users.id]
  }),
  results: many(levyScenarioResults)
}));

// Define levy scenario results relations
export const levyScenarioResultsRelations = relations(levyScenarioResults, ({ one }) => ({
  scenario: one(levyScenarios, {
    fields: [levyScenarioResults.scenarioId],
    references: [levyScenarios.id]
  })
}));