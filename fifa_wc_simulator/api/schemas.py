from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, model_validator


class TeamFeatures(BaseModel):
    name: str = Field(..., description="Team name")
    team_strength: float = Field(..., description="Calculated team strength")
    recent_form: float = Field(..., description="Recent form score between 0 and 1")


class MatchPredictionRequest(BaseModel):
    """Predict or simulate a match. Prefer home_team/away_team names."""

    home_team: Optional[str] = Field(None, description="Home team name (from team_features.csv)")
    away_team: Optional[str] = Field(None, description="Away team name")
    team_a: Optional[Union[str, Dict[str, float]]] = Field(
        None,
        description="Legacy home side: team name or feature dict",
    )
    team_b: Optional[Union[str, Dict[str, float]]] = Field(
        None,
        description="Legacy away side: team name or feature dict",
    )

    @model_validator(mode="after")
    def resolve_sides(self) -> MatchPredictionRequest:
        if self.home_team is None and self.team_a is not None:
            if isinstance(self.team_a, str):
                self.home_team = self.team_a
            elif isinstance(self.team_a, dict) and "name" in self.team_a:
                self.home_team = str(self.team_a["name"])
        if self.away_team is None and self.team_b is not None:
            if isinstance(self.team_b, str):
                self.away_team = self.team_b
            elif isinstance(self.team_b, dict) and "name" in self.team_b:
                self.away_team = str(self.team_b["name"])
        if self.team_a is not None and self.team_b is not None:
            return self
        if self.home_team and self.away_team:
            return self
        raise ValueError("Provide home_team and away_team, or team_a and team_b")


class MatchOutcomeResponse(BaseModel):
    outcome: Dict[str, float]
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    source: Optional[str] = Field(None, description="xgboost or heuristic")


class TournamentSimulationRequest(BaseModel):
    teams: List[TeamFeatures] = Field(default_factory=list, description="Reserved for custom draws")
    seed: Optional[int] = Field(None, description="Optional RNG seed for reproducible simulation")


class MonteCarloRequest(BaseModel):
    iterations: int = Field(
        100,
        ge=1,
        le=2000,
        description="Number of full tournaments to simulate (1–2000)",
    )
    seed: Optional[int] = Field(
        None,
        description="Optional base seed; iteration i uses seed + i for reproducibility",
    )


class MonteCarloResponse(BaseModel):
    format: str
    iterations: int
    seed: Optional[int]
    champion_probabilities: Dict[str, float]
    finalist_probabilities: Dict[str, float]
    runner_up_probabilities: Dict[str, float]
    most_likely_champion: Optional[Dict[str, object]] = None


class TeamStrengthResponse(BaseModel):
    team_strengths: List[Dict[str, float]]


class GroupStageResponse(BaseModel):
    matches_played: int
    groups: Dict[str, object]
    qualifiers: List[Dict[str, object]]
    advancing_third_place: List[str]
    eliminated_third_place: List[str]
