from fastapi import APIRouter, HTTPException

from ..models.predict_match import predict_match
from ..models.team_lookup import get_team_lookup, list_team_names
from ..preprocessing.validate_raw import validate_raw_datasets
from ..simulation.monte_carlo import MAX_ITERATIONS, run_monte_carlo
from ..simulation.tournament_engine import run_tournament_2026
from ..simulation.wc2026_groups import group_stage_summary, run_group_stage_2026
from .schemas import (
    GroupStageResponse,
    MatchOutcomeResponse,
    MatchPredictionRequest,
    MonteCarloRequest,
    MonteCarloResponse,
    TeamStrengthResponse,
    TournamentSimulationRequest,
)

router = APIRouter(prefix="/api")


@router.get("/health-data")
def health_data() -> dict:
    """Check raw datasets and model availability."""
    raw_ok, raw_messages = validate_raw_datasets()
    return {
        "raw_datasets_ok": raw_ok,
        "raw_messages": raw_messages,
        "teams_loaded": len(list_team_names()),
    }


@router.post("/simulate-match", response_model=MatchOutcomeResponse)
def simulate_match_endpoint(request: MatchPredictionRequest) -> dict:
    """Predict match outcome probabilities (home win / draw / away win)."""
    home = request.home_team or request.team_a
    away = request.away_team or request.team_b
    try:
        outcome = predict_match(home, away)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {
        "outcome": {
            "win_probability": outcome["win_probability"],
            "draw_probability": outcome["draw_probability"],
            "loss_probability": outcome["loss_probability"],
        },
        "home_team": request.home_team or (home if isinstance(home, str) else None),
        "away_team": request.away_team or (away if isinstance(away, str) else None),
        "source": outcome.get("source"),
    }


@router.post("/simulate-group-stage", response_model=GroupStageResponse)
def simulate_group_stage() -> dict:
    """Simulate the full 2026 group stage (72 matches, 32 qualifiers)."""
    result = run_group_stage_2026()
    return group_stage_summary(result)

@router.post("/simulate-tournament")
def simulate_tournament(
    request: TournamentSimulationRequest | None = None
) -> dict:
    if request and request.seed is not None:
        import random

        random.seed(request.seed)
    return run_tournament_2026()


@router.post("/monte-carlo", response_model=MonteCarloResponse)
def monte_carlo_endpoint(request: MonteCarloRequest) -> dict:
    """Run Monte Carlo simulations and return champion/finalist probabilities."""
    try:
        return run_monte_carlo(iterations=request.iterations, seed=request.seed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/monte-carlo/limits")
def monte_carlo_limits() -> dict:
    """Return iteration bounds for Monte Carlo requests."""
    return {
        "default_iterations": 100,
        "max_iterations": MAX_ITERATIONS,
        "matches_per_tournament": 104,
    }


@router.get("/team-strengths", response_model=TeamStrengthResponse)
def team_strengths() -> dict:
    """Return overall strength for all teams in team_features.csv."""
    lookup = get_team_lookup()
    rows = [
        {
            "team": name,
            "strength": round(float(data.get("overall_strength", 0.0)), 4),
            "elo": round(float(data.get("elo", 0.0)), 2),
        }
        for name, data in sorted(lookup.items())
    ]
    return {"team_strengths": rows}


@router.get("/teams")
def list_teams() -> dict:
    """List national team names available for simulation."""
    return {"teams": list_team_names()}
