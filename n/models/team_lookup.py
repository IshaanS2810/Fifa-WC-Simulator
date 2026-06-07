"""Load and resolve team feature rows from processed team_features.csv."""
from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Union

import pandas as pd

from ..preprocessing.standardize_teams import standardize_team_names

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_TEAM_FEATURES_PATH = ROOT_DIR / "datasets" / "processed" / "team_features.csv"
TEST_TEAM_FEATURES_PATH = ROOT_DIR / "tests" / "fixtures" / "team_features_wc2026.csv"


def get_team_features_path() -> Path:
    """Resolve team features CSV (env override → processed data → test fixture)."""
    env_path = os.environ.get("FIFA_WC_TEAM_FEATURES_PATH")
    if env_path:
        return Path(env_path)
    if DEFAULT_TEAM_FEATURES_PATH.exists():
        return DEFAULT_TEAM_FEATURES_PATH
    if TEST_TEAM_FEATURES_PATH.exists():
        return TEST_TEAM_FEATURES_PATH
    return DEFAULT_TEAM_FEATURES_PATH

REQUIRED_FEATURE_KEYS = (
    "attack",
    "midfield",
    "defense",
    "goalkeeper",
    "overall_strength",
    "squad_depth",
    "superstar_index",
    "final_team_rating",
    "elo",
    "elo_normalized",
    "enhanced_team_rating",
    "wins_last5_overall",
    "goals_scored_last5_overall",
    "goals_conceded_last5_overall",
)


@lru_cache(maxsize=1)
def _load_team_features_df(path: str) -> pd.DataFrame:
    features_path = Path(path)
    if not features_path.exists():
        raise FileNotFoundError(f"Team features file not found: {features_path}")
    return pd.read_csv(features_path)


@lru_cache(maxsize=1)
def get_team_lookup(path: str | None = None) -> Dict[str, Dict[str, Any]]:
    """Return team feature dicts keyed by standardized nationality name."""
    resolved = str(path or get_team_features_path())
    df = _load_team_features_df(resolved)
    if "nationality" not in df.columns:
        raise ValueError("team_features.csv must contain a 'nationality' column")
    lookup: Dict[str, Dict[str, Any]] = {}
    for _, row in df.iterrows():
        name = standardize_team_names(str(row["nationality"]))
        lookup[name] = row.to_dict()
    logger.debug("Loaded %d teams from %s", len(lookup), resolved)
    return lookup


def list_team_names(path: str | None = None) -> List[str]:
    """Return sorted team names available for simulation."""
    return sorted(get_team_lookup(path).keys())


def resolve_team_features(team: Union[str, Dict[str, Any]], path: str | None = None) -> Dict[str, Any]:
    """Resolve a team name or partial dict into a full feature row for the model."""
    if isinstance(team, str):
        name = standardize_team_names(team)
        lookup = get_team_lookup(path)
        if name not in lookup:
            raise KeyError(f"Team not found in team_features: {name}")
        features = dict(lookup[name])
        features["nationality"] = name
        return features

    if not isinstance(team, dict):
        raise TypeError(f"Expected team name or dict, got {type(team)}")

    if "name" in team and len(team) == 1:
        return resolve_team_features(team["name"], path=path)

    if "nationality" in team:
        base = resolve_team_features(str(team["nationality"]), path=path)
        base.update(team)
        return base

    missing = [key for key in REQUIRED_FEATURE_KEYS if key not in team]
    if missing:
        raise ValueError(f"Team feature dict missing required keys: {missing}")
    return dict(team)


def clear_team_lookup_cache() -> None:
    """Clear cached team data (useful in tests)."""
    _load_team_features_df.cache_clear()
    get_team_lookup.cache_clear()
