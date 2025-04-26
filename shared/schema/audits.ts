import { pgTable, serial, varchar, text, timestamp, integer, jsonb, boolean, doublePrecision } from 'drizzle-orm/pg-core';
import { InferSelectModel, InferInsertModel } from 'drizzle-orm';
import { users } from './users';
import { taxDistricts } from './taxDistricts';
import { taxCodes } from './taxCodes';

/**
 * AuditLog model for tracking all significant data changes.
 */
export const auditLogs = pgTable('audit_log', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id),
  timestamp: timestamp('timestamp').notNull().defaultNow(),
  tableName: varchar('table_name', { length: 64 }).notNull(),
  recordId: integer('record_id').notNull(),
  action: varchar('action', { length: 16 }).notNull(), // CREATE, UPDATE, DELETE
  oldValues: jsonb('old_values'),
  newValues: jsonb('new_values'),
  ipAddress: varchar('ip_address', { length: 45 }),
  userAgent: varchar('user_agent', { length: 256 })
});

/**
 * UserActionLog model for tracking detailed user interactions with the system.
 */
export const userActionLogs = pgTable('user_action_log', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id),
  timestamp: timestamp('timestamp').notNull().defaultNow(),
  actionType: varchar('action_type', { length: 64 }).notNull(), // VIEW, SEARCH, EXPORT, CALCULATE, etc.
  module: varchar('module', { length: 64 }).notNull(), // levy_calculator, reports, admin, etc.
  submodule: varchar('submodule', { length: 64 }),
  actionDetails: jsonb('action_details'),
  entityType: varchar('entity_type', { length: 64 }),
  entityId: integer('entity_id'),
  ipAddress: varchar('ip_address', { length: 45 }),
  userAgent: varchar('user_agent', { length: 256 }),
  sessionId: varchar('session_id', { length: 128 }),
  success: boolean('success').notNull().default(true),
  errorMessage: text('error_message'),
  durationMs: doublePrecision('duration_ms')
});

/**
 * LevyOverrideLog model for tracking levy calculation overrides.
 */
export const levyOverrideLogs = pgTable('levy_override_log', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id),
  timestamp: timestamp('timestamp').notNull().defaultNow(),
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
  calculationParams: jsonb('calculation_params')
});

/**
 * LevyAuditRecord model for storing levy audit results.
 */
export const levyAuditRecords = pgTable('levy_audit_record', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id),
  taxDistrictId: integer('tax_district_id').references(() => taxDistricts.id),
  taxCodeId: integer('tax_code_id').references(() => taxCodes.id),
  year: integer('year'),
  auditType: varchar('audit_type', { length: 32 }).notNull(), // COMPLIANCE, RECOMMENDATION, VERIFICATION, QUERY
  fullAudit: boolean('full_audit').default(false),
  complianceScore: doublePrecision('compliance_score'),
  query: text('query'),
  results: jsonb('results'),
  status: varchar('status', { length: 32 }).notNull().default('PENDING'), // PENDING, COMPLETED, FAILED
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  errorDetails: text('error_details')
});

/**
 * APICallLog model for logging historical API calls for monitoring and analytics.
 */
export const apiCallLogs = pgTable('api_call_log', {
  id: serial('id').primaryKey(),
  service: varchar('service', { length: 64 }).notNull(), // e.g. "anthropic", "openai", etc.
  endpoint: varchar('endpoint', { length: 128 }).notNull(),
  method: varchar('method', { length: 16 }).notNull(), // HTTP method
  timestamp: timestamp('timestamp').notNull().defaultNow(),
  durationMs: doublePrecision('duration_ms'),
  statusCode: integer('status_code'),
  success: boolean('success').notNull().default(false),
  errorMessage: text('error_message'),
  retryCount: integer('retry_count').notNull().default(0),
  params: jsonb('params'), // Redacted parameters
  responseSummary: jsonb('response_summary'), // Summarized response
  userId: integer('user_id').references(() => users.id)
});

// Types for TypeScript type safety
export type AuditLog = InferSelectModel<typeof auditLogs>;
export type NewAuditLog = InferInsertModel<typeof auditLogs>;

export type UserActionLog = InferSelectModel<typeof userActionLogs>;
export type NewUserActionLog = InferInsertModel<typeof userActionLogs>;

export type LevyOverrideLog = InferSelectModel<typeof levyOverrideLogs>;
export type NewLevyOverrideLog = InferInsertModel<typeof levyOverrideLogs>;

export type LevyAuditRecord = InferSelectModel<typeof levyAuditRecords>;
export type NewLevyAuditRecord = InferInsertModel<typeof levyAuditRecords>;

export type APICallLog = InferSelectModel<typeof apiCallLogs>;
export type NewAPICallLog = InferInsertModel<typeof apiCallLogs>;