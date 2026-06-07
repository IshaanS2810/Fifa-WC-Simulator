from fifa_wc_simulator.simulation.match_simulator import simulate_match


def test_simulate_match_returns_score_and_probabilities():
    result = simulate_match("Brazil", "Argentina")
    assert "score" in result
    assert "probabilities" in result
    assert result["score"]["team_a"] >= 0
    assert result["score"]["team_b"] >= 0
    total_prob = sum(result["probabilities"].values())
    assert 0.99 <= total_prob <= 1.01
