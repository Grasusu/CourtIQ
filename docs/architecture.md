# Architecture

CourtIQ should grow in stages.

## MVP Architecture

```txt
CSV upload
   |
FastAPI endpoint
   |
CSV validation
   |
Analytics calculations
   |
Database records
   |
Dashboard API response
```

This is enough for the first serious version.

## Full-Stack Depth Architecture

```txt
React frontend
   |
FastAPI backend
   |
PostgreSQL
   |
UploadJob table
   |
Redis/RQ or Celery worker
   |
Analytics module
   |
Metric snapshots and reports
```

## Cloud Extension

```txt
React frontend
   |
FastAPI backend
   |
PostgreSQL
   |
S3 uploaded CSV storage
   |
SQS queue
   |
Python worker or Lambda
   |
Metrics saved to PostgreSQL
```

## Current Docker Architecture

```txt
React preview container
   |
FastAPI backend container
   |
PostgreSQL container
```

The backend container runs Alembic migrations at startup, then starts Uvicorn.

Do not build the cloud version first. Build the MVP locally, then replace local storage and local processing with cloud-backed pieces.
