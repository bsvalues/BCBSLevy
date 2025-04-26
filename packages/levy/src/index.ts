import express, { Express, Request, Response } from 'express';
import http from 'http';
import cors from 'cors';
import { Pool } from 'pg';
import { drizzle } from 'drizzle-orm/node-postgres';
import morgan from 'morgan';
import helmet from 'helmet';
import dotenv from 'dotenv';
import path from 'path';

// Import routes
import levyCalculatorRoutes from './routes/levy-calculator';
import forecastingRoutes from './routes/forecasting';
import dataManagementRoutes from './routes/data-management';
import historicalAnalysisRoutes from './routes/historical-analysis';

// Load environment variables
dotenv.config();

// Create Express application
const app: Express = express();
const port = process.env.PORT || 3000;

// Initialize PostgreSQL connection
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

// Initialize Drizzle ORM
export const db = drizzle(pool);

// Apply middleware
app.use(cors());
app.use(helmet());
app.use(morgan('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Define root route
app.get('/', (req: Request, res: Response) => {
  return res.json({
    message: 'TerraFusion Levy API',
    version: '1.0.0',
    status: 'operational'
  });
});

// Register routes
app.use('/api/levy-calculator', levyCalculatorRoutes);
app.use('/api/forecasting', forecastingRoutes);
app.use('/api/data-management', dataManagementRoutes);
app.use('/api/historical-analysis', historicalAnalysisRoutes);

// Create HTTP server
const server = http.createServer(app);

// Start server
server.listen(port, () => {
  console.log(`Server running on port ${port}`);
  console.log(`http://localhost:${port}`);
});

export default app;