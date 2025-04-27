import { pgTable, serial, integer, text, timestamp, boolean, jsonb, varchar, doublePrecision } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { users } from './users';
import { taxDistricts } from './taxDistricts';
import { taxCodes } from './taxCodes';

/**
 * Import Log schema
 * 
 * Tracks data import events including source, status, and associated metadata
 */
export const importLogs = pgTable('import_log', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id),
  importType: varchar('import_type', { length: 32 }).notNull(),
  fileName: varchar('file_name', { length: 255 }),
  filePath: varchar('file_path', { length: 512 }),
  status: varchar('status', { length: 32 }).notNull().default('PENDING'),
  recordsProcessed: integer('records_processed'),
  recordsSuccessful: integer('records_successful'),
  recordsFailed: integer('records_failed'),
  startTime: timestamp('start_time').defaultNow(),
  endTime: timestamp('end_time'),
  errorDetails: text('error_details'),
  metadata: jsonb('metadata'),
  year: integer('year'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id),
});

/**
 * User Action Log schema
 * 
 * Tracks detailed user interactions with the system
 */
export const userActionLogs = pgTable('user_action_log', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id),
  timestamp: timestamp('timestamp').defaultNow().notNull(),
  actionType: varchar('action_type', { length: 64 }).notNull(),
  module: varchar('module', { length: 64 }).notNull(),
  submodule: varchar('submodule', { length: 64 }),
  actionDetails: jsonb('action_details'),
  entityType: varchar('entity_type', { length: 64 }),
  entityId: integer('entity_id'),
  ipAddress: varchar('ip_address', { length: 45 }),
  userAgent: varchar('user_agent', { length: 256 }),
  sessionId: varchar('session_id', { length: 128 }),
  success: boolean('success').default(true).notNull(),
  errorMessage: text('error_message'),
  durationMs: doublePrecision('duration_ms'),
});

/**
 * Levy Override Log schema
 * 
 * Tracks instances where users override calculated levy values
 */
export const levyOverrideLogs = pgTable('levy_override_log', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id).notNull(),
  timestamp: timestamp('timestamp').defaultNow().notNull(),
  taxDistrictId: integer('tax_district_id').references(() => taxDistricts.id),
  taxCodeId: integer('tax_code_id').references(() => taxCodes.id),
  year: integer('year').notNull(),
  fieldName: varchar('field_name', { length: 64 }).notNull(),
  originalValue: doublePrecision('original_value').notNull(),
  overrideValue: doublePrecision('override_value').notNull(),
  percentChange: doublePrecision('percent_change'),
  justification: text('justification'),
  requiresApproval: boolean('requires_approval').default(false),
  approved: boolean('approved'),
  approverId: integer('approver_id').references(() => users.id),
  approvalTimestamp: timestamp('approval_timestamp'),
  approvalNotes: text('approval_notes'),
  calculationParams: jsonb('calculation_params'),
});

// Define relations for import logs
export const importLogsRelations = relations(importLogs, ({ one }) => ({
  user: one(users, {
    fields: [importLogs.userId],
    references: [users.id]
  }),
  createdBy: one(users, {
    fields: [importLogs.createdById],
    references: [users.id]
  }),
  updatedBy: one(users, {
    fields: [importLogs.updatedById],
    references: [users.id]
  })
}));

// Define relations for user action logs
export const userActionLogsRelations = relations(userActionLogs, ({ one }) => ({
  user: one(users, {
    fields: [userActionLogs.userId],
    references: [users.id]
  })
}));

// Define relations for levy override logs
export const levyOverrideLogsRelations = relations(levyOverrideLogs, ({ one }) => ({
  user: one(users, {
    fields: [levyOverrideLogs.userId],
    references: [users.id]
  }),
  approver: one(users, {
    fields: [levyOverrideLogs.approverId],
    references: [users.id]
  }),
  taxDistrict: one(taxDistricts, {
    fields: [levyOverrideLogs.taxDistrictId],
    references: [taxDistricts.id]
  }),
  taxCode: one(taxCodes, {
    fields: [levyOverrideLogs.taxCodeId],
    references: [taxCodes.id]
  })
}));