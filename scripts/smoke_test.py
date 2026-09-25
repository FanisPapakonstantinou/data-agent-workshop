#!/usr/bin/env python3
"""Offline acceptance test for the workshop environment and bundled data."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DATABASE = REPO_ROOT / "worldcups-1930-2026.duckdb"
EXPECTED_TABLES = {
    "bookings",
    "goals",
    "lineups",
    "match_referees",
    "matches",
    "penalty_shootouts",
    "players",
    "referees",
    "substitutions",
    "teams",
    "tournaments",
}
REQUIRED_IMPORTS = (
    "boto3",
    "duckdb",
    "ipywidgets",
    "litellm",
    "markdown_it",
    "pandas",
    "pygments",
    "smolagents",
    "sqlparse",
    "tabulate",
)


def main() -> None:
    if sys.version_info < (3, 11) or sys.version_info >= (3, 13):
        raise RuntimeError(
            f"Python 3.11 or 3.12 is required; found {sys.version.split()[0]}."
        )

    # LiteLLM normally refreshes pricing metadata on import. The acceptance
    # check must also work in a prepared space without internet egress.
    os.environ["LITELLM_LOCAL_MODEL_COST_MAP"] = "True"

    for module_name in REQUIRED_IMPORTS:
        importlib.import_module(module_name)

    sys.path.insert(0, str(REPO_ROOT))
    importlib.import_module("agent")
    bedrock = importlib.import_module("bedrock")
    evaluation = importlib.import_module("evaluation")
    importlib.import_module("notebook_ui")

    if not bedrock.DEFAULT_MODEL.startswith("bedrock/"):
        raise RuntimeError("The default model must use LiteLLM's bedrock/ prefix.")
    if not bedrock.DEFAULT_REGION:
        raise RuntimeError("The default AWS region is empty.")
    if not evaluation.DEFAULT_JUDGE_MODEL.startswith("bedrock/"):
        raise RuntimeError("The judge model must use the bedrock/ prefix.")
    if len(evaluation.DEFAULT_CANDIDATE_MODELS) < 2:
        raise RuntimeError("The eval must compare at least two candidate models.")
    if not DATABASE.is_file():
        raise FileNotFoundError(f"Missing workshop database: {DATABASE}")

    duckdb = importlib.import_module("duckdb")
    with duckdb.connect(str(DATABASE), read_only=True) as connection:
        tables = {row[0] for row in connection.execute("SHOW TABLES").fetchall()}
        match_count = connection.execute("SELECT count(*) FROM matches").fetchone()[0]
        career_leaders = connection.execute(
            """
            WITH careers AS (
                SELECT p.player_name, t.team_name,
                       count(DISTINCT m.tournament_id) AS tournaments
                FROM lineups l
                JOIN matches m USING (match_id)
                JOIN players p USING (player_id)
                JOIN teams t ON p.team_id = t.team_id
                GROUP BY p.player_name, t.team_name
            )
            SELECT player_name, team_name, tournaments
            FROM careers
            WHERE tournaments = (SELECT max(tournaments) FROM careers)
            ORDER BY player_name
            """
        ).fetchall()
        booking_leader = connection.execute(
            """
            WITH tournament_matches AS (
                SELECT match_id
                FROM matches
                JOIN tournaments USING (tournament_id)
                WHERE season = 2022
            ),
            booking_totals AS (
                SELECT b.team_id, count(*) AS bookings
                FROM bookings b
                JOIN tournament_matches USING (match_id)
                GROUP BY b.team_id
            ),
            goal_totals AS (
                SELECT g.credited_team_id AS team_id, count(*) AS goals
                FROM goals g
                JOIN tournament_matches USING (match_id)
                GROUP BY g.credited_team_id
            )
            SELECT t.team_name, b.bookings, coalesce(g.goals, 0)
            FROM booking_totals b
            JOIN teams t USING (team_id)
            LEFT JOIN goal_totals g USING (team_id)
            ORDER BY b.bookings DESC, t.team_name
            LIMIT 1
            """
        ).fetchone()

    if tables != EXPECTED_TABLES:
        missing = sorted(EXPECTED_TABLES - tables)
        unexpected = sorted(tables - EXPECTED_TABLES)
        raise RuntimeError(
            f"Unexpected database schema; missing={missing}, unexpected={unexpected}"
        )
    if match_count <= 0:
        raise RuntimeError("The matches table is empty.")
    expected_career_leaders = [
        ("CRISTIANO RONALDO", "Portugal", 6),
        ("Lionel MESSI", "Argentina", 6),
    ]
    if career_leaders != expected_career_leaders:
        raise RuntimeError(f"Eval reference changed: career leaders={career_leaders}")
    if booking_leader != ("Argentina", 17, 15):
        raise RuntimeError(f"Eval reference changed: booking leader={booking_leader}")

    print(
        "SMOKE_TEST_OK "
        f"python={sys.version.split()[0]} tables={len(tables)} matches={match_count} "
        f"eval_references=2 region={bedrock.DEFAULT_REGION} "
        f"model={bedrock.DEFAULT_MODEL}"
    )


if __name__ == "__main__":
    main()
