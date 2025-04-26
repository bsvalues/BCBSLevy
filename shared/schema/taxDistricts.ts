import { pgTable, serial, varchar, text, integer, numeric, boolean, timestamp } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { users } from './users';

/**
 * Tax District schema - represents tax districts
 * Corresponds to the TaxDistrict model in SQLAlchemy
 */
export const taxDistricts = pgTable('tax_district', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 100 }).notNull(),
  districtType: varchar('district_type', { length: 50 }).notNull(),
  county: varchar('county', { length: 50 }).notNull(),
  state: varchar('state', { length: 2 }).notNull(),
  taxDistrictId: varchar('tax_district_id', { length: 20 }),
  levyCode: varchar('levy_code', { length: 20 }),
  linkedLevyCode: varchar('linked_levy_code', { length: 20 }),
  description: text('description'),
  active: boolean('active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id)
});

/**
 * Levy Rate schema - represents levy rates for districts
 * Corresponds to the TaxDistrictRate model in SQLAlchemy
 */
export const taxDistrictRates = pgTable('tax_district_rate', {
  id: serial('id').primaryKey(),
  taxDistrictId: integer('tax_district_id').notNull().references(() => taxDistricts.id),
  year: integer('year').notNull(),
  baseRate: numeric('base_rate').notNull(),
  specialRate: numeric('special_rate'),
  totalRate: numeric('total_rate').notNull(),
  assessedValue: numeric('assessed_value'),
  newConstructionValue: numeric('new_construction_value'),
  totalLevyAmount: numeric('total_levy_amount'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow()
});

// Define relationships
export const taxDistrictsRelations = relations(taxDistricts, ({ many, one }) => ({
  taxCodes: many(taxCodes),
  rates: many(taxDistrictRates),
  createdBy: one(users, {
    fields: [taxDistricts.createdById],
    references: [users.id]
  }),
  updatedBy: one(users, {
    fields: [taxDistricts.updatedById],
    references: [users.id]
  })
}));

export const taxDistrictRatesRelations = relations(taxDistrictRates, ({ one }) => ({
  district: one(taxDistricts, {
    fields: [taxDistrictRates.taxDistrictId],
    references: [taxDistricts.id]
  })
}));

// Placeholder declarations to resolve relation references
// These will be fully defined in their respective files
export const taxCodes = pgTable('tax_code', {
  id: serial('id').primaryKey(),
  taxDistrictId: integer('tax_district_id').references(() => taxDistricts.id)
});