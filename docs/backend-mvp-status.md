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

## Next Build Slice

1. Add API tests with `TestClient`.
2. Add Alembic migrations instead of relying only on startup table creation.
3. Add duplicate-name error handling for teams and players.
4. Add frontend upload and player profile pages.
5. Dockerize backend + database.
