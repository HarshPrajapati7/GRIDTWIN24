from pathlib import Path
import sys
import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from gridtwin.data import load_hourly_series
from gridtwin.forecasting import fit_evaluate_forecast
from gridtwin.dispatch import schedule_flexible_loads
from gridtwin.demo_data import make_synthetic_load
from gridtwin.gemma_tools import ToolContext
from gridtwin.gemma_agent import ask_gemma
from gridtwin.battery import optimise_battery_dispatch, make_demo_site_profile

st.set_page_config(page_title="GRIDTWIN-24", page_icon="⚡", layout="wide")
st.title("GRIDTWIN-24")
st.caption("Forecast-to-Physics Energy Intelligence | Tomorrow's Load")
st.info("Demo data is synthetic. Upload the organiser-provided dataset before reporting any performance result.")

uploaded = st.file_uploader("Upload hourly demand CSV", type=["csv"])
with st.sidebar:
    st.header("Dataset mapping")
    default_ts = st.text_input("Timestamp column", "timestamp")
    default_y = st.text_input("Demand column", "demand")
    source_timezone = st.text_input("Assumed timezone for naive timestamps", "Asia/Kolkata", help="Used only if the CSV timestamps have no timezone. Verify this against the dataset documentation.")
    use_demo = st.checkbox("Use synthetic demo dataset", value=uploaded is None)

if uploaded is not None:
    tmp = ROOT / "outputs" / "uploaded_dataset_temp.csv"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_bytes(uploaded.getvalue())
    data_path = tmp
elif use_demo:
    df_demo = make_synthetic_load(days=90)
    data_path = ROOT / "outputs" / "synthetic_for_app.csv"
    data_path.parent.mkdir(exist_ok=True)
    df_demo.to_csv(data_path, index=False)
else:
    st.warning("Upload a CSV or select the synthetic demo dataset.")
    st.stop()

try:
    series = load_hourly_series(data_path, default_ts, default_y, timezone=source_timezone.strip() or None)
    with st.spinner("Training and evaluating the 24-hour model..."):
        result = fit_evaluate_forecast(series)
except Exception as exc:
    st.error(f"Could not build forecast: {exc}")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Observations", f"{len(series):,}")
c2.metric("Model MAE", f"{result.metrics['model']['mae']:.2f}")
c3.metric("Seasonal baseline MAE", f"{result.metrics['seasonal_naive']['mae']:.2f}")
c4.metric("Validation origins", str(result.metrics["validation_origins"]))

st.subheader("Next 24 hours")
fig = go.Figure()
fig.add_trace(go.Scatter(x=series.index[-168:], y=series.iloc[-168:], name="Observed history", mode="lines"))
fig.add_trace(go.Scatter(x=result.forecast.timestamp, y=result.forecast.forecast, name="24h forecast", mode="lines+markers"))
peak_rows = result.forecast[result.forecast["peak_flag"]]
if not peak_rows.empty:
    fig.add_trace(go.Scatter(x=peak_rows.timestamp, y=peak_rows.forecast, name="Peak flag (training P90)", mode="markers", marker=dict(size=11, symbol="diamond", color="#F59E0B")))
if result.interval_calibrated:
    fig.add_trace(go.Scatter(x=result.forecast.timestamp, y=result.forecast.upper, name="Upper empirical band", mode="lines", line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=result.forecast.timestamp, y=result.forecast.lower, name="Empirical interval", mode="lines", fill="tonexty", line=dict(width=0)))
fig.update_layout(height=440, xaxis_title="Time (UTC)", yaxis_title="Demand (dataset units)", legend_orientation="h")
st.plotly_chart(fig, use_container_width=True)

if not peak_rows.empty:
    st.warning(f"{len(peak_rows)} forecast hours exceed the training-period 90th-percentile threshold ({result.metrics['peak_threshold_training_p90']:.2f} dataset units). This is a statistical flag, not a grid alert.")

st.subheader("Forecast evaluation")
metrics_df = pd.DataFrame([result.metrics["model"], result.metrics["seasonal_naive"]], index=["GRIDTWIN model", "Seasonal-naive baseline"])
st.dataframe(metrics_df, use_container_width=True)
st.caption(f"Validation period: {result.metrics['validation_start']} to {result.metrics['validation_end']}. Interval: {result.metrics['interval_method']}.")
if result.interval_calibrated:
    coverage = result.metrics.get("interval_validation_coverage")
    if coverage is not None:
        st.caption(f"Disjoint residual-slice interval coverage check: {coverage:.1%} on {result.metrics.get('interval_validation_samples', 0)} points. This is an empirical diagnostic, not a guarantee of future coverage.")

