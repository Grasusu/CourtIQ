# CV Depth Roadmap

These features should come after the MVP works.

## Backend Depth

- JWT auth.
- Coach/player roles.
- PostgreSQL database.
- Alembic migrations.
- Background upload processing with a local worker entrypoint.
- Upload job status tracking.
- Clear CSV validation errors.
- Unit and API tests.

## Data Product Depth

- Rolling averages.
- Consistency score.
- Team average comparisons.
- Best/worst game detection.
- Generated match summaries.
- PDF reports.

## Cloud Depth

- Docker Compose for local development.
- S3 for CSV storage.
- SQS or Redis-backed queue.
- Worker process for async analytics.
- CI with GitHub Actions.
- Deployed demo.

## Current Cloud-Ready Pieces

- `UploadJob` table stores job metadata, status, counters, and failure messages.
- Upload endpoint stores CSV files locally and queues work through FastAPI `BackgroundTasks`.
- `backend/app/workers/upload_worker.py` exposes a worker entrypoint that can later be called by SQS/Celery/RQ.
- Frontend polls upload job status, so the UI is already compatible with cloud workers.

## CV Bullet Target

```txt
Built and deployed CourtIQ, a full-stack basketball analytics platform using FastAPI, PostgreSQL, React, Docker, and cloud storage; implemented authenticated team workspaces, CSV ingestion, advanced player efficiency metrics, async processing, and a tested REST API.
```
