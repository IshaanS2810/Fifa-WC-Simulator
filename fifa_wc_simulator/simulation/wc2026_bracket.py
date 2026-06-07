"""2026 FIFA World Cup knockout bracket: R32 through final and third-place match."""
from __future__ import annotations

import logging
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from .match_simulator import simulate_match
from .team import Team
from .wc2026_annex_c import resolve_third_place_assignments
from .wc2026_groups import GroupStageResult, Qualifier

logger = logging.getLogger(__name__)

# Fixed Round of 32 fixtures (match id, home slot, away slot)
R32_FIXED: Tuple[Tuple[int, str, str], ...] = (
    (73, "2A", "2B"),
    (75, "1F", "2C"),
    (76, "1C", "2F"),
    (78, "2E", "2I"),
    (83, "2K", "2L"),
    (84, "1H", "2J"),
    (86, "1J", "2H"),
    (88, "2D", "2G"),
)

# Winner vs third-place (away third resolved via Annex C on winner slot = home slot)
R32_THIRD_HOME_SLOTS: Tuple[Tuple[int, str], ...] = (
    (74, "1E"),
    (77, "1I"),
    (79, "1A"),
    (80, "1L"),
    (81, "1D"),
    (82, "1G"),
    (85, "1B"),
    (87, "1K"),
)

# Later rounds: (match_id, feeder_a, feeder_b) where feeders are W{id} or L{id}
KNOCKOUT_ROUNDS: Tuple[Tuple[str, Tuple[Tuple[int, str, str], ...]], ...] = (
    (
        "round_of_16",
        (
            (90, "W73", "W75"),
            (89, "W74", "W77"),
            (91, "W76", "W78"),
            (92, "W79", "W80"),
            (93, "W83", "W84"),
            (94, "W81", "W82"),
            (95, "W86", "W88"),
            (96, "W85", "W87"),
        ),
    ),
    (
        "quarter_final",
        (
            (97, "W89", "W90"),
            (98, "W93", "W94"),
            (99, "W91", "W92"),
            (100, "W95", "W96"),
        ),
    ),
    (
        "semi_final",
        (
            (101, "W97", "W98"),
            (102, "W99", "W100"),
        ),
    ),
    (
        "third_place",
        ((103, "L101", "L102"),),
    ),
    (
        "final",
        ((104, "W101", "W102"),),
    ),
)


@dataclass
class KnockoutMatch:
    """Single knockout fixture and result."""

    match_id: int
    round_name: str
    home: Team
    away: Team
    home_goals: int = 0
    away_goals: int = 0
    went_to_extra_time: bool = False
    went_to_penalties: bool = False
    winner: Optional[Team] = None
    loser: Optional[Team] = None

    @property
    def scoreline(self) -> str:
        return f"{self.home_goals}-{self.away_goals}"


@dataclass
class KnockoutStageResult:
    """All knockout matches by round."""

    round_of_32: List[KnockoutMatch] = field(default_factory=list)
    round_of_16: List[KnockoutMatch] = field(default_factory=list)
    quarter_final: List[KnockoutMatch] = field(default_factory=list)
    semi_final: List[KnockoutMatch] = field(default_factory=list)
    third_place: List[KnockoutMatch] = field(default_factory=list)
    final: List[KnockoutMatch] = field(default_factory=list)
    annex_c_assignments: Dict[str, str] = field(default_factory=dict)

    @property
    def champion(self) -> Optional[Team]:
        return self.final[-1].winner if self.final else None

    @property
    def runner_up(self) -> Optional[Team]:
        return self.final[-1].loser if self.final else None

    @property
    def third_place_team(self) -> Optional[Team]:
        return self.third_place[-1].winner if self.third_place else None


def build_qualifier_lookup(qualifiers: List[Qualifier]) -> Dict[str, Team]:
    """Map slot code (1A, 2B, 3E, …) to Team."""
    lookup: Dict[str, Team] = {}
    for q in qualifiers:
        lookup[q.slot] = q.team
    return lookup


def build_round_of_32_fixtures(
    qualifier_lookup: Dict[str, Team],
    annex_assignments: Dict[str, str],
) -> List[Tuple[int, Team, Team]]:
    """Build 16 R32 fixtures as (match_id, home, away)."""
    fixtures: List[Tuple[int, Team, Team]] = []

    for match_id, home_slot, away_slot in R32_FIXED:
        fixtures.append((match_id, qualifier_lookup[home_slot], qualifier_lookup[away_slot]))

    for match_id, winner_slot in R32_THIRD_HOME_SLOTS:
        third_slot = annex_assignments[winner_slot]
        fixtures.append(
            (match_id, qualifier_lookup[winner_slot], qualifier_lookup[third_slot])
        )

    fixtures.sort(key=lambda row: row[0])
    return fixtures


def _simulate_extra_time(home: Team, away: Team) -> Tuple[int, int]:
    """Brief extra-time model: one simulated scoring period with dampened variance."""
    result = simulate_match(home, away)
    home_goals = int(result["score"]["team_a"])
    away_goals = int(result["score"]["team_b"])
    if home_goals == away_goals == 0:
        leader = home if random.random() < 0.52 else away
        if leader is home:
            return 1, 0
        return 0, 1
    return home_goals, away_goals


