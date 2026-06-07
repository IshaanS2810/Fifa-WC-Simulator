import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def save_processed_data(df: pd.DataFrame, path: Path) -> None:
    """Persist a processed DataFrame to the target path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Saved processed data to %s", path)
