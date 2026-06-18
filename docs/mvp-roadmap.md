# MVP Roadmap

## Phase 1: Analytics Core

Goal: prove CourtIQ can calculate real basketball insights.

- Add `backend/app/analytics/metrics.py`.
- Add `backend/app/analytics/trends.py`.
- Add `backend/app/analytics/validators.py`.
- Add tests for formulas and invalid CSV files.

## Phase 2: Data Model

Goal: store teams, players, games, and stats.

- Add SQLAlchemy setup.
- Add `Team`, `Player`, `Game`, and `PlayerGameStats`.
- Add Alembic migrations.

## Phase 3: Upload Flow

Goal: make the first end-to-end product workflow.

- Upload CSV through FastAPI.
- Validate the file.
- Save game/player stat rows.
- Return a clean upload result.

## Phase 4: Analytics API

Goal: expose dashboard-ready data.

- Player profile endpoint.
- Team summary endpoint.
- Recent trend endpoint.
- Comparison endpoint.

## Phase 5: Frontend MVP

Goal: make the project demoable.

- Upload page.
- Team dashboard.
- Player profile page.
- Simple charts and stat cards.

## Phase 6: Product Hardening

Goal: make the MVP feel like a serious backend project.

- API workflow tests.
- Alembic migrations.
- Duplicate handling for teams and players.
- Team analytics endpoint.
- Clear local run and migration documentation.

## Done Means

The MVP is done when someone can run the app locally, upload sample data, and understand how a player/team is performing without reading the raw CSV.
