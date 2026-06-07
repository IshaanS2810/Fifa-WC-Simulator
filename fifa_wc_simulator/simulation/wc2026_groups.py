"""2026 FIFA World Cup group stage: round-robin, standings, best third-place teams."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from itertools import combinations
from typing import Dict, List, Optional, Tuple

from .match_simulator import simulate_match
from .team import Team
from .wc2026_config import (
    ADVANCING_THIRD_PLACES,
    AUTO_QUALIFIERS,
    GROUP_IDS,
    KNOCKOUT_FIELD_SIZE,
    OFFICIAL_GROUPS,
    TOTAL_GROUP_MATCHES,
    resolve_wc2026_team_name,
)

logger = logging.getLogger(__name__)


@dataclass
class GroupStanding:
    """One team's record in a group."""

    team: Team
    played: int = 0
    won: int = 0
    drawn: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0
    fair_play_score: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def slot(self) -> str:
        return self.team.slot or ""

    def ranking_key(self) -> Tuple[int, int, int, int, float]:
        """FIFA-style ordering: points, GD, GF, fair play, Elo."""
        return (
            self.points,
            self.goal_difference,
            self.goals_for,
            self.fair_play_score,
            self.team.elo,
        )


@dataclass
class GroupMatchResult:
    """Played group match."""

    group_id: str
    home: Team
    away: Team
    home_goals: int
    away_goals: int
    prediction_source: str = "unknown"

    @property
    def winner(self) -> Optional[Team]:
        if self.home_goals > self.away_goals:
            return self.home
        if self.away_goals > self.home_goals:
            return self.away
        return None


@dataclass
class GroupResult:
    """Completed group stage for one group."""

    group_id: str
    standings: List[GroupStanding]
    matches: List[GroupMatchResult] = field(default_factory=list)

    @property
    def winner(self) -> GroupStanding:
        return self.standings[0]

    @property
    def runner_up(self) -> GroupStanding:
        return self.standings[1]

    @property
    def third_place(self) -> GroupStanding:
        return self.standings[2]


@dataclass
class Qualifier:
    """Team advancing to the Round of 32."""

    team: Team
    slot: str
    group_id: str
    rank: int


@dataclass
class GroupStageResult:
    """Full 2026 group stage output."""

    groups: Dict[str, GroupResult]
    matches_played: int
    auto_qualifiers: List[Qualifier]
    advancing_thirds: List[Qualifier]
    eliminated_thirds: List[GroupStanding]
    all_qualifiers: List[Qualifier]


def build_official_teams() -> Dict[str, List[Team]]:
    """Load all 48 teams from the official draw with group slots."""
    groups: Dict[str, List[Team]] = {}
    for group_id in GROUP_IDS:
        teams: List[Team] = []
        for position, draw_name in enumerate(OFFICIAL_GROUPS[group_id], start=1):
            features_name = resolve_wc2026_team_name(draw_name)
            slot = f"{position}{group_id}"
            teams.append(Team.from_name(features_name, group=group_id, slot=slot))
        groups[group_id] = teams
    return groups


def _init_standings(teams: List[Team]) -> Dict[str, GroupStanding]:
    return {team.name: GroupStanding(team=team) for team in teams}


def _apply_result(standings: Dict[str, GroupStanding], home_goals: int, away_goals: int, home: Team, away: Team) -> None:
    home_row = standings[home.name]
    away_row = standings[away.name]
    home_row.played += 1
    away_row.played += 1
    home_row.goals_for += home_goals
    home_row.goals_against += away_goals
    away_row.goals_for += away_goals
    away_row.goals_against += home_goals

    if home_goals > away_goals:
        home_row.won += 1
        home_row.points += 3
        away_row.lost += 1
    elif home_goals < away_goals:
        away_row.won += 1
        away_row.points += 3
        home_row.lost += 1
    else:
        home_row.drawn += 1
        away_row.drawn += 1
        home_row.points += 1
        away_row.points += 1


def _head_to_head_points(team_a: Team, team_b: Team, matches: List[GroupMatchResult]) -> Tuple[int, int]:
    """Points each team earned in direct fixtures within this group."""
    points_a = 0
    points_b = 0
    for match in matches:
        if {match.home.name, match.away.name} != {team_a.name, team_b.name}:
            continue
        if match.home_goals == match.away_goals:
            points_a += 1
            points_b += 1
        elif match.home.name == team_a.name:
            if match.home_goals > match.away_goals:
                points_a += 3
            else:
                points_b += 3
        else:
            if match.away_goals > match.home_goals:
                points_a += 3
            else:
                points_b += 3
    return points_a, points_b


def rank_group_standings(standings: List[GroupStanding], matches: List[GroupMatchResult]) -> List[GroupStanding]:
    """
    Rank teams using points, goal difference, goals scored, fair play, then Elo.
    If exactly two teams are tied on the first three criteria, use head-to-head points.
    """
    ordered = sorted(standings, key=lambda row: row.ranking_key(), reverse=True)

    def tied_on_core_metrics(rows: List[GroupStanding]) -> bool:
        if len(rows) < 2:
            return False
        keys = {(r.points, r.goal_difference, r.goals_for) for r in rows}
        return len(keys) == 1

    i = 0
    while i < len(ordered):
        j = i
        while j < len(ordered) and ordered[j].ranking_key()[:3] == ordered[i].ranking_key()[:3]:
            j += 1
        block = ordered[i:j]
        if len(block) == 2 and tied_on_core_metrics(block):
            a, b = block
            pts_a, pts_b = _head_to_head_points(a.team, b.team, matches)
            if pts_a != pts_b:
                block = [a, b] if pts_a > pts_b else [b, a]
                ordered[i:j] = block
        i = j
    return ordered


