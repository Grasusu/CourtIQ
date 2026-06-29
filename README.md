# CourtIQ

CourtIQ is a basketball analytics platform for coaches and players.

The current version is a focused MVP: coaches can authenticate, create teams, upload box-score CSV data, track upload jobs, validate stats, calculate useful basketball metrics, and view player/team insights. After the local product is stable, the project can grow into a deeper full-stack CV project with cloud storage, queues, PDF reports, CI, and deployment.

## MVP Goal

Build the smallest serious version of the product:

1. Create teams and players.
2. Upload a game stats CSV.
3. Validate the CSV with useful error messages.
4. Track upload status with an `UploadJob`.
5. Store game and player stats.
6. Calculate basketball metrics.
7. Show player profile and team dashboard data.

The first impressive milestone is:

> A coach can upload a CSV and view a player's averages, efficiency metrics, recent trend, best/worst game, and a short performance summary.

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
│       ├── pages/
│       └── types/
├── sample_data/
├── docs/
└── .github/
    └── workflows/
```

## Build Order

Start with the backend analytics core before spending time on deployment.

1. `backend/app/analytics/`
   Build metrics, trend calculations, CSV validation, and summaries.

2. `backend/tests/`
   Add tests for every metric and CSV validation rule.

3. `backend/app/models/`
   Add `Team`, `Player`, `Game`, and `PlayerGameStats`.

4. `backend/app/api/routes/`
   Add upload, teams, players, and analytics endpoints.

5. `frontend/src/`
   Build the upload screen, player profile, and team dashboard.

6. Background processing
   Track CSV processing with `UploadJob` rows and a worker entrypoint.

7. Docker, CI, and deployment
   Add this after the MVP is usable locally.

## Backend MVP Modules

```txt
analytics/
├── metrics.py       # points per minute, eFG%, TS%, AST/TO, consistency
├── trends.py        # rolling averages, improvement/decline, best/worst games
├── validators.py    # required CSV columns, numeric checks, row-level errors
└── summaries.py     # readable coach/player performance summaries
```

## Later CV Depth

After the MVP:

- Auth with coach/player roles.
- PostgreSQL and Alembic migrations.
- Upload job status tracking and background processing.
- S3 storage for uploaded CSV files.
- SQS or cloud worker for processing jobs.
- PDF match reports.
- GitHub Actions test pipeline.
- Docker Compose local setup.
- Public deployed demo.

See the `docs/` folder for the roadmap, CSV format, architecture, metrics plan, and cloud migration path.

## Current Local Demo

Backend:

```bash
cd backend
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
