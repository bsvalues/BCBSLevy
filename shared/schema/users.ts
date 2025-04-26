import { pgTable, serial, varchar, text, boolean, timestamp } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

/**
 * User schema - represents application users
 * Corresponds to the User model in SQLAlchemy
 */
export const users = pgTable('user', {
  id: serial('id').primaryKey(),
  username: varchar('username', { length: 64 }).notNull().unique(),
  email: varchar('email', { length: 120 }).notNull().unique(),
  passwordHash: varchar('password_hash', { length: 256 }),
  firstName: varchar('first_name', { length: 64 }),
  lastName: varchar('last_name', { length: 64 }),
  isAdmin: boolean('is_admin').default(false),
  isActive: boolean('is_active').default(true),
  lastLogin: timestamp('last_login'),
  createdAt: timestamp('created_at').defaultNow(),
  updatedAt: timestamp('updated_at').defaultNow()
});

// Define relationships
export const usersRelations = relations(users, ({ many }) => ({
  levyScenarios: many(levyScenarios),
  levyAudits: many(levyAuditRecords),
  apiCalls: many(apiCallLogs)
}));

// Placeholder declarations to resolve relation references
// These will be fully defined in their respective files
export const levyScenarios = pgTable('levy_scenario', {
  id: serial('id').primaryKey(),
  userId: serial('user_id').references(() => users.id)
});

export const levyAuditRecords = pgTable('levy_audit_record', {
  id: serial('id').primaryKey(),
  userId: serial('user_id').references(() => users.id)
});

export const apiCallLogs = pgTable('api_call_log', {
  id: serial('id').primaryKey(),
  userId: serial('user_id').references(() => users.id)
});