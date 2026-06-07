import logging
from typing import Dict, List, Optional

from .wc2026_groups import GroupStageResult, build_official_teams, run_group_stage_2026

logger = logging.getLogger(__name__)


def run_group_stage(teams: Optional[List[Dict[str, object]]] = None) -> List[Dict[str, object]]:
    """
    Run the 2026 group stage when called without explicit teams.

    Legacy dict standings are returned for the first group only when teams are passed;
    prefer ``run_group_stage_2026`` for the full tournament.
    """
    if teams is not None:
        logger.warning("Custom team list ignored; use run_group_stage_2026 with Team objects")
    result = run_group_stage_2026()
    first_group = next(iter(result.groups.values()))
    return [
        {
            "team": row.team.name,
            "slot": row.slot,
            "points": row.points,
            "goals_for": row.goals_for,
            "goals_against": row.goals_against,
            "played": row.played,
        }
        for row in first_group.standings
    ]


def award_group_points(standing: Dict[str, object], goals_for: int, goals_against: int) -> None:
    """Update a team's group standing after a match (legacy helper)."""
    standing["goals_for"] = int(standing.get("goals_for", 0)) + goals_for
    standing["goals_against"] = int(standing.get("goals_against", 0)) + goals_against
    if goals_for > goals_against:
        standing["points"] = int(standing.get("points", 0)) + 3
    elif goals_for == goals_against:
        standing["points"] = int(standing.get("points", 0)) + 1
    logger.debug(
        "Updated standing for %s: points=%s, gf=%s, ga=%s",
        standing.get("team"),
        standing.get("points"),
        standing.get("goals_for"),
        standing.get("goals_against"),
    )


def run_wc2026_group_stage() -> GroupStageResult:
    """Simulate all twelve 2026 groups and return structured results."""
    return run_group_stage_2026(build_official_teams())
