import logging
import pickle
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier, plot_importance

from .match_features import FEATURE_COLUMNS, build_feature_row

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

ROOT_DIR = Path(__file__).resolve().parents[1]
MATCHES_PATH = ROOT_DIR / "datasets" / "cleaned" / "cleaned_matches.csv"
TEAM_FEATURES_PATH = ROOT_DIR / "datasets" / "processed" / "team_features.csv"
MATCH_DATASET_PATH = ROOT_DIR / "datasets" / "processed" / "match_dataset.csv"
MODEL_DIR = ROOT_DIR / "models"
MODEL_PATH = MODEL_DIR / "fifa_wc_model.pkl"
FEATURE_COLUMNS_PATH = MODEL_DIR / "feature_columns.pkl"


def load_data(matches_path: Path, team_features_path: Path) -> (pd.DataFrame, pd.DataFrame):
    """Load the cleaned matches and processed team features datasets."""
    logger.info("Loading matches from %s", matches_path)
    matches = pd.read_csv(matches_path)
    logger.info("Loading team features from %s", team_features_path)
    team_features = pd.read_csv(team_features_path)

    matches["date"] = pd.to_datetime(matches["date"], errors="coerce")
    if matches["date"].isna().any():
        raise ValueError("Some dates in cleaned_matches.csv could not be parsed")

    return matches, team_features


def create_match_result_target(matches: pd.DataFrame) -> pd.DataFrame:
    """Create the home/away result target label for each match."""
    matches = matches.copy()

    def result_label(row: pd.Series) -> int:
        if row["home_score"] > row["away_score"]:
            return 1
        if row["home_score"] < row["away_score"]:
            return -1
        return 0

    matches["result"] = matches.apply(result_label, axis=1)
    return matches


def build_team_lookup(team_features: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Create a lookup dictionary keyed by nationality."""
    if "nationality" not in team_features.columns:
        raise ValueError("team_features.csv must contain a nationality column")
    return team_features.set_index("nationality").to_dict("index")


def build_training_row(home: Dict[str, Any], away: Dict[str, Any], result: int) -> Dict[str, Any]:
    """Build a training row with label from home/away team features."""
    row = build_feature_row(home, away)
    row["result"] = result
    return row


def build_match_dataset(matches: pd.DataFrame, team_lookup: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
    """Generate the match-level training dataset from match results and team features."""
    training_rows: List[Dict[str, Any]] = []
    skipped_matches = 0

    for _, row in matches.iterrows():
        home_team = row["home_team"]
        away_team = row["away_team"]

        if home_team not in team_lookup or away_team not in team_lookup:
            skipped_matches += 1
            continue

        home_features = team_lookup[home_team]
        away_features = team_lookup[away_team]
        training_rows.append(build_training_row(home_features, away_features, row["result"]))

    if skipped_matches:
        logger.warning("Skipped %d matches because one or both teams were missing from team_features.csv", skipped_matches)

    match_dataset = pd.DataFrame(training_rows)
    return match_dataset


def save_dataset(dataset: pd.DataFrame, path: Path) -> None:
    """Save the processed dataset to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(path, index=False)
    logger.info("Saved dataset to %s", path)


def convert_result_labels(dataset: pd.DataFrame) -> pd.DataFrame:
    """Map result labels from [-1, 0, 1] to [0, 1, 2] for XGBoost multiclass."""
    mapping = {-1: 0, 0: 1, 1: 2}
    if not set(dataset["result"]).issubset(set(mapping.keys())):
        raise ValueError("Result column contains values outside [-1, 0, 1]")
    dataset = dataset.copy()
    dataset["result"] = dataset["result"].map(mapping)
    return dataset


def train_xgboost_model(dataset_path: Path, model_path: Path, feature_columns_path: Path) -> XGBClassifier:
    """Train an XGBoost classifier and save the model plus feature column list."""
    logger.info("Loading training dataset from %s", dataset_path)
    dataset = pd.read_csv(dataset_path)
    dataset = convert_result_labels(dataset)

    X = dataset.drop(columns=["result"])
    y = dataset["result"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        eval_metric="mlogloss",
        random_state=42,
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        use_label_encoder=False,
    )

    logger.info("Fitting XGBoost model")
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    accuracy = accuracy_score(y_test, preds)
    logger.info("Test accuracy: %.4f", accuracy)

    print("Accuracy:", accuracy)
    print("Classification Report:\n", classification_report(y_test, preds, digits=4))

    disp = ConfusionMatrixDisplay.from_predictions(y_test, preds)
    disp.ax_.set_title("XGBoost Match Outcome Confusion Matrix")
    plt.tight_layout()
    plt.show()

    fig, ax = plt.subplots(figsize=(10, 8))
    plot_importance(model, ax=ax, max_num_features=15, importance_type="gain")
    ax.set_title("Top 15 XGBoost Feature Importances")
    plt.tight_layout()
    plt.show()

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    logger.info("Saved model to %s", model_path)

    feature_columns = X.columns.tolist()
    with open(feature_columns_path, "wb") as f:
        pickle.dump(feature_columns, f)
    logger.info("Saved feature columns to %s", feature_columns_path)

    print("Training Complete")
    print("Model Saved Successfully")
    print("Feature Columns Saved Successfully")

    return model


def main() -> None:
    matches, team_features = load_data(MATCHES_PATH, TEAM_FEATURES_PATH)
    matches = create_match_result_target(matches)
    team_lookup = build_team_lookup(team_features)
    match_dataset = build_match_dataset(matches, team_lookup)

    print("match_dataset.shape:", match_dataset.shape)
    print(match_dataset.head())
    print(match_dataset["result"].value_counts())
    print(match_dataset.isnull().sum())

    save_dataset(match_dataset, MATCH_DATASET_PATH)
    train_xgboost_model(MATCH_DATASET_PATH, MODEL_PATH, FEATURE_COLUMNS_PATH)


if __name__ == "__main__":
    main()
