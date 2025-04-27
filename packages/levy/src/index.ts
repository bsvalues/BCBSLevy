import express, { Request, Response, NextFunction, Application } from 'express';
import cors from 'cors';
import morgan from 'morgan';
import helmet from 'helmet';
import { json, urlencoded } from 'body-parser';
import { requireAuth } from './middleware/mockAuth';
import { db } from '../../shared/db';

// Import API routes
import apiRoutes from './routes/api';

// Create Express application
const app = express();
const PORT = process.env.PORT || 3000;

// Configure middleware
app.use(cors());
app.use(helmet());
app.use(json());
app.use(urlencoded({ extended: true }));
app.use(morgan('dev'));

// Middleware to attach db to request (useful for transactions)
app.use((req: Request, res: Response, next: NextFunction) => {
  (req as any).db = db;
  next();
});

// API routes
app.use('/api', apiRoutes);

// Simple home route for testing
app.get('/', (req: Request, res: Response) => {
  return res.json({
    name: 'TerraFusion Levy Management API',
    version: '1.0.0',
    documentation: '/api/docs',
    health: '/api/health'
  });
});

// Basic documentation route
app.get('/api/docs', (req: Request, res: Response) => {
  return res.json({
    message: 'API documentation available at /api/docs/swagger or see README.md',
    endpoints: {
      levies: '/api/levies',
      taxDistricts: '/api/tax-districts',
      taxCodes: '/api/tax-codes',
      properties: '/api/properties',
      users: '/api/users'
    }
  });
});

// Global error handler
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error('Global error handler caught:', err);
  
  return res.status(500).json({
    success: false,
    message: 'Internal Server Error',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// Handle 404 errors for routes that don't exist
app.use((req: Request, res: Response) => {
  return res.status(404).json({
    success: false,
    message: `Not Found: ${req.method} ${req.originalUrl}`
  });
});

// Start the server if not imported by another file
if (require.main === module) {
  app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
    
    // Log database connection information
    console.log('Database connected:', {
      host: process.env.PGHOST || 'default',
      port: process.env.PGPORT || '5432',
      database: process.env.PGDATABASE || 'default',
      ssl: process.env.PGSSLMODE || 'prefer'
    });
  });
}

export default app;