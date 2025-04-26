import { pgTable, serial, varchar, text, timestamp, integer, pgEnum, jsonb, doublePrecision } from 'drizzle-orm/pg-core';
import { InferSelectModel, InferInsertModel } from 'drizzle-orm';
import { users } from './users';

/**
 * Import type enum for classifying imports
 */
export const importTypeEnum = pgEnum('import_type', [
  'TAX_DISTRICT',
  'TAX_CODE',
  'PROPERTY',
  'RATE',
  'LEVY',
  'OTHER'
]);

/**
 * ImportLog model for tracking and auditing data imports.
 */
export const importLogs = pgTable('import_log', {
  id: serial('id').primaryKey(),
  userId: integer('user_id').references(() => users.id),
  filename: varchar('filename', { length: 256 }).notNull(),
  importType: importTypeEnum('import_type'),
  recordCount: integer('record_count').default(0),
  successCount: integer('success_count').default(0),
  errorCount: integer('error_count').default(0),
  status: varchar('status', { length: 32 }).default('PENDING'),
  errorDetails: text('error_details'),
  processingTime: doublePrecision('processing_time'),
  year: integer('year').notNull(),
  importMetadata: jsonb('import_metadata'),
  createdAt: timestamp('created_at').notNull().defaultNow(),
  updatedAt: timestamp('updated_at').notNull().defaultNow(),
  createdById: integer('created_by_id').references(() => users.id),
  updatedById: integer('updated_by_id').references(() => users.id)
});

// Types for TypeScript type safety
export type ImportLog = InferSelectModel<typeof importLogs>;
export type NewImportLog = InferInsertModel<typeof importLogs>;