# Backend MVP Status

This is the current backend MVP slice.

## Implemented

- SQLAlchemy database setup.
- JWT auth with register/login/me endpoints.
- Coach-owned teams with authenticated access checks.
- MVP database models:
  - `User`
  - `Team`
  - `Player`
  - `Game`
  - `PlayerGameStats`
  - `UploadJob`
- Pydantic schemas for API request and response data.
- CSV validation and typed box-score parsing.
- Services for:
  - creating/listing teams
  - creating/listing players
  - listing games
  - importing box-score CSV files
  - creating/listing/tracking upload jobs
  - processing upload jobs through a worker entrypoint
  - generating player analytics
  - generating team analytics
- FastAPI routes for:
  - `GET /health`
  - `POST /auth/register`
  - `POST /auth/login`
  - `GET /auth/me`
  - `POST /teams`
  - `GET /teams`
  - `POST /teams/{team_id}/players`
  - `GET /teams/{team_id}/players`
  - `GET /players/{player_id}`
  - `GET /teams/{team_id}/games`
  - `POST /teams/{team_id}/uploads/box-score`
  - `GET /uploads/jobs/{job_id}`
  - `GET /teams/{team_id}/uploads/jobs`
  - `GET /players/{player_id}/analytics`
  - `GET /teams/{team_id}/analytics`
  - `POST /demo/seed`
  - `DELETE /demo/reset`
- API workflow tests with `TestClient`.
- Initial Alembic migration for the MVP schema.
- Duplicate-name handling for teams and players.
- CORS support for the local React frontend.
- Demo seed/reset endpoints for portfolio walkthroughs.
- Docker Compose setup for backend and frontend.
- PostgreSQL container for Docker-based local development.
- GitHub Actions workflow for backend tests and frontend build.
- Local `scripts/check.sh` verification script.
- Local background upload processing with `UploadJob` status tracking.

## Frontend Implemented

- Vite + React + TypeScript app.
- Register/login screen with persisted JWT session.
- API client for teams, players, tracked CSV uploads, team analytics, and player analytics.
- Team workspace sidebar.
- CSV upload panel.
- Upload job status display with completed/failed states.
- Demo load/reload/reset controls.
- Team metric cards.
- Team scoring trend chart.
- Player table.
- Player analytics panel.

## Local Run

From `backend/`:

```bash
venv/bin/python -m uvicorn app.main:app --reload
```

Then open:

```txt
http://127.0.0.1:8000/docs
```

## Current Test Command

From `backend/`:

```bash
venv/bin/python -m pytest tests -q
```

## Migration Command

From `backend/`:

```bash
venv/bin/python -m alembic -c alembic.ini upgrade head
```

## Next Build Slice

1. Replace startup table creation with migration-only setup before deployment.
2. Add a storage abstraction so local CSV storage can become S3.
3. Add a queue abstraction so FastAPI `BackgroundTasks` can become SQS or Redis.
4. Add PDF report generation for completed games.
5. Add more frontend pages: game detail, player comparison, and trends.
