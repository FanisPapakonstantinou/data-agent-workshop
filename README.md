# World Cup Data-Agent Workshop

This workshop teaches participants to build and improve a SQL data agent over
a supplied DuckDB database covering 1930–2026. Participants start with a basic
agent and progressively add schema inspection and business rules to improve
answer quality. The final section turns those examples into a reusable eval
suite that holds the tools and prompt constant while comparing Haiku 4.5,
Sonnet 4.5, and Sonnet 4.6 on quality, steps, latency, tokens, and cost. Opus
4.5 judges each answer against a reference answer.

## Included files

- `world_cup_data_agent_workshop_final.ipynb` — workshop notebook
- `worldcups-1930-2026.duckdb` — read-only workshop database
- `agent.py` — `smolagents` wrapper
- `bedrock.py` — hidden Bedrock API-key input and model setup
- `evaluation.py` — LLM-as-judge evaluation and comparison harness
- `notebook_ui.py` — agent trace renderer
- `requirements.lock.txt` — tested workshop dependency versions
- `scripts/setup_sagemaker.sh` — idempotent environment and kernel setup
- `scripts/smoke_test.py` — offline environment and data acceptance test
- `SAGEMAKER.md` — organizer and participant setup guide

Keep the notebook, database, and Python modules in the same directory.

## SageMaker Studio

The delivery target is Amazon SageMaker Studio JupyterLab with Amazon Bedrock.
The recommended setup uses the stock SageMaker Distribution image and a
repository-local, pinned Python environment. Follow [SAGEMAKER.md](SAGEMAKER.md)
to prepare and rehearse participant spaces.

## Local development

Python 3.11 or 3.12 is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
jupyter lab
```

Select the Python kernel from `.venv`, open
`world_cup_data_agent_workshop_final.ipynb`, and run the cells in order.

To validate the environment without calling Bedrock:

```bash
python scripts/smoke_test.py
```

If `python3` is not the compatible interpreter on your machine, pass it to the
setup script explicitly, for example:

```bash
WORKSHOP_PYTHON=/path/to/python3.12 bash scripts/setup_sagemaker.sh
```
