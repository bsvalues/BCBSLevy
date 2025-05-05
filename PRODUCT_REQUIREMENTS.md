# Product Requirements Document (PRD) - TerraLevy

## Target Users
- County Clerks: responsible for levy input and data validation
- Deputy Assessors: responsible for statutory review and AI drift analysis
- County Assessors: final approval and communication

## Core Features
- File Upload: XLS/XLSX/CSV ingest for levy scenarios
- RBAC Workflow: multi-stage review pipeline
- Drift Detection: ML-backed forecasting and red flag warnings
- Audit Logs: complete before/after snapshots
- Report Generation: PDF/JSON certification documents

## Future Features
- Esri Map Layer Integration
- Treasurer sync API
- Legislative change simulator

## Non-Functional
- Replit compatible
- Fast UI rendering under 100ms DOM load
- Supports >100 concurrent users