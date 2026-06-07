import pytest
from fastapi.testclient import TestClient

from fifa_wc_simulator.api.app import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_data():
    response = client.get("/api/health-data")
    assert response.status_code == 200
    body = response.json()
    assert "teams_loaded" in body
    assert body["teams_loaded"] >= 48


def test_list_teams():
    response = client.get("/api/teams")
    assert response.status_code == 200
    teams = response.json()["teams"]
    assert "Brazil" in teams
    assert "United States" in teams


def test_simulate_match_by_name():
    response = client.post(
        "/api/simulate-match",
        json={"home_team": "Brazil", "away_team": "Argentina"},
    )
    assert response.status_code == 200
    body = response.json()
    probs = body["outcome"]
    total = probs["win_probability"] + probs["draw_probability"] + probs["loss_probability"]
    assert abs(total - 1.0) < 1e-3
    assert body["home_team"] == "Brazil"


def test_simulate_match_unknown_team_returns_404():
    response = client.post(
        "/api/simulate-match",
        json={"home_team": "Not A Real Nation", "away_team": "Brazil"},
    )
    assert response.status_code == 404


def test_monte_carlo_limits():
    response = client.get("/api/monte-carlo/limits")
    assert response.status_code == 200
    assert response.json()["max_iterations"] == 2000


def test_monte_carlo_endpoint():
    response = client.post(
        "/api/monte-carlo",
        json={"iterations": 3, "seed": 7},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["iterations"] == 3
    assert abs(sum(body["champion_probabilities"].values()) - 1.0) < 1e-6
    assert body["most_likely_champion"]["team"] in body["champion_probabilities"]


def test_monte_carlo_rejects_excessive_iterations():
    response = client.post(
        "/api/monte-carlo",
        json={"iterations": 5000},
    )
    assert response.status_code == 422


@pytest.mark.slow
def test_simulate_group_stage():
    response = client.post("/api/simulate-group-stage")
    assert response.status_code == 200
    body = response.json()
    assert body["matches_played"] == 72
    assert len(body["qualifiers"]) == 32
