import logging
from typing import Dict, List, Union

from .team import Team
from .wc2026_bracket import play_knockout_match

logger = logging.getLogger(__name__)


def run_knockout_stage(matches: List[Dict[str, dict]]) -> List[Dict[str, object]]:
    """
    Simulate a list of knockout fixtures (legacy API).

    Each match dict must include ``team_a``, ``team_b``, and optional ``match_id``.
    """
    winners = []
    for index, match in enumerate(matches):
        team_a = match["team_a"]
        team_b = match["team_b"]
        home = Team.from_input(team_a)
        away = Team.from_input(team_b)
        match_id = int(match.get("match_id", 900 + index))
        played = play_knockout_match(match_id, "knockout", home, away)
        winner_dict = played.winner.to_simulator_dict() if played.winner else {}
        winners.append(
            {
                "winner": winner_dict,
                "match": match,
                "result": {
                    "score": {"team_a": played.home_goals, "team_b": played.away_goals},
                    "extra_time": played.went_to_extra_time,
                    "penalties": played.went_to_penalties,
                },
            }
        )
        logger.debug("Knockout match winner: %s", played.winner.name if played.winner else None)
    return winners
