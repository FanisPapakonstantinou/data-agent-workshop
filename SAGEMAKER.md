# SageMaker Studio setup

This guide prepares the workshop in the current Amazon SageMaker Studio
JupyterLab experience. It intentionally uses a stock SageMaker Distribution
image and a repository-local Python environment; a custom image is not needed
for the first delivery.

## Recommended workshop configuration

- Region: `eu-north-1`
- Python: 3.11 or 3.12
- Kernel shown to participants: **Data Agent Workshop**
- LiteLLM model ID: `bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0`
- Data: keep `worldcup-2026.duckdb` in the repository

The database is about 5.8 MB. Keeping it with the notebook removes an S3
download and permissions dependency from every participant session.

## One-time preparation by the organizer

1. Create the SageMaker Studio domain and participant user profiles or private
   spaces in `eu-north-1`.
2. Select and pin a SageMaker Distribution image that provides Python 3.11 or
   3.12. Use the same image for the rehearsal and the workshop.
3. Clone the repository and check out the release tag selected for the
   workshop. Replace `<release-tag>` with the tag agreed for the delivery:

   ```bash
   git clone https://github.com/FanisPapakonstantinou/data-agent-workshop.git
   cd data-agent-workshop
   git switch --detach <release-tag>
   ```

   Avoid using a moving branch on workshop day.
4. From the same terminal, run:

   ```bash
   bash scripts/setup_sagemaker.sh
   ```

5. Start or restart JupyterLab, open
   `world_cup_data_agent_workshop_final.ipynb`, and select the
   **Data Agent Workshop** kernel.
6. Run the notebook from top to bottom with a fresh Bedrock API key.

The setup script is idempotent. It reinstalls dependencies only when
`requirements.lock.txt` changes, registers the kernel, and runs an offline
smoke test against the bundled database.

### Test the open pull request

Before the release tag exists, use these exact commands to test PR #2:

```bash
git clone https://github.com/FanisPapakonstantinou/data-agent-workshop.git
cd data-agent-workshop
git fetch origin pull/2/head:sagemaker-workshop-setup
git switch sagemaker-workshop-setup
bash scripts/setup_sagemaker.sh
```

## Optional lifecycle configuration

For many participants, attach a JupyterLab lifecycle configuration that calls
the checked-in setup script. Replace the repository path below with the exact
path used in the participant spaces:

```bash
#!/usr/bin/env bash
set -euo pipefail

cd /home/sagemaker-user/data-agent-workshop
bash scripts/setup_sagemaker.sh
```

Test the lifecycle configuration on the chosen image before attaching it to
all spaces. Lifecycle configurations run during application startup, so keep
this wrapper small and use the repository script as the source of truth.

If startup-time package downloads are slow or blocked, run the setup script
once while preparing each persistent space. Use a custom SageMaker image only
when the organization requires an approved image or the environment cannot
reach the Python package index during preparation.

## Bedrock prerequisites

Before the rehearsal, confirm all of the following in the workshop AWS account:

- First-time Anthropic model access requirements have been completed.
- The selected inference profile can be invoked in `eu-north-1`.
- API keys will still be valid during the workshop and can invoke
  `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` as needed.
- The planned number of concurrent participants fits the account's Bedrock
  quotas.
- Each participant has an individual key when possible. Never commit keys to
  Git or save them in notebook output, and rotate the workshop keys afterward.

The notebook asks for the API key with hidden input and keeps it only in the
kernel process environment.

## Acceptance test

Run this in the repository before distributing the environment:

```bash
.venv/bin/python scripts/smoke_test.py
```

Expected output starts with `SMOKE_TEST_OK`. This check is deliberately
offline: it verifies Python, imports, helper modules, the default Bedrock
configuration, and all 11 DuckDB tables without consuming model quota.

Then perform one online check by running the notebook through at least one
agent question. Repeat with the expected participant concurrency during the
final rehearsal.

## Participant flow

1. Open the prepared SageMaker Studio JupyterLab space.
2. Open `world_cup_data_agent_workshop_final.ipynb`.
3. Confirm that the **Data Agent Workshop** kernel is selected.
4. Run the cells in order.
5. Paste the supplied Bedrock API key into the hidden prompt and press Enter.
6. Press Enter at the region and model prompts to accept the tested defaults.

## AWS references

- [SageMaker Studio JupyterLab guide](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-jl-user-guide.html)
- [Configure a JupyterLab space](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-jl-user-guide-configure-space.html)
- [Studio lifecycle configurations](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-lifecycle-configurations.html)
- [Create a lifecycle configuration](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-lifecycle-configurations-create.html)
- [Bring your own SageMaker image](https://docs.aws.amazon.com/sagemaker/latest/dg/studio-updated-byoi.html)
