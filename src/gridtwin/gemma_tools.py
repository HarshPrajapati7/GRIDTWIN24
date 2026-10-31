"""Allow-listed, deterministic tools for a Gemma 4 operator agent.

The module contains no GPIO or hardware-write function. It is safe by design:
Gemma may inspect forecasts, inspect cached telemetry and run a scenario, but
cannot directly switch a load. A separately authenticated backend workflow
must request human approval and pass hardware interlocks.
"""
from __future__ import annotations
from typing import Any
import pandas as pd
from .dispatch import schedule_flexible_loads
from .battery import optimise_battery_dispatch

TOOL_DECLARATIONS = [
    {
        "name": "get_next_day_forecast",
        "description": "Return the stored 24-hour demand forecast. Do not invent or modify numeric values.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_peak_windows",
        "description": "Return forecast hours above the specified preconfigured threshold percentile.",
        "parameters": {"type": "object", "properties": {"percentile": {"type": "number", "minimum": 50, "maximum": 99}}, "required": ["percentile"]},
    },
    {
        "name": "run_load_shift_scenario",
        "description": "Run a deterministic local-site load-shifting scenario. This is simulation only and does not operate hardware.",
        "parameters": {
            "type": "object",
            "properties": {
                "base_load_kw": {"type": "array", "items": {"type": "number"}, "minItems": 24, "maxItems": 24},
                "tariff_per_kwh": {"type": "array", "items": {"type": "number"}, "minItems": 24, "maxItems": 24},
                "tasks": {"type": "array", "items": {"type": "object"}},
                "capacity_kw": {"type": "number", "minimum": 0},
            },
            "required": ["base_load_kw", "tariff_per_kwh", "tasks"],
        },
    },
    {
        "name": "run_pv_battery_scenario",
        "description": "Run the preconfigured local-site PV and battery optimisation scenario. Simulation only; does not control a physical battery.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_live_rig_telemetry",
        "description": "Read the most recent cached low-voltage demonstrator telemetry. Read-only.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
]


class ToolContext:
    def __init__(
        self,
        forecast: pd.DataFrame | None = None,
        telemetry: dict[str, Any] | None = None,
        battery_scenario: dict[str, Any] | None = None,
    ):
        self.forecast = forecast
        self.telemetry = telemetry or {"available": False, "message": "No physical rig telemetry has been connected."}
        self.battery_scenario = battery_scenario

    def get_next_day_forecast(self) -> dict[str, Any]:
        if self.forecast is None or self.forecast.empty:
            return {"available": False, "message": "No forecast is loaded."}
        records = self.forecast.copy()
        records["timestamp"] = records["timestamp"].astype(str)
        return {"available": True, "records": records.to_dict(orient="records")}

    def get_peak_windows(self, percentile: float = 90) -> dict[str, Any]:
        if not 50 <= float(percentile) <= 99:
            raise ValueError("percentile must be between 50 and 99")
        if self.forecast is None or self.forecast.empty:
            return {"available": False, "message": "No forecast is loaded."}
        threshold = float(self.forecast["forecast"].quantile(float(percentile) / 100.0))
        peaks = self.forecast.loc[self.forecast["forecast"] >= threshold, ["timestamp", "forecast"]].copy()
        peaks["timestamp"] = peaks["timestamp"].astype(str)
        return {"available": True, "percentile": percentile, "threshold": threshold, "peak_hours": peaks.to_dict(orient="records")}

    def run_load_shift_scenario(self, base_load_kw, tariff_per_kwh, tasks, capacity_kw=None) -> dict[str, Any]:
        return schedule_flexible_loads(base_load_kw, tariff_per_kwh, tasks, capacity_kw=capacity_kw)

    def run_pv_battery_scenario(self) -> dict[str, Any]:
        if not self.battery_scenario:
            return {"available": False, "message": "No local-site PV/battery profile is configured."}
        return optimise_battery_dispatch(**self.battery_scenario)

    def get_live_rig_telemetry(self) -> dict[str, Any]:
        # Deliberately read-only. No setter / GPIO command exists in this module.
        return self.telemetry

    def execute(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        handlers = {
            "get_next_day_forecast": self.get_next_day_forecast,
            "get_peak_windows": self.get_peak_windows,
            "run_load_shift_scenario": self.run_load_shift_scenario,
            "run_pv_battery_scenario": self.run_pv_battery_scenario,
            "get_live_rig_telemetry": self.get_live_rig_telemetry,
        }
        if name not in handlers:
            raise ValueError(f"Tool is not allow-listed: {name}")
        if not isinstance(args, dict):
            raise ValueError("Tool arguments must be an object")
        return handlers[name](**args)
