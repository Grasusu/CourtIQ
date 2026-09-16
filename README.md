# CourtIQ

CourtIQ is a full-stack basketball analytics platform for coaches and players.

Coaches can upload box-score CSV data, validate it, store it, and turn it into team and player insights: efficiency metrics, trends, upload history, player summaries, and dashboard views.

The project is built as a serious MVP rather than a simple chart demo. It includes authentication, a relational data model, tested analytics logic, tracked CSV ingestion jobs, and replaceable storage/queue adapters so the upload pipeline can later move from local processing to cloud-backed processing.

## Current Features

- Coach registration/login with JWT authentication.
- Coach-owned team workspaces.
- Team and player management.
- CSV box-score upload with validation.
- `UploadJob` tracking with `pending`, `processing`, `completed`, and `failed` states.
- Upload history in the frontend.
- Team dashboard metrics and scoring trends.
- Player analytics: averages, efficiency, recent form, best/worst game, and summary text.
- Demo seed/reset flow for portfolio walkthroughs.
- Backend tests for metrics, validators, API workflows, storage, queueing, and upload processing.
- Docker Compose setup with PostgreSQL.

## Project Structure

```txt
CourtIQ/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── analytics/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── workers/
│   │   └── main.py
│   ├── alembic/
│   ├── local_uploads/
│   ├── tests/
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/
│       ├── components/
│       └── types/
├── sample_data/
├── docs/
└── .github/
    └── workflows/
```

## Stack

- Backend: FastAPI, SQLAlchemy, Alembic, PostgreSQL, PyJWT
- Analytics: Python, typed CSV validation, tested basketball metrics
- Frontend: React, TypeScript, Vite
- DevOps: Docker Compose, GitHub Actions, local verification script
- Cloud-ready boundaries: local upload storage adapter, local upload queue adapter, worker entrypoint

## Local Demo

Backend:

```bash
cd backend
venv/bin/python -m alembic -c alembic.ini upgrade head
venv/bin/python -m uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
PATH=/Users/alexandrubogdan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:/Users/alexandrubogdan/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin:$PATH \
/Users/alexandrubogdan/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pnpm dev
```

Open:

```txt
http://127.0.0.1:5173
```

## Docker Demo

```bash
docker compose up --build
```

Then open:

```txt
http://127.0.0.1:5173
```

The API docs are available at:

```txt
http://127.0.0.1:8000/docs
```

Docker Compose starts:

```txt
PostgreSQL on 5432
FastAPI on 8000
React preview on 5173
```

The backend runs Alembic migrations automatically before starting.

## Verification

```bash
scripts/check.sh
```

## Next Improvements

- Make database startup migration-only for production.
- Improve the frontend visual polish and responsive dashboard layout.
- Add game detail and player comparison pages.
- Add PDF report export.
- Deploy the frontend on Vercel and the backend on a Python-friendly platform such as Render.
- Use a managed PostgreSQL database such as Neon or Supabase.
- Later, replace local upload storage with an object storage provider such as Cloudflare R2 or Supabase Storage.

See `docs/` for architecture notes, CSV format, metrics, backend status, and [deployment planning](docs/deployment.md).
