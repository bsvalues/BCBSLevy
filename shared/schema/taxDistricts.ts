import { pgTable, serial, integer, text, timestamp, boolean, jsonb, varchar, doublePrecision } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { users } from './users';

/**
 * Tax Districts schema
 * 
 * Stores information about tax districts including their geographical and administrative details
 */
export const taxDistricts = pgTable('tax_district', {
  id: serial('id').primaryKey(),
  name: varchar('name', { length: 128 }).notNull(),
  description: text('description'),
  countyName: varchar('county_name', { length: 64 }).notNull(),
  stateName: varchar('state_name', { length: 64 }).notNull(),
  taxDistrictId: varchar('tax_district_id', { length: 32 }),
  levyCode: varchar('levy_code', { length: 32 }),
  linkedLevyCode: varchar('linked_levy_code', { length: 32 }),
  districtType: varchar('district_type', { length: 32 }).notNull(),
  creationYear: integer('creation_year'),
  isActive: boolean('is_active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id),
  metadata: jsonb('metadata'),
});

/**
 * District Configuration schema
 * 
 * Stores district-specific configuration and settings
 */
export const districtConfigurations = pgTable('district_configuration', {
  id: serial('id').primaryKey(),
  taxDistrictId: integer('tax_district_id').references(() => taxDistricts.id).notNull(),
  configKey: varchar('config_key', { length: 64 }).notNull(),
  configValue: jsonb('config_value').notNull(),
  description: text('description'),
  active: boolean('active').default(true),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
  updatedById: integer('updated_by_id').references(() => users.id),
});

// Define tax district relations
export const taxDistrictsRelations = relations(taxDistricts, ({ one, many }) => ({
  createdBy: one(users, {
    fields: [taxDistricts.createdById],
    references: [users.id]
  }),
  updatedBy: one(users, {
    fields: [taxDistricts.updatedById],
    references: [users.id]
  }),
  configuration: many(districtConfigurations)
}));

// Define district configuration relations
export const districtConfigurationsRelations = relations(districtConfigurations, ({ one }) => ({
  taxDistrict: one(taxDistricts, {
    fields: [districtConfigurations.taxDistrictId],
    references: [taxDistricts.id]
  }),
  updatedBy: one(users, {
    fields: [districtConfigurations.updatedById],
    references: [users.id]
  })
}));