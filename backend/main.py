"""GRIDTWIN-24 REST API.

Thin FastAPI wrapper around the existing deterministic gridtwin functions. It
does not re-implement any model logic: it imports and calls
``gridtwin.forecasting``, ``gridtwin.dispatch`` and ``gridtwin.battery`` and
serialises their output to JSON for the React frontend.

The next-day forecast is expensive (it trains a model), so it is computed once
per dataset and cached in-process. Scenario endpoints are cheap and run on
each request.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path
from threading import Lock
from typing import Any

import numpy as np
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gridtwin.data import load_hourly_series  # noqa: E402
from gridtwin.forecasting import fit_evaluate_forecast  # noqa: E402
from gridtwin.dispatch import schedule_flexible_loads  # noqa: E402
from gridtwin.battery import optimise_battery_dispatch, make_demo_site_profile  # noqa: E402
from gridtwin.demo_data import make_synthetic_load  # noqa: E402

app = FastAPI(title="GRIDTWIN-24 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# In-process forecast cache. Key = short signature of the series so an upload
# recomputes but repeated requests for the same data are instant.
# ---------------------------------------------------------------------------
_CACHE: dict[str, dict[str, Any]] = {}
_LOCK = Lock()


def _series_signature(series: pd.Series) -> str:
    return f"{len(series)}:{float(series.iloc[0]):.4f}:{float(series.iloc[-1]):.4f}:{series.index[-1].isoformat()}"


def _build_forecast_payload(series: pd.Series, source_label: str, synthetic: bool) -> dict[str, Any]:
    result = fit_evaluate_forecast(series)

    history = series.iloc[-168:]
    history_points = [
        {"timestamp": ts.isoformat(), "demand": round(float(v), 3)}
        for ts, v in history.items()
    ]
    forecast_points = [
        {
            "timestamp": pd.Timestamp(r.timestamp).isoformat(),
            "forecast": round(float(r.forecast), 3),
            "lower": None if pd.isna(r.lower) else round(float(r.lower), 3),
            "upper": None if pd.isna(r.upper) else round(float(r.upper), 3),
            "peak_flag": bool(r.peak_flag),
        }
        for r in result.forecast.itertuples()
    ]
    validation_points = [
        {
            "timestamp": pd.Timestamp(r.timestamp).isoformat(),
            "actual": round(float(r.actual), 3),
            "model_forecast": round(float(r.model_forecast), 3),
            "seasonal_naive": round(float(r.seasonal_naive), 3),
        }
        for r in result.validation.tail(24 * 7).itertuples()
    ]
    feature_importance = [
        {
            "feature": str(r.feature),
            "mae_increase": round(float(r.mae_increase), 5),
            "std": round(float(r.std), 5),
        }
        for r in result.feature_importance.head(10).itertuples()
    ]

    model_mae = float(result.metrics["model"]["mae"])
    naive_mae = float(result.metrics["seasonal_naive"]["mae"])
    improvement = (naive_mae - model_mae) / naive_mae * 100 if naive_mae else 0.0

    return {
        "source_label": source_label,
        "synthetic": synthetic,
        "observations": int(len(series)),
        "history": history_points,
        "forecast": forecast_points,
        "validation": validation_points,
        "feature_importance": feature_importance,
        "metrics": result.metrics,
        "summary": {
            "model_mae": round(model_mae, 3),
            "naive_mae": round(naive_mae, 3),
            "improvement_pct": round(improvement, 1),
            "peak_hours": int(sum(1 for p in forecast_points if p["peak_flag"])),
            "peak_threshold": round(float(result.metrics["peak_threshold_training_p90"]), 3),
            "interval_calibrated": bool(result.interval_calibrated),
            "validation_start": result.metrics["validation_start"],
            "validation_end": result.metrics["validation_end"],
        },
    }


def _get_cached_forecast(series: pd.Series, source_label: str, synthetic: bool) -> dict[str, Any]:
    sig = _series_signature(series)
    with _LOCK:
        if sig not in _CACHE:
            _CACHE[sig] = _build_forecast_payload(series, source_label, synthetic)
        return _CACHE[sig]


def _demo_series() -> pd.Series:
    df = make_synthetic_load(days=90)
    tmp = ROOT / "outputs" / "api_synthetic.csv"
    tmp.parent.mkdir(exist_ok=True)
    df.to_csv(tmp, index=False)
    return load_hourly_series(tmp)


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------
class FlexTask(BaseModel):
    name: str
    power_kw: float = Field(gt=0)
    duration_hours: int = Field(ge=1, le=24)
    earliest_start: int = Field(ge=0, le=23)
    latest_start: int = Field(ge=0, le=23)


class LoadShiftRequest(BaseModel):
    base_load_kw: float = Field(default=1.2, gt=0)
    capacity_kw: float = Field(default=2.0, gt=0)
    offpeak_tariff: float = Field(default=3.0, ge=0)
    peak_tariff: float = Field(default=7.0, ge=0)
    tasks: list[FlexTask] | None = None


class BatteryRequest(BaseModel):
    battery_capacity_kwh: float = Field(default=8.0, gt=0)
    max_power_kw: float = Field(default=2.0, gt=0)
    demand_charge_per_kw: float = Field(default=0.0, ge=0)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "gridtwin-24", "version": app.version}


@app.get("/api/forecast")
def get_forecast() -> dict[str, Any]:
    """Return the cached next-day forecast for the synthetic demo dataset."""
    try:
        series = _demo_series()
        return _get_cached_forecast(series, "Synthetic demo dataset (90 days)", synthetic=True)
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Forecast failed: {exc}") from exc


@app.post("/api/forecast/upload")
async def upload_forecast(
    file: UploadFile = File(...),
    timestamp_col: str = "timestamp",
    demand_col: str = "demand",
    timezone: str = "Asia/Kolkata",
) -> dict[str, Any]:
    """Train and evaluate on an uploaded hourly demand CSV."""
    try:
        raw = await file.read()
        df = pd.read_csv(io.BytesIO(raw))
        tmp = ROOT / "outputs" / "api_uploaded.csv"
        tmp.parent.mkdir(exist_ok=True)
        df.to_csv(tmp, index=False)
        series = load_hourly_series(tmp, timestamp_col, demand_col, timezone=timezone or None)
        return _get_cached_forecast(series, f"Uploaded: {file.filename}", synthetic=False)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not process upload: {exc}") from exc


@app.post("/api/load-shift")
def run_load_shift(req: LoadShiftRequest) -> dict[str, Any]:
    profile = [req.base_load_kw + (0.6 if 17 <= h <= 21 else 0.0) for h in range(24)]
    tariff = [
        req.offpeak_tariff if h < 7 or h >= 23
        else req.peak_tariff if 17 <= h <= 21
        else (req.offpeak_tariff + req.peak_tariff) / 2
        for h in range(24)
    ]
    if req.tasks:
        tasks = [t.model_dump() for t in req.tasks]
    else:
        tasks = [
            {"name": "EV / battery charging", "power_kw": 0.7, "duration_hours": 2, "earliest_start": 0, "latest_start": 22},
            {"name": "Water pump", "power_kw": 0.3, "duration_hours": 1, "earliest_start": 6, "latest_start": 20},
        ]
    try:
        return schedule_flexible_loads(profile, tariff, tasks, capacity_kw=req.capacity_kw)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Load-shift scenario failed: {exc}") from exc


@app.post("/api/battery")
def run_battery(req: BatteryRequest) -> dict[str, Any]:
    profile = make_demo_site_profile()
    try:
        result = optimise_battery_dispatch(
            profile["load_kw"], profile["pv_kw"], profile["import_tariff"],
            battery_capacity_kwh=req.battery_capacity_kwh,
            max_charge_kw=req.max_power_kw,
            max_discharge_kw=req.max_power_kw,
            initial_soc_fraction=0.50, min_soc_fraction=0.10, max_soc_fraction=0.95,
            charge_efficiency=0.95, discharge_efficiency=0.95,
            degradation_cost_per_kwh=0.05, demand_charge_per_kw=req.demand_charge_per_kw,
        )
        result["pv_kw"] = [round(float(v), 4) for v in profile["pv_kw"]]
        result["load_kw"] = [round(float(v), 4) for v in profile["load_kw"]]
        result["import_tariff"] = [round(float(v), 4) for v in profile["import_tariff"]]
        return result
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Battery optimisation failed: {exc}") from exc
