"""Shared pytest configuration and fixtures."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from fifa_wc_simulator.models.predict_match import clear_prediction_cache
from fifa_wc_simulator.models.team_lookup import clear_team_lookup_cache
from fifa_wc_simulator.simulation.wc2026_annex_c import clear_annex_cache

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEAM_FEATURES_FIXTURE = FIXTURES_DIR / "team_features_wc2026.csv"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "slow: marks tests as slow (full tournament loops)")


@pytest.fixture(autouse=True)
def _use_committed_test_fixtures(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prefer committed WC2026 team fixture so CI works without datasets/."""
    if TEAM_FEATURES_FIXTURE.exists():
        monkeypatch.setenv("FIFA_WC_TEAM_FEATURES_PATH", str(TEAM_FEATURES_FIXTURE))
    clear_team_lookup_cache()
    clear_prediction_cache()
    clear_annex_cache()
    yield
    clear_team_lookup_cache()
    clear_prediction_cache()
    clear_annex_cache()
