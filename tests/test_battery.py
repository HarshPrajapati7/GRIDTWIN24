import numpy as np
import pytest
from gridtwin.battery import optimise_battery_dispatch


def test_battery_dispatch_respects_soc_and_can_reduce_peak():
    load = [1.0] * 24
    pv = [0.0] * 24
    tariff = [2.0] * 24
    for h in range(17, 21):
        tariff[h] = 10.0
        load[h] = 2.2
    result = optimise_battery_dispatch(
        load, pv, tariff, battery_capacity_kwh=8.0,
        max_charge_kw=2.0, max_discharge_kw=2.0,
        initial_soc_fraction=0.5, min_soc_fraction=0.1,
        max_soc_fraction=0.95, degradation_cost_per_kwh=0.02,
        demand_charge_per_kw=50.0,
    )
    soc = np.asarray(result["battery_soc_kwh"])
    assert len(soc) == 25
    assert np.isclose(soc[0], soc[-1], atol=1e-6)
    assert soc.min() >= 0.8 - 1e-6
    assert soc.max() <= 7.6 + 1e-6
    assert result["optimised_peak_import_kw"] <= result["baseline_peak_import_kw"] + 1e-6


def test_rejects_wrong_horizon_and_export_arbitrage():
    with pytest.raises(ValueError):
        optimise_battery_dispatch([1.0] * 23, [0.0] * 24, [1.0] * 24)
    with pytest.raises(ValueError, match="Export tariff cannot exceed"):
        optimise_battery_dispatch([1.0] * 24, [0.0] * 24, [2.0] * 24, export_tariff=[3.0] * 24)


def test_rejects_non_finite_battery_parameters():
    with pytest.raises(ValueError, match="parameters must all be finite"):
        optimise_battery_dispatch([1.0] * 24, [0.0] * 24, [1.0] * 24, battery_capacity_kwh=float("nan"))
    with pytest.raises(ValueError, match="grid_import_limit_kw must be finite"):
        optimise_battery_dispatch([1.0] * 24, [0.0] * 24, [1.0] * 24, grid_import_limit_kw=float("inf"))
