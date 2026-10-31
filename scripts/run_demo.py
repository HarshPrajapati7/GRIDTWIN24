from pathlib import Path
import sys, json
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from gridtwin.data import load_hourly_series
from gridtwin.forecasting import fit_evaluate_forecast
from gridtwin.dispatch import schedule_flexible_loads
from gridtwin.battery import optimise_battery_dispatch, make_demo_site_profile

root = Path(__file__).resolve().parents[1]
series = load_hourly_series(root / "data" / "synthetic_hourly_load.csv")
result = fit_evaluate_forecast(series)
result.forecast.to_csv(root / "outputs" / "demo_forecast.csv", index=False)
result.validation.to_csv(root / "outputs" / "demo_validation_forecast_vs_actual.csv", index=False)
result.feature_importance.to_csv(root / "outputs" / "demo_feature_importance.csv", index=False)
(root / "outputs" / "demo_metrics.json").write_text(json.dumps(result.metrics, indent=2))
# Illustrative site-level scenario separate from the organiser grid-load series.
base = [1.0 + 0.5 * (i in range(17, 22)) + 0.2 * (i in range(8, 10)) for i in range(24)]
tariff = [5.0 if 17 <= i <= 22 else 3.0 if 0 <= i <= 6 else 4.0 for i in range(24)]
scenario = schedule_flexible_loads(base, tariff, [
    {"name": "EV charging demo", "power_kw": 0.8, "duration_hours": 2, "earliest_start": 0, "latest_start": 22, "baseline_start": 18},
    {"name": "Water pump demo", "power_kw": 0.35, "duration_hours": 1, "earliest_start": 6, "latest_start": 20, "baseline_start": 17},
], capacity_kw=2.0)
(root / "outputs" / "demo_dispatch_scenario.json").write_text(json.dumps(scenario, indent=2))
profile = make_demo_site_profile()
battery_scenario = optimise_battery_dispatch(
    **profile,
    battery_capacity_kwh=8.0,
    max_charge_kw=2.0,
    max_discharge_kw=2.0,
    initial_soc_fraction=0.50,
    min_soc_fraction=0.10,
    max_soc_fraction=0.95,
    charge_efficiency=0.95,
    discharge_efficiency=0.95,
    degradation_cost_per_kwh=0.05,
    demand_charge_per_kw=20.0,
)
(root / "outputs" / "demo_pv_battery_scenario.json").write_text(json.dumps(battery_scenario, indent=2))
print("FORECAST METRICS — SYNTHETIC SMOKE TEST ONLY")
print(json.dumps(result.metrics, indent=2))
print("\nNEXT 24 HOURS")
print(result.forecast.to_string(index=False))
print("\nFLEXIBLE-LOAD SCENARIO — SYNTHETIC SITE PROFILE")
print(json.dumps(scenario, indent=2))
print("\nPV + BATTERY SCENARIO — SYNTHETIC SITE PROFILE")
print(json.dumps({k: v for k, v in battery_scenario.items() if k not in {"optimised_grid_import_kw", "baseline_grid_import_kw", "grid_export_kw", "battery_charge_kw", "battery_discharge_kw", "battery_soc_kwh"}}, indent=2))
