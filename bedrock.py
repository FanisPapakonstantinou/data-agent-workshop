"""Amazon Bedrock setup for the workshop notebook."""

from __future__ import annotations

import getpass
import os

from smolagents import LiteLLMModel


DEFAULT_REGION = "eu-north-1"
DEFAULT_MODEL = "bedrock/eu.anthropic.claude-sonnet-4-5-20250929-v1:0"


def build_bedrock_model() -> LiteLLMModel:
    """Prompt for the workshop's Bedrock settings and build its model."""
    api_key = getpass.getpass(
        "Bedrock API key (input hidden; paste and press Enter): "
    )
    if not api_key:
        raise ValueError("A Bedrock API key is required.")

    region = input(f"AWS region [{DEFAULT_REGION}]: ").strip() or DEFAULT_REGION
    model_id = input(f"Bedrock model [{DEFAULT_MODEL}]: ").strip() or DEFAULT_MODEL

    os.environ["AWS_BEARER_TOKEN_BEDROCK"] = api_key
    os.environ["AWS_REGION_NAME"] = region

    print("model:", model_id)
    return LiteLLMModel(model_id=model_id, max_tokens=1200)
