# Official problem-statement fit

## Selected statement

**Problem 02 — Tomorrow's Load (Time Series)** from the uploaded Hacktoberfest Hack Day Lucknow problem-statement PDF.

The official brief says that grid operators must match supply and demand hourly; demand changes with time of day, season, weather and holidays. It asks for a model that forecasts each of the next 24 hours using past demand and related data, plus a chart/dashboard/CLI comparing forecast with actual demand. Bonus ideas are a low/high range, unusual peak/spike flags and explanations of drivers.

## How GRIDTWIN-24 maps to the brief

| Official requirement | Implementation | Evidence in demo |
|---|---|---|
| Next-day 24 hourly values | Horizon-conditioned time-series model | 24 timestamped forecast rows |
| Past demand and related data | Demand lags, rolling statistics, calendar features; add organiser covariates only after schema audit | Feature list + data contract |
| Forecast vs actual | Rolling-origin validation and dashboard | Historical forecast-vs-actual chart |
| Low/high range | Empirical residual band only when enough calibration residuals exist | Range and observed coverage label |
| Peak/spike flag | Top-decile/threshold flags and residual anomaly warning | Hourly peak markers |
| Explain drivers | Feature attribution and controlled model explanation | “Why this hour?” panel |

## What is an extension, not part of the official requirement

- Local building energy scenarios.
- Solar/battery assumptions and flexible-load shifting.
- Low-voltage hardware-in-the-loop bench.
- Gemma 4 operator agent.

These extensions must never obscure the core 24-hour forecast or substitute synthetic data for the dataset supplied by organisers.

## Dataset unknowns to resolve immediately on hack day

1. Exact timestamp column, timezone and daylight-saving convention.
2. Demand target name, unit (kW, MW or another unit) and measurement interval.
3. Whether observations are grid, feeder, substation, campus or another aggregate.
4. Missing values, duplicated timestamps, outages and revised readings.
5. Dataset duration and number of complete weeks/seasons.
6. Availability and publication time of exogenous fields (temperature, weather forecast, calendar, holidays, etc.).
7. Whether organisers provide a fixed train/test split or evaluation metric.

No future-realised covariate may be used as an input unless it would truly be available when a forecast is issued.
