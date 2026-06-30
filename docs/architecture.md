# Architecture

CourtIQ should grow in stages.

## MVP Architecture

```txt
CSV upload
   |
FastAPI endpoint
   |
Upload storage adapter
   |
local file storage
   |
UploadJob row
   |
Upload queue adapter
   |
BackgroundTasks worker entrypoint
   |
CSV validation
   |
Analytics calculations
   |
Database records
   |
Dashboard API response
```

This is enough for the first serious version while still looking like a real ingestion system.

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
Worker entrypoint
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

The current local upload pipeline already has the cloud-facing shape:

- `LocalUploadStorage` can become an S3 storage adapter.
- `BackgroundUploadQueue` can become an SQS queue adapter.
- `backend/app/workers/upload_worker.py` can become the worker process.
- The frontend can keep polling the same upload job endpoints.

See `docs/cloud-roadmap.md` for the step-by-step cloud migration path.
