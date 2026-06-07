"""Historical feature engineering utilities for FIFA WC simulator.

Implements:
- Elo lookup before each match using pd.merge_asof
- Rolling form features (last 5 matches overall/home/away) computed per team
- Yearly historical team snapshots built from player appearances and market values
- Retrieval of historical team snapshots for a match date
- Building match_dataset_v2 with no future leakage

Assumptions documented in functions where applicable.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler


def get_elo_before_matches(matches: pd.DataFrame, elo_history: pd.DataFrame) -> pd.DataFrame:
    """Attach latest Elo for home and away teams BEFORE each match date.

    Uses pd.merge_asof for efficiency. Assumes both inputs are sorted by date.

    Parameters
    - matches: DataFrame with at least ['date','home_team','away_team']
    - elo_history: DataFrame with ['date','team','elo'] where each row represents a team's Elo at that date (before matches on that date)

    Returns matches with added columns: 'elo_home','elo_away'
    """
    matches = matches.copy()
    elo = elo_history.copy()

    # Ensure datetime
    matches["date"] = pd.to_datetime(matches["date"]) 
    elo["date"] = pd.to_datetime(elo["date"]) 

    # Sort for merge_asof
    matches = matches.sort_values("date").reset_index(drop=True)
    elo = elo.sort_values("date").reset_index(drop=True)

    # Merge-asof for home team
    left = matches[["date", "home_team"]].rename(columns={"home_team": "team"})
    merged_home = pd.merge_asof(
        left.sort_values("date"),
        elo.sort_values("date"),
        left_on="date",
        right_on="date",
        by="team",
        direction="backward",
        allow_exact_matches=True,
    )
    matches["elo_home"] = merged_home["elo"].values

    # Merge-asof for away team
    left = matches[["date", "away_team"]].rename(columns={"away_team": "team"})
    merged_away = pd.merge_asof(
        left.sort_values("date"),
        elo.sort_values("date"),
        left_on="date",
        right_on="date",
        by="team",
        direction="backward",
        allow_exact_matches=True,
    )
    matches["elo_away"] = merged_away["elo"].values

    # Elo diff from home perspective
    matches["elo_diff"] = matches["elo_home"] - matches["elo_away"]

    return matches


def build_team_match_rows(matches: pd.DataFrame) -> pd.DataFrame:
    """Convert matches DataFrame into team-centric historical rows.

    For each match, produces two rows: one for home team (is_home=True) and one for away.
    Columns: team, date, is_home, goals_for, goals_against, win, draw, loss, clean_sheet
    """
    records = []
    for _, r in matches.iterrows():
        d = r["date"]
        # Home row
        records.append(
            {
                "team": r["home_team"],
                "date": d,
                "is_home": True,
                "goals_for": r["home_score"],
                "goals_against": r["away_score"],
                "win": int(r["home_score"] > r["away_score"]),
                "draw": int(r["home_score"] == r["away_score"]),
                "loss": int(r["home_score"] < r["away_score"]),
                "clean_sheet": int(r["away_score"] == 0),
            }
        )
        # Away row
        records.append(
            {
                "team": r["away_team"],
                "date": d,
                "is_home": False,
                "goals_for": r["away_score"],
                "goals_against": r["home_score"],
                "win": int(r["away_score"] > r["home_score"]),
                "draw": int(r["away_score"] == r["home_score"]),
                "loss": int(r["away_score"] < r["home_score"]),
                "clean_sheet": int(r["home_score"] == 0),
            }
        )
    team_rows = pd.DataFrame.from_records(records)
    team_rows["date"] = pd.to_datetime(team_rows["date"]) 
    team_rows = team_rows.sort_values(["team", "date"]).reset_index(drop=True)
    return team_rows


def compute_rolling_form(team_rows: pd.DataFrame, window: int = 5) -> pd.DataFrame:
    """Compute rolling form features for each team up to (but excluding) each match.

    Uses shift(1) then rolling(window).sum() so the current match is excluded from its own features.

    Returns a DataFrame with index matching team_rows and added columns for recent stats.
    """
    df = team_rows.copy()
    # Ensure sorted by team/date
    df = df.sort_values(["team", "date"]).reset_index(drop=True)

    # Group and compute shifted series then rolling sums
    def _compute(group: pd.DataFrame) -> pd.DataFrame:
        g = group.copy()
        # shift to exclude current match
        g["win_s"] = g["win"].shift(1).fillna(0)
        g["draw_s"] = g["draw"].shift(1).fillna(0)
        g["loss_s"] = g["loss"].shift(1).fillna(0)
        g["goals_for_s"] = g["goals_for"].shift(1).fillna(0)
        g["goals_against_s"] = g["goals_against"].shift(1).fillna(0)
        g["clean_sheet_s"] = g["clean_sheet"].shift(1).fillna(0)

        # overall last N
        g["wins_last5_overall"] = g["win_s"].rolling(window, min_periods=0).sum()
        g["draws_last5_overall"] = g["draw_s"].rolling(window, min_periods=0).sum()
        g["losses_last5_overall"] = g["loss_s"].rolling(window, min_periods=0).sum()
        g["goals_scored_last5_overall"] = g["goals_for_s"].rolling(window, min_periods=0).sum()
        g["goals_conceded_last5_overall"] = g["goals_against_s"].rolling(window, min_periods=0).sum()
        g["clean_sheets_last5_overall"] = g["clean_sheet_s"].rolling(window, min_periods=0).sum()

        # averages (avoid division by zero)
        g["avg_goals_scored_last5_overall"] = g.apply(
            lambda row: (row["goals_scored_last5_overall"] / max(min(window, len(group.loc[:row.name])), 1)), axis=1
        )
        g["avg_goals_conceded_last5_overall"] = g.apply(
            lambda row: (row["goals_conceded_last5_overall"] / max(min(window, len(group.loc[:row.name])), 1)), axis=1
        )

        # Home last N
        g["is_home_s"] = g["is_home"].shift(1).astype(float)
        # mask home stats: set non-home entries to NaN before rolling so they are skipped
        home_win = g["win_s"].where(g["is_home_s"].fillna(0) == 1, 0)
        home_draw = g["draw_s"].where(g["is_home_s"].fillna(0) == 1, 0)
        home_loss = g["loss_s"].where(g["is_home_s"].fillna(0) == 1, 0)
        home_gf = g["goals_for_s"].where(g["is_home_s"].fillna(0) == 1, 0)
        home_ga = g["goals_against_s"].where(g["is_home_s"].fillna(0) == 1, 0)
        home_cs = g["clean_sheet_s"].where(g["is_home_s"].fillna(0) == 1, 0)

        g["wins_last5_home"] = home_win.rolling(window, min_periods=0).sum()
        g["draws_last5_home"] = home_draw.rolling(window, min_periods=0).sum()
        g["losses_last5_home"] = home_loss.rolling(window, min_periods=0).sum()
        g["goals_scored_last5_home"] = home_gf.rolling(window, min_periods=0).sum()
        g["goals_conceded_last5_home"] = home_ga.rolling(window, min_periods=0).sum()
        g["clean_sheets_last5_home"] = home_cs.rolling(window, min_periods=0).sum()

        # Away last N (same approach)
        away_win = g["win_s"].where(g["is_home_s"].fillna(0) == 0, 0)
        away_draw = g["draw_s"].where(g["is_home_s"].fillna(0) == 0, 0)
        away_loss = g["loss_s"].where(g["is_home_s"].fillna(0) == 0, 0)
        away_gf = g["goals_for_s"].where(g["is_home_s"].fillna(0) == 0, 0)
        away_ga = g["goals_against_s"].where(g["is_home_s"].fillna(0) == 0, 0)

        g["wins_last5_away"] = away_win.rolling(window, min_periods=0).sum()
        g["draws_last5_away"] = away_draw.rolling(window, min_periods=0).sum()
        g["losses_last5_away"] = away_loss.rolling(window, min_periods=0).sum()
        g["goals_scored_last5_away"] = away_gf.rolling(window, min_periods=0).sum()
        g["goals_conceded_last5_away"] = away_ga.rolling(window, min_periods=0).sum()

        return g

    rolled = df.groupby("team", group_keys=False).apply(_compute).reset_index(drop=True)
    return rolled


def top_n_average(df: pd.DataFrame, n: int) -> float:
    if df.empty:
        return 0.0
    return df.nlargest(n, "player_strength")["player_strength"].mean()


def build_yearly_team_snapshots(
    players: pd.DataFrame,
    appearances: pd.DataFrame,
    matches: pd.DataFrame,
    start_year: int = None,
    end_year: int = None,
) -> pd.DataFrame:
    """Build yearly historical team snapshots using appearances to determine active players.

    Approach and assumptions:
    - Use `appearances` to determine whether a player was active up to a given year (appearance date <= year-end).
    - Compute player strength using market_value and appearances-derived minutes/goals/assists where available.
    - If `appearances` lacks dates, fall back to using the static players table (conservative approximation).

    Returns DataFrame with columns: nationality, year, attack, midfield, defense, goalkeeper, overall_strength, squad_depth, superstar_index
    """
    players = players.copy()
    appearances = appearances.copy()
    matches = matches.copy()
    players_cols = players.columns

    # Prepare appearances with dates; try common column names
    if "date" in appearances.columns:
        appearances["date"] = pd.to_datetime(appearances["date"])
    elif "match_date" in appearances.columns:
        appearances["date"] = pd.to_datetime(appearances["match_date"])
    else:
        # Attempt join via match_id -> matches to get date
        if "match_id" in appearances.columns and "match_id" in matches.columns:
            mp = matches[["match_id", "date"]].drop_duplicates()
            appearances = appearances.merge(mp, on="match_id", how="left")
            appearances["date"] = pd.to_datetime(appearances["date"])
        else:
            # No dates available: fallback to static snapshot using players only
            appearances["date"] = pd.NaT

    # Determine year range
    if start_year is None:
        start_year = int(matches["date"].dt.year.min())
    if end_year is None:
        end_year = int(matches["date"].dt.year.max())

    snapshots = []

    for year in range(start_year, end_year + 1):
        cutoff = pd.Timestamp(year=year, month=12, day=31)
        # players active up to cutoff: those with any appearance date <= cutoff
        if appearances["date"].notna().any():
            active_player_ids = (
                appearances[appearances["date"] <= cutoff]["player_id"].unique().tolist()
            )
            active_players = players[players["player_id"].isin(active_player_ids)].copy()
        else:
            # fallback: use all players (no temporal info available)
            active_players = players.copy()

        if active_players.empty:
            continue

        # categorize positions
        def categorize_position(position):
            position = str(position)
            if any(pos in position for pos in ["CF", "ST", "LW", "RW", "Forward"]):
                return "Attack"
            if any(pos in position for pos in ["CM", "CDM", "CAM", "LM", "RM", "Midfield"]):
                return "Midfield"
            if any(pos in position for pos in ["CB", "LB", "RB", "LWB", "RWB", "Defender"]):
                return "Defense"
            if "GK" in position or "Goalkeeper" in position:
                return "Goalkeeper"
            return "Other"

        active_players["Position_Category"] = active_players["position"].apply(categorize_position)

        # player_strength: prefer precomputed column, else derive from market_value
        if "player_strength" not in active_players.columns:
            active_players["player_strength"] = (
                active_players.get("market_value", active_players.get("market_value_in_eur", 0)) / 1_000_000
            )

        # compute position groups and top-N averages (robust to Series/DataFrame returns)
        def _group_topn(position_label: str, n: int):
            grp = (
                active_players[active_players["Position_Category"] == position_label]
                .groupby("nationality")
                .apply(lambda x: top_n_average(x, n))
            )
            if isinstance(grp, pd.DataFrame):
                grp = grp.iloc[:, 0]
            return grp.rename(position_label.lower())

        attack = _group_topn("Attack", 3)
        midfield = _group_topn("Midfield", 4)
        defense = _group_topn("Defense", 4)
        goalkeeper = _group_topn("Goalkeeper", 1)

        team_features = (
            pd.concat([attack, midfield, defense, goalkeeper], axis=1)
            .fillna(0)
            .reset_index()
        )

        team_features["overall_strength"] = (
            0.35 * team_features["attack"]
            + 0.30 * team_features["midfield"]
            + 0.25 * team_features["defense"]
            + 0.10 * team_features["goalkeeper"]
        )

        # squad_depth: average of top 23 players by player_strength
        squad_depth = (
            active_players.groupby("nationality")
            .apply(lambda x: x.nlargest(min(23, len(x)), "player_strength")["player_strength"].mean())
            .rename("squad_depth")
            .reset_index()
        )

        superstar_index = (
            active_players.groupby("nationality")["player_strength"].max().reset_index()
        )
        superstar_index = superstar_index.rename(columns={"player_strength": "superstar_index"})

        team_features = team_features.merge(squad_depth, on="nationality", how="left")
        team_features = team_features.merge(superstar_index, on="nationality", how="left")

        team_features["year"] = year
        snapshots.append(team_features)

    if snapshots:
        historical_team_features = pd.concat(snapshots, ignore_index=True).fillna(0)
    else:
        historical_team_features = pd.DataFrame(columns=["nationality", "year"])

    # reorder columns
    cols = ["nationality", "year", "attack", "midfield", "defense", "goalkeeper", "overall_strength", "squad_depth", "superstar_index"]
    historical_team_features = historical_team_features[cols]
    return historical_team_features


def attach_historical_team_features(matches: pd.DataFrame, historical_team_features: pd.DataFrame) -> pd.DataFrame:
    """For each match, attach the most recent snapshot BEFORE match year for home and away teams.

    Uses merge_asof on year with by=team/nationality for efficiency.
    """
    m = matches.copy()
    m["date"] = pd.to_datetime(m["date"]) 
    m = m.sort_values("date").reset_index(drop=True)
    m["match_year"] = m["date"].dt.year

    # Prepare snapshots
    snaps = historical_team_features.copy()
    # ensure key dtypes match for merge_asof
    if "year" in snaps.columns:
        snaps["year"] = snaps["year"].astype("int64")
    snaps = snaps.sort_values(["nationality", "year"]) 

    # Home team merge_asof
    left = m[["match_year", "home_team", "date"]].rename(columns={"home_team": "nationality", "match_year": "year"})
    if "year" in left.columns:
        left["year"] = left["year"].astype("int64")
    merged_home = pd.merge_asof(
        left.sort_values("date"),
        snaps.sort_values("year"),
        left_on="year",
        right_on="year",
        by="nationality",
        direction="backward",
    )
    # rename columns with _home suffix
    home_cols = {c: f"{c}_home" for c in ["attack", "midfield", "defense", "goalkeeper", "overall_strength", "squad_depth", "superstar_index", "year"]}
    for rc, nc in home_cols.items():
        merged_home = merged_home.rename(columns={rc: nc})
    merged_home = merged_home[["nationality"] + list(home_cols.values())]

    # Away team merge_asof
    left = m[["match_year", "away_team", "date"]].rename(columns={"away_team": "nationality", "match_year": "year"})
    if "year" in left.columns:
        left["year"] = left["year"].astype("int64")
    merged_away = pd.merge_asof(
        left.sort_values("date"),
        snaps.sort_values("year"),
        left_on="year",
        right_on="year",
        by="nationality",
        direction="backward",
    )
    away_cols = {c: f"{c}_away" for c in ["attack", "midfield", "defense", "goalkeeper", "overall_strength", "squad_depth", "superstar_index", "year"]}
    for rc, nc in away_cols.items():
        merged_away = merged_away.rename(columns={rc: nc})
    merged_away = merged_away[["nationality"] + list(away_cols.values())]

    # Attach back to matches (preserve order)
    m = m.reset_index()
    m = m.merge(merged_home, left_on=["home_team"], right_on=["nationality"], how="left")
    m = m.merge(merged_away, left_on=["away_team"], right_on=["nationality"], how="left", suffixes=("", "_awaydrop"))

    # Clean duplicate cols
    m = m.drop(columns=[c for c in m.columns if c.endswith("_awaydrop") or c == "nationality"]) 
    return m


def build_match_dataset_v2(matches: pd.DataFrame, elo_history: pd.DataFrame, historical_team_features: pd.DataFrame) -> pd.DataFrame:
    """Create match-level dataset using only historical info before each match.

    Steps:
    - Attach historical team snapshots for home/away using attach_historical_team_features
    - Attach Elo before match using get_elo_before_matches
    - Build rolling form features using compute_rolling_form and merge back per team
    - Compute differences and final dataset
    """
    m = matches.copy()
    m["date"] = pd.to_datetime(m["date"]) 

    # attach team snapshots
    m = attach_historical_team_features(m, historical_team_features)

    # attach elo before match (compute on a lightweight subset to avoid heavy dataframe copies)
    elo_subset = get_elo_before_matches(m[["date", "home_team", "away_team"]].copy(), elo_history)
    # assign elo fields back to full matches frame
    for col in ["elo_home", "elo_away", "elo_diff"]:
        if col in elo_subset.columns:
            m[col] = elo_subset[col].values

    # Build team-centric rows for rolling form
    team_rows = build_team_match_rows(matches=m[["date", "home_team", "away_team", "home_score", "away_score"]])
    rolled = compute_rolling_form(team_rows, window=5)

    # For each match, pick team's rolled row that corresponds to that match (team + date)
    # pivot rolled to have team+date as key and select columns
    key_cols = ["team", "date"]
    rolled_keyed = rolled.set_index(["team", "date"])  # multiindex

    # helper to fetch rolled stats for a team/date
    def fetch_stats(team: str, date: pd.Timestamp) -> Dict[str, float]:
        try:
            row = rolled_keyed.loc[(team, date)]
        except KeyError:
            # no previous matches for this team-date; return zeros
            cols = [
                "wins_last5_overall","draws_last5_overall","losses_last5_overall",
                "goals_scored_last5_overall","goals_conceded_last5_overall","clean_sheets_last5_overall",
                "avg_goals_scored_last5_overall","avg_goals_conceded_last5_overall",
                "wins_last5_home","draws_last5_home","losses_last5_home",
                "goals_scored_last5_home","goals_conceded_last5_home",
                "wins_last5_away","draws_last5_away","losses_last5_away",
                "goals_scored_last5_away","goals_conceded_last5_away"
            ]
            return {c: 0.0 for c in cols}
        # select needed columns
        out = {}
        cols_needed = [
            "wins_last5_overall","draws_last5_overall","losses_last5_overall",
            "goals_scored_last5_overall","goals_conceded_last5_overall","clean_sheets_last5_overall",
            "avg_goals_scored_last5_overall","avg_goals_conceded_last5_overall",
            "wins_last5_home","draws_last5_home","losses_last5_home",
            "goals_scored_last5_home","goals_conceded_last5_home",
            "wins_last5_away","draws_last5_away","losses_last5_away",
            "goals_scored_last5_away","goals_conceded_last5_away"
        ]
        for c in cols_needed:
            out[c] = float(row.get(c, 0.0)) if isinstance(row, pd.Series) else float(row[c])
        return out

    # Iterate matches and construct feature rows (vectorized-ish)
    training_rows = []
    for _, row in m.iterrows():
        home = row
        away = row
        home_stats = fetch_stats(row["home_team"], row["date"])
        away_stats = fetch_stats(row["away_team"], row["date"])

        # If snapshots missing, skip
        if pd.isna(row.get("overall_strength_home")) or pd.isna(row.get("overall_strength_away")):
            # skip matches where historical team snapshot unavailable
            continue

        feature_row = {
            "attack_diff": float(row["attack_home"] - row["attack_away"]),
            "midfield_diff": float(row["midfield_home"] - row["midfield_away"]),
            "defense_diff": float(row["defense_home"] - row["defense_away"]),
            "goalkeeper_diff": float(row["goalkeeper_home"] - row["goalkeeper_away"]),
            "overall_strength_diff": float(row["overall_strength_home"] - row["overall_strength_away"]),
            "squad_depth_diff": float(row["squad_depth_home"] - row["squad_depth_away"]),
            "superstar_diff": float(row["superstar_index_home"] - row["superstar_index_away"]),
            "final_team_rating_diff": float(row.get("final_team_rating_home", 0) - row.get("final_team_rating_away", 0)),
            "elo_diff": float(row.get("elo_diff", 0.0)),

            # rolling form diffs
            "wins_last5_overall_diff": float(home_stats["wins_last5_overall"] - away_stats["wins_last5_overall"]),
            "goals_scored_last5_diff": float(home_stats["goals_scored_last5_overall"] - away_stats["goals_scored_last5_overall"]),
            "goals_conceded_last5_diff": float(home_stats["goals_conceded_last5_overall"] - away_stats["goals_conceded_last5_overall"]),

            # target
            "result": int(
                1 if row.get("home_score", 0) > row.get("away_score", 0) else (-1 if row.get("home_score", 0) < row.get("away_score", 0) else 0)
            ),
            "date": row["date"],
            "home_team": row["home_team"],
            "away_team": row["away_team"],
        }
        training_rows.append(feature_row)

    match_dataset_v2 = pd.DataFrame(training_rows)
    return match_dataset_v2


# End of module
