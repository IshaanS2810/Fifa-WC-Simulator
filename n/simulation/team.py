"""Team representation for tournament simulation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Union

from ..models.team_lookup import resolve_team_features


@dataclass
class Team:
    """A national team with optional 2026 group slot and model features."""

    name: str
    group: Optional[str] = None
    slot: Optional[str] = None
    attack: float = 0.0
    midfield: float = 0.0
    defense: float = 0.0
    goalkeeper: float = 0.0
    overall_strength: float = 0.0
    squad_depth: float = 0.0
    superstar_index: float = 0.0
    final_team_rating: float = 0.0
    elo: float = 0.0
    elo_normalized: float = 0.0
    enhanced_team_rating: float = 0.0
    wins_last5_overall: float = 0.0
    goals_scored_last5_overall: float = 0.0
    goals_conceded_last5_overall: float = 0.0
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def team_strength(self) -> float:
        """Alias used by legacy simulation helpers."""
        return self.overall_strength

    @property
    def recent_form(self) -> float:
        """Simple form proxy from last-five wins (0–1 scale)."""
        total = self.wins_last5_overall + max(
            0.0,
            5.0 - self.wins_last5_overall,
        )
        if total <= 0:
            return 0.5
        return min(1.0, self.wins_last5_overall / 5.0)

    @classmethod
    def from_name(cls, name: str, group: Optional[str] = None, slot: Optional[str] = None) -> Team:
        """Build a team from processed team_features.csv by nationality name."""
        features = resolve_team_features(name)
        return cls.from_features(features, group=group, slot=slot)

    @classmethod
    def from_features(
        cls,
        features: Dict[str, Any],
        group: Optional[str] = None,
        slot: Optional[str] = None,
    ) -> Team:
        """Build a team from a feature dictionary."""
        name = str(features.get("nationality", features.get("name", "Unknown")))
        known_keys = {
            "attack",
            "midfield",
            "defense",
            "goalkeeper",
            "overall_strength",
            "squad_depth",
            "superstar_index",
            "final_team_rating",
            "elo",
            "elo_normalized",
            "enhanced_team_rating",
            "wins_last5_overall",
            "goals_scored_last5_overall",
            "goals_conceded_last5_overall",
        }
        extra = {k: v for k, v in features.items() if k not in known_keys and k not in {"name", "nationality"}}
        return cls(
            name=name,
            group=group,
            slot=slot,
            attack=float(features.get("attack", 0.0)),
            midfield=float(features.get("midfield", 0.0)),
            defense=float(features.get("defense", 0.0)),
            goalkeeper=float(features.get("goalkeeper", 0.0)),
            overall_strength=float(features.get("overall_strength", 0.0)),
            squad_depth=float(features.get("squad_depth", 0.0)),
            superstar_index=float(features.get("superstar_index", 0.0)),
            final_team_rating=float(features.get("final_team_rating", 0.0)),
            elo=float(features.get("elo", 0.0)),
            elo_normalized=float(features.get("elo_normalized", 0.0)),
            enhanced_team_rating=float(features.get("enhanced_team_rating", 0.0)),
            wins_last5_overall=float(features.get("wins_last5_overall", 0.0)),
            goals_scored_last5_overall=float(features.get("goals_scored_last5_overall", 0.0)),
            goals_conceded_last5_overall=float(features.get("goals_conceded_last5_overall", 0.0)),
            extra=extra,
        )

    @classmethod
    def from_input(cls, team: Union[str, Dict[str, Any], Team], group: Optional[str] = None, slot: Optional[str] = None) -> Team:
        """Accept a Team instance, name string, or feature dict."""
        if isinstance(team, Team):
            if group is not None:
                team.group = group
            if slot is not None:
                team.slot = slot
            return team
        if isinstance(team, str):
            return cls.from_name(team, group=group, slot=slot)
        return cls.from_features(resolve_team_features(team), group=group, slot=slot)

    def to_features_dict(self) -> Dict[str, Any]:
        """Feature dict for model inference (home/away rows)."""
        return {
            "nationality": self.name,
            "attack": self.attack,
            "midfield": self.midfield,
            "defense": self.defense,
            "goalkeeper": self.goalkeeper,
            "overall_strength": self.overall_strength,
            "squad_depth": self.squad_depth,
            "superstar_index": self.superstar_index,
            "final_team_rating": self.final_team_rating,
            "elo": self.elo,
            "elo_normalized": self.elo_normalized,
            "enhanced_team_rating": self.enhanced_team_rating,
            "wins_last5_overall": self.wins_last5_overall,
            "goals_scored_last5_overall": self.goals_scored_last5_overall,
            "goals_conceded_last5_overall": self.goals_conceded_last5_overall,
            **self.extra,
        }

    def to_simulator_dict(self) -> Dict[str, Any]:
        """Dict for match simulation helpers (includes display name)."""
        return {
            "name": self.name,
            "team_strength": self.team_strength,
            "recent_form": self.recent_form,
            **self.to_features_dict(),
        }
