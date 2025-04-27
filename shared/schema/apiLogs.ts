import { pgTable, serial, integer, text, timestamp, boolean, jsonb, varchar, doublePrecision } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';
import { users } from './users';

/**
 * API Call Log schema
 * 
 * Tracks all API calls made to external services for monitoring and analytics
 */
export const apiCallLogs = pgTable('api_call_log', {
  id: serial('id').primaryKey(),
  service: varchar('service', { length: 64 }).notNull(),
  endpoint: varchar('endpoint', { length: 128 }).notNull(),
  method: varchar('method', { length: 16 }).notNull(),
  timestamp: timestamp('timestamp').defaultNow().notNull(),
  durationMs: doublePrecision('duration_ms'),
  statusCode: integer('status_code'),
  success: boolean('success').default(false).notNull(),
  errorMessage: text('error_message'),
  retryCount: integer('retry_count').default(0).notNull(),
  params: jsonb('params'),
  responseSummary: jsonb('response_summary'),
  userId: integer('user_id').references(() => users.id),
});

// Define relations for API call logs
export const apiCallLogsRelations = relations(apiCallLogs, ({ one }) => ({
  user: one(users, {
    fields: [apiCallLogs.userId],
    references: [users.id]
  })
}));