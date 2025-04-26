import { pgTable, serial, text, timestamp, integer, doublePrecision, boolean } from 'drizzle-orm/pg-core';
import { InferSelectModel, InferInsertModel } from 'drizzle-orm';
import { users } from './users';
import { taxDistricts } from './taxDistricts';

/**
 * Levy rate model for setting and tracking tax rates by district.
 */
export const levyRates = pgTable('levy_rate', {
  id: serial('id').primaryKey(),
  taxDistrictId: integer('tax_district_id').notNull().references(() => taxDistricts.id),
  levyRate: doublePrecision('levy_rate').notNull(),
  levyAmount: doublePrecision('levy_amount').notNull(),
  assessedValueBasis: doublePrecision('assessed_value_basis').notNull(),
  isFinal: boolean('is_final').default(false),
  notes: text('notes'),
  year: integer('year').notNull(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id)
});

/**
 * Levy scenario model for analysis and forecasting.
 */
export const levyScenarios = pgTable('levy_scenario', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id),
  name: text('name').notNull(),
  description: text('description'),
  taxDistrictId: integer('tax_district_id').notNull().references(() => taxDistricts.id),
  baseYear: integer('base_year').notNull(),
  targetYear: integer('target_year').notNull(),
  levyAmount: doublePrecision('levy_amount'),
  assessedValueChange: doublePrecision('assessed_value_change').default(0.0),
  newConstructionValue: doublePrecision('new_construction_value').default(0.0),
  annexationValue: doublePrecision('annexation_value').default(0.0),
  isPublic: boolean('is_public').default(false),
  resultLevyRate: doublePrecision('result_levy_rate'),
  resultLevyAmount: doublePrecision('result_levy_amount'),
  status: text('status').default('DRAFT'),
  year: integer('year').notNull(),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id)
});

// Types for TypeScript type safety
export type LevyRate = InferSelectModel<typeof levyRates>;
export type NewLevyRate = InferInsertModel<typeof levyRates>;

export type LevyScenario = InferSelectModel<typeof levyScenarios>;
export type NewLevyScenario = InferInsertModel<typeof levyScenarios>;