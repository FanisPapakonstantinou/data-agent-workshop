"""Amazon Bedrock setup for the workshop notebook."""

from __future__ import annotations

import os

from smolagents import LiteLLMModel


DEFAULT_REGION = "eu-north-1"
DEFAULT_MODEL = "bedrock/eu.anthropic.claude-haiku-4-5-20251001-v1:0"


def configure_bedrock_iam(region: str | None = None) -> str:
    """Use AWS credentials, clearing a bearer token from earlier notebook runs."""
    region = region or os.environ.get("AWS_REGION_NAME", DEFAULT_REGION)
    os.environ.pop("AWS_BEARER_TOKEN_BEDROCK", None)
    os.environ["AWS_REGION_NAME"] = region
    return region


def build_bedrock_model() -> LiteLLMModel:
    """Build the workshop model using AWS IAM credentials, without an API key."""
    region = input(f"AWS region [{DEFAULT_REGION}]: ").strip() or DEFAULT_REGION
    model_id = input(f"Bedrock model [{DEFAULT_MODEL}]: ").strip() or DEFAULT_MODEL

    configure_bedrock_iam(region)

    print("authentication: AWS IAM credentials (Studio execution role)")
    print("model:", model_id)
    return LiteLLMModel(
        model_id=model_id,
        api_key=None,
        aws_region_name=region,
        max_tokens=1200,
        tool_choice="auto",
        reasoning_effort="low",
    )
