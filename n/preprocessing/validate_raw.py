"""Validate that required raw dataset files are present."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Tuple

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "datasets" / "raw"

REQUIRED_RAW_FILES = [
    "results.csv",
    "players.csv",
    "appearances.csv",
]

OPTIONAL_RAW_FILES = [
    "games.csv",
    "goalscorers.csv",
    "national_teams.csv",
    "fifa_ranking-2024-06-20.csv",
]


def validate_raw_datasets(raw_dir: Path = RAW_DIR) -> Tuple[bool, List[str]]:
    """
    Check that the raw data directory contains required CSV files.

    Returns (ok, messages) where ok is True when all required files exist.
    """
    messages: List[str] = []
    if not raw_dir.exists():
        messages.append(f"Missing raw data directory: {raw_dir}")
        return False, messages

    missing = [name for name in REQUIRED_RAW_FILES if not (raw_dir / name).is_file()]
    if missing:
        messages.append(f"Missing required raw files: {', '.join(missing)}")
        return False, messages

    messages.append(f"Raw data OK ({len(REQUIRED_RAW_FILES)} required files present at {raw_dir})")
    for name in OPTIONAL_RAW_FILES:
        if (raw_dir / name).is_file():
            messages.append(f"  optional: {name}")
    return True, messages


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ok, messages = validate_raw_datasets()
    for line in messages:
        logger.info(line)
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
