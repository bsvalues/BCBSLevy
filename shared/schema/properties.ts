import { pgTable, serial, integer, text, timestamp, boolean, jsonb, varchar, doublePrecision, date } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { users } from './users';
import { taxCodes } from './taxCodes';

/**
 * Properties schema
 * 
 * Stores property records with basic information
 */
export const properties = pgTable('property', {
  id: serial('id').primaryKey(),
  parcelId: varchar('parcel_id', { length: 64 }).notNull().unique(),
  taxCodeId: integer('tax_code_id').references(() => taxCodes.id),
  propertyName: varchar('property_name', { length: 255 }),
  address: varchar('address', { length: 255 }),
  city: varchar('city', { length: 64 }),
  state: varchar('state', { length: 32 }),
  zipCode: varchar('zip_code', { length: 16 }),
  latitude: doublePrecision('latitude'),
  longitude: doublePrecision('longitude'),
  propertyType: varchar('property_type', { length: 32 }),
  landUseCode: varchar('land_use_code', { length: 32 }),
  zoning: varchar('zoning', { length: 32 }),
  acreage: doublePrecision('acreage'),
  yearBuilt: integer('year_built'),
  lastModified: timestamp('last_modified').defaultNow(),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id),
  isActive: boolean('is_active').default(true),
  metadata: jsonb('metadata'),
});

/**
 * Property Assessments schema
 * 
 * Stores yearly property assessment values
 */
export const propertyAssessments = pgTable('property_assessment', {
  id: serial('id').primaryKey(),
  propertyId: integer('property_id').references(() => properties.id).notNull(),
  assessmentYear: integer('assessment_year').notNull(),
  assessmentDate: date('assessment_date'),
  landValue: doublePrecision('land_value').notNull(),
  improvementValue: doublePrecision('improvement_value').notNull(),
  totalAssessedValue: doublePrecision('total_assessed_value').notNull(),
  marketValue: doublePrecision('market_value'),
  exemptionAmount: doublePrecision('exemption_amount').default(0),
  taxableValue: doublePrecision('taxable_value'),
  assessmentMethod: varchar('assessment_method', { length: 64 }),
  assessorId: integer('assessor_id').references(() => users.id),
  notes: text('notes'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
  updatedById: integer('updated_by_id').references(() => users.id),
});

/**
 * Property Details schema
 * 
 * Stores extended property characteristics and details
 */
export const propertyDetails = pgTable('property_detail', {
  id: serial('id').primaryKey(),
  propertyId: integer('property_id').references(() => properties.id).notNull(),
  squareFootage: integer('square_footage'),
  bedrooms: integer('bedrooms'),
  bathrooms: doublePrecision('bathrooms'),
  stories: integer('stories'),
  heatingType: varchar('heating_type', { length: 64 }),
  coolingType: varchar('cooling_type', { length: 64 }),
  foundation: varchar('foundation', { length: 64 }),
  roofMaterial: varchar('roof_material', { length: 64 }),
  exteriorWalls: varchar('exterior_walls', { length: 64 }),
  garageType: varchar('garage_type', { length: 64 }),
  garageCapacity: integer('garage_capacity'),
  poolFlag: boolean('pool_flag').default(false),
  qualityGrade: varchar('quality_grade', { length: 16 }),
  condition: varchar('condition', { length: 32 }),
  additionalFeatures: jsonb('additional_features'),
  updatedAt: timestamp('updated_at').defaultNow(),
});

// Define property relations
export const propertiesRelations = relations(properties, ({ one, many }) => ({
  taxCode: one(taxCodes, {
    fields: [properties.taxCodeId],
    references: [taxCodes.id]
  }),
  createdBy: one(users, {
    fields: [properties.createdById],
    references: [users.id]
  }),
  updatedBy: one(users, {
    fields: [properties.updatedById],
    references: [users.id]
  }),
  assessments: many(propertyAssessments),
  details: one(propertyDetails)
}));

// Define property assessment relations
export const propertyAssessmentsRelations = relations(propertyAssessments, ({ one }) => ({
  property: one(properties, {
    fields: [propertyAssessments.propertyId],
    references: [properties.id]
  }),
  assessor: one(users, {
    fields: [propertyAssessments.assessorId],
    references: [users.id]
  }),
  updatedBy: one(users, {
    fields: [propertyAssessments.updatedById],
    references: [users.id]
  })
}));

// Define property details relations
export const propertyDetailsRelations = relations(propertyDetails, ({ one }) => ({
  property: one(properties, {
    fields: [propertyDetails.propertyId],
    references: [properties.id]
  })
}));