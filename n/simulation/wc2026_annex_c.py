"""FIFA World Cup 2026 Annex C: third-place team assignments for Round of 32."""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, Set

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).resolve().parents[1]
ANNEX_C_PATH = ROOT_DIR / "data" / "wc2026_annex_c.json"

# Winner slots that face a third-placed team (column order in Annex C)
WINNER_THIRD_SLOTS = ("1A", "1B", "1D", "1E", "1G", "1I", "1K", "1L")


@lru_cache(maxsize=1)
def _load_annex_table() -> Dict[str, Dict[str, str]]:
    """Load Annex C keyed by sorted eight-letter group code (e.g. 'DEFGHIJK')."""
    if not ANNEX_C_PATH.exists():
        raise FileNotFoundError(
            f"Annex C data missing at {ANNEX_C_PATH}. "
            "Regenerate from Wikipedia/regulations table if needed."
        )
    with open(ANNEX_C_PATH, encoding="utf-8") as handle:
        rows = json.load(handle)
    table: Dict[str, Dict[str, str]] = {}
    for row in rows:
        table[row["key"]] = row["assignments"]
    logger.debug("Loaded %d Annex C combinations", len(table))
    return table


def clear_annex_cache() -> None:
    _load_annex_table.cache_clear()


def resolve_third_place_assignments(advancing_third_groups: Iterable[str]) -> Dict[str, str]:
    """
    Return mapping of winner slot → third-place slot (e.g. ``{'1E': '3J', '1A': '3E'}``).

    ``advancing_third_groups`` is the set of group letters (A–L) whose third-place teams qualified.
    """
    groups = sorted({g.strip().upper() for g in advancing_third_groups})
    if len(groups) != 8:
        raise ValueError(f"Annex C requires exactly 8 advancing third-place groups, got {groups}")

    key = "".join(groups)
    table = _load_annex_table()
    if key not in table:
        raise KeyError(f"No Annex C row for advancing third-place groups: {groups}")

    assignments = table[key]
    for winner_slot in WINNER_THIRD_SLOTS:
        if winner_slot not in assignments:
            raise ValueError(f"Annex C row missing assignment for {winner_slot}")
    return assignments
