import { pgTable, serial, varchar, text, timestamp, integer, pgEnum, jsonb, doublePrecision } from 'drizzle-orm/pg-core';
import { InferSelectModel, InferInsertModel } from 'drizzle-orm';
import { users } from './users';

/**
 * Export type enum for classifying exports
 */
export const exportTypeEnum = pgEnum('export_type', [
  'TAX_DISTRICT',
  'TAX_CODE',
  'PROPERTY',
  'RATE',
  'LEVY',
  'REPORT',
  'LEVY_REPORT',
  'ANALYSIS',
  'OTHER'
]);

/**
 * ExportLog model for tracking and auditing data exports.
 */
export const exportLogs = pgTable('export_log', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').notNull().references(() => users.id),
  filename: varchar('filename', { length: 256 }).notNull(),
  exportType: exportTypeEnum('export_type').notNull(),
  recordCount: integer('record_count').default(0),
  status: varchar('status', { length: 32 }).default('PENDING'),
  errorDetails: text('error_details'),
  processingTime: doublePrecision('processing_time'),
  year: integer('year').notNull(),
  exportMetadata: jsonb('export_metadata'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id)
});

// Types for TypeScript type safety
export type ExportLog = InferSelectModel<typeof exportLogs>;
export type NewExportLog = InferInsertModel<typeof exportLogs>;