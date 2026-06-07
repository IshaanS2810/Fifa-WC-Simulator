import logging
from pathlib import Path
from typing import List

import pandas as pd

logger = logging.getLogger(__name__)

IMPORTANT_TOURNAMENTS = [
    "FIFA World Cup",
    "UEFA Euro",
    "Copa America",
    "UEFA Nations League",
    "African Cup of Nations",
    "AFC Asian Cup",
    "FIFA World Cup qualification",
]


def clean_matches(matches: pd.DataFrame) -> pd.DataFrame:
    """Clean match-level results for competition analysis."""
    logger.debug("Starting clean_matches with %d rows", len(matches))
    df = matches.copy()
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        logger.debug("Converted date column to datetime")
    else:
        logger.warning("No date column found in matches dataframe")

    df = df[df["date"].dt.year >= 1990]
    logger.debug("Filtered matches from 1990 onwards, remaining %d rows", len(df))

    if "tournament" in df.columns:
        df = df[df["tournament"].isin(IMPORTANT_TOURNAMENTS)]
        logger.debug("Filtered important tournaments, remaining %d rows", len(df))

    df = df.drop_duplicates()
    logger.debug("Dropped duplicate rows, remaining %d rows", len(df))

    df = df.dropna(subset=[col for col in ["date", "home_team", "away_team"] if col in df.columns])
    logger.debug("Dropped rows with missing key match identifiers, remaining %d rows", len(df))

    return df.reset_index(drop=True)
