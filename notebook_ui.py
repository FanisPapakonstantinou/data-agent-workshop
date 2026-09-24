"""Notebook-native, real-time rendering for the data-agent workshop."""

from __future__ import annotations

import html
import json

from IPython.display import HTML, display
from markdown_it import MarkdownIt
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import SqlLexer

try:
    import sqlparse
except ImportError:  # The query is still highlighted if sqlparse is unavailable.
    sqlparse = None


_STYLES = """
<style>
:root {
  --agent-border: #e2e8f0;
  --agent-muted: #64748b;
  --agent-surface: #ffffff;
  --agent-soft: #f8fafc;
}
.agent-run { max-width: 1080px; margin: 10px 0 24px; color: #172033; }
.agent-question {
  padding: 16px 18px; background: linear-gradient(135deg, #f5f3ff, #faf5ff);
  border: 1px solid #e9d5ff; border-left: 4px solid #7c3aed;
  border-radius: 10px; margin-bottom: 14px;
}
.agent-label {
  color: var(--agent-muted); font-size: 11px; font-weight: 750;
  letter-spacing: .08em; text-transform: uppercase; margin-bottom: 5px;
}
.agent-question-text { font-size: 16px; font-weight: 600; }
.agent-status { color: var(--agent-muted); font-size: 13px; margin: 8px 2px 12px; }
.agent-thinking {
  padding: 13px 15px; margin: 12px 0 8px; background: #fffbeb;
  border: 1px solid #fde68a; border-radius: 10px;
}
.agent-thinking-head {
  color: #92400e; font-size: 12px; font-weight: 750; margin-bottom: 7px;
}
.agent-thinking-head::before { content: "✦"; margin-right: 7px; }
.agent-thinking-body { color: #3f3a2e; font-size: 14px; line-height: 1.5; }
.agent-thinking-body > :first-child { margin-top: 0; }
.agent-thinking-body > :last-child { margin-bottom: 0; }
.agent-tool {
  margin: 8px 0 16px; background: var(--agent-surface);
  border: 1px solid var(--agent-border); border-radius: 10px; overflow: hidden;
  box-shadow: 0 1px 2px rgba(15, 23, 42, .04);
}
.agent-tool-error {
  border: 2px solid #ef4444; background: #fff7f7;
  box-shadow: 0 2px 8px rgba(220, 38, 38, .14);
}
.agent-tool-error .agent-tool-head {
  background: #fee2e2; border-bottom-color: #fca5a5;
}
.agent-tool-error .agent-step-pill { color: #991b1b; background: #fee2e2; }
.agent-error-badge {
  flex: 0 0 auto; align-self: center; padding: 3px 8px; border-radius: 999px;
  color: #fff; background: #dc2626; font-size: 10px; font-weight: 800;
  letter-spacing: .05em; text-transform: uppercase;
}
.agent-tool-head {
  display: flex; align-items: flex-start; gap: 10px; padding: 11px 13px;
  background: var(--agent-soft); border-bottom: 1px solid var(--agent-border);
}
.agent-step-pill {
  flex: 0 0 auto; color: #475569; background: #e2e8f0; border-radius: 999px;
  padding: 3px 8px; font-size: 11px; font-weight: 750; margin-top: 1px;
}
.agent-call {
  min-width: 0; flex: 1; margin: 0; color: #0f172a; font-size: 13px;
  line-height: 1.45; white-space: pre-wrap; overflow-wrap: anywhere;
}
.agent-meta { flex: 0 0 auto; color: var(--agent-muted); font-size: 11px; padding-top: 3px; }
.agent-sql {
  position: relative; margin: 0; padding: 13px 15px 14px 48px;
  background: #f8fafc; border-bottom: 1px solid #e2e8f0; overflow-x: auto;
}
.agent-sql::before {
  content: "SQL"; position: absolute; top: 15px; left: 13px;
  color: #2563eb; font-size: 10px; font-weight: 800; letter-spacing: .08em;
}
.agent-sql pre {
  margin: 0 !important; padding: 0 !important; border: 0 !important;
  color: #334155; background: transparent !important;
  font: 12.5px/1.65 ui-monospace, SFMono-Regular,
    Menlo, Monaco, Consolas, "Liberation Mono", monospace; white-space: pre;
}
.agent-sql .k, .agent-sql .kn { color: #6d28d9; font-weight: 750; }
.agent-sql .nf, .agent-sql .nb { color: #0369a1; font-weight: 650; }
.agent-sql .s1, .agent-sql .s2 { color: #15803d; }
.agent-sql .mi, .agent-sql .mf { color: #b45309; }
.agent-sql .o, .agent-sql .p { color: #475569; }
.agent-sql .c1, .agent-sql .cm { color: #64748b; font-style: italic; }
.agent-result summary {
  cursor: pointer; list-style: none; padding: 10px 13px; color: #475569;
  font-size: 12px; font-weight: 700; user-select: none;
}
.agent-result summary::-webkit-details-marker { display: none; }
.agent-result summary::before { content: "▸"; display: inline-block; margin-right: 7px; transition: transform .15s; }
.agent-result[open] summary::before { transform: rotate(90deg); }
.agent-result-body {
  padding: 2px 13px 13px; color: #334155; font-size: 13px;
  overflow-x: auto;
}
.agent-result-body > :first-child { margin-top: 0; }
.agent-result-body > :last-child { margin-bottom: 0; }
.agent-result-body table { border-collapse: collapse; font-size: 13px; }
.agent-result-body th, .agent-result-body td {
  border: 1px solid var(--agent-border); padding: 6px 9px; text-align: left;
}
.agent-result-body th { background: var(--agent-soft); }
.agent-result-error summary {
  color: #991b1b; background: #fef2f2; border-top: 1px solid #fecaca;
}
.agent-error-box {
  display: flex; gap: 9px; align-items: flex-start; margin: 2px 0 0;
  padding: 11px 12px; color: #991b1b; background: #fef2f2;
  border: 1px solid #fecaca; border-radius: 8px;
  font: 12.5px/1.55 ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
    "Liberation Mono", monospace; white-space: pre-wrap; overflow-wrap: anywhere;
}
.agent-error-box::before {
  content: "!"; flex: 0 0 auto; display: grid; place-items: center;
  width: 18px; height: 18px; margin-top: 1px; border-radius: 999px;
  color: #fff; background: #dc2626; font: 800 11px/1 system-ui, sans-serif;
}
.agent-more {
  margin-top: 9px; border-top: 1px solid var(--agent-border); padding-top: 4px;
}
.agent-more summary {
  padding: 7px 0 3px; color: #2563eb; font-size: 12px; font-weight: 700;
}
.agent-more-body { padding-top: 7px; overflow-x: auto; }
.agent-preview-note { color: var(--agent-muted); font-size: 11px; margin-top: 7px; }
.agent-error { color: #b91c1c; }
.agent-answer {
  padding: 16px 18px; margin-top: 14px; background: #f0fdf4;
  border: 1px solid #bbf7d0; border-left: 4px solid #16a34a; border-radius: 10px;
}
.agent-answer-text { color: #14532d; font-size: 16px; font-weight: 600; line-height: 1.5; }
</style>
"""


