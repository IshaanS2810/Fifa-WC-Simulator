"""Shared match-level feature construction for training and inference."""
from __future__ import annotations

from typing import Any, Dict, List

FEATURE_COLUMNS: List[str] = [
    "attack_diff",
    "midfield_diff",
    "defense_diff",
    "goalkeeper_diff",
    "overall_strength_diff",
    "squad_depth_diff",
    "superstar_diff",
    "final_team_rating_diff",
    "elo_diff",
    "elo_normalized_diff",
    "enhanced_team_rating_diff",
    "wins_last5_overall_diff",
    "goals_scored_last5_diff",
    "goals_conceded_last5_diff",
]


def build_feature_row(home: Dict[str, Any], away: Dict[str, Any]) -> Dict[str, float]:
    """Build a single match feature row from home/away team feature dicts."""
    return {
        "attack_diff": home["attack"] - away["attack"],
        "midfield_diff": home["midfield"] - away["midfield"],
        "defense_diff": home["defense"] - away["defense"],
        "goalkeeper_diff": home["goalkeeper"] - away["goalkeeper"],
        "overall_strength_diff": home["overall_strength"] - away["overall_strength"],
        "squad_depth_diff": home["squad_depth"] - away["squad_depth"],
        "superstar_diff": home["superstar_index"] - away["superstar_index"],
        "final_team_rating_diff": home["final_team_rating"] - away["final_team_rating"],
        "elo_diff": home["elo"] - away["elo"],
        "elo_normalized_diff": home["elo_normalized"] - away["elo_normalized"],
        "enhanced_team_rating_diff": home["enhanced_team_rating"] - away["enhanced_team_rating"],
        "wins_last5_overall_diff": home["wins_last5_overall"] - away["wins_last5_overall"],
        "goals_scored_last5_diff": home["goals_scored_last5_overall"] - away["goals_scored_last5_overall"],
        "goals_conceded_last5_diff": home["goals_conceded_last5_overall"] - away["goals_conceded_last5_overall"],
    }
