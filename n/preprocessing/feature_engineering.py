import logging
from typing import Dict

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def categorize_position(position: str) -> str:
    """Convert detailed position codes into broad categories."""
    if position is None:
        return "Unknown"
    position = position.lower()
    if "goal" in position or position == "gk":
        return "Goalkeeper"
    if any(token in position for token in ["def", "cb", "lb", "rb"]):
        return "Defender"
    if any(token in position for token in ["mid", "cm", "dm", "am"]):
        return "Midfielder"
    if any(token in position for token in ["fw", "st", "striker", "att"]):
        return "Forward"
    return "Unknown"


def calculate_attack_rating(df: pd.DataFrame) -> pd.Series:
    """Estimate attack rating from goals, assists, and forward player ratings."""
    return (df.get("goals", 0) * 0.5 + df.get("assists", 0) * 0.3 + df.get("rating", 0) * 0.2).fillna(0)


def calculate_midfield_rating(df: pd.DataFrame) -> pd.Series:
    """Estimate midfield quality from passes, assists, and contribution metrics."""
    return (df.get("rating", 0) * 0.6 + df.get("appearances", 0) * 0.1 + df.get("assists", 0) * 0.3).fillna(0)


def calculate_defense_rating(df: pd.DataFrame) -> pd.Series:
    """Estimate defense rating using defensive contributions and experience."""
    return (df.get("rating", 0) * 0.5 + df.get("appearances", 0) * 0.3 + df.get("clean_sheets", 0) * 0.2).fillna(0)


def calculate_goalkeeper_rating(df: pd.DataFrame) -> pd.Series:
    """Calculate goalkeeper strength from rating and clean sheet data."""
    return (df.get("rating", 0) * 0.7 + df.get("clean_sheets", 0) * 0.2 + df.get("appearances", 0) * 0.1).fillna(0)


def calculate_team_strength(team_features: Dict[str, float]) -> float:
    """Combine component ratings into a single team strength measure."""
    attack = team_features.get("attack", 0.0)
    midfield = team_features.get("midfield", 0.0)
    defense = team_features.get("defense", 0.0)
    goalkeeper = team_features.get("goalkeeper", 0.0)
    strength = 0.35 * attack + 0.30 * midfield + 0.25 * defense + 0.10 * goalkeeper
    logger.debug(
        "Computed team strength: attack=%s, midfield=%s, defense=%s, goalkeeper=%s, overall=%s",
        attack,
        midfield,
        defense,
        goalkeeper,
        strength,
    )
    return float(strength)


def calculate_recent_form(match_history: pd.DataFrame, window: int = 5) -> float:
    """Calculate recent form based on the last N match results."""
    results = match_history.tail(window).get("result", pd.Series(dtype=object))
    score_map = {"win": 1.0, "draw": 0.5, "loss": 0.0}
    form_scores = results.map(score_map).fillna(0)
    form = float(form_scores.mean())
    logger.debug("Recent form over last %d matches: %s", window, form)
    return form


def calculate_goals_scored_average(match_history: pd.DataFrame, window: int = 5) -> float:
    """Calculate average goals scored over a recent match window."""
    goals = match_history.tail(window).get("goals_for", pd.Series(dtype=float)).fillna(0)
    average = float(goals.mean())
    logger.debug("Goals scored average: %s", average)
    return average


def calculate_goals_conceded_average(match_history: pd.DataFrame, window: int = 5) -> float:
    """Calculate average goals conceded over a recent match window."""
    goals = match_history.tail(window).get("goals_against", pd.Series(dtype=float)).fillna(0)
    average = float(goals.mean())
    logger.debug("Goals conceded average: %s", average)
    return average


def build_feature_matrix(players: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    """Build a feature matrix combining player and match statistics for model training."""
    logger.info("Building feature matrix from player and match data")
    team_strength = players.groupby("nationality").agg({"rating": "mean", "goals": "sum", "assists": "sum"})
    team_strength = team_strength.rename(columns={"rating": "avg_rating", "goals": "total_goals", "assists": "total_assists"})
    logger.debug("Computed team strength aggregated features")
    return team_strength.reset_index()
