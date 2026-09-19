# World Cup data-agent workshop

This workshop builds a small SQL data agent over an included DuckDB database. It demonstrates how schema inspection, business rules, and a lightweight evaluation improve an agent's answers.

## TODO

- Make sure the model setup works fine with whatever model they will have access to in sagemaker
- Find interesting questions to show non-determinism and fix after the human data context.


## Included files

- `world_cup_data_agent_workshop_final.ipynb` — the workshop notebook
- `worldcup-2026.duckdb` — the read-only workshop database
- `agent.py` — a small `smolagents` wrapper used by the notebook
- `notebook_ui.py` — notebook trace rendering used by the workshop
- `requirements.txt` — Python dependencies

Keep the notebook, database, and both Python modules in the same directory.

## Run locally

Python 3.12 is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

Open `world_cup_data_agent_workshop_final.ipynb` and run its cells in order.

When prompted, enter your own OpenAI API key. The prompt uses `getpass`, so the key is not displayed or saved in the notebook. You may instead set `OPENAI_API_KEY` in your environment before starting Jupyter. Never commit an API key or `.env` file.

## Google Colab

Upload the notebook, `worldcup-2026.duckdb`, `agent.py`, and `notebook_ui.py` into the same Colab session. Run the notebook cells in order and enter your API key only when prompted.

## Data

The included DuckDB file contains 11 related tables for the 2026 World Cup workshop: matches, teams, players, goals, bookings, lineups, substitutions, referees, match referees, penalty shootouts, and tournaments.

The database was derived from the [OpenFootball World Cup dataset](https://github.com/openfootball/worldcup.json), which is released under CC0 1.0/public domain. The provenance is also recorded in the database metadata.
