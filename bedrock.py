from __future__ import annotations

import getpass
import os

from smolagents import LiteLLMModel


DEFAULT_MODEL = "anthropic/claude-haiku-4-5" 


def build_bedrock_model() -> LiteLLMModel:
    """Prompt for the workshop's Anthropic key and build its model."""
    # Clear Bedrock leftovers from the old cell (the kernel keeps env vars across cells)
    os.environ.pop("AWS_BEARER_TOKEN_BEDROCK", None)
    os.environ.pop("AWS_REGION_NAME", None)

    api_key = getpass.getpass(
        "Anthropic API key (input hidden; paste and press Enter): "
    ).strip()
    if not api_key:
        raise ValueError("An Anthropic API key is required.")
    if not api_key.startswith("sk-ant-"):
        print(f"warning: unusual key prefix {api_key[:8]!r}... (expected 'sk-ant-'), continuing anyway")

    model_id = input(f"Model [{DEFAULT_MODEL}]: ").strip() or DEFAULT_MODEL

    print("model:", model_id)
    return LiteLLMModel(model_id=model_id, api_key=api_key, max_tokens=1200,  tool_choice="auto",  reasoning_effort="low")