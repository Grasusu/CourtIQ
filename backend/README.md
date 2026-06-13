# Backend

FastAPI backend for CourtIQ.

The backend should own authentication, teams, players, CSV uploads, validation, analytics calculations, persistence, and eventually background jobs.

## MVP Build Order

1. Analytics functions in `app/analytics/`.
2. CSV validation in `app/analytics/validators.py`.
3. Database models in `app/models/`.
4. API routes in `app/api/routes/`.
5. Service layer in `app/services/`.
6. Tests in `tests/`.

## Local Run

From this folder:

```bash
uvicorn app.main:app --reload
```

Then open:

```txt
http://127.0.0.1:8000/docs
```

## Important Principle

Keep basketball calculations separate from API routes. The API should call analytics functions; the analytics functions should be testable without starting FastAPI.
