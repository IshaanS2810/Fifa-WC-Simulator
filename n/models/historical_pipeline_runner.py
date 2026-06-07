"""Runner script to create historical match dataset v2 and train XGBoost.

Usage: run from repo root
    python fifa_wc_simulator/models/historical_pipeline_runner.py

This script writes:
- ../datasets/processed/match_dataset_v2.csv
- ../models/fifa_wc_model_v2.pkl
- ../models/feature_columns_v2.pkl

It is defensive: checks for required files and logs progress.
"""
from pathlib import Path
import pickle
import logging

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier

from .historical_feature_engineering import (
    build_yearly_team_snapshots,
    get_elo_before_matches,
    build_match_dataset_v2,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parents[1]
MATCHES_PATH = ROOT / "datasets" / "cleaned" / "cleaned_matches.csv"
TEAM_FEATURES_PATH = ROOT / "datasets" / "processed" / "team_features.csv"
APPEARANCES_PATH = ROOT / "datasets" / "cleaned" / "cleaned_appearances.csv"
ELO_HISTORY_PATH = ROOT / "datasets" / "processed" / "elo_history.csv"

OUT_MATCH_DS = ROOT / "datasets" / "processed" / "match_dataset_v2.csv"
MODEL_PATH = ROOT / "models" / "fifa_wc_model_v2.pkl"
FEATURE_COLS_PATH = ROOT / "models" / "feature_columns_v2.pkl"


def main():
    logger.info("Loading inputs")
    if not MATCHES_PATH.exists():
        raise FileNotFoundError(MATCHES_PATH)
    if not TEAM_FEATURES_PATH.exists():
        raise FileNotFoundError(TEAM_FEATURES_PATH)

    matches = pd.read_csv(MATCHES_PATH, parse_dates=["date"]) 
    # Prefer raw players table for yearly snapshots; fall back to processed team_features
    players_raw_path = ROOT / "datasets" / "raw" / "players.csv"
    if players_raw_path.exists():
        players = pd.read_csv(players_raw_path, low_memory=False)
    else:
        players = pd.read_csv(TEAM_FEATURES_PATH, low_memory=False)

    # Ensure a `nationality` column exists for grouping; synthesize from common raw fields if missing
    if "nationality" not in players.columns:
        if "country_of_citizenship" in players.columns:
            players["nationality"] = players["country_of_citizenship"]
        elif "country_of_birth" in players.columns:
            players["nationality"] = players["country_of_birth"]
        elif "current_national_team_id" in players.columns:
            players["nationality"] = players["current_national_team_id"].astype(str)
        else:
            players["nationality"] = "Unknown"

    try:
        appearances = pd.read_csv(APPEARANCES_PATH)
    except Exception:
        appearances = pd.DataFrame()
    elo_history = pd.read_csv(ELO_HISTORY_PATH, parse_dates=["date"]) if ELO_HISTORY_PATH.exists() else pd.DataFrame()

    # Build historical snapshots
    # NOTE: ideally we would use raw players table; here we try to derive from processed team features or appearances
    logger.info("Building historical team snapshots (this may take a while)")
    historical_team_features = build_yearly_team_snapshots(
        players=players,
        appearances=appearances,
        matches=matches,
    )

    logger.info("Building match_dataset_v2")
    match_dataset_v2 = build_match_dataset_v2(matches=matches, elo_history=elo_history, historical_team_features=historical_team_features)

    logger.info("Saving match_dataset_v2 to %s", OUT_MATCH_DS)
    OUT_MATCH_DS.parent.mkdir(parents=True, exist_ok=True)
    match_dataset_v2.to_csv(OUT_MATCH_DS, index=False)

    # Train XGBoost model
    logger.info("Training XGBoost v2 model")
    ds = match_dataset_v2.copy()
    mapping = {-1: 0, 0: 1, 1: 2}
    ds["result"] = ds["result"].map(mapping)

    X = ds.drop(columns=["result", "date", "home_team", "away_team"]) if {"date", "home_team", "away_team"}.issubset(ds.columns) else ds.drop(columns=["result"])
    y = ds["result"]

    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        random_state=42,
        n_estimators=500,
        max_depth=6,
        learning_rate=0.03,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    acc = accuracy_score(y_test, preds)
    logger.info("v2 Test accuracy: %.4f", acc)
    print("Classification report:\n", classification_report(y_test, preds))

    MODEL_DIR = MODEL_PATH.parent
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(FEATURE_COLS_PATH, "wb") as f:
        pickle.dump(X.columns.tolist(), f)

    logger.info("Training complete. Model saved to %s", MODEL_PATH)


if __name__ == '__main__':
    main()
