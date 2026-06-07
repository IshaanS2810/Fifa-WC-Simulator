import logging
import pickle
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def save_model(model: Any, path: Path) -> None:
    """Serialize a trained model to disk."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as handle:
        pickle.dump(model, handle)
    logger.info("Saved model to %s", path)


def load_model(path: Path) -> Any:
    """Load a serialized model from disk."""
    if not path.exists():
        logger.error("Model file not found: %s", path)
        raise FileNotFoundError(f"Model not found: {path}")
    with open(path, "rb") as handle:
        model = pickle.load(handle)
    logger.info("Loaded model from %s", path)
    return model
