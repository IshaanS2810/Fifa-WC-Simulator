import logging
from pathlib import Path
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


def _validate_path(path: Path) -> None:
    """Validate that a path exists and is a file."""
    if not path.exists():
        logger.error("Dataset file missing: %s", path)
        raise FileNotFoundError(f"Dataset file not found: {path}")
    if not path.is_file():
        logger.error("Expected file but found directory: %s", path)
        raise FileNotFoundError(f"Expected file but found directory: {path}")


def load_results(path: Path) -> pd.DataFrame:
    """Load tournament match results from CSV."""
    _validate_path(path)
    logger.info("Loading match results from %s", path)
    return pd.read_csv(path)


def load_players(path: Path) -> pd.DataFrame:
    """Load player metadata and statistics from CSV."""
    _validate_path(path)
    logger.info("Loading player information from %s", path)
    return pd.read_csv(path)


def load_appearances(path: Path) -> pd.DataFrame:
    """Load player appearance records from CSV."""
    _validate_path(path)
    logger.info("Loading appearance records from %s", path)
    return pd.read_csv(path)
