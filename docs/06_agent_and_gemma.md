# Gemma 4 operator agent

## Role

Gemma 4 is a natural-language interface to a small set of deterministic, allow-listed Python functions. Forecasting, optimisation, validation and arithmetic remain in Python. Gemma is not the forecaster, optimiser or safety controller.

## Implemented integration

`src/gridtwin/gemma_agent.py` contains an optional Google Gen AI SDK adapter. It declares the tools, receives function calls, validates each name through `ToolContext.execute()`, executes the corresponding Python function, returns the result to Gemma and records tool name / arguments / status in an in-memory trace. The Streamlit dashboard exposes the agent when `GEMINI_API_KEY` is configured. The default model is `gemma-4-26b-a4b-it`; verify current account access and model availability before the demo. An actual API call has not been verified without a user key.

## Implemented tool allow-list

- `get_next_day_forecast()` — read-only 24-hour forecast query.
- `get_peak_windows(percentile)` — read-only forecast peak query.
- `run_load_shift_scenario(base_load_kw, tariff_per_kwh, tasks, capacity_kw)` — deterministic local-site flexible-load simulation.
- `run_pv_battery_scenario()` — deterministic configured PV / battery linear-programming scenario.
- `get_live_rig_telemetry()` — read-only cached low-voltage bench telemetry.

The actual allow-list is in `src/gridtwin/gemma_tools.py`. There is no hardware-write function in the agent. `scripts/rig_console.py` is a separate human-operated utility and requires explicit typed confirmation; firmware and physical interlocks are independent safeguards.

## Example interactions

- “Show tomorrow's 24-hour forecast and identify its highest-demand windows.”
- “Compare the forecast with the seasonal-naive baseline.”
- “Run the configured flexible-load schedule and explain the constraints.”
- “Run the local PV and battery simulation. State the assumptions and estimated cost difference.”
- “Read the latest telemetry from the DC demonstrator.”

## Hard rules

1. Model-generated code is never executed.
2. Tool names are checked against a fixed allow-list.
3. Forecast values come from Python model outputs; the LLM does not invent them.
4. Scenario arithmetic and battery optimisation run in deterministic Python code.
5. The agent has no GPIO or physical relay-write function.
6. The human bench console requires fresh telemetry and typed confirmation; firmware checks independent interlocks.
7. MQTT commands are non-retained.
8. When data is missing, the agent must say so rather than fabricate a forecast, measurement or saving.
9. Tool traces are currently in-memory for the session; persistent production audit logging remains future work.
