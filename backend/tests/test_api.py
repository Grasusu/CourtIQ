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


def test_different_coaches_can_use_the_same_team_name(api_client):
    first_headers = auth_headers(api_client, "first@example.com")
    second_headers = auth_headers(api_client, "second@example.com")
    payload = {"name": "CourtIQ Demo", "season": "2026-27"}

    first_response = api_client.post("/teams", json=payload, headers=first_headers)
    second_response = api_client.post("/teams", json=payload, headers=second_headers)

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert first_response.json()["id"] != second_response.json()["id"]


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
    assert completed_job["rows_processed"] == 24

    jobs_response = api_client.get(f"/teams/{team_id}/uploads/jobs", headers=headers)
    assert jobs_response.status_code == 200
    assert jobs_response.json()[0]["id"] == upload_job["id"]

    players_response = api_client.get(f"/teams/{team_id}/players", headers=headers)
    assert players_response.status_code == 200
    assert len(players_response.json()) == 4

    player_id = players_response.json()[0]["id"]
    player_analytics_response = api_client.get(f"/players/{player_id}/analytics", headers=headers)
    assert player_analytics_response.status_code == 200
    assert player_analytics_response.json()["games_played"] == 6
    assert player_analytics_response.json()["average_points"] == 20.67

    team_analytics_response = api_client.get(f"/teams/{team_id}/analytics", headers=headers)
    assert team_analytics_response.status_code == 200
    assert team_analytics_response.json()["games_played"] == 6
    assert team_analytics_response.json()["roster_size"] == 4
    assert team_analytics_response.json()["top_scorers"][0]["player_name"] == "Alex"


def test_compare_players_and_read_game_detail(api_client):
    headers = auth_headers(api_client)
    seed_response = api_client.post("/demo/seed", headers=headers)
    assert seed_response.status_code == 201
    team_id = seed_response.json()["team_id"]

    players_response = api_client.get(f"/teams/{team_id}/players", headers=headers)
    players = players_response.json()
    selected_ids = [players[0]["id"], players[1]["id"]]

    comparison_response = api_client.get(
        f"/teams/{team_id}/player-comparison",
        params=[("player_ids", player_id) for player_id in selected_ids],
        headers=headers,
    )
    assert comparison_response.status_code == 200
    comparison = comparison_response.json()
    assert comparison["team_id"] == team_id
    assert [player["player_id"] for player in comparison["players"]] == selected_ids
    assert all(player["games_played"] == 6 for player in comparison["players"])

    games_response = api_client.get(f"/teams/{team_id}/games", headers=headers)
    assert games_response.status_code == 200
    game_id = games_response.json()[0]["id"]

    detail_response = api_client.get(f"/games/{game_id}", headers=headers)
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["id"] == game_id
    assert len(detail["player_stats"]) == 4
    assert detail["team_totals"]["points"] == sum(
        stat["points"] for stat in detail["player_stats"]
    )
    assert detail["player_stats"][0]["points"] >= detail["player_stats"][1]["points"]


