# Workers

CourtIQ now has a small worker boundary for CSV ingestion.

Current local flow:

1. API receives CSV upload.
2. API creates an `UploadJob`.
3. API stores the uploaded file locally.
4. FastAPI `BackgroundTasks` calls `upload_worker.run_upload_job`.
5. Worker saves metrics and marks the job completed or failed.

Later cloud flow:

1. API stores the uploaded file in S3.
2. API creates an `UploadJob`.
3. API sends the job id to SQS or Redis.
4. A separate Python worker calls `upload_worker.run_upload_job`.
5. Frontend keeps polling the same job-status endpoints.
