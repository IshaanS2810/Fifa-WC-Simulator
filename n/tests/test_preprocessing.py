import pandas as pd

from fifa_wc_simulator.preprocessing.clean_matches import clean_matches
from fifa_wc_simulator.preprocessing.clean_players import clean_players, normalize_position
from fifa_wc_simulator.preprocessing.standardize_teams import apply_standardization


def test_clean_matches_filters_by_year():
    data = pd.DataFrame({
        "date": ["1988-06-12", "1994-07-17"],
        "tournament": ["FIFA World Cup", "FIFA World Cup"],
        "home_team": ["Brazil", "Italy"],
        "away_team": ["Italy", "Brazil"],
    })
    result = clean_matches(data)
    assert len(result) == 1
    assert result.iloc[0]["home_team"] == "Italy"


def test_clean_players_normalizes_positions():
    data = pd.DataFrame({
        "player_id": [1, 2],
        "name": ["Player A", "Player B"],
        "position": ["GK", "CB"],
        "age": [28, 24],
        "appearances": [10, 8],
        "goals": [0, 0],
        "assists": [0, 0],
        "rating": [6.5, 6.7],
    })
    result = clean_players(data)
    assert "Goalkeeper" in result["position"].values
    assert "Defender" in result["position"].values


def test_normalize_position_codes():
    assert normalize_position("CB") == "Defender"
    assert normalize_position("GK") == "Goalkeeper"
    assert normalize_position("ST") == "Forward"
    assert normalize_position("unknown role") == "Unknown"


def test_apply_standardization_changes_team_names():
    data = pd.DataFrame({"home_team": ["USA", "IR Iran"], "away_team": ["Korea Republic", "Cote d'Ivoire"]})
    result = apply_standardization(data, ["home_team", "away_team"])
    assert "United States" in result["home_team"].values
    assert "South Korea" in result["away_team"].values
