import logging
from typing import Dict

import numpy as np
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

logger = logging.getLogger(__name__)


def evaluate_model(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, object]:
    """Return evaluation metrics for classifier predictions."""
    logger.debug("Evaluating model predictions")
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "classification_report": classification_report(y_true, y_pred, output_dict=True),
    }
    logger.info("Evaluation metrics computed")
    return metrics
