import { pgTable, serial, integer, text, timestamp, boolean, jsonb, varchar, doublePrecision } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { users } from './users';
import { taxDistricts } from './taxDistricts';

/**
 * Levy Scenario schema
 * 
 * Stores user-created levy calculation scenarios
 */
export const levyScenarios = pgTable('levy_scenario', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 128 }).notNull(),
  description: text('description'),
  userId: integer('user_id').references(() => users.id),
  taxDistrictId: integer('tax_district_id').references(() => taxDistricts.id).notNull(),
  year: integer('year').notNull(),
  priorYearLevyAmount: doublePrecision('prior_year_levy_amount').notNull(),
  targetLevyAmount: doublePrecision('target_levy_amount').notNull(),
  assessedValueChange: doublePrecision('assessed_value_change').default(0),
  newConstructionValue: doublePrecision('new_construction_value').default(0),
  annexationValue: doublePrecision('annexation_value').default(0),
  inflationRate: doublePrecision('inflation_rate').default(0.01),
  resultLevyRate: doublePrecision('result_levy_rate'),
  resultLevyAmount: doublePrecision('result_levy_amount'),
  parameters: jsonb('parameters'),
  isTemplate: boolean('is_template').default(false),
  isActive: boolean('is_active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id),
});

/**
 * Levy Scenario Results schema
 * 
 * Stores detailed calculation results for levy scenarios
 */
export const levyScenarioResults = pgTable('levy_scenario_result', {
  id: serial('id').primaryKey(),
  scenarioId: integer('scenario_id').references(() => levyScenarios.id).notNull(),
  calculationDate: timestamp('calculation_date').defaultNow().notNull(),
  calculationMethod: varchar('calculation_method', { length: 64 }).notNull(),
  totalAssessedValue: doublePrecision('total_assessed_value'),
  baseRegularLevyRate: doublePrecision('base_regular_levy_rate'),
  baseExcessLevyRate: doublePrecision('base_excess_levy_rate'),
  effectiveLevyRate: doublePrecision('effective_levy_rate').notNull(),
  actualLevyAmount: doublePrecision('actual_levy_amount').notNull(),
  inflationImpact: doublePrecision('inflation_impact'),
  newConstructionImpact: doublePrecision('new_construction_impact'),
  annexationImpact: doublePrecision('annexation_impact'),
  refundImpact: doublePrecision('refund_impact'),
  calculationDetails: jsonb('calculation_details'),
  complianceNotes: text('compliance_notes'),
  recommendedActions: text('recommended_actions'),
  isCompliant: boolean('is_compliant').default(true),
});

// Define levy scenario relations
export const levyScenariosRelations = relations(levyScenarios, ({ one, many }) => ({
  user: one(users, {
    fields: [levyScenarios.userId],
    references: [users.id]
  }),
  taxDistrict: one(taxDistricts, {
    fields: [levyScenarios.taxDistrictId],
    references: [taxDistricts.id]
  }),
  createdBy: one(users, {
    fields: [levyScenarios.createdById],
    references: [users.id]
  }),
  updatedBy: one(users, {
    fields: [levyScenarios.updatedById],
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