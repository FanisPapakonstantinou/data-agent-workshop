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
    importlib.import_module("notebook_ui")

    if not bedrock.DEFAULT_MODEL.startswith("bedrock/"):
        raise RuntimeError("The default model must use LiteLLM's bedrock/ prefix.")
    if not bedrock.DEFAULT_REGION:
        raise RuntimeError("The default AWS region is empty.")
    if not DATABASE.is_file():
        raise FileNotFoundError(f"Missing workshop database: {DATABASE}")

    duckdb = importlib.import_module("duckdb")
    with duckdb.connect(str(DATABASE), read_only=True) as connection:
        tables = {row[0] for row in connection.execute("SHOW TABLES").fetchall()}
        match_count = connection.execute("SELECT count(*) FROM matches").fetchone()[0]

    if tables != EXPECTED_TABLES:
        missing = sorted(EXPECTED_TABLES - tables)
        unexpected = sorted(tables - EXPECTED_TABLES)
        raise RuntimeError(
            f"Unexpected database schema; missing={missing}, unexpected={unexpected}"
        )
    if match_count <= 0:
        raise RuntimeError("The matches table is empty.")

    print(
        "SMOKE_TEST_OK "
        f"python={sys.version.split()[0]} tables={len(tables)} matches={match_count} "
        f"region={bedrock.DEFAULT_REGION} model={bedrock.DEFAULT_MODEL}"
    )


if __name__ == "__main__":
    main()
