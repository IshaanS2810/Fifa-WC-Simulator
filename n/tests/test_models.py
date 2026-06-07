from fifa_wc_simulator.models.predict_match import clear_prediction_cache, predict_match
from fifa_wc_simulator.models.team_lookup import clear_team_lookup_cache


def setup_function():
    clear_team_lookup_cache()
    clear_prediction_cache()


def teardown_function():
    clear_team_lookup_cache()
    clear_prediction_cache()


def test_predict_match_probabilities_sum_to_one():
    outcome = predict_match("Brazil", "Argentina")
    total = outcome["win_probability"] + outcome["draw_probability"] + outcome["loss_probability"]
    assert abs(total - 1.0) < 1e-3


def test_predict_match_legacy_feature_dicts():
    team_a = {
        "attack": 0.5,
        "midfield": 0.5,
        "defense": 0.5,
        "goalkeeper": 0.4,
        "overall_strength": 0.48,
        "squad_depth": 0.4,
        "superstar_index": 0.6,
        "final_team_rating": 0.5,
        "elo": 1800.0,
        "elo_normalized": 0.8,
        "enhanced_team_rating": 0.55,
        "wins_last5_overall": 3.0,
        "goals_scored_last5_overall": 8.0,
        "goals_conceded_last5_overall": 2.0,
    }
    team_b = {**team_a, "overall_strength": 0.35, "elo": 1600.0, "wins_last5_overall": 1.0}
    outcome = predict_match(team_a, team_b)
    total = outcome["win_probability"] + outcome["draw_probability"] + outcome["loss_probability"]
    assert abs(total - 1.0) < 1e-3
    assert outcome["win_probability"] >= outcome["loss_probability"]