_MARKDOWN = MarkdownIt("commonmark", {"html": False}).enable("table")


def _reasoning_summary(step) -> str:
    """Return provider-supplied reasoning, if one was returned."""
    model_message = getattr(step, "model_output_message", None)
    raw_response = getattr(model_message, "raw", None)
    try:
        raw_message = raw_response.choices[0].message
    except (AttributeError, IndexError, TypeError):
        raw_message = None

    reasoning = getattr(raw_message, "reasoning_content", None)
    if reasoning:
        return str(reasoning).strip()

    provider_fields = getattr(raw_message, "provider_specific_fields", None) or {}
    blocks = (provider_fields.get("thinking_blocks") or []) if isinstance(provider_fields, dict) else []
    block_text = []
    for block in blocks:
        text = block.get("thinking") if isinstance(block, dict) else getattr(block, "thinking", None)
        if text:
            block_text.append(str(text).strip())
    if block_text:
        return "\n\n".join(block_text)

    return str(getattr(step, "model_output", None) or "").strip()


def _format_arguments(arguments) -> str:
    """Format all tool arguments inline with the tool name."""
    arguments = arguments or {}
    if not isinstance(arguments, dict):
        return str(arguments)
    return ", ".join(
        f"{key}={json.dumps(value, ensure_ascii=False, default=str)}"
        for key, value in arguments.items()
    )


