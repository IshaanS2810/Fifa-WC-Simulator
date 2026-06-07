"""FIFA World Cup 2026 format constants and official group draw."""
from __future__ import annotations

from typing import Dict, List, Tuple

from ..preprocessing.standardize_teams import standardize_team_names

# Official draw (December 2025) — team names mapped to team_features.csv where needed.
# Sources: FIFA final draw, Sporting News group tables (post-draw).
OFFICIAL_GROUPS: Dict[str, List[str]] = {
    "A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

GROUP_IDS: Tuple[str, ...] = tuple("ABCDEFGHIJKL")
TEAMS_PER_GROUP = 4
GROUP_MATCHES_PER_GROUP = 6
TOTAL_GROUP_MATCHES = len(GROUP_IDS) * GROUP_MATCHES_PER_GROUP  # 72
AUTO_QUALIFIERS = len(GROUP_IDS) * 2  # 24
ADVANCING_THIRD_PLACES = 8
KNOCKOUT_FIELD_SIZE = AUTO_QUALIFIERS + ADVANCING_THIRD_PLACES  # 32

# Display / draw names → team_features.csv nationality column
WC2026_NAME_ALIASES: Dict[str, str] = {
    "South Korea": "Korea, South",
    "Korea Republic": "Korea, South",
    "Ivory Coast": "Cote d'Ivoire",
    "Côte d'Ivoire": "Cote d'Ivoire",
    "Bosnia and Herzegovina": "Bosnia-Herzegovina",
    "Czechia": "Czech Republic",
    "USA": "United States",
    "IR Iran": "Iran",
    "Cabo Verde": "Cape Verde",
    "Türkiye": "Turkey",
}


def resolve_wc2026_team_name(name: str) -> str:
    """Map official draw name to team_features nationality."""
    normalized = standardize_team_names(name.strip())
    return WC2026_NAME_ALIASES.get(normalized, normalized)


def official_group_slots() -> Dict[str, List[Tuple[str, str]]]:
    """Return {group_id: [(slot, team_name), ...]} e.g. ('1A', 'Mexico')."""
    slots: Dict[str, List[Tuple[str, str]]] = {}
    for group_id, teams in OFFICIAL_GROUPS.items():
        slots[group_id] = [
            (f"{position}{group_id}", team)
            for position, team in zip([1, 2, 3, 4], teams)
        ]
    return slots
