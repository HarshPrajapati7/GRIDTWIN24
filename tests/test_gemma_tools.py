import pytest
import pandas as pd
from gridtwin.gemma_tools import ToolContext
from gridtwin.battery import make_demo_site_profile

def test_gemma_tools_read_forecast_and_peaks():
    forecast = pd.DataFrame({"timestamp": pd.date_range("2026-01-01", periods=24, freq="h", tz="UTC"), "forecast": list(range(24)), "lower": list(range(24)), "upper": list(range(24))})
    tools = ToolContext(forecast=forecast, telemetry={"available": True, "armed": False})
    assert tools.execute("get_next_day_forecast", {})["available"] is True
    peaks = tools.execute("get_peak_windows", {"percentile": 90})
    assert peaks["threshold"] >= 20
    assert tools.execute("get_live_rig_telemetry", {})["armed"] is False

def test_gemma_cannot_call_unapproved_hardware_write():
    tools = ToolContext()
    with pytest.raises(ValueError):
        tools.execute("switch_relay", {"channel": 1, "on": True})


def test_gemma_agent_requires_key_without_network(monkeypatch):
    from gridtwin.gemma_agent import ask_gemma
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        ask_gemma("Explain tomorrow's demand", ToolContext(), api_key=None)


def test_gemma_can_run_only_configured_battery_scenario():
    profile = make_demo_site_profile()
    context = ToolContext(battery_scenario={
        **profile, "battery_capacity_kwh": 8.0, "max_charge_kw": 2.0,
        "max_discharge_kw": 2.0, "demand_charge_per_kw": 20.0,
    })
    result = context.execute("run_pv_battery_scenario", {})
    assert len(result["battery_soc_kwh"]) == 25
    assert "not measured savings" in result["note"]
