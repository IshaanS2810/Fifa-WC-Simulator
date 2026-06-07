import logging
import random
from typing import Dict, Tuple, Union

from ..models.predict_match import predict_match
from .team import Team

logger = logging.getLogger(__name__)


def _coerce_team(team: Union[str, Dict[str, float], Team]) -> Dict[str, object]:
    if isinstance(team, Team):
        return team.to_simulator_dict()
    if isinstance(team, str):
        return Team.from_name(team).to_simulator_dict()
    if "name" not in team and "nationality" in team:
        team = {**team, "name": team["nationality"]}
    elif "name" not in team:
        raise ValueError("Team dict must include 'name' or 'nationality'")
    return dict(team)


def simulate_match(
    team_a: Union[str, Dict[str, float], Team],
    team_b: Union[str, Dict[str, float], Team],
) -> Dict[str, object]:
    """Simulate a single match using model-based outcome probabilities."""
    home = _coerce_team(team_a)
    away = _coerce_team(team_b)

    outcome_probs = predict_match(home, away)
    win_probability = outcome_probs["win_probability"]
    draw_probability = outcome_probs["draw_probability"]
    loss_probability = outcome_probs["loss_probability"]

    logger.debug(
        "Match probabilities (%s): win=%s, draw=%s, loss=%s",
        outcome_probs.get("source", "unknown"),
        win_probability,
        draw_probability,
        loss_probability,
    )

    outcome = random.choices(
        ["team_a", "draw", "team_b"],
        weights=[win_probability, draw_probability, loss_probability],
        k=1,
    )[0]

    strength_diff = home.get("team_strength", 0.0) - away.get("team_strength", 0.0)
    score_a, score_b = _generate_scoreline(outcome, strength_diff)
    return {
        "result": outcome,
        "score": {"team_a": score_a, "team_b": score_b},
        "probabilities": {
            "team_a_win": win_probability,
            "draw": draw_probability,
            "team_b_win": loss_probability,
        },
        "prediction_source": outcome_probs.get("source", "unknown"),
        "home_team": home.get("name"),
        "away_team": away.get("name"),
    }


def _generate_scoreline(outcome: str, strength_diff: float) -> Tuple[int, int]:
    """Create a realistic scoreline based on the predicted outcome."""
    base_goals = max(0, int(1.2 + 0.5 * abs(strength_diff)))
    if outcome == "draw":
        score = random.choice([0, 1, 2])
        return score, score
    if outcome == "team_a":
        return base_goals + random.randint(0, 2), random.randint(0, 2)
    return random.randint(0, 2), base_goals + random.randint(0, 2)