def _sql_argument(call) -> str | None:
    """Return the SQL string for database tool calls, when present."""
    arguments = getattr(call, "arguments", None)
    if not isinstance(arguments, dict):
        return None
    query = arguments.get("query")
    return query if isinstance(query, str) and query.strip() else None


def _render_sql(query: str) -> str:
    """Format and syntax-highlight SQL without exposing notebook UI code."""
    formatted = query.strip()
    if sqlparse is not None:
        formatted = sqlparse.format(
            formatted,
            reindent=True,
            keyword_case="upper",
            use_space_around_operators=True,
        )
    highlighted = highlight(
        formatted,
        SqlLexer(),
        HtmlFormatter(nowrap=True, cssclass="agent-sql-code"),
    )
    return f"<div class='agent-sql'><pre>{highlighted}</pre></div>"


def _step_meta(step) -> str:
    timing = getattr(step, "timing", None)
    usage = getattr(step, "token_usage", None)
    details = []
    duration = getattr(timing, "duration", None)
    if duration is not None:
        details.append(f"{duration:.2f}s")
    if usage is not None:
        details.append(f"{usage.input_tokens:,} in")
        details.append(f"{usage.output_tokens:,} out")
    return " · ".join(details)


def _render_result(observation, preview_rows: int = 10) -> str:
    """Render a Markdown result, folding table rows after the preview."""
    if not observation:
        return "<em>No output</em>"

    text = str(observation).strip()
    lines = text.splitlines()
    table_start = next(
        (
            index
            for index in range(len(lines) - 1)
            if "|" in lines[index]
            and "|" in lines[index + 1]
            and set(lines[index + 1].replace("|", "").replace(":", "").strip()) <= {"-", " "}
        ),
        None,
    )
    if table_start is None:
        return _MARKDOWN.render(text)

    table_end = table_start + 2
    while table_end < len(lines) and "|" in lines[table_end] and lines[table_end].strip():
        table_end += 1

    header = lines[table_start : table_start + 2]
    rows = lines[table_start + 2 : table_end]
    prefix = lines[:table_start]
    suffix = lines[table_end:]
    if len(rows) <= preview_rows:
        return _MARKDOWN.render(text)

    preview_markdown = "\n".join(prefix + header + rows[:preview_rows])
    remaining_markdown = "\n".join(header + rows[preview_rows:])
    suffix_html = _MARKDOWN.render("\n".join(suffix).strip()) if any(line.strip() for line in suffix) else ""
    remaining_count = len(rows) - preview_rows
    return (
        _MARKDOWN.render(preview_markdown)
        + f"<div class='agent-preview-note'>Showing {preview_rows} of {len(rows)} returned rows</div>"
        + "<details class='agent-more'>"
        + f"<summary>Show {remaining_count} more rows</summary>"
        + f"<div class='agent-more-body'>{_MARKDOWN.render(remaining_markdown)}{suffix_html}</div>"
        + "</details>"
    )


def _tool_error(observation, error) -> str | None:
    """Return a prominent message for framework or tool-reported errors."""
    if error:
        return str(error)
    if observation:
        message = str(observation).strip()
        normalized = message.upper()
        # The workshop deliberately begins with an unhelpful "Query failed."
        # observation, then improves it to "ERROR: <database details>". Treat
        # both as failures so a collapsed result never hides the failed state.
        if normalized.startswith(("ERROR:", "QUERY FAILED", "TOOL ERROR:")):
            return message
    return None


