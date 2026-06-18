"""API workflow tests."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def test_health_check(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_team_rejects_duplicate_name(api_client):
    payload = {"name": "CourtIQ Demo", "season": "2025-26"}

    first_response = api_client.post("/teams", json=payload)
    second_response = api_client.post("/teams", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Team name already exists"


def test_create_player_rejects_duplicate_name_inside_team(api_client):
    team_response = api_client.post("/teams", json={"name": "CourtIQ Demo", "season": "2025-26"})
    team_id = team_response.json()["id"]
    payload = {"name": "Alex", "position": "Guard", "jersey_number": 7}

    first_response = api_client.post(f"/teams/{team_id}/players", json=payload)
    second_response = api_client.post(f"/teams/{team_id}/players", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Player already exists on this team"


def test_upload_csv_and_read_player_and_team_analytics(api_client):
    team_response = api_client.post("/teams", json={"name": "CourtIQ Demo", "season": "2025-26"})
    team_id = team_response.json()["id"]

    csv_path = PROJECT_ROOT / "sample_data" / "demo_multi_game.csv"
    with csv_path.open("rb") as file:
        upload_response = api_client.post(
            f"/teams/{team_id}/uploads/box-score",
            files={"file": ("demo_multi_game.csv", file, "text/csv")},
        )

    assert upload_response.status_code == 201
    assert upload_response.json()["rows_processed"] == 6

    players_response = api_client.get(f"/teams/{team_id}/players")
    assert players_response.status_code == 200
    assert len(players_response.json()) == 1

    player_id = players_response.json()[0]["id"]
    player_analytics_response = api_client.get(f"/players/{player_id}/analytics")
    assert player_analytics_response.status_code == 200
    assert player_analytics_response.json()["games_played"] == 6
    assert player_analytics_response.json()["average_points"] == 20.67

    team_analytics_response = api_client.get(f"/teams/{team_id}/analytics")
    assert team_analytics_response.status_code == 200
    assert team_analytics_response.json()["games_played"] == 6
    assert team_analytics_response.json()["roster_size"] == 1
    assert team_analytics_response.json()["top_scorers"][0]["player_name"] == "Alex"
