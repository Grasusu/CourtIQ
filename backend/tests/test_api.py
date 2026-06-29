"""API workflow tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def auth_headers(api_client, email: str = "coach@example.com") -> dict[str, str]:
    response = api_client.post(
        "/auth/register",
        json={"email": email, "password": "strong-password"},
    )
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health_check(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_register_login_and_me(api_client):
    register_response = api_client.post(
        "/auth/register",
        json={"email": "coach@example.com", "password": "strong-password"},
    )
    assert register_response.status_code == 201
    assert register_response.json()["user"]["email"] == "coach@example.com"

    login_response = api_client.post(
        "/auth/login",
        json={"email": "coach@example.com", "password": "strong-password"},
    )
    assert login_response.status_code == 200

    me_response = api_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {login_response.json()['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "coach@example.com"


def test_team_routes_require_authentication(api_client):
    response = api_client.get("/teams")

    assert response.status_code == 401


def test_create_team_rejects_duplicate_name(api_client):
    headers = auth_headers(api_client)
    payload = {"name": "CourtIQ Demo", "season": "2025-26"}

    first_response = api_client.post("/teams", json=payload, headers=headers)
    second_response = api_client.post("/teams", json=payload, headers=headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Team name already exists"


def test_create_player_rejects_duplicate_name_inside_team(api_client):
    headers = auth_headers(api_client)
    team_response = api_client.post(
        "/teams",
        json={"name": "CourtIQ Demo", "season": "2025-26"},
        headers=headers,
    )
    team_id = team_response.json()["id"]
    payload = {"name": "Alex", "position": "Guard", "jersey_number": 7}

    first_response = api_client.post(f"/teams/{team_id}/players", json=payload, headers=headers)
    second_response = api_client.post(f"/teams/{team_id}/players", json=payload, headers=headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Player already exists on this team"


def test_upload_csv_and_read_player_and_team_analytics(api_client):
    headers = auth_headers(api_client)
    team_response = api_client.post(
        "/teams",
        json={"name": "CourtIQ Demo", "season": "2025-26"},
        headers=headers,
    )
    team_id = team_response.json()["id"]

    csv_path = PROJECT_ROOT / "sample_data" / "demo_multi_game.csv"
    with csv_path.open("rb") as file:
        upload_response = api_client.post(
            f"/teams/{team_id}/uploads/box-score",
            files={"file": ("demo_multi_game.csv", file, "text/csv")},
            headers=headers,
    )

    assert upload_response.status_code == 201
    upload_job = upload_response.json()
    assert upload_job["filename"] == "demo_multi_game.csv"
    assert upload_job["status"] in {"pending", "processing", "completed"}

    job_response = api_client.get(f"/uploads/jobs/{upload_job['id']}", headers=headers)
    assert job_response.status_code == 200
    completed_job = job_response.json()
    assert completed_job["status"] == "completed"
    assert completed_job["rows_processed"] == 6

    jobs_response = api_client.get(f"/teams/{team_id}/uploads/jobs", headers=headers)
    assert jobs_response.status_code == 200
    assert jobs_response.json()[0]["id"] == upload_job["id"]

    players_response = api_client.get(f"/teams/{team_id}/players", headers=headers)
    assert players_response.status_code == 200
    assert len(players_response.json()) == 1

    player_id = players_response.json()[0]["id"]
    player_analytics_response = api_client.get(f"/players/{player_id}/analytics", headers=headers)
    assert player_analytics_response.status_code == 200
    assert player_analytics_response.json()["games_played"] == 6
    assert player_analytics_response.json()["average_points"] == 20.67

    team_analytics_response = api_client.get(f"/teams/{team_id}/analytics", headers=headers)
    assert team_analytics_response.status_code == 200
    assert team_analytics_response.json()["games_played"] == 6
    assert team_analytics_response.json()["roster_size"] == 1
    assert team_analytics_response.json()["top_scorers"][0]["player_name"] == "Alex"


def test_upload_job_tracks_validation_failure(api_client):
    headers = auth_headers(api_client)
    team_response = api_client.post(
        "/teams",
        json={"name": "CourtIQ Demo", "season": "2025-26"},
        headers=headers,
    )
    team_id = team_response.json()["id"]

    upload_response = api_client.post(
        f"/teams/{team_id}/uploads/box-score",
        files={"file": ("broken.csv", b"game_date,player\n2026-02-12,Alex\n", "text/csv")},
        headers=headers,
    )

    assert upload_response.status_code == 201
    job_id = upload_response.json()["id"]

    job_response = api_client.get(f"/uploads/jobs/{job_id}", headers=headers)
    assert job_response.status_code == 200
    failed_job = job_response.json()
    assert failed_job["status"] == "failed"
    assert "Missing required columns" in failed_job["error_message"]


def test_seed_and_reset_demo_data(api_client):
    headers = auth_headers(api_client)
    seed_response = api_client.post("/demo/seed", headers=headers)

    assert seed_response.status_code == 201
    seeded = seed_response.json()
    assert seeded["team_name"] == "CourtIQ Demo"
    assert seeded["upload"]["rows_processed"] == 6
    assert seeded["player_count"] == 1

    teams_response = api_client.get("/teams", headers=headers)
    assert teams_response.status_code == 200
    assert len(teams_response.json()) == 1

    second_seed_response = api_client.post("/demo/seed", headers=headers)
    assert second_seed_response.status_code == 201
    assert second_seed_response.json()["upload"]["stats_updated"] == 6

    reset_response = api_client.delete("/demo/reset", headers=headers)
    assert reset_response.status_code == 200
    assert reset_response.json()["deleted_teams"] == 1

    empty_teams_response = api_client.get("/teams", headers=headers)
    assert empty_teams_response.json() == []
