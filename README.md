# GRIDTWIN-24

**Forecast-to-Physics Energy Intelligence**  
*Tomorrow's demand. Today's decisions.*

GRIDTWIN-24 is an open-source prototype that takes the Hacktoberfest Hack Day Lucknow **Tomorrow's Load** problem beyond a forecast chart. It combines:

1. **A 24-hour demand forecaster** configured to train and evaluate on the organiser-provided hourly demand dataset once that data is available.
2. **An uncertainty-aware operator view** with peak-hour flags, interpretable features and a strict rolling-origin evaluation protocol.
3. **A local energy scenario engine** with flexible-load scheduling and a constrained PV + battery dispatch optimiser (linear programming with explicit SOC, efficiency, power, tariff and optional demand-charge limits).
4. **A low-voltage hardware-in-the-loop (HIL) DC energy bench** designed to measure and switch three DC loads, allowing the telemetry and dispatch path to be validated physically after safe assembly.
5. **A Gemma 4 energy-operator agent** that calls deterministic forecasting, scenario and telemetry tools; the model does not invent forecasts or directly bypass hardware interlocks.

> **Scope honesty:** The organisers' dataset is not included in this repository. `data/synthetic_hourly_load.csv` is synthetic smoke-test data only. No model result, forecast accuracy, energy saving or hardware measurement in this repository should be represented as a result from the organisers' dataset or a real customer site.

## Why this is the selected track

The official brief for **Tomorrow's Load** asks for an hourly 24-hour-ahead grid-demand forecast using past demand and related data, a chart/dashboard comparing forecast with actual demand, and lists forecast ranges, peak/spike flags and driver explanations as bonus ideas. GRIDTWIN-24 preserves that required core and adds a clearly separated energy-management demonstrator.

The extra product layer is deliberately bounded: the challenge dataset forecasts the target grid series; the optional local-site energy scenario uses its own site profile, constraints, tariff and hardware telemetry. Do not silently treat a system-level forecast as an individual building's load profile.

