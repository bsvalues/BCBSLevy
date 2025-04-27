/**
 * Database configuration and connection setup
 * 
 * This module sets up the database connection using Drizzle ORM
 * and exports the configured database client.
 */

import { drizzle } from 'drizzle-orm/node-postgres';
import { Pool } from 'pg';
import * as schema from './schema';

// Configure the PostgreSQL connection pool
const pool = new Pool({
  host: process.env.PGHOST,
  port: parseInt(process.env.PGPORT || '5432'),
  user: process.env.PGUSER,
  password: process.env.PGPASSWORD,
  database: process.env.PGDATABASE,
  ssl: process.env.PGSSLMODE === 'require' ? {
    rejectUnauthorized: false // Required for some cloud providers
  } : false,
  max: parseInt(process.env.PG_MAX_CONNECTIONS || '10'), // Maximum pool size
  idleTimeoutMillis: 30000, // Close idle connections after 30 seconds
  connectionTimeoutMillis: 5000, // Return an error after 5 seconds if connection could not be established
});

// Add error handler for unexpected pool errors
pool.on('error', (err: Error) => {
  console.error('Unexpected error on idle client', err);
  process.exit(-1);
});

// Add connect handler to log successful connections
pool.on('connect', (client) => {
  console.log('Connected to PostgreSQL database');
});

// Create and configure Drizzle ORM instance
export const db = drizzle(pool, { schema });

// Helper function to check database connection
export const checkDatabaseConnection = async (): Promise<boolean> => {
  try {
    // Perform a simple query to verify database connectivity
    const client = await pool.connect();
    try {
      await client.query('SELECT NOW()');
      return true;
    } finally {
      client.release();
    }
  } catch (error) {
    console.error('Database connection check failed:', error);
    return false;
  }
};

// Export pool for direct SQL queries if needed
export { pool };