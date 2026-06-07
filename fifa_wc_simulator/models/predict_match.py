"""Match outcome prediction using the trained XGBoost model."""
from __future__ import annotations

import logging
import pickle
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import numpy as np
import pandas as pd

from .match_features import FEATURE_COLUMNS, build_feature_row
from .model_utils import load_model
from .team_lookup import resolve_team_features

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = ROOT_DIR / "models" / "fifa_wc_model.pkl"
DEFAULT_FEATURE_COLUMNS_PATH = ROOT_DIR / "models" / "feature_columns.pkl"

# XGBoost class order after training label map {-1: 0, 0: 1, 1: 2}
CLASS_HOME_LOSS = 0
CLASS_DRAW = 1
CLASS_HOME_WIN = 2


@lru_cache(maxsize=1)
def _load_feature_columns(path: str = str(DEFAULT_FEATURE_COLUMNS_PATH)) -> Tuple[str, ...]:
    columns_path = Path(path)
    if not columns_path.exists():
        logger.warning("Feature columns file missing, using built-in FEATURE_COLUMNS")
        return tuple(FEATURE_COLUMNS)
    with open(columns_path, "rb") as handle:
        columns = pickle.load(handle)
    return tuple(columns)


@lru_cache(maxsize=1)
def _get_model(path: str = str(DEFAULT_MODEL_PATH)) -> Any:
    return load_model(Path(path))


def clear_prediction_cache() -> None:
    """Clear cached model and feature columns (useful in tests)."""
    _load_feature_columns.cache_clear()
    _get_model.cache_clear()


def _heuristic_probabilities(home: Dict[str, Any], away: Dict[str, Any]) -> Dict[str, float]:
    """Fallback when the trained model is unavailable."""
    strength_a = float(home.get("overall_strength", home.get("team_strength", 0.0)))
    strength_b = float(away.get("overall_strength", away.get("team_strength", 0.0)))
    form_a = float(home.get("recent_form", 0.5))
    form_b = float(away.get("recent_form", 0.5))
    rating_diff = strength_a - strength_b
    form_diff = form_a - form_b
    base_prob = 0.5 + 0.1 * (rating_diff / 10.0) + 0.05 * form_diff
    win_prob = max(0.01, min(0.85, base_prob))
    loss_prob = max(0.01, min(0.85, 1 - base_prob))
    draw_prob = max(0.01, 1.0 - win_prob - loss_prob)
    total = win_prob + draw_prob + loss_prob
    return {
        "win_probability": round(win_prob / total, 4),
        "draw_probability": round(draw_prob / total, 4),
        "loss_probability": round(loss_prob / total, 4),
        "source": "heuristic",
    }


def predict_match(
    home: Union[str, Dict[str, Any]],
    away: Union[str, Dict[str, Any]],
    *,
    model_path: Path | None = None,
    use_model: bool = True,
) -> Dict[str, float]:
    """
    Predict home win / draw / away win probabilities.

    ``home`` and ``away`` may be team name strings or feature dicts compatible
    with ``team_features.csv``. Probabilities are from the home team's perspective:
    win = home win, loss = away win.
    """
    home_features = resolve_team_features(home)
    away_features = resolve_team_features(away)

    if not use_model:
        return _heuristic_probabilities(home_features, away_features)

    model_file = model_path or DEFAULT_MODEL_PATH
    if not model_file.exists():
        logger.warning("Model not found at %s, using heuristic fallback", model_file)
        return _heuristic_probabilities(home_features, away_features)

    try:
        model = _get_model(str(model_file))
        row = build_feature_row(home_features, away_features)
        columns = _load_feature_columns()
        frame = pd.DataFrame([row])[list(columns)]
        proba = model.predict_proba(frame)[0]
        # Align probabilities with model.classes_ order
        class_to_prob = {int(c): float(p) for c, p in zip(model.classes_, proba)}
        return {
            "win_probability": round(class_to_prob.get(CLASS_HOME_WIN, 0.0), 4),
            "draw_probability": round(class_to_prob.get(CLASS_DRAW, 0.0), 4),
            "loss_probability": round(class_to_prob.get(CLASS_HOME_LOSS, 0.0), 4),
            "source": "xgboost",
        }
    except Exception as exc:
        logger.exception("Model prediction failed, using heuristic: %s", exc)
        return _heuristic_probabilities(home_features, away_features)


def predict_match_proba_array(
    home: Union[str, Dict[str, Any]],
    away: Union[str, Dict[str, Any]],
) -> np.ndarray:
    """Return raw probability array [home_loss, draw, home_win] for sampling."""
    outcome = predict_match(home, away)
    return np.array(
        [
            outcome["loss_probability"],
            outcome["draw_probability"],
            outcome["win_probability"],
        ],
        dtype=float,
    )
