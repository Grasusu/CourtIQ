# Backend MVP Status

This is the current backend MVP slice.

## Implemented

- SQLAlchemy database setup.
- MVP database models:
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
  - `POST /teams`
  - `GET /teams`
  - `POST /teams/{team_id}/players`
  - `GET /teams/{team_id}/players`
  - `GET /players/{player_id}`
  - `GET /teams/{team_id}/games`
  - `POST /teams/{team_id}/uploads/box-score`
  - `GET /players/{player_id}/analytics`
  - `GET /teams/{team_id}/analytics`
- API workflow tests with `TestClient`.
- Initial Alembic migration for the MVP schema.
- Duplicate-name handling for teams and players.

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
2. Add frontend upload and player profile pages.
3. Add Docker Compose with backend + database.
4. Replace startup table creation with migration-only setup before deployment.
5. Add async upload processing with Redis/RQ after the synchronous MVP feels stable.
