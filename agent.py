"""Small wrapper that keeps framework plumbing out of the workshop notebook."""

from smolagents import ToolCallingAgent as _ToolCallingAgent
from smolagents.monitoring import LogLevel


_HARNESS_INSTRUCTIONS = """
The final_answer tool is internal framework protocol.
Call it silently when the task is complete.
Do not mention final_answer to the user.
Do not mention or leak final_answer in reasoning summaries, thinking steps, or answers.
Before each tool call, state in one short sentence what you are doing and why
""".strip()


class ToolCallingAgent(_ToolCallingAgent):
    """smolagents ToolCallingAgent with invisible harness instructions."""

    def __init__(self, *args, instructions: str | None = None, **kwargs):
        # The notebook has its own live trace renderer. Disable smolagents'
        # Rich console renderer completely so steps are never shown twice.
        kwargs["verbosity_level"] = LogLevel.OFF
        participant_instructions = (instructions or "").strip()
        combined_instructions = "\n\n".join(
            part for part in (participant_instructions, _HARNESS_INSTRUCTIONS) if part
        )
        super().__init__(*args, instructions=combined_instructions, **kwargs)
