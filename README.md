# World Cup Data-Agent Workshop

This workshop teaches participants to build and improve a SQL data agent over a supplied DuckDB database.

Participants start with a basic agent and progressively add schema inspection, business rules, and executable evaluations to improve answer quality.

## Target environment

The workshop will run in **Amazon SageMaker JupyterLab** using **Amazon Bedrock models**.

SageMaker JupyterLab is required because the workshop uses:

- Local Python modules
- A local DuckDB database
- Interactive notebook input
- Custom HTML rendering for agent traces

## Work before delivery

### Bedrock support

- Ensure model calling is fine through Bedrock. 
- Select and use a Bedrock model for the workshop. 

### SageMaker environment
Look into these: 
 - SageMaker Docker image with dependencies preinstalled.
 - SageMaker lifecycle configuration that installs dependencies at startup.

The notebook’s `%pip install` cell should remain only as a fallback.

### Workshop content

- Improve the progression of suggested questions.
- Make sure the flow works well with one of the bedrock models. 
- Add evaluation cases covering schema discovery, joins, aggregation, and business rules.
- Validate expected answers and repeatability with the selected Bedrock model.

## Workshop-ready criteria

The workshop is ready when:
- A fresh SageMaker JupyterLab environment runs without manual setup.
- All required files are available automatically.

## Included files
- `world_cup_data_agent_workshop_final.ipynb` — workshop notebook
- `worldcup-2026.duckdb` — read-only workshop database
- `agent.py` — `smolagents` wrapper
- `notebook_ui.py` — agent trace renderer
- `requirements.txt` — Python dependencies

Keep the notebook, database, and Python modules in the same directory.

## Local development

Python 3.12 is recommended.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
jupyter lab
