import logging
from typing import Dict, List, Optional

from .wc2026_bracket import KnockoutStageResult, knockout_summary, run_knockout_stage
from .wc2026_groups import GroupStageResult, group_stage_summary, run_group_stage_2026

logger = logging.getLogger(__name__)


def run_tournament_2026(seed: Optional[int] = None) -> Dict[str, object]:
    """
    Run the full 2026 World Cup: 72 group matches → 32 qualifiers → 32 knockout matches.

    Returns group standings, knockout bracket, champion, and medalists.
    """
    if seed is not None:
        import random

        random.seed(seed)

    logger.info("Starting full 2026 World Cup simulation")
    group_stage = run_group_stage_2026()
    knockout = run_knockout_stage(group_stage)

    return {
        "format": "FIFA World Cup 2026 (48 teams)",
        "group_stage": group_stage_summary(group_stage),
        "knockout": knockout_summary(knockout),
        "champion": knockout.champion.name if knockout.champion else None,
        "runner_up": knockout.runner_up.name if knockout.runner_up else None,
        "third_place": knockout.third_place_team.name if knockout.third_place_team else None,
        "matches_total": group_stage.matches_played + _knockout_match_count(knockout),
    }


def _knockout_match_count(knockout: KnockoutStageResult) -> int:
    return (
        len(knockout.round_of_32)
        + len(knockout.round_of_16)
        + len(knockout.quarter_final)
        + len(knockout.semi_final)
        + len(knockout.third_place)
        + len(knockout.final)
    )


def run_tournament(teams: List[Dict[str, object]]) -> Dict[str, object]:
    """Run full 2026 tournament (legacy entry point; ``teams`` argument is ignored)."""
    logger.info(
        "run_tournament called with %d teams; using official 2026 draw",
        len(teams),
    )
    return run_tournament_2026()
