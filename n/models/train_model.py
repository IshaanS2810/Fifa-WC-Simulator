import logging
import pickle
from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from .model_utils import save_model

logger = logging.getLogger(__name__)


def train_model(processed_data_path: Path, model_path: Path) -> Tuple[XGBClassifier, dict]:
    """Train an XGBoost classifier on processed tournament data."""
    logger.info("Loading processed data from %s", processed_data_path)
    df = pd.read_csv(processed_data_path)
    if "target" not in df.columns:
        raise ValueError("Processed dataset must include a 'target' column")

    features = df.drop(columns=["target"])
    target = df["target"]

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    logger.info("Training XGBoost classifier")
    model = XGBClassifier(use_label_encoder=False, eval_metric="logloss", random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    metrics = {
        "accuracy": float((predictions == y_test).mean()),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
    }
    logger.info("Training complete: %s", metrics)
    save_model(model, model_path)
    return model, metrics
