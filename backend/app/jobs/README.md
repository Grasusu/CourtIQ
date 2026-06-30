# Jobs

Job queue adapters isolate how work is enqueued.

Current adapter:

- `BackgroundUploadQueue` uses FastAPI `BackgroundTasks` to process uploads locally.

Future adapter:

- `SQSUploadQueue` can send `{ "upload_job_id": 123 }` messages to AWS SQS.

Routes should create durable database jobs first, then enqueue work through this layer.
