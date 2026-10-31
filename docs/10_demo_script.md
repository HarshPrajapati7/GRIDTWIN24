# Demo script (5–7 minutes)

## Opening (30 seconds)

“An electricity forecast is useful only when someone can make a better decision from it. GRIDTWIN-24 forecasts the next 24 hours and explores the operating choices. We have also designed a 12-volt DC energy bench to validate the sensing and control path once the hardware is assembled.”

## Act 1 — Forecast (90 seconds)

- Load the actual organiser dataset.
- Show timestamp/unit/data-quality audit.
- Show seasonal-naive baseline and model scores.
- Show next-day 24-hour chart and peak flags.
- Explain the validation split and show the held-out forecast-vs-actual comparison.

## Act 2 — Scenario (90 seconds)

- Enter an illustrative site profile, tariff and capacity limit.
- Add one shiftable task (e.g. demo water pump or EV charging session).
- Run the scenario and show the schedule and estimated bill / peak effect.
- Emphasise that this is a scenario estimate, not a measured saving.

## Act 3 — Gemma 4 operator (60 seconds)

Ask: “Why is the forecast highest at 19:00, and what can I shift without breaking the capacity limit?”

Show Gemma calling `get_next_day_forecast`, `get_peak_windows` and, when configured, `run_pv_battery_scenario`. Verify that the numeric answer comes from tool outputs.

## Act 4 — Physical DC energy bench (90 seconds)

- Only if assembled and all component ratings / safeguards have been checked: show the 12 V bus and three load channels.
- Only claim live measurements if read from the actual INA3221; otherwise show the separately labelled simulator.
- Confirm physical ARM switch and E-stop status locally; do not infer safety from a dashboard.
- Submit a user-confirmed demonstration schedule; show a non-critical DC load switching OFF during the simulated peak window.
- Show telemetry confirms the current drop. Use only real sensor readings. If the bench has not been built and tested, skip the physical demonstration and show the wiring / design as planned work.

## Closing (30 seconds)

“GRIDTWIN-24 connects forecasting to constrained operating scenarios and provides a safe physical test path. The next step is a read-only pilot with a campus or hostel using its own interval-meter data.”

## If the hardware fails

Use the same telemetry simulator and label it clearly as simulated. Do not pretend simulated readings came from the physical sensor.
