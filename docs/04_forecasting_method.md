# Forecasting methodology and evaluation protocol

## Baseline first

Use a seasonal-naive benchmark (same hour on the previous day; compare with previous-week same hour where useful). A complex model must beat this baseline on a time-respecting test protocol before it is presented as better.

## Starter model in this repository

A horizon-conditioned HistGradientBoostingRegressor learns 1–24 hour targets from:

- Demand lags: 1, 2, 3, 24, 48 and 168 hours.
- Rolling summaries over 24 and 168 hours, computed only from history available at the forecast origin.
- Calendar encodings: hour, day of week, weekend and day-of-year cyclic features.
- Explicit forecast horizon.

This is a reproducible baseline, not a claim that boosted trees are the optimal model. Compare alternatives only under the same data preparation and backtesting protocol.

## Evaluation protocol

1. Sort observations and resolve timezone explicitly.
2. Use rolling-origin evaluation. Each origin sees only measurements available up to that origin.
3. Forecast the following 24 hours as a block. Evaluate multiple origins at least 24 hours apart for non-overlapping test windows.
4. Keep a final untouched time period if the organisers provide enough data.
5. Compare model with seasonal-naive and a simple regression baseline.
6. Report MAE, RMSE, WAPE and peak recall / precision above the training-period P90 threshold. Include units, time window, number of origins and missing-data handling.
7. Examine errors by hour, weekday/weekend, season and high-demand regime where sample size permits.

## Leakage traps

- Randomly splitting hourly rows.
- Scaling or imputing on the full dataset before splitting.
- Using realised future temperature/weather at a forecast origin.
- Computing rolling features that include the target or any later sample.
- Decomposing the full series before the train/test split.
- Tuning repeatedly on the final test window.

## Uncertainty

The starter implementation builds an empirical pooled residual band from rolling-origin residuals and withholds it when too few observations exist. It estimates coverage on a later, disjoint slice of the residual sequence and reports the sample count. The next-day band is then refit using all out-of-sample residuals. This is a diagnostic, not a guarantee of future coverage; report both interval width and observed disjoint-slice coverage. For a stronger product, implement horizon-conditional conformal calibration or quantile models and validate coverage over multiple periods.

## Peak and spike definitions

Do not pick a threshold after looking at the test labels. The starter model fixes its threshold at the 90th percentile of the training-period demand and applies that same threshold to both actual and predicted validation values and the next-day forecast. Do not compute separate thresholds from held-out actual and predicted values. Report peak recall separately from general MAE. This is a statistical high-demand flag, not an operational grid alert. Distinguish recurring daily peaks from anomalous spikes.

## Data limitations

If less than a full seasonal cycle is provided, do not claim seasonal generalisation. If only one aggregate series is provided, do not claim feeder- or household-level recommendations. If no weather forecast is supplied, calendar and past-load features are valid inputs; future realised weather is not.


## Local PV + battery dispatch extension

`src/gridtwin/battery.py` contains a separate 24-hour linear-programming scenario. It balances site load, PV, grid import/export, battery charge/discharge and SOC. Constraints include charge/discharge power, minimum/maximum SOC, round-trip efficiency components, a fixed terminal SOC equal to the initial SOC (so stored energy is not treated as free), battery-throughput degradation cost, optional import cap and optional peak-demand charge.

This optimiser is not part of the required grid-load forecast and is not a real battery controller. Its outputs are scenario estimates under explicit assumptions. The application does not use the organiser's grid series as a building profile.
