# Tests

Tests should make the analytics trustworthy.

Add these first:

- `test_metrics.py`
- `test_csv_validation.py`
- `test_trends.py`

Then add API tests:

- `test_uploads.py`
- `test_players.py`
- `test_teams.py`

Do not use fake placeholder tests that only assert `True`. Each test should prove a real basketball or API behavior.