st.subheader("Held-out validation: forecast vs actual")
validation_view = result.validation.tail(24 * 7)
validation_fig = go.Figure()
validation_fig.add_trace(go.Scatter(x=validation_view["timestamp"], y=validation_view["actual"], name="Actual demand", mode="lines"))
validation_fig.add_trace(go.Scatter(x=validation_view["timestamp"], y=validation_view["model_forecast"], name="GRIDTWIN forecast", mode="lines"))
validation_fig.add_trace(go.Scatter(x=validation_view["timestamp"], y=validation_view["seasonal_naive"], name="Seasonal-naive", mode="lines", line=dict(dash="dot")))
validation_fig.update_layout(height=380, xaxis_title="Validation timestamp", yaxis_title="Demand (dataset units)", legend_orientation="h")
st.plotly_chart(validation_fig, use_container_width=True)

if not result.feature_importance.empty:
    st.subheader("Forecast drivers — global permutation importance")
    fi = result.feature_importance.head(10).sort_values("mae_increase", ascending=True)
    fi_fig = go.Figure(go.Bar(x=fi["mae_increase"], y=fi["feature"], orientation="h", error_x=dict(type="data", array=fi["std"])))
    fi_fig.update_layout(height=360, xaxis_title="Increase in held-out MAE when shuffled", yaxis_title="Feature")
    st.plotly_chart(fi_fig, use_container_width=True)
    st.caption("Global predictive importance on held-out supervised rows; not a causal explanation for an individual forecast hour.")
if result.interval_calibrated:
    coverage = result.metrics.get("interval_validation_coverage")
    if coverage is not None:
        st.caption(f"Disjoint residual-slice interval coverage check: {coverage:.1%} on {result.metrics.get('interval_validation_samples', 0)} points. This is an empirical diagnostic, not a guarantee of future coverage.")
st.download_button("Download next-day forecast CSV", result.forecast.to_csv(index=False), "gridtwin_next_24h.csv", "text/csv")

st.subheader("Local-site load-shift scenario (separate from the grid dataset)")
st.caption("Illustrative site scenario only. Enter your own local profile, tariff and flexible loads before using operationally.")
base = st.number_input("Illustrative base load (kW)", 0.2, 100.0, 1.2, 0.1)
peak = st.number_input("Peak capacity limit (kW)", 0.2, 100.0, 2.0, 0.1)
cheap_rate = st.number_input("Off-peak tariff (per kWh)", 0.0, 100.0, 3.0, 0.1)
peak_rate = st.number_input("Peak tariff (per kWh)", 0.0, 100.0, 7.0, 0.1)
if st.button("Run illustrative flexible-load scenario"):
    profile = [base + (0.6 if 17 <= h <= 21 else 0.0) for h in range(24)]
    tariff = [cheap_rate if h < 7 or h >= 23 else peak_rate if 17 <= h <= 21 else (cheap_rate + peak_rate) / 2 for h in range(24)]
    scenario = schedule_flexible_loads(profile, tariff, [
        {"name":"EV / battery charging", "power_kw":0.7, "duration_hours":2, "earliest_start":0, "latest_start":22},
        {"name":"Water pump", "power_kw":0.3, "duration_hours":1, "earliest_start":6, "latest_start":20},
    ], capacity_kw=peak)
    s1, s2 = st.columns(2)
    s1.metric("Scenario energy cost", f"{scenario['scheduled_cost']:.2f}")
    s2.metric("Estimated change vs baseline", f"{scenario['estimated_cost_difference']:.2f}")
    st.json(scenario)
    st.warning(scenario["note"])


