import logging
from typing import List

import pandas as pd

logger = logging.getLogger(__name__)

EXACT_POSITION_CODES = {
    "GK": "Goalkeeper",
    "G": "Goalkeeper",
    "CB": "Defender",
    "LB": "Defender",
    "RB": "Defender",
    "LWB": "Defender",
    "RWB": "Defender",
    "DF": "Defender",
    "CDM": "Midfielder",
    "CM": "Midfielder",
    "CAM": "Midfielder",
    "LM": "Midfielder",
    "RM": "Midfielder",
    "DM": "Midfielder",
    "AM": "Midfielder",
    "MF": "Midfielder",
    "CF": "Forward",
    "ST": "Forward",
    "LW": "Forward",
    "RW": "Forward",
    "FW": "Forward",
}


def clean_players(players: pd.DataFrame) -> pd.DataFrame:
    """Clean player-level statistics for team strength and injury modeling."""
    logger.debug("Starting clean_players with %d rows", len(players))
    df = players.copy()

    to_keep = [
        col
        for col in [
            "player_id",
            "name",
            "position",
            "nationality",
            "age",
            "appearances",
            "goals",
            "assists",
            "rating",
            "injury_status",
            "suspension_status",
        ]
        if col in df.columns
    ]
    df = df[to_keep]
    logger.debug("Retained columns: %s", to_keep)

    df["position"] = df["position"].astype(str).str.strip().map(normalize_position).fillna("Unknown")
    df = df[df["position"] != "Unknown"]
    logger.debug("Normalized player positions")

    numeric_columns = [col for col in ["age", "appearances", "goals", "assists", "rating"] if col in df.columns]
    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)
    logger.debug("Filled missing numeric player values")

    df = df.dropna(subset=["player_id", "name"])
    logger.debug("Dropped invalid player rows, remaining %d rows", len(df))

    return df.reset_index(drop=True)


def normalize_position(position: str) -> str:
    """Normalize common player position labels to broad categories."""
    if position is None:
        return "Unknown"
    position = str(position).upper().strip()
    if not position or position == "NAN":
        return "Unknown"

    if position in EXACT_POSITION_CODES:
        return EXACT_POSITION_CODES[position]

    if any(token in position for token in ("GOAL", "GK", "KEEPER")):
        return "Goalkeeper"
    if any(token in position for token in ("DEF", "BACK", "CB", "LB", "RB", "WB")):
        return "Defender"
    if any(token in position for token in ("MID", "CM", "DM", "AM", "WM")):
        return "Midfielder"
    if any(token in position for token in ("FWD", "STRIKER", "ST", "FW", "WING")):
        return "Forward"

    return "Unknown"
