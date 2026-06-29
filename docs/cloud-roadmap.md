# Cloud Roadmap

CourtIQ is now structured so the upload pipeline can move to cloud services without rewriting the product flow.

## Current Local Flow

```txt
React upload form
   |
FastAPI upload endpoint
   |
local_uploads/ CSV file
   |
UploadJob row in PostgreSQL or SQLite
   |
FastAPI BackgroundTasks calls upload_worker.run_upload_job
   |
CSV validation and stats import
   |
UploadJob becomes completed or failed
```

This is still local, but it already has the important production shape: stored file, job metadata, worker entrypoint, status polling, and clear failure states.

## AWS Version Later

```txt
React upload form
   |
FastAPI backend
   |
S3 CSV object
   |
UploadJob row in managed PostgreSQL
   |
SQS message with upload_job_id
   |
Python worker on ECS, Render, Fly.io, or Lambda
   |
Metrics saved to PostgreSQL
   |
Frontend polls UploadJob status
```

The frontend does not need a big rewrite because it already talks to job-status endpoints.

## Migration Steps

1. Add an upload storage abstraction.
   - Local adapter writes to `local_uploads/`.
   - S3 adapter writes to a private S3 bucket.
   - `UploadJob.stored_path` can become an S3 key.

2. Add a queue abstraction.
   - Local adapter uses FastAPI `BackgroundTasks`.
   - Cloud adapter sends `{ "upload_job_id": 123 }` to SQS.

3. Run a worker outside the API process.
   - Start with a simple Python process that calls `run_upload_job(job_id)`.
   - Later deploy it as an ECS service, Fly worker, Render worker, or Lambda consumer.

4. Move the database to managed PostgreSQL.
   - Use the existing Alembic migrations.
   - Keep local Docker Compose for development.

5. Add operational basics.
   - AWS Budget alert.
   - S3 lifecycle rule for old uploads.
   - Job retry limits.
   - Dead-letter queue for failed SQS messages.

## What Not To Do Yet

- Do not start with Lambda, SQS, IAM, and S3 before the MVP is stable.
- Do not upload public CSVs; use private storage.
- Do not put AWS credentials in the repo.
- Do not replace the frontend flow; keep job polling as the stable contract.

## CV Angle

This local implementation already supports a strong explanation:

```txt
Implemented a tracked CSV ingestion pipeline with UploadJob persistence, background processing, status polling, validation failures, and analytics persistence, designed to be migrated from local storage/background tasks to S3/SQS workers.
```
