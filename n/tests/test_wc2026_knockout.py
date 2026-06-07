import pytest

from fifa_wc_simulator.models.predict_match import clear_prediction_cache
from fifa_wc_simulator.models.team_lookup import clear_team_lookup_cache
from fifa_wc_simulator.simulation.wc2026_annex_c import clear_annex_cache, resolve_third_place_assignments
from fifa_wc_simulator.simulation.wc2026_bracket import (
    build_round_of_32_fixtures,
    run_knockout_stage,
)
from fifa_wc_simulator.simulation.wc2026_groups import build_official_teams, run_group_stage_2026
from fifa_wc_simulator.simulation.tournament_engine import run_tournament_2026


@pytest.fixture(autouse=True)
def clear_caches():
    clear_team_lookup_cache()
    clear_prediction_cache()
    clear_annex_cache()
    yield
    clear_team_lookup_cache()
    clear_prediction_cache()
    clear_annex_cache()


def test_annex_c_resolves_eight_third_groups():
    assignments = resolve_third_place_assignments(["E", "F", "G", "H", "I", "J", "K", "L"])
    assert assignments["1A"] == "3E"
    assert assignments["1E"] == "3F"
    assert len(assignments) == 8


def test_annex_c_rejects_wrong_count():
    with pytest.raises(ValueError):
        resolve_third_place_assignments(["A", "B", "C"])


@pytest.mark.slow
def test_round_of_32_has_sixteen_fixtures():
    group_stage = run_group_stage_2026()
    advancing = [q.group_id for q in group_stage.advancing_thirds]
    annex = resolve_third_place_assignments(advancing)
    from fifa_wc_simulator.simulation.wc2026_bracket import build_qualifier_lookup

    lookup = build_qualifier_lookup(group_stage.all_qualifiers)
    fixtures = build_round_of_32_fixtures(lookup, annex)
    assert len(fixtures) == 16
    match_ids = {m[0] for m in fixtures}
    assert match_ids == set(range(73, 89))


@pytest.mark.slow
def test_knockout_produces_champion_and_medalists():
    group_stage = run_group_stage_2026()
    knockout = run_knockout_stage(group_stage)
    assert len(knockout.round_of_32) == 16
    assert len(knockout.round_of_16) == 8
    assert len(knockout.quarter_final) == 4
    assert len(knockout.semi_final) == 2
    assert len(knockout.third_place) == 1
    assert len(knockout.final) == 1
    assert knockout.champion is not None
    assert knockout.runner_up is not None
    assert knockout.third_place_team is not None


@pytest.mark.slow
def test_full_tournament_match_count():
    result = run_tournament_2026(seed=42)
    assert result["matches_total"] == 104
    assert result["champion"] is not None
    assert result["knockout"]["round_of_32"]