st.divider()
st.subheader("PV + battery dispatch lab")
st.caption("Separate local-site scenario: synthetic 24-hour load / PV / tariff profiles. This does not use the organiser's grid-demand series and does not control a real battery.")
hours = np.arange(24)
site_profile = make_demo_site_profile()
site_load = np.asarray(site_profile["load_kw"], dtype=float)
site_pv = np.asarray(site_profile["pv_kw"], dtype=float)
site_tariff = np.asarray(site_profile["import_tariff"], dtype=float)
b1, b2, b3 = st.columns(3)
battery_capacity = b1.number_input("Battery capacity (kWh)", 1.0, 30.0, 8.0, 1.0)
battery_power = b2.number_input("Charge/discharge limit (kW)", 0.5, 10.0, 2.0, 0.5)
demand_charge = b3.number_input("Daily peak charge (per kW)", 0.0, 1000.0, 0.0, 10.0)
if st.button("Optimise local PV + battery scenario"):
    try:
        battery_result = optimise_battery_dispatch(
            site_load.tolist(), site_pv.tolist(), site_tariff.tolist(),
            battery_capacity_kwh=float(battery_capacity),
            max_charge_kw=float(battery_power),
            max_discharge_kw=float(battery_power),
            initial_soc_fraction=0.50, min_soc_fraction=0.10, max_soc_fraction=0.95,
            charge_efficiency=0.95, discharge_efficiency=0.95,
            degradation_cost_per_kwh=0.05, demand_charge_per_kw=float(demand_charge),
        )
        q1, q2, q3 = st.columns(3)
        q1.metric("Estimated bill delta", f"{battery_result['estimated_cost_difference']:.2f}")
        q2.metric("Peak import reduction", f"{battery_result['peak_reduction_kw']:.2f} kW")
        q3.metric("Optimised peak import", f"{battery_result['optimised_peak_import_kw']:.2f} kW")
        dispatch_fig = go.Figure()
        dispatch_fig.add_trace(go.Scatter(x=hours, y=battery_result["baseline_grid_import_kw"], name="Grid import — no battery"))
        dispatch_fig.add_trace(go.Scatter(x=hours, y=battery_result["optimised_grid_import_kw"], name="Grid import — optimised"))
        dispatch_fig.add_trace(go.Scatter(x=hours, y=site_pv, name="PV generation", line=dict(dash="dot")))
        dispatch_fig.update_layout(height=350, xaxis_title="Hour of day", yaxis_title="Power (kW)")
        st.plotly_chart(dispatch_fig, use_container_width=True)
        soc_fig = go.Figure()
        soc_fig.add_trace(go.Scatter(x=list(range(25)), y=battery_result["battery_soc_kwh"], name="Battery state of charge (kWh)", fill="tozeroy"))
        soc_fig.update_layout(height=260, xaxis_title="Hour boundary", yaxis_title="Stored energy (kWh)")
        st.plotly_chart(soc_fig, use_container_width=True)
        st.json({k: v for k, v in battery_result.items() if k not in {"optimised_grid_import_kw", "baseline_grid_import_kw", "grid_export_kw", "battery_charge_kw", "battery_discharge_kw", "battery_soc_kwh"}})
        st.warning(battery_result["note"])
    except Exception as exc:
        st.error(f"Battery optimisation failed: {exc}")

st.divider()
st.subheader("Gemma 4 energy-operator copilot")
st.caption("Gemma 4 can query the deterministic forecast and run the configured PV/battery scenario. It cannot directly operate hardware.")
if not os.getenv("GEMINI_API_KEY"):
    st.info("Set GEMINI_API_KEY in your environment and restart Streamlit to enable the optional Gemma 4 agent. The forecasting application works without it.")
question = st.text_input("Ask about the forecast or a load-shift scenario", placeholder="Which hours are expected to be the peak tomorrow?")
if st.button("Ask Gemma 4", disabled=not bool(os.getenv("GEMINI_API_KEY")) or not question.strip()):
    try:
        context = ToolContext(
            forecast=result.forecast,
            battery_scenario={
                **site_profile,
                "battery_capacity_kwh": float(battery_capacity),
                "max_charge_kw": float(battery_power),
                "max_discharge_kw": float(battery_power),
                "initial_soc_fraction": 0.50,
                "min_soc_fraction": 0.10,
                "max_soc_fraction": 0.95,
                "charge_efficiency": 0.95,
                "discharge_efficiency": 0.95,
                "degradation_cost_per_kwh": 0.05,
                "demand_charge_per_kw": float(demand_charge),
            },
        )
        with st.spinner("Gemma 4 is querying the forecast tools..."):
            answer = ask_gemma(question, context)
        st.markdown(answer["text"])
        if answer.get("tool_calls"):
            with st.expander("Tool-call audit trace"):
                st.json(answer["tool_calls"])
    except Exception as exc:
        st.error(f"Gemma request failed: {exc}")