def play_group_round_robin(teams: List[Team], group_id: str) -> GroupResult:
    """Play six group matches (double round-robin round) and return standings."""
    standings_map = _init_standings(teams)
    matches: List[GroupMatchResult] = []

    for home, away in combinations(teams, 2):
        result = simulate_match(home, away)
        home_goals = int(result["score"]["team_a"])
        away_goals = int(result["score"]["team_b"])
        _apply_result(standings_map, home_goals, away_goals, home, away)
        matches.append(
            GroupMatchResult(
                group_id=group_id,
                home=home,
                away=away,
                home_goals=home_goals,
                away_goals=away_goals,
                prediction_source=str(result.get("prediction_source", "unknown")),
            )
        )

    standings = rank_group_standings(list(standings_map.values()), matches)
    for rank, row in enumerate(standings, start=1):
        row.team.slot = f"{rank}{group_id}"

    return GroupResult(group_id=group_id, standings=standings, matches=matches)


def select_best_third_places(group_results: Dict[str, GroupResult]) -> Tuple[List[Qualifier], List[GroupStanding]]:
    """Pick the eight best third-placed teams across all groups."""
    thirds: List[GroupStanding] = [result.third_place for result in group_results.values()]
    ranked = sorted(thirds, key=lambda row: row.ranking_key(), reverse=True)
    advancing = ranked[:ADVANCING_THIRD_PLACES]
    eliminated = ranked[ADVANCING_THIRD_PLACES:]

    qualifiers = [
        Qualifier(
            team=row.team,
            slot=f"3{row.team.group}",
            group_id=row.team.group or "",
            rank=3,
        )
        for row in advancing
    ]
    return qualifiers, eliminated


def run_group_stage_2026(groups: Optional[Dict[str, List[Team]]] = None) -> GroupStageResult:
    """
    Simulate the full 2026 group stage (12 × 4 teams, 72 matches).

    Returns 32 qualifiers: top two per group plus eight best third-place teams.
    """
    groups = groups or build_official_teams()
    if sum(len(teams) for teams in groups.values()) != 48:
        raise ValueError("2026 group stage requires exactly 48 teams")

    group_results: Dict[str, GroupResult] = {}
    match_count = 0

    for group_id in GROUP_IDS:
        if group_id not in groups or len(groups[group_id]) != 4:
            raise ValueError(f"Group {group_id} must contain exactly 4 teams")
        logger.info("Simulating group %s", group_id)
        result = play_group_round_robin(groups[group_id], group_id)
        group_results[group_id] = result
        match_count += len(result.matches)

    auto_qualifiers: List[Qualifier] = []
    for group_id, result in group_results.items():
        for rank, row in enumerate(result.standings[:2], start=1):
            auto_qualifiers.append(
                Qualifier(team=row.team, slot=f"{rank}{group_id}", group_id=group_id, rank=rank)
            )

    advancing_thirds, eliminated_thirds = select_best_third_places(group_results)
    all_qualifiers = auto_qualifiers + advancing_thirds

    assert match_count == TOTAL_GROUP_MATCHES
    assert len(all_qualifiers) == KNOCKOUT_FIELD_SIZE

    logger.info(
        "Group stage complete: %d matches, %d qualifiers (%d auto + %d third)",
        match_count,
        len(all_qualifiers),
        len(auto_qualifiers),
        len(advancing_thirds),
    )

    return GroupStageResult(
        groups=group_results,
        matches_played=match_count,
        auto_qualifiers=auto_qualifiers,
        advancing_thirds=advancing_thirds,
        eliminated_thirds=eliminated_thirds,
        all_qualifiers=all_qualifiers,
    )


def group_stage_summary(result: GroupStageResult) -> Dict[str, object]:
    """Serialize group stage results for API responses."""
    groups_out = {}
    for group_id, group in result.groups.items():
        groups_out[group_id] = {
            "standings": [
                {
                    "slot": row.slot,
                    "team": row.team.name,
                    "played": row.played,
                    "won": row.won,
                    "drawn": row.drawn,
                    "lost": row.lost,
                    "goals_for": row.goals_for,
                    "goals_against": row.goals_against,
                    "goal_difference": row.goal_difference,
                    "points": row.points,
                }
                for row in group.standings
            ],
            "matches": [
                {
                    "home": m.home.name,
                    "away": m.away.name,
                    "score": f"{m.home_goals}-{m.away_goals}",
                }
                for m in group.matches
            ],
        }

    return {
        "matches_played": result.matches_played,
        "groups": groups_out,
        "qualifiers": [
            {"slot": q.slot, "team": q.team.name, "group": q.group_id, "rank": q.rank}
            for q in result.all_qualifiers
        ],
        "advancing_third_place": [q.team.name for q in result.advancing_thirds],
        "eliminated_third_place": [row.team.name for row in result.eliminated_thirds],
    }