## Quick start

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
source .venv/bin/activate
pip install -r requirements.txt
python scripts/generate_demo_data.py
python scripts/run_demo.py
pytest -q
```

The smoke test writes `outputs/demo_forecast.csv`, `outputs/demo_validation_forecast_vs_actual.csv`, `outputs/demo_feature_importance.csv`, `outputs/demo_metrics.json`, `outputs/demo_dispatch_scenario.json` and `outputs/demo_pv_battery_scenario.json`. All demo profiles are synthetic.

### Enable the optional Gemma 4 operator agent

Copy `.env.example` values into your shell environment or set `GEMINI_API_KEY` before launching Streamlit. The default API model is `gemma-4-26b-a4b-it`; change `GEMMA_MODEL` only to a model currently enabled for your account. The code manually validates every returned function call against an allow-list in `ToolContext`. The agent has no hardware-write function.

```bash
# macOS / Linux
export GEMINI_API_KEY="your-key"
export GEMMA_MODEL="gemma-4-26b-a4b-it"
```

### Launch the interactive dashboard

```bash
streamlit run streamlit_app.py
```

Upload a CSV with at least two columns: timestamp and demand. The app lets you map the columns and set the assumed timezone for naive timestamps; verify it against the dataset documentation. A timezone offset in the data takes precedence. For the command line, use canonical `timestamp,demand` columns. Hourly observations are expected. Short internal gaps of up to two hours are interpolated. Longer or boundary gaps are rejected; dropping them would corrupt hourly lag features.

## Train on the hackathon dataset

1. Inspect the supplied file and its data dictionary before modelling.
2. Identify the actual timestamp, target demand, units, time zone, missing-data conventions and any related features.
3. Map the timestamp and demand columns into the canonical CSV schema. Add a covariate only if it is available at forecast issuance time. For example, realised future weather is leakage; a weather forecast issued at the origin may be a valid exogenous input.
4. Run the model and compare it with the seasonal-naive benchmark.
5. Use rolling-origin 24-hour evaluation. Keep complete forecast windows separate from training. Never randomly split hourly rows for the final performance claim.
6. Report MAE, RMSE, WAPE and peak recall / precision using a threshold fixed from training data. Show baseline results beside model results. Include the exact evaluation dates and target units.
7. Only display an empirical prediction band when the residual-calibration sample is large enough. Report observed coverage; do not call it a guaranteed interval.

The included forecasting pipeline is a defensible starter benchmark, not a claim that gradient boosting is optimal. The empirical interval diagnostic reports coverage on a disjoint later slice of rolling-origin residuals; this remains a sample diagnostic, not a guarantee of future coverage. If the supplied data supports it, test seasonal models, CatBoost/LightGBM, linear models and specialised probabilistic methods under the same rolling-origin protocol.

## Hardware: safe prototype boundary

The included electronics design is a **12 V DC-only tabletop energy bench**. It is not connected to building wiring or the public grid. The planned ESP32 rig reads an INA3221 current/voltage monitor and switches three small DC loads through appropriately rated MOSFET driver modules. The firmware is supplied, but the hardware has not been assembled or independently safety-tested. Every branch must have an inline fuse. An emergency stop physically interrupts the 12 V load supply. A separate physical ARM switch is wired in series with the gate-drive signals and sensed by the ESP32. External MOSFET gate-to-source pulldowns are required so outputs stay OFF during reset. Wi-Fi/MQTT loss causes the firmware to fail OFF; E-stop physically interrupts the 12 V load bus.

Do not connect the prototype to AC mains, distribution boards, utility meters or real building loads. The tabletop setup is an energy bench, not a complete microgrid or grid controller. A commercial installation requires certified metering/contactor hardware, protection coordination, electrician-led installation, regulatory review and independent safety testing.

### Optional human-operated bench console

After configuring the MQTT broker and flashing the bench firmware, set the `MQTT_*` environment variables and run `python scripts/rig_console.py`. The console requires explicit typed confirmation and waits for a new telemetry packet to verify the channel state. A successful MQTT publish is not proof of a physical switch action. The ESP32 interlocks and physical E-stop remain mandatory.

## Gemma 4 integration

Gemma 4 is the natural-language operator interface. It can call a narrow allow-list of functions such as `get_forecast`, `get_peak_windows`, `run_load_shift_scenario` and `get_live_telemetry`. The forecast, optimisation and arithmetic remain deterministic Python functions. Hardware commands require both a user confirmation and a physical interlock; the LLM has no direct GPIO access.

The official Gemma documentation describes native function calling and multimodal capabilities. Model availability, hardware requirements and API endpoint names can change; verify the current model card before deployment. See `docs/06_agent_and_gemma.md`.

## Product thesis

Start with **campuses, hostels, apartment complexes, clinics, co-working spaces and small commercial facilities** that have repeated energy bills, a facilities owner and a reason to monitor peaks. Provide a software-only pilot from historical interval data first; add the gateway only after proving that the forecast and operational reports are valuable. A consumer/home edition can follow, but it should not be the first go-to-market motion.

Revenue hypotheses:
- Per-site SaaS subscription for forecasting, alerts, reports and scenario planning.
- One-time installation / gateway revenue after a paid pilot validates hardware need.
- Multi-site reporting for facility operators and energy-service companies.
- Open-source community edition, with paid hosted collaboration, fleet monitoring and support.

No savings claim should be made until a site pilot measures a baseline, records interventions and compares actual outcomes under a credible methodology.

## Repository map

```text
GRIDTWIN24_Project_Pack/
├── README.md
├── requirements.txt / pyproject.toml / .env.example
├── config/                  # dataset mapping template
├── data/                    # synthetic demo fixture only
├── src/gridtwin/             # ingestion, forecasting, scheduling, Gemma function-calling
├── scripts/                  # generate and run reproducible demo
├── tests/                    # automated smoke tests
├── streamlit_app.py          # interactive upload + forecast demo
├── firmware/esp32/           # telemetry and guarded DC load control
├── hardware/                 # bill of materials and bench notes
├── diagrams/                 # architecture, HIL and product diagrams
├── docs/                     # product, ML, business, safety, pitch and 100-point red-team review
└── slides/GRIDTWIN24_pitch.pptx
```

## Sources and acknowledgement

See `docs/12_references.md` for official event, Gemma, sensor and technical background links. The project name is a working name; complete a trademark/domain check before commercial launch.
