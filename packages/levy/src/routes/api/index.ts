import { Router } from 'express';
import taxDistrictsRouter from './tax-districts';
import taxCodesRouter from './tax-codes';
import propertiesRouter from './properties';
import leviesRouter from './levies';
import usersRouter from './users';

const router = Router();

// Register all API routes
router.use('/tax-districts', taxDistrictsRouter);
router.use('/tax-codes', taxCodesRouter);
router.use('/properties', propertiesRouter);
router.use('/levies', leviesRouter);
router.use('/users', usersRouter);

// Add a simple health check endpoint
router.get('/health', (req, res) => {
  return res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    services: {
      api: 'operational',
      database: 'operational'
    }
  });
});

export default router;