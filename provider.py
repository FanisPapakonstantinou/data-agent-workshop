"""Model provider selection, so the notebook carries no credential plumbing."""

from __future__ import annotations

import getpass
import os

from smolagents import LiteLLMModel


_PROVIDERS = {
    "openai": {
        "default_model": "openai/gpt-5-mini",
        # Reasoning arguments are OpenAI-only; Bedrock rejects reasoning_summary.
        "default_model_kwargs": {"reasoning_effort": "low", "reasoning_summary": "auto"},
    },
    "bedrock": {
        # Check your Bedrock console for the exact model id enabled in your region.
        "default_model": "bedrock/anthropic.claude-sonnet-5",
        "default_model_kwargs": {},
    },
}


def _ensure_credentials(provider: str) -> None:
    """Put the provider's credentials in the environment, prompting if absent."""
    if provider == "bedrock":
        os.environ.setdefault("AWS_REGION_NAME", "us-east-1")
        # A Bedrock API key is a bearer token; long-lived AWS keys work too.
        if not (os.environ.get("AWS_BEARER_TOKEN_BEDROCK") or os.environ.get("AWS_ACCESS_KEY_ID")):
            os.environ["AWS_BEARER_TOKEN_BEDROCK"] = getpass.getpass("Bedrock API key: ")
    elif not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API key: ")


def build_model(model_id: str | None = None, provider: str | None = None, **kwargs) -> LiteLLMModel:
    """Build a LiteLLM model, reading credentials from the environment.

    Args:
        model_id: Overrides the provider default and the MODEL_ID variable.
        provider: "openai" or "bedrock". Defaults to the PROVIDER variable.
        kwargs: Passed through to LiteLLMModel.
    """
    provider = provider or os.environ.get("PROVIDER", "openai")
    if provider not in _PROVIDERS:
        raise ValueError(f"Unknown provider {provider!r}. Choose one of: {', '.join(_PROVIDERS)}")

    settings = _PROVIDERS[provider]
    resolved = model_id or os.environ.get("MODEL_ID") or settings["default_model"]
    # The reasoning arguments suit the default model, not every model on the provider.
    tuned = settings["default_model_kwargs"] if resolved == settings["default_model"] else {}

    _ensure_credentials(provider)

    print("provider:", provider)
    print("model:", resolved)
    return LiteLLMModel(model_id=resolved, **{"max_tokens": 1200, **tuned, **kwargs})
