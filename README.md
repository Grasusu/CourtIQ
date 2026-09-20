# CourtIQ

CourtIQ is a full-stack basketball analytics platform for coaches and players.

Coaches can upload box-score CSV data, validate it, store it, and turn it into team and player insights: efficiency metrics, trends, upload history, player summaries, and dashboard views.

The project is built as a production-style portfolio application rather than a simple chart demo. It includes authentication, a relational data model, tested analytics logic, tracked CSV ingestion jobs, responsive product UI, and replaceable storage/queue adapters.

## Live Demo

- Application: [court-iq-ecru.vercel.app](https://court-iq-ecru.vercel.app/)
- API documentation: [courtiq-api-jqz4.onrender.com/docs](https://courtiq-api-jqz4.onrender.com/docs)
- Demo email: `coach@example.com`
- Demo password: `strong-password`

The Render Free backend sleeps after inactivity, so the first action can take a little longer while the API starts.

![CourtIQ team performance dashboard](docs/images/courtiq-dashboard.png)

## Current Features

- Coach registration/login with JWT authentication.
- Coach-owned team workspaces.
- Team and player management.
- CSV box-score upload with validation.
- `UploadJob` tracking with `pending`, `processing`, `completed`, and `failed` states.
- Upload history in the frontend.
- Team dashboard metrics and scoring trends.
- Player analytics: averages, efficiency, recent form, best/worst game, and summary text.
- Two-to-four player comparison with metric leaders and authenticated team boundaries.
- Game log with team totals, complete player box scores, and shooting efficiency.
- Manual roster management from the coach workspace.
- Responsive desktop, split-screen, tablet, and mobile layouts.
- Reduced-motion-aware interface animation and animated analytics charts.
- Demo seed/reset flow for portfolio walkthroughs.
- Backend tests for metrics, validators, API workflows, storage, queueing, and upload processing.
- Docker Compose setup with PostgreSQL.
- Public deployment using Vercel, Render, and Supabase PostgreSQL.
- Persistent private CSV storage using Supabase Storage in production.

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
- DevOps: Docker Compose, GitHub Actions, Render, Vercel, local verification script
- Cloud: Supabase PostgreSQL with local and Supabase upload storage adapters

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

- Add PDF report export.
- Replace in-process background tasks with a durable external queue.
- Add rate limiting, audit logs, and richer role permissions.

See `docs/` for architecture notes, CSV format, metrics, backend status, and [deployment planning](docs/deployment.md).
