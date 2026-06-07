import logging
from typing import Dict, Iterable

import pandas as pd

logger = logging.getLogger(__name__)

TEAM_NAME_MAPPING: Dict[str, str] = {
    "USA": "United States",
    "Korea Republic": "South Korea",
    "IR Iran": "Iran",
    "Cote d'Ivoire": "Ivory Coast",
    "Republic of Ireland": "Ireland",
}


def standardize_team_names(name: str) -> str:
    """Replace known alternate team names with standardized values."""
    if not isinstance(name, str):
        return name
    return TEAM_NAME_MAPPING.get(name.strip(), name.strip())


def apply_standardization(df: pd.DataFrame, team_columns: Iterable[str]) -> pd.DataFrame:
    """Apply team name standardization to specific dataframe columns."""
    result = df.copy()
    for column in team_columns:
        if column in result.columns:
            result[column] = result[column].astype(str).map(standardize_team_names)
            logger.debug("Standardized team names in column: %s", column)
    return result