def _render_step(step, detailed: bool) -> str:
    """Build the HTML for one completed agent step."""
    all_calls = getattr(step, "tool_calls", None) or []
    if not detailed and all_calls and all(call.name == "final_answer" for call in all_calls):
        return ""

    calls = all_calls if detailed else [call for call in all_calls if call.name != "final_answer"]
    error = getattr(step, "error", None)
    reasoning = _reasoning_summary(step)
    if not calls and not error and not reasoning:
        return ""

    parts = []
    if reasoning:
        parts.append(
                "<div class='agent-thinking'>"
                "<div class='agent-thinking-head'>Thinking</div>"
                f"<div class='agent-thinking-body'>{_MARKDOWN.render(reasoning)}</div>"
                "</div>"
        )

    observation = getattr(step, "observations", None)
    tool_error = _tool_error(observation, error)
    result_html = (
        f"<div class='agent-error-box'>{html.escape(tool_error)}</div>"
        if tool_error
        else _render_result(observation)
    )

    meta = html.escape(_step_meta(step))
    for call in calls:
        sql = _sql_argument(call)
        arguments = "query=…" if sql else _format_arguments(call.arguments)
        invocation = f"{call.name}({arguments})"
        call_id = f" · {call.id}" if detailed else ""
        tool_class = "agent-tool agent-tool-error" if tool_error else "agent-tool"
        result_class = "agent-result agent-result-error" if tool_error else "agent-result"
        result_label = "Query failed" if tool_error else "Tool result"
        error_badge = "<span class='agent-error-badge'>Failed</span>" if tool_error else ""
        result_open = " open" if tool_error else ""
        parts.append(
                f"<div class='{tool_class}'>"
                "<div class='agent-tool-head'>"
                f"<span class='agent-step-pill'>STEP {step.step_number}</span>"
                f"<code class='agent-call'>{html.escape(invocation + call_id)}</code>"
                f"{error_badge}"
                f"<span class='agent-meta'>{meta}</span>"
                "</div>"
                + (_render_sql(sql) if sql else "")
                +
                f"<details class='{result_class}'{result_open}>"
                f"<summary>{result_label}</summary>"
                f"<div class='agent-result-body'>{result_html}</div>"
                "</details>"
                "</div>"
        )
    return "".join(parts)


def _render_run(question: str, steps: list[str], status: str = "", answer=None) -> str:
    """Render the complete trace in one output area so Jupyter keeps its CSS."""
    status_html = f"<div class='agent-status'>{html.escape(status)}</div>" if status else ""
    answer_html = ""
    if answer is not None:
        answer_html = (
            "<div class='agent-answer'>"
            "<div class='agent-label'>Final answer</div>"
            f"<div class='agent-answer-text'>{_MARKDOWN.render(str(answer))}</div>"
            "</div>"
        )
    return (
        _STYLES
        + "<div class='agent-run'>"
        + "<div class='agent-question'>"
        + "<div class='agent-label'>Question</div>"
        + f"<div class='agent-question-text'>{html.escape(question)}</div>"
        + "</div>"
        + status_html
        + "".join(steps)
        + answer_html
        + "</div>"
    )


def run_agent(
    agent,
    question: str,
    detailed: bool = False,
    return_answer: bool = False,
):
    """Run an agent and stream its trace; optionally return the final answer."""
    steps = []
    seen_step_objects = set()
    panel = display(
        HTML(_render_run(question, steps, status="Waiting for the model…")),
        display_id=True,
    )

    def update_panel(status: str = "", answer=None) -> None:
        rendered = HTML(_render_run(question, steps, status=status, answer=answer))
        if panel is not None:
            panel.update(rendered)
        else:
            display(rendered)

    answer = None
    try:
        for event in agent.run(question, reset=True, stream=True):
            if type(event).__name__ == "FinalAnswerStep":
                answer = event.output
            elif getattr(event, "step_number", None) is not None:
                # smolagents 1.26 yields the last ActionStep a second time when
                # max_steps is reached. It is the exact same object, not a new
                # model/tool step, so do not append it twice to the notebook UI.
                event_identity = id(event)
                if event_identity in seen_step_objects:
                    continue
                seen_step_objects.add(event_identity)
                step_html = _render_step(event, detailed=detailed)
                if step_html:
                    steps.append(step_html)
                    update_panel(status="Running the next step…")
    except Exception:
        update_panel(status="Run failed.")
        raise
    update_panel(answer=answer)
    return answer if return_answer else None
