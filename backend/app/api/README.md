# API

This package should contain FastAPI route wiring and dependencies.

Suggested MVP routes:

- `auth.py` later, after the analytics MVP is working.
- `teams.py` for creating and listing teams.
- `players.py` for creating players and viewing profiles.
- `uploads.py` for CSV uploads.
- `analytics.py` for dashboard-ready metrics.

Keep route functions thin. Put business logic in `app/services/` and calculations in `app/analytics/`.
