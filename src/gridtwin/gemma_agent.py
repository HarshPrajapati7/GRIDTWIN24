"""Optional Gemma 4 function-calling adapter.

Numerical operations remain in the deterministic ToolContext. The model can
only request functions declared in gemma_tools.TOOL_DECLARATIONS, and every
request passes through ToolContext.execute() allow-list validation.
"""
from __future__ import annotations

import os
from typing import Any

from .gemma_tools import TOOL_DECLARATIONS, ToolContext

SYSTEM_INSTRUCTION = """You are GRIDTWIN-24, an energy operations copilot.
Use tools for all numerical claims about forecasts, peak windows, scenarios,
and rig telemetry. Never invent values, savings, hardware status, or data.
Clearly distinguish the organiser's grid-demand forecast from a separate
local-site scenario. A simulated saving is not a measured saving. The rig
telemetry tool is read-only. Never claim to have controlled hardware.
When data is unavailable, say so. State assumptions and uncertainty plainly.
"""


def ask_gemma(
    question: str,
    tool_context: ToolContext,
    *,
    api_key: str | None = None,
    model: str | None = None,
    max_tool_rounds: int = 3,
) -> dict[str, Any]:
    """Ask Gemma 4 and manually execute only allow-listed deterministic tools.

    Requires GEMINI_API_KEY (or api_key) and the optional google-genai SDK.
    No hardware-write function is available to the model.
    """
    if not question or not question.strip():
        raise ValueError("question must not be empty")
    resolved_key = api_key or os.getenv("GEMINI_API_KEY")
    if not resolved_key:
        raise RuntimeError("Set GEMINI_API_KEY before using the Gemma agent.")
    resolved_model = model or os.getenv("GEMMA_MODEL", "gemma-4-26b-a4b-it")

    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError("Install google-genai to use the Gemma agent.") from exc

    client = genai.Client(api_key=resolved_key)
    tool = types.Tool(function_declarations=TOOL_DECLARATIONS)
    config = types.GenerateContentConfig(
        tools=[tool],
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.2,
    )
    user_content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=question.strip())],
    )
    history: list[Any] = [user_content]
    response = client.models.generate_content(
        model=resolved_model,
        contents=history,
        config=config,
    )
    trace: list[dict[str, Any]] = []

    for _ in range(max_tool_rounds + 1):
        calls = response.function_calls or []
        if not calls:
            return {
                "text": response.text or "The model returned no text response.",
                "tool_calls": trace,
                "model": resolved_model,
            }

        candidate_content = response.candidates[0].content if response.candidates else None
        if candidate_content is not None:
            history.append(candidate_content)

        tool_parts = []
        for call in calls:
            args = dict(call.args or {})
            try:
                result = tool_context.execute(call.name, args)
                payload = {"result": result}
                trace.append({"name": call.name, "arguments": args, "status": "ok"})
            except Exception as exc:  # return a bounded tool error to the model
                payload = {"error": f"{type(exc).__name__}: {exc}"}
                trace.append({"name": call.name, "arguments": args, "status": "error"})
            tool_parts.append(
                types.Part.from_function_response(name=call.name, response=payload)
            )
        history.append(types.Content(role="tool", parts=tool_parts))
        response = client.models.generate_content(
            model=resolved_model,
            contents=history,
            config=config,
        )

    return {
        "text": "The tool-call limit was reached. Narrow the request and try again.",
        "tool_calls": trace,
        "model": resolved_model,
        "truncated": True,
    }
