"""Monte Carlo tournament simulation for 2026 World Cup outcome probabilities."""
from __future__ import annotations

import logging
import random
from collections import Counter
from typing import Dict, List, Optional

from .tournament_engine import run_tournament_2026

logger = logging.getLogger(__name__)

DEFAULT_ITERATIONS = 100
MAX_ITERATIONS = 2000


def run_monte_carlo(
    iterations: int = DEFAULT_ITERATIONS,
    seed: Optional[int] = None,
) -> Dict[str, object]:
    """
    Run repeated full 2026 tournaments and estimate outcome probabilities.

    Returns champion, finalist (semi winner), and runner-up rates sorted by probability.
    """
    if iterations < 1:
        raise ValueError("iterations must be at least 1")
    if iterations > MAX_ITERATIONS:
        raise ValueError(f"iterations must not exceed {MAX_ITERATIONS}")

    logger.info("Running Monte Carlo simulation for %d iterations (seed=%s)", iterations, seed)

    champions: Counter[str] = Counter()
    finalists: Counter[str] = Counter()
    runners_up: Counter[str] = Counter()

    for i in range(iterations):
        if seed is not None:
            random.seed(seed + i)
        result = run_tournament_2026()
        champion = result.get("champion")
        runner_up = result.get("runner_up")
        if champion:
            champions[str(champion)] += 1
        if runner_up:
            runners_up[str(runner_up)] += 1

        knockout = result.get("knockout", {})
        for match in knockout.get("semi_final", []):
            winner = match.get("winner")
            if winner:
                finalists[str(winner)] += 1

    champion_probs = _normalize_counter(champions, iterations)
    finalist_probs = _normalize_counter(finalists, iterations)
    runner_up_probs = _normalize_counter(runners_up, iterations)

    logger.info("Monte Carlo complete after %d iterations", iterations)

    return {
        "format": "FIFA World Cup 2026 (48 teams)",
        "iterations": iterations,
        "seed": seed,
        "champion_probabilities": champion_probs,
        "finalist_probabilities": finalist_probs,
        "runner_up_probabilities": runner_up_probs,
        "most_likely_champion": _top_entry(champion_probs),
    }


def _normalize_counter(counter: Counter[str], iterations: int) -> Dict[str, float]:
    return {
        team: round(count / iterations, 6)
        for team, count in counter.most_common()
    }


def _top_entry(probabilities: Dict[str, float]) -> Optional[Dict[str, object]]:
    if not probabilities:
        return None
    team = next(iter(probabilities))
    return {"team": team, "probability": probabilities[team]}
