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

# ---------------------------------------------------------------------------
# Presentation layer only. Every numeric result below comes from the same
# deterministic functions used by scripts/run_demo.py and the test suite.
# No value on this page is hand-typed or faked.
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
      .block-container {padding-top: 2.2rem; padding-bottom: 2rem;}
      .gt-hero {background: linear-gradient(120deg,#161B26 0%,#1E2A3A 60%,#2A1E0E 100%);
                border:1px solid #2A3345; border-radius:16px; padding:22px 26px; margin-bottom:10px;}
      .gt-hero h1 {margin:0; font-size:2.15rem; letter-spacing:-0.5px; color:#F5F7FA;}
      .gt-hero p {margin:.3rem 0 0; color:#9AA6B8; font-size:1.02rem;}
      .gt-badge {display:inline-block; background:#1F2937; color:#F59E0B; border:1px solid #F59E0B55;
                 padding:3px 10px; border-radius:999px; font-size:.72rem; margin-right:6px; font-weight:600;}
      .gt-badge.ok {color:#34D399; border-color:#34D39955;}
      div[data-testid="stMetric"] {background:#161B26; border:1px solid #232B3A; border-radius:12px; padding:12px 14px;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="gt-hero">
      <h1>⚡ GRIDTWIN-24</h1>
      <p>Forecast-to-Physics Energy Intelligence &nbsp;·&nbsp; Tomorrow's demand, today's decisions.</p>
      <div style="margin-top:12px">
        <span class="gt-badge">Problem 02 · Tomorrow's Load</span>
        <span class="gt-badge ok">Deterministic ML</span>
        <span class="gt-badge ok">Rolling-origin eval</span>
        <span class="gt-badge ok">LP battery dispatch</span>
        <span class="gt-badge">Gemma 4 copilot</span>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar: dataset selection / mapping
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("1 · Data")
    uploaded = st.file_uploader("Upload hourly demand CSV", type=["csv"])
    st.caption("At least `timestamp` and `demand` columns.")
    st.divider()
    st.subheader("Column mapping")
    default_ts = st.text_input("Timestamp column", "timestamp")
    default_y = st.text_input("Demand column", "demand")
    source_timezone = st.text_input(
        "Timezone for naive timestamps", "Asia/Kolkata",
        help="Used only if the CSV timestamps have no timezone. Verify against the dataset docs.",
    )
    use_demo = st.checkbox("Use synthetic demo dataset", value=uploaded is None)
    st.divider()
    st.caption(
        "⚠️ The demo dataset is **synthetic** smoke-test data. Upload the "
        "organiser's real CSV before reporting any accuracy result."
    )

if uploaded is not None:
    tmp = ROOT / "outputs" / "uploaded_dataset_temp.csv"
    tmp.parent.mkdir(exist_ok=True)
    tmp.write_bytes(uploaded.getvalue())
    data_path = tmp
    data_label = f"Uploaded: {uploaded.name}"
    is_synthetic = False
elif use_demo:
    df_demo = make_synthetic_load(days=90)
    data_path = ROOT / "outputs" / "synthetic_for_app.csv"
    data_path.parent.mkdir(exist_ok=True)
    df_demo.to_csv(data_path, index=False)
    data_label = "Synthetic demo dataset (90 days)"
    is_synthetic = True
else:
    st.warning("Upload a CSV or tick **Use synthetic demo dataset** in the sidebar to begin.")
    st.stop()

if is_synthetic:
    st.warning(
        "Showing results for the **synthetic demo dataset**. These numbers are a "
        "software smoke test, not a real grid or customer result.",
        icon="🧪",
    )
else:
    st.success(f"Loaded **{data_label}**. Results below are computed live from this file.", icon="✅")

try:
    series = load_hourly_series(data_path, default_ts, default_y, timezone=source_timezone.strip() or None)
    with st.spinner("Training and evaluating the 24-hour model on this dataset..."):
        result = fit_evaluate_forecast(series)
except Exception as exc:
    st.error(f"Could not build forecast: {exc}")
    st.stop()

# ---------------------------------------------------------------------------
# Headline metrics (live, from the trained model)
# ---------------------------------------------------------------------------
peak_rows = result.forecast[result.forecast["peak_flag"]]
model_mae = result.metrics["model"]["mae"]
naive_mae = result.metrics["seasonal_naive"]["mae"]
improvement = (naive_mae - model_mae) / naive_mae * 100 if naive_mae else 0.0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Observations", f"{len(series):,}")
c2.metric("Model MAE", f"{model_mae:.2f}")
c3.metric("Baseline MAE", f"{naive_mae:.2f}")
c4.metric("Beats baseline by", f"{improvement:.0f}%")
c5.metric("Peak hours flagged", str(len(peak_rows)))

tab_forecast, tab_eval, tab_shift, tab_battery, tab_copilot = st.tabs(
    ["📈 Forecast", "🎯 Evaluation", "🔀 Load-Shift", "🔋 Battery Lab", "🤖 Gemma Copilot"]
)

# ---------------------------------------------------------------------------
# TAB 1 — Next 24 hours
# ---------------------------------------------------------------------------
with tab_forecast:
    st.subheader("Next 24 hours")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=series.index[-168:], y=series.iloc[-168:], name="Observed history", mode="lines", line=dict(color="#60A5FA")))
    fig.add_trace(go.Scatter(x=result.forecast.timestamp, y=result.forecast.forecast, name="24h forecast", mode="lines+markers", line=dict(color="#34D399")))
    if not peak_rows.empty:
        fig.add_trace(go.Scatter(x=peak_rows.timestamp, y=peak_rows.forecast, name="Peak flag (training P90)", mode="markers", marker=dict(size=11, symbol="diamond", color="#F59E0B")))
    if result.interval_calibrated:
        fig.add_trace(go.Scatter(x=result.forecast.timestamp, y=result.forecast.upper, name="Upper empirical band", mode="lines", line=dict(width=0), showlegend=False))
        fig.add_trace(go.Scatter(x=result.forecast.timestamp, y=result.forecast.lower, name="Empirical interval", mode="lines", fill="tonexty", line=dict(width=0), fillcolor="rgba(52,211,153,0.15)"))
    fig.update_layout(height=460, xaxis_title="Time (UTC)", yaxis_title="Demand (dataset units)", legend_orientation="h", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)

    if not peak_rows.empty:
        st.warning(f"{len(peak_rows)} forecast hours exceed the training-period 90th-percentile threshold ({result.metrics['peak_threshold_training_p90']:.2f} dataset units). This is a statistical flag, not a grid alert.")

    st.download_button("⬇️ Download next-day forecast CSV", result.forecast.to_csv(index=False), "gridtwin_next_24h.csv", "text/csv")

# ---------------------------------------------------------------------------
# TAB 2 — Evaluation
# ---------------------------------------------------------------------------
with tab_eval:
    st.subheader("Rolling-origin evaluation: forecast vs actual")
    validation_view = result.validation.tail(24 * 7)
    validation_fig = go.Figure()
    validation_fig.add_trace(go.Scatter(x=validation_view["timestamp"], y=validation_view["actual"], name="Actual demand", mode="lines", line=dict(color="#E6EAF1")))
    validation_fig.add_trace(go.Scatter(x=validation_view["timestamp"], y=validation_view["model_forecast"], name="GRIDTWIN forecast", mode="lines", line=dict(color="#34D399")))
    validation_fig.add_trace(go.Scatter(x=validation_view["timestamp"], y=validation_view["seasonal_naive"], name="Seasonal-naive", mode="lines", line=dict(dash="dot", color="#9AA6B8")))
    validation_fig.update_layout(height=400, xaxis_title="Validation timestamp", yaxis_title="Demand (dataset units)", legend_orientation="h", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(validation_fig, use_container_width=True)

    st.subheader("Metrics — model vs baseline")
    metrics_df = pd.DataFrame([result.metrics["model"], result.metrics["seasonal_naive"]], index=["GRIDTWIN model", "Seasonal-naive baseline"])
    st.dataframe(metrics_df, use_container_width=True)
    st.caption(f"Validation period: {result.metrics['validation_start']} to {result.metrics['validation_end']}. Interval: {result.metrics['interval_method']}.")
    if result.interval_calibrated:
        coverage = result.metrics.get("interval_validation_coverage")
        if coverage is not None:
            st.caption(f"Disjoint residual-slice interval coverage check: {coverage:.1%} on {result.metrics.get('interval_validation_samples', 0)} points. Empirical diagnostic, not a guarantee of future coverage.")

    if not result.feature_importance.empty:
        st.subheader("Forecast drivers — global permutation importance")
        fi = result.feature_importance.head(10).sort_values("mae_increase", ascending=True)
        fi_fig = go.Figure(go.Bar(x=fi["mae_increase"], y=fi["feature"], orientation="h", marker=dict(color="#F59E0B"), error_x=dict(type="data", array=fi["std"])))
        fi_fig.update_layout(height=380, xaxis_title="Increase in held-out MAE when shuffled", yaxis_title="Feature", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fi_fig, use_container_width=True)
        st.caption("Global predictive importance on held-out supervised rows; not a causal explanation for an individual forecast hour.")

# ---------------------------------------------------------------------------
# TAB 3 — Load-shift scenario
# ---------------------------------------------------------------------------
with tab_shift:
    st.subheader("Local-site load-shift scenario")
    st.caption("Separate from the grid dataset. Illustrative site scenario only — enter your own local profile, tariff and flexible loads before using operationally.")
    base = st.number_input("Illustrative base load (kW)", 0.2, 100.0, 1.2, 0.1)
    peak = st.number_input("Peak capacity limit (kW)", 0.2, 100.0, 2.0, 0.1)
    cheap_rate = st.number_input("Off-peak tariff (per kWh)", 0.0, 100.0, 3.0, 0.1)
    peak_rate = st.number_input("Peak tariff (per kWh)", 0.0, 100.0, 7.0, 0.1)
    if st.button("Run illustrative flexible-load scenario", type="primary"):
        profile = [base + (0.6 if 17 <= h <= 21 else 0.0) for h in range(24)]
        tariff = [cheap_rate if h < 7 or h >= 23 else peak_rate if 17 <= h <= 21 else (cheap_rate + peak_rate) / 2 for h in range(24)]
        scenario = schedule_flexible_loads(profile, tariff, [
            {"name": "EV / battery charging", "power_kw": 0.7, "duration_hours": 2, "earliest_start": 0, "latest_start": 22},
            {"name": "Water pump", "power_kw": 0.3, "duration_hours": 1, "earliest_start": 6, "latest_start": 20},
        ], capacity_kw=peak)
        s1, s2 = st.columns(2)
        s1.metric("Scenario energy cost", f"{scenario['scheduled_cost']:.2f}")
        s2.metric("Estimated change vs baseline", f"{scenario['estimated_cost_difference']:.2f}")
        shift_fig = go.Figure()
        shift_fig.add_trace(go.Bar(x=list(range(24)), y=scenario["baseline_load_with_earliest_tasks_kw"], name="Baseline load", marker=dict(color="#9AA6B8")))
        shift_fig.add_trace(go.Bar(x=list(range(24)), y=scenario["scheduled_load_kw"], name="Shifted load", marker=dict(color="#34D399")))
        shift_fig.update_layout(height=320, barmode="overlay", xaxis_title="Hour of day", yaxis_title="Power (kW)", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_orientation="h")
        shift_fig.update_traces(opacity=0.75)
        st.plotly_chart(shift_fig, use_container_width=True)
        with st.expander("Full scenario JSON"):
            st.json(scenario)
        st.warning(scenario["note"])

# ---------------------------------------------------------------------------
# TAB 4 — PV + battery dispatch lab
# ---------------------------------------------------------------------------
hours = np.arange(24)
site_profile = make_demo_site_profile()
site_load = np.asarray(site_profile["load_kw"], dtype=float)
site_pv = np.asarray(site_profile["pv_kw"], dtype=float)
site_tariff = np.asarray(site_profile["import_tariff"], dtype=float)

with tab_battery:
    st.subheader("PV + battery dispatch lab")
    st.caption("Separate local-site scenario with synthetic 24-hour load / PV / tariff profiles. Does not use the organiser's grid-demand series and does not control a real battery.")
    b1, b2, b3 = st.columns(3)
    battery_capacity = b1.number_input("Battery capacity (kWh)", 1.0, 30.0, 8.0, 1.0)
    battery_power = b2.number_input("Charge/discharge limit (kW)", 0.5, 10.0, 2.0, 0.5)
    demand_charge = b3.number_input("Daily peak charge (per kW)", 0.0, 1000.0, 0.0, 10.0)
    if st.button("Optimise local PV + battery scenario", type="primary"):
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
            dispatch_fig.add_trace(go.Scatter(x=hours, y=battery_result["baseline_grid_import_kw"], name="Grid import — no battery", line=dict(color="#9AA6B8")))
            dispatch_fig.add_trace(go.Scatter(x=hours, y=battery_result["optimised_grid_import_kw"], name="Grid import — optimised", line=dict(color="#34D399")))
            dispatch_fig.add_trace(go.Scatter(x=hours, y=site_pv, name="PV generation", line=dict(dash="dot", color="#F59E0B")))
            dispatch_fig.update_layout(height=350, xaxis_title="Hour of day", yaxis_title="Power (kW)", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", legend_orientation="h")
            st.plotly_chart(dispatch_fig, use_container_width=True)
            soc_fig = go.Figure()
            soc_fig.add_trace(go.Scatter(x=list(range(25)), y=battery_result["battery_soc_kwh"], name="Battery state of charge (kWh)", fill="tozeroy", line=dict(color="#60A5FA")))
            soc_fig.update_layout(height=260, xaxis_title="Hour boundary", yaxis_title="Stored energy (kWh)", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(soc_fig, use_container_width=True)
            with st.expander("Full scenario JSON"):
                st.json({k: v for k, v in battery_result.items() if k not in {"optimised_grid_import_kw", "baseline_grid_import_kw", "grid_export_kw", "battery_charge_kw", "battery_discharge_kw", "battery_soc_kwh"}})
            st.warning(battery_result["note"])
        except Exception as exc:
            st.error(f"Battery optimisation failed: {exc}")

# ---------------------------------------------------------------------------
# TAB 5 — Gemma copilot
# ---------------------------------------------------------------------------
with tab_copilot:
    st.subheader("Gemma 4 energy-operator copilot")
    st.caption("Gemma 4 can query the deterministic forecast and run the configured PV/battery scenario. It cannot directly operate hardware.")
    if not os.getenv("GEMINI_API_KEY"):
        st.info("Set `GEMINI_API_KEY` in your environment and restart Streamlit to enable the optional Gemma 4 agent. The forecasting application works without it.")
    question = st.text_input("Ask about the forecast or a load-shift scenario", placeholder="Which hours are expected to be the peak tomorrow?")
    if st.button("Ask Gemma 4", type="primary", disabled=not bool(os.getenv("GEMINI_API_KEY")) or not question.strip()):
        try:
            context = ToolContext(
                forecast=result.forecast,
                battery_scenario={
                    **site_profile,
                    "battery_capacity_kwh": 8.0,
                    "max_charge_kw": 2.0,
                    "max_discharge_kw": 2.0,
                    "initial_soc_fraction": 0.50,
                    "min_soc_fraction": 0.10,
                    "max_soc_fraction": 0.95,
                    "charge_efficiency": 0.95,
                    "discharge_efficiency": 0.95,
                    "degradation_cost_per_kwh": 0.05,
                    "demand_charge_per_kw": 0.0,
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

st.divider()
st.caption("GRIDTWIN-24 · All metrics on this page are computed live by the deterministic pipeline in `src/gridtwin/`. Synthetic demo data is labelled as such and must not be reported as a real result.")
