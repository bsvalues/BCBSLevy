/**
 * Mock BaseController for testing LevyController
 */

import { Request, Response } from 'express';
import { vi } from 'vitest';

export class BaseController {
  protected tableName: string;
  protected primaryKey: string;
  
  constructor(options: { tableName: string; primaryKey: string }) {
    this.tableName = options.tableName;
    this.primaryKey = options.primaryKey;
  }
  
  // Mock common CRUD methods
  create = vi.fn(async (req: Request, res: Response) => {
    return res.status(201).json({ success: true });
  });
  
  get = vi.fn(async (req: Request, res: Response) => {
    return res.status(200).json({ success: true });
  });
  
  update = vi.fn(async (req: Request, res: Response) => {
    return res.status(200).json({ success: true });
  });
  
  delete = vi.fn(async (req: Request, res: Response) => {
    return res.status(204).json();
  });
  
  list = vi.fn(async (req: Request, res: Response) => {
    return res.status(200).json({ success: true, data: [] });
  });
}

export default BaseController;