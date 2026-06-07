import pytest

from fifa_wc_simulator.models.predict_match import clear_prediction_cache
from fifa_wc_simulator.models.team_lookup import clear_team_lookup_cache
from fifa_wc_simulator.simulation.monte_carlo import run_monte_carlo
from fifa_wc_simulator.simulation.wc2026_annex_c import clear_annex_cache


@pytest.fixture(autouse=True)
def clear_caches():
    clear_team_lookup_cache()
    clear_prediction_cache()
    clear_annex_cache()
    yield
    clear_team_lookup_cache()
    clear_prediction_cache()
    clear_annex_cache()


@pytest.mark.slow
def test_monte_carlo_probabilities_sum_for_champion():
    result = run_monte_carlo(iterations=5, seed=99)
    total = sum(result["champion_probabilities"].values())
    assert abs(total - 1.0) < 1e-6
    assert result["iterations"] == 5
    assert result["most_likely_champion"]["team"] in result["champion_probabilities"]


def test_monte_carlo_rejects_invalid_iterations():
    with pytest.raises(ValueError):
        run_monte_carlo(iterations=0)
    with pytest.raises(ValueError):
        run_monte_carlo(iterations=5000)


@pytest.mark.slow
def test_monte_carlo_seed_is_reproducible():
    first = run_monte_carlo(iterations=3, seed=42)
    second = run_monte_carlo(iterations=3, seed=42)
    assert first["champion_probabilities"] == second["champion_probabilities"]