def test_manual_game_entry_updates_analytics_and_rejects_duplicates(api_client):
    headers = auth_headers(api_client)
    team = api_client.post(
        "/teams",
        json={"name": "Manual Stats", "season": "2026-27"},
        headers=headers,
    ).json()
    alex = api_client.post(
        f"/teams/{team['id']}/players",
        json={"name": "Alex", "position": "Guard", "jersey_number": 7},
        headers=headers,
    ).json()
    maya = api_client.post(
        f"/teams/{team['id']}/players",
        json={"name": "Maya", "position": "Forward", "jersey_number": 12},
        headers=headers,
    ).json()
    payload = {
        "game_date": "2026-09-20",
        "opponent": "Rotterdam Waves",
        "player_stats": [
            {
                "player_id": alex["id"], "minutes": 31, "points": 18,
                "rebounds": 5, "assists": 7, "steals": 2, "blocks": 0,
                "turnovers": 2, "fgm": 7, "fga": 14, "three_pm": 2,
                "three_pa": 5, "ftm": 2, "fta": 3,
            },
            {
                "player_id": maya["id"], "minutes": 29, "points": 12,
                "rebounds": 9, "assists": 3, "steals": 1, "blocks": 2,
                "turnovers": 1, "fgm": 5, "fga": 11, "three_pm": 1,
                "three_pa": 3, "ftm": 1, "fta": 2,
            },
        ],
    }

    response = api_client.post(
        f"/teams/{team['id']}/games/manual",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["team_totals"]["points"] == 30
    assert len(response.json()["player_stats"]) == 2

    analytics = api_client.get(f"/teams/{team['id']}/analytics", headers=headers)
    assert analytics.json()["games_played"] == 1
    player_analytics = api_client.get(f"/players/{alex['id']}/analytics", headers=headers).json()
    assert player_analytics["games_played"] == 1
    assert player_analytics["intelligence"]["forecast"]["confidence"] == "insufficient"

    duplicate = api_client.post(
        f"/teams/{team['id']}/games/manual",
        json=payload,
        headers=headers,
    )
    assert duplicate.status_code == 409


def test_manual_game_entry_validates_shooting_math(api_client):
    headers = auth_headers(api_client)
    team = api_client.post(
        "/teams",
        json={"name": "Validation Team"},
        headers=headers,
    ).json()
    player = api_client.post(
        f"/teams/{team['id']}/players",
        json={"name": "Alex"},
        headers=headers,
    ).json()

    response = api_client.post(
        f"/teams/{team['id']}/games/manual",
        json={
            "game_date": "2026-09-20",
            "opponent": "Invalid Totals",
            "player_stats": [{
                "player_id": player["id"], "minutes": 20, "points": 99,
                "rebounds": 2, "assists": 2, "steals": 0, "blocks": 0,
                "turnovers": 1, "fgm": 4, "fga": 8, "three_pm": 1,
                "three_pa": 3, "ftm": 1, "fta": 2,
            }],
        },
        headers=headers,
    )
    assert response.status_code == 422
    assert "Points must equal shooting totals" in response.text


def test_player_analytics_include_predictive_intelligence(api_client):
    headers = auth_headers(api_client)
    seed = api_client.post("/demo/seed", headers=headers).json()
    players = api_client.get(f"/teams/{seed['team_id']}/players", headers=headers).json()

    response = api_client.get(f"/players/{players[0]['id']}/analytics", headers=headers)
    assert response.status_code == 200
    intelligence = response.json()["intelligence"]
    assert intelligence["forecast"]["projected_points"] is not None
    assert intelligence["forecast"]["sample_size"] == 6
    assert intelligence["impact_profile"]["archetype"] != "Insufficient data"
    assert intelligence["recommendation"]
    assert intelligence["signals"]


def test_comparison_rejects_duplicate_or_foreign_players(api_client):
    headers = auth_headers(api_client)
    first_team = api_client.post(
        "/teams",
        json={"name": "First Team", "season": "2025-26"},
        headers=headers,
    ).json()
    second_team = api_client.post(
        "/teams",
        json={"name": "Second Team", "season": "2025-26"},
        headers=headers,
    ).json()
    first_player = api_client.post(
        f"/teams/{first_team['id']}/players",
        json={"name": "Alex"},
        headers=headers,
    ).json()
    second_player = api_client.post(
        f"/teams/{second_team['id']}/players",
        json={"name": "Maya"},
        headers=headers,
    ).json()

    duplicate_response = api_client.get(
        f"/teams/{first_team['id']}/player-comparison",
        params=[("player_ids", first_player["id"]), ("player_ids", first_player["id"])],
        headers=headers,
    )
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Select each player only once"

    foreign_response = api_client.get(
        f"/teams/{first_team['id']}/player-comparison",
        params=[("player_ids", first_player["id"]), ("player_ids", second_player["id"])],
        headers=headers,
    )
    assert foreign_response.status_code == 400
    assert foreign_response.json()["detail"] == "Every selected player must belong to this team"


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


def test_upload_returns_bad_gateway_when_storage_is_unavailable(api_client, monkeypatch):
    headers = auth_headers(api_client)
    team_response = api_client.post(
        "/teams",
        json={"name": "CourtIQ Demo", "season": "2025-26"},
        headers=headers,
    )
    team_id = team_response.json()["id"]

    class UnavailableStorage:
        def save(self, filename, content, namespace=None):
            raise RuntimeError("storage provider unavailable")

    monkeypatch.setattr(
        "app.api.routes.uploads.get_upload_storage",
        lambda: UnavailableStorage(),
    )

    response = api_client.post(
        f"/teams/{team_id}/uploads/box-score",
        files={"file": ("stats.csv", b"game_date,player\n", "text/csv")},
        headers=headers,
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Upload storage is temporarily unavailable"


def test_seed_and_reset_demo_data(api_client):
    headers = auth_headers(api_client)
    seed_response = api_client.post("/demo/seed", headers=headers)

    assert seed_response.status_code == 201
    seeded = seed_response.json()
    assert seeded["team_name"] == "CourtIQ Demo"
    assert seeded["upload"]["rows_processed"] == 24
    assert seeded["player_count"] == 4

    teams_response = api_client.get("/teams", headers=headers)
    assert teams_response.status_code == 200
    assert len(teams_response.json()) == 1

    second_seed_response = api_client.post("/demo/seed", headers=headers)
    assert second_seed_response.status_code == 201
    assert second_seed_response.json()["upload"]["stats_updated"] == 24

    reset_response = api_client.delete("/demo/reset", headers=headers)
    assert reset_response.status_code == 200
    assert reset_response.json()["deleted_teams"] == 1

    empty_teams_response = api_client.get("/teams", headers=headers)
    assert empty_teams_response.json() == []
