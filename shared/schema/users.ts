import { pgTable, serial, varchar, boolean, timestamp, text } from 'drizzle-orm/pg-core';
import { relations } from 'drizzle-orm';

/**
 * Users schema
 * 
 * Stores user account information and credentials
 */
export const users = pgTable('user', {
  id: serial('id').primaryKey(),
  username: varchar('username', { length: 64 }).notNull().unique(),
  email: varchar('email', { length: 120 }).notNull().unique(),
  passwordHash: varchar('password_hash', { length: 256 }).notNull(),
  firstName: varchar('first_name', { length: 64 }),
  lastName: varchar('last_name', { length: 64 }),
  isActive: boolean('is_active').default(true).notNull(),
  isAdmin: boolean('is_admin').default(false).notNull(),
  lastLogin: timestamp('last_login'),
  createdAt: timestamp('created_at').defaultNow().notNull(),
  updatedAt: timestamp('updated_at').defaultNow().notNull(),
  resetToken: varchar('reset_token', { length: 100 }),
  resetTokenExpiry: timestamp('reset_token_expiry'),
  preferences: text('preferences'),
});

/**
 * User roles schema
 * 
 * Stores role assignments for users to enable role-based access control
 */
export const userRoles = pgTable('user_role', {
  id: serial('id').primaryKey(),
  userId: serial('user_id').references(() => users.id).notNull(),
  role: varchar('role', { length: 64 }).notNull(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

// Define user relations
export const usersRelations = relations(users, ({ many }) => ({
  roles: many(userRoles)
}));

// Define user role relations
export const userRolesRelations = relations(userRoles, ({ one }) => ({
  user: one(users, {
    fields: [userRoles.userId],
    references: [users.id]
  })
}));