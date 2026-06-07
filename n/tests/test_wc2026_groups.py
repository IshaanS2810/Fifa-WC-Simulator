import pytest

from fifa_wc_simulator.models.team_lookup import clear_team_lookup_cache
from fifa_wc_simulator.models.predict_match import clear_prediction_cache
from fifa_wc_simulator.simulation.wc2026_config import (
    ADVANCING_THIRD_PLACES,
    AUTO_QUALIFIERS,
    GROUP_IDS,
    KNOCKOUT_FIELD_SIZE,
    OFFICIAL_GROUPS,
    TOTAL_GROUP_MATCHES,
    resolve_wc2026_team_name,
)
from fifa_wc_simulator.simulation.wc2026_groups import (
    build_official_teams as load_teams,
    play_group_round_robin,
    run_group_stage_2026,
    select_best_third_places,
)


@pytest.fixture(autouse=True)
def clear_caches():
    clear_team_lookup_cache()
    clear_prediction_cache()
    yield
    clear_team_lookup_cache()
    clear_prediction_cache()


def test_official_draw_has_48_teams():
    teams = load_teams()
    assert len(teams) == 12
    assert sum(len(g) for g in teams.values()) == 48
    assert teams["A"][0].name == "Mexico"
    assert teams["A"][0].slot == "1A"
    assert teams["D"][0].name == "United States"


def test_name_aliases_resolve():
    assert resolve_wc2026_team_name("South Korea") == "Korea, South"
    assert resolve_wc2026_team_name("Ivory Coast") == "Cote d'Ivoire"
    assert resolve_wc2026_team_name("Bosnia and Herzegovina") == "Bosnia-Herzegovina"


def test_single_group_round_robin_plays_six_matches():
    teams = load_teams()["C"]
    result = play_group_round_robin(teams, "C")
    assert len(result.matches) == 6
    assert all(m.home_goals >= 0 and m.away_goals >= 0 for m in result.matches)
    assert sum(row.played for row in result.standings) == 12  # 6 matches × 2 teams


@pytest.mark.slow
def test_full_group_stage_produces_32_qualifiers():
    result = run_group_stage_2026()
    assert result.matches_played == TOTAL_GROUP_MATCHES
    assert len(result.auto_qualifiers) == AUTO_QUALIFIERS
    assert len(result.advancing_thirds) == ADVANCING_THIRD_PLACES
    assert len(result.all_qualifiers) == KNOCKOUT_FIELD_SIZE
    assert len(result.eliminated_thirds) == len(GROUP_IDS) - ADVANCING_THIRD_PLACES


@pytest.mark.slow
def test_group_winners_get_slots_1_and_2():
    result = run_group_stage_2026()
    for group_id in GROUP_IDS:
        top_two = [q for q in result.auto_qualifiers if q.group_id == group_id]
        assert len(top_two) == 2
        slots = {q.slot for q in top_two}
        assert slots == {f"1{group_id}", f"2{group_id}"}


@pytest.mark.slow
def test_third_place_selection_returns_eight():
    result = run_group_stage_2026()
    advancing, eliminated = select_best_third_places(result.groups)
    assert len(advancing) == 8
    assert len(eliminated) == 4
    for q in advancing:
        assert q.slot.startswith("3")


def test_every_official_team_loads_from_features():
    from fifa_wc_simulator.simulation.team import Team

    for names in OFFICIAL_GROUPS.values():
        for draw_name in names:
            team = Team.from_name(resolve_wc2026_team_name(draw_name))
            assert team.overall_strength >= 0
