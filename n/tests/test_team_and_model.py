from pathlib import Path

import pytest

from fifa_wc_simulator.models.predict_match import clear_prediction_cache, predict_match
from fifa_wc_simulator.models.team_lookup import clear_team_lookup_cache, list_team_names
from fifa_wc_simulator.preprocessing.validate_raw import validate_raw_datasets
from fifa_wc_simulator.simulation.match_simulator import simulate_match
from fifa_wc_simulator.simulation.team import Team


@pytest.fixture(autouse=True)
def clear_caches():
    clear_team_lookup_cache()
    clear_prediction_cache()
    yield
    clear_team_lookup_cache()
    clear_prediction_cache()


def test_raw_datasets_present():
    raw_dir = Path(__file__).resolve().parents[1] / "datasets" / "raw"
    if not raw_dir.exists():
        pytest.skip("datasets/raw not present (optional for CI)")
    ok, messages = validate_raw_datasets()
    assert ok, messages


def test_team_from_name_loads_features():
    names = list_team_names()
    assert len(names) > 0
    team = Team.from_name(names[0])
    assert team.name == names[0]
    assert team.overall_strength >= 0
    assert "attack" in team.to_features_dict()


def test_predict_match_by_name_uses_model():
    outcome = predict_match("Brazil", "Argentina")
    total = outcome["win_probability"] + outcome["draw_probability"] + outcome["loss_probability"]
    assert abs(total - 1.0) < 1e-3
    assert outcome.get("source") in ("xgboost", "heuristic")


def test_simulate_match_with_team_objects():
    home = Team.from_name("Brazil")
    away = Team.from_name("Argentina")
    result = simulate_match(home, away)
    assert result["prediction_source"] in ("xgboost", "heuristic")
    assert result["home_team"] == "Brazil"
    assert result["away_team"] == "Argentina"
    assert sum(result["probabilities"].values()) == pytest.approx(1.0, abs=0.02)
