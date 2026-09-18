# Cloud Roadmap

CourtIQ is now structured so the upload pipeline can move to cloud services without rewriting the product flow.

## Current Production Flow

```txt
React upload form
   |
FastAPI upload endpoint
   |
SupabaseUploadStorage adapter
   |
private Supabase Storage object
   |
UploadJob row in Supabase PostgreSQL
   |
BackgroundUploadQueue adapter
   |
FastAPI BackgroundTasks calls upload_worker.run_upload_job
   |
CSV validation and stats import
   |
UploadJob becomes completed or failed
```

The deployed app uses Vercel for React, Render for FastAPI, and Supabase for PostgreSQL and private upload storage. Local development keeps the same flow with SQLite and `LocalUploadStorage`.

## Implemented Cloud-Ready Boundaries

- `backend/app/storage/uploads.py` contains `LocalUploadStorage` and `SupabaseUploadStorage`.
- `backend/app/jobs/upload_queue.py` contains `BackgroundUploadQueue`.
- `backend/app/workers/upload_worker.py` is the worker entrypoint.
- The frontend displays current upload status and recent upload jobs.

## Durable Queue Later

```txt
React upload form
   |
FastAPI backend
   |
Supabase Storage CSV object
   |
UploadJob row in managed PostgreSQL
   |
Redis, SQS, or managed queue message with upload_job_id
   |
Python worker on ECS, Render, Fly.io, or Lambda
   |
Metrics saved to PostgreSQL
   |
Frontend polls UploadJob status
```

The frontend does not need a big rewrite because it already talks to job-status endpoints.

## Migration Steps

1. Add the cloud queue adapter.
   - Local adapter already uses FastAPI `BackgroundTasks`.
   - Cloud adapter should send `{ "upload_job_id": 123 }` to Redis, SQS, or another managed queue.

2. Run a worker outside the API process.
   - Start with a simple Python process that calls `run_upload_job(job_id)`.
   - Later deploy it as an ECS service, Fly worker, Render worker, or Lambda consumer.

3. Add operational basics.
   - Storage lifecycle rules for old uploads.
   - Job retry limits.
   - Dead-letter queue for failed SQS messages.

## What Not To Do Yet

- Do not upload public CSVs; use private storage.
- Do not put service credentials in the repo.
- Do not replace the frontend flow; keep job polling as the stable contract.

## CV Angle

This local implementation already supports a strong explanation:

```txt
Implemented a tracked CSV ingestion pipeline with UploadJob persistence, background processing, status polling, validation failures, and analytics persistence, designed to be migrated from local storage/background tasks to S3/SQS workers.
```
