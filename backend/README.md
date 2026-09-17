# Backend

FastAPI backend for CourtIQ.

The backend owns authentication, teams, players, CSV uploads, validation, analytics calculations, persistence, upload job tracking, and background processing.

## Main Modules

- `app/api/routes/` - FastAPI route handlers.
- `app/analytics/` - basketball metrics and CSV validation.
- `app/models/` - SQLAlchemy models.
- `app/schemas/` - Pydantic request/response schemas.
- `app/services/` - business logic.
- `app/storage/` - upload storage adapters.
- `app/jobs/` - upload queue adapters.
- `app/workers/` - worker entrypoints.
- `tests/` - API, analytics, upload, storage, and queue tests.

## Local Run

From this folder:

```bash
venv/bin/python -m alembic -c alembic.ini upgrade head
venv/bin/python -m uvicorn app.main:app --reload
```

Then open:

```txt
http://127.0.0.1:8000/docs
```

Uploads use local storage by default. Set `UPLOAD_STORAGE_BACKEND=supabase` together with `SUPABASE_URL`, `SUPABASE_SECRET_KEY`, and `SUPABASE_STORAGE_BUCKET` to use the private Supabase Storage adapter in production.

## Important Principle

Keep basketball calculations, CSV validation, storage, queueing, and API routing separated. Each part should be testable without starting the full application.
