# Final project definition — GRIDTWIN-24

## Official problem statement selected

**Problem 02: Tomorrow's Load — Time Series** (Hacktoberfest Hack Day Lucknow).

## Product thesis

**GRIDTWIN-24 is an open, forecast-to-action energy intelligence platform that predicts the next 24 hours of electricity demand, lets an operator test practical load-shifting scenarios, and includes a design for validating the sensing/control workflow on a low-voltage physical energy bench.**

## What is built for the actual problem

A model trained on the organiser-provided hourly load dataset. It must output 24 hourly next-day values and a forecast-vs-actual evaluation view. The model is compared with a seasonal-naive baseline using rolling-origin backtesting. Peak flags, interpretable drivers and prediction intervals are added only when data supports them.

## What makes the project unusual

The forecast is not the final screen. It becomes the input to a deterministic energy scenario engine with flexible-load scheduling and a constrained PV + battery linear-programming optimiser. The operator can model a local facility's load, tariff, capacity and flexible tasks, then inspect an alternative schedule. A designed low-voltage DC hardware rig is intended to demonstrate the last mile: ESP32 command path, measured current, switched physical loads and physical interlocks. The hardware has not yet been assembled or validated.

The challenge grid forecast and local facility profile are distinct data products. Do not directly convert a national/utility-level forecast into a household control command.

## Why hardware is included

The hardware creates a tangible engineering demo without connecting to hazardous mains. It is not required by the official problem statement and should be built only after the forecast is working.

## Why Gemma 4 is included

Gemma 4 is a natural-language operator layer that invokes approved functions. It can answer questions about forecasts, retrieve model explanations, run scenarios and read live telemetry. It does not produce numerical forecasts itself, execute generated code or bypass local hardware safety.

## Product path

Initial customer: facilities managers at campuses, hostels, apartment common areas, clinics, small hotels and co-working spaces. Start read-only with historical interval data; prove the recurring value of forecast reports and peak warnings; only then add hardware and approved scheduling integrations.

## What is not claimed

- No world-first claim.
- No proven energy-saving percentage.
- No utility-grade forecasting claim before testing on the provided dataset.
- No grid-scale or mains control.
- No assertion that a scaled tabletop rig validates real grid operation.
- No assertion that Gemma 4 is the source of numerical truth.
