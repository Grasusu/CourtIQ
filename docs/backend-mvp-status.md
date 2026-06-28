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
- Pydantic schemas for API request and response data.
- CSV validation and typed box-score parsing.
- Services for:
  - creating/listing teams
  - creating/listing players
  - listing games
  - importing box-score CSV files
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
- GitHub Actions workflow for backend tests and frontend build.
- Local `scripts/check.sh` verification script.

## Frontend Implemented

- Vite + React + TypeScript app.
- Register/login screen with persisted JWT session.
- API client for teams, players, CSV uploads, team analytics, and player analytics.
- Team workspace sidebar.
- CSV upload panel.
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

1. Add auth basics: register/login and coach-owned teams.
2. Add Docker Compose with backend + database.
3. Replace startup table creation with migration-only setup before deployment.
4. Add seeded demo data/reset script.
5. Add async upload processing with Redis/RQ after the synchronous MVP feels stable.
