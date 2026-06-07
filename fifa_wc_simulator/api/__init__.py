"""API package for FIFA World Cup Simulator."""

from .app import app
from .routes import router
from .schemas import MatchPredictionRequest, TournamentSimulationRequest, TeamStrengthResponse

__all__ = ["app", "router", "MatchPredictionRequest", "TournamentSimulationRequest", "TeamStrengthResponse"]
