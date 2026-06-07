from typing import Dict, List


def compute_standings(groups: List[Dict[str, object]]) -> List[Dict[str, object]]:
    """Compute rankings for group standings based on points and goal difference."""
    return sorted(
        groups,
        key=lambda row: (
            -row.get("points", 0),
            -(row.get("goals_for", 0) - row.get("goals_against", 0)),
            -row.get("goals_for", 0),
        ),
    )