def _simulate_penalties(home: Team, away: Team) -> Team:
    strength_diff = home.team_strength - away.team_strength
    probability_home = 0.5 + 0.12 * max(-1.0, min(1.0, strength_diff / 10.0))
    return home if random.random() < probability_home else away


def play_knockout_match(
    match_id: int,
    round_name: str,
    home: Team,
    away: Team,
) -> KnockoutMatch:
    """Play a knockout match with extra time and penalties if drawn after 90 minutes."""
    result = simulate_match(home, away)
    home_goals = int(result["score"]["team_a"])
    away_goals = int(result["score"]["team_b"])
    extra_time = False
    penalties = False

    if home_goals == away_goals:
        extra_time = True
        et_home, et_away = _simulate_extra_time(home, away)
        home_goals += et_home
        away_goals += et_away

    if home_goals == away_goals:
        penalties = True
        winner = _simulate_penalties(home, away)
        loser = away if winner is home else home
        return KnockoutMatch(
            match_id=match_id,
            round_name=round_name,
            home=home,
            away=away,
            home_goals=home_goals,
            away_goals=away_goals,
            went_to_extra_time=extra_time,
            went_to_penalties=penalties,
            winner=winner,
            loser=loser,
        )

    if home_goals > away_goals:
        winner, loser = home, away
    else:
        winner, loser = away, home

    return KnockoutMatch(
        match_id=match_id,
        round_name=round_name,
        home=home,
        away=away,
        home_goals=home_goals,
        away_goals=away_goals,
        went_to_extra_time=extra_time,
        went_to_penalties=penalties,
        winner=winner,
        loser=loser,
    )


def _resolve_feeder(code: str, winners: Dict[int, Team], losers: Dict[int, Team]) -> Team:
    if code.startswith("W"):
        return winners[int(code[1:])]
    if code.startswith("L"):
        return losers[int(code[1:])]
    raise ValueError(f"Unknown feeder code: {code}")


def _play_round(
    round_name: str,
    fixtures: Tuple[Tuple[int, str, str], ...],
    winners: Dict[int, Team],
    losers: Dict[int, Team],
) -> List[KnockoutMatch]:
    matches: List[KnockoutMatch] = []
    for match_id, feeder_home, feeder_away in fixtures:
        home = _resolve_feeder(feeder_home, winners, losers)
        away = _resolve_feeder(feeder_away, winners, losers)
        match = play_knockout_match(match_id, round_name, home, away)
        winners[match_id] = match.winner  # type: ignore[assignment]
        losers[match_id] = match.loser  # type: ignore[assignment]
        matches.append(match)
    return matches


def run_knockout_stage(group_stage: GroupStageResult) -> KnockoutStageResult:
    """Run R32 → R16 → QF → SF → third-place → final."""
    qualifier_lookup = build_qualifier_lookup(group_stage.all_qualifiers)
    advancing_groups = [q.group_id for q in group_stage.advancing_thirds]
    annex = resolve_third_place_assignments(advancing_groups)

    r32_fixtures = build_round_of_32_fixtures(qualifier_lookup, annex)
    winners: Dict[int, Team] = {}
    losers: Dict[int, Team] = {}

    r32_matches: List[KnockoutMatch] = []
    for match_id, home, away in r32_fixtures:
        match = play_knockout_match(match_id, "round_of_32", home, away)
        winners[match_id] = match.winner  # type: ignore[assignment]
        losers[match_id] = match.loser  # type: ignore[assignment]
        r32_matches.append(match)

    logger.info("Round of 32 complete (%d matches)", len(r32_matches))

    result = KnockoutStageResult(round_of_32=r32_matches, annex_c_assignments=annex)

    for round_name, fixtures in KNOCKOUT_ROUNDS:
        matches = _play_round(round_name, fixtures, winners, losers)
        if round_name == "round_of_16":
            result.round_of_16 = matches
        elif round_name == "quarter_final":
            result.quarter_final = matches
        elif round_name == "semi_final":
            result.semi_final = matches
        elif round_name == "third_place":
            result.third_place = matches
        elif round_name == "final":
            result.final = matches

    logger.info(
        "Knockout stage complete. Champion: %s",
        result.champion.name if result.champion else "unknown",
    )
    return result


def knockout_summary(knockout: KnockoutStageResult) -> Dict[str, object]:
    """Serialize knockout results for APIs."""

    def _round(matches: List[KnockoutMatch]) -> List[Dict[str, object]]:
        return [
            {
                "match_id": m.match_id,
                "home": m.home.name,
                "away": m.away.name,
                "score": m.scoreline,
                "winner": m.winner.name if m.winner else None,
                "extra_time": m.went_to_extra_time,
                "penalties": m.went_to_penalties,
            }
            for m in matches
        ]

    return {
        "annex_c_assignments": knockout.annex_c_assignments,
        "round_of_32": _round(knockout.round_of_32),
        "round_of_16": _round(knockout.round_of_16),
        "quarter_final": _round(knockout.quarter_final),
        "semi_final": _round(knockout.semi_final),
        "third_place": _round(knockout.third_place),
        "final": _round(knockout.final),
        "champion": knockout.champion.name if knockout.champion else None,
        "runner_up": knockout.runner_up.name if knockout.runner_up else None,
        "third_place_team": knockout.third_place_team.name if knockout.third_place_team else None,
    }
