# Commudle form draft — Tomorrow's Load

## Selected problem statement

Tomorrow's Load — Time Series

## Why did you choose this problem?

I chose Tomorrow's Load because electricity demand forecasting becomes valuable when it helps operators make decisions before a peak occurs. I want to build more than a forecast chart: a system that produces a transparent 24-hour demand forecast, communicates uncertainty, identifies peak windows and lets an operator test practical load-management scenarios. The problem combines applied time-series modelling with a clear path to a useful energy-management product.

## Proposed solution

I propose GRIDTWIN-24, an open-source forecast-to-action energy intelligence system. It will use the organiser-provided dataset to forecast hourly demand for the next 24 hours and compare the results with a seasonal-naive baseline using time-respecting evaluation. The dashboard will display forecast-versus-actual performance, peak windows, uncertainty ranges where calibration supports them and the main factors associated with the forecast.

As an extension, a local-site scenario engine will simulate how shiftable loads could be scheduled under user-defined tariff, capacity and operating constraints. A low-voltage hardware-in-the-loop demonstrator will measure and switch three small DC loads to validate the telemetry and dispatch path. Gemma 4 will act as an operator copilot that calls the numerical forecasting, explanation and scenario tools; it will not generate the forecasts itself or bypass hardware safety controls.

## Technical implementation approach

I will first inspect the supplied dataset, map the actual timestamp and demand columns, verify units, time zones and gaps, and create a canonical hourly series. I will establish a seasonal-naive baseline, then develop a horizon-conditioned model for the next 24 hourly values. Evaluation will use rolling-origin 24-hour windows rather than random row splits to avoid temporal leakage. I will report MAE, RMSE, WAPE and peak-hour recall, with validation dates and target units. Prediction intervals will be shown only if the residual calibration sample supports them.

I will expose the forecast and scenario functions through a Python backend and build an interactive dashboard. The optional HIL rig will use an ESP32 and a three-channel INA3221 power monitor on an isolated 12 V DC bench, with fused branches, MOSFET drivers, a physical emergency stop and a local arm switch. Gemma 4 will interact through a restricted function-calling interface and all numerical operations will remain deterministic and auditable.

## Technologies

Python, Pandas, NumPy, Scikit-learn, HistGradientBoostingRegressor, time-series backtesting, Plotly, Streamlit, FastAPI, Gemma 4, Google GenAI SDK / Transformers, ESP32, INA3221, Arduino C++, MQTT, PostgreSQL, Docker, Git, GitHub.

## Strongest skills / preferred contribution

Use only skills you can personally demonstrate. Suitable areas for this project include time-series modelling, data preprocessing, model evaluation, backend/API development, dashboard implementation, Gemma tool integration, embedded telemetry and system integration.
