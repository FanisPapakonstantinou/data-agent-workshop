# World Cup data-agent workshop

This workshop builds a small SQL data agent over an included DuckDB database. It demonstrates how schema inspection, business rules, and a lightweight evaluation improve an agent's answers.

## TODO

- Find interesting questions to show non-determinism and fix after the human data context.


## Included files

- `world_cup_data_agent_workshop_final.ipynb` — the workshop notebook
- `worldcup-2026.duckdb` — the read-only workshop database
- `agent.py` — a small `smolagents` wrapper used by the notebook
- `notebook_ui.py` — notebook trace rendering used by the workshop
- `provider.py` — model and credential selection used by the notebook
- `requirements.txt` — Python dependencies

Keep the notebook, database, and all three Python modules in the same directory.

## Run locally

Python 3.12 is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
```

Open `world_cup_data_agent_workshop_final.ipynb` and run its cells in order.

When prompted, enter your own API key. The prompt uses `getpass`, so the key is not displayed or saved in the notebook. Never commit an API key or `.env` file.

## Choosing a provider

`provider.py` reads credentials from the environment, so switching provider needs no code change.

| Provider | Environment variables |
| --- | --- |
| OpenAI | `OPENAI_API_KEY` |
| Amazon Bedrock | either `AWS_BEARER_TOKEN_BEDROCK` (a Bedrock API key) or `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` |

`PROVIDER` selects the provider explicitly. Without it, whichever credentials are already in the environment decide; if none are, the notebook asks which provider you are using before requesting a key.

For Bedrock, set `AWS_REGION_NAME` if you are not in `us-east-1`, and set `MODEL_ID` to a model enabled in your account — check the Bedrock console for the exact id, since it varies by region and account.

```bash
export PROVIDER=bedrock
export AWS_BEARER_TOKEN_BEDROCK=...
export MODEL_ID=bedrock/anthropic.claude-sonnet-5
```

## Google Colab

Upload the notebook, `worldcup-2026.duckdb`, `agent.py`, `notebook_ui.py`, and `provider.py` into the same Colab session. Run the notebook cells in order and enter your API key only when prompted.

Colab secrets are not environment variables — the notebook will still prompt unless you copy the secret across first:

```python
import os
from google.colab import userdata
os.environ["OPENAI_API_KEY"] = userdata.get("OPENAI_API_KEY")
```

## Data

The included DuckDB file contains 11 related tables for the 2026 World Cup workshop: matches, teams, players, goals, bookings, lineups, substitutions, referees, match referees, penalty shootouts, and tournaments.

The database was derived from the [OpenFootball World Cup dataset](https://github.com/openfootball/worldcup.json), which is released under CC0 1.0/public domain. The provenance is also recorded in the database metadata.
