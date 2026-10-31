"""Constrained hourly PV + battery dispatch simulation for a local site.

This simulator is separate from the organiser's grid-demand forecast. It is a
planning scenario, not a controller or a measured-savings claim.
"""
from __future__ import annotations
from typing import Any
import numpy as np
from scipy.optimize import linprog


def optimise_battery_dispatch(
    load_kw: list[float],
    pv_kw: list[float],
    import_tariff: list[float],
    *,
    export_tariff: list[float] | None = None,
    battery_capacity_kwh: float = 8.0,
    max_charge_kw: float = 2.0,
    max_discharge_kw: float = 2.0,
    initial_soc_fraction: float = 0.50,
    min_soc_fraction: float = 0.10,
    max_soc_fraction: float = 0.95,
    charge_efficiency: float = 0.95,
    discharge_efficiency: float = 0.95,
    degradation_cost_per_kwh: float = 0.05,
    demand_charge_per_kw: float = 0.0,
    grid_import_limit_kw: float | None = None,
) -> dict[str, Any]:
    """Minimise 24-hour energy and optional peak-demand cost with LP.

    Power values are kW and each time step is one hour. The model supports
    grid imports/exports, charge/discharge power, SOC bounds, efficiencies,
    and an optional daily peak-demand charge. Tariffs are per kWh; demand
    charge is per kW for the simulated horizon.
    """
    load = np.asarray(load_kw, dtype=float)
    pv = np.asarray(pv_kw, dtype=float)
    buy = np.asarray(import_tariff, dtype=float)
    sell = np.asarray(export_tariff if export_tariff is not None else [0.0] * 24, dtype=float)
    if any(len(x) != 24 for x in (load, pv, buy, sell)):
        raise ValueError("load_kw, pv_kw, import_tariff and export_tariff must each contain 24 values")
    if not all(np.isfinite(x).all() for x in (load, pv, buy, sell)):
        raise ValueError("All profiles must contain finite numbers")
    if np.any(load < 0) or np.any(pv < 0) or np.any(buy < 0) or np.any(sell < 0):
        raise ValueError("Load, PV and tariffs must be non-negative")
    if np.any(sell > buy):
        raise ValueError("Export tariff cannot exceed import tariff in this non-arbitrage model")
    scalar_values = [battery_capacity_kwh, max_charge_kw, max_discharge_kw,
                     initial_soc_fraction, min_soc_fraction, max_soc_fraction,
                     charge_efficiency, discharge_efficiency,
                     degradation_cost_per_kwh, demand_charge_per_kw]
    if not np.isfinite(np.asarray(scalar_values, dtype=float)).all():
        raise ValueError("Battery parameters must all be finite")
    if battery_capacity_kwh <= 0 or max_charge_kw < 0 or max_discharge_kw < 0:
        raise ValueError("Battery capacity must be positive and power limits non-negative")
    if not (0 < charge_efficiency <= 1 and 0 < discharge_efficiency <= 1):
        raise ValueError("Battery efficiencies must be in (0, 1]")
    if not (0 <= min_soc_fraction <= initial_soc_fraction <= max_soc_fraction <= 1):
        raise ValueError("SOC fractions must satisfy 0 <= min <= initial <= max <= 1")
    if degradation_cost_per_kwh < 0 or demand_charge_per_kw < 0:
        raise ValueError("Degradation and demand-charge costs must be non-negative")
    if grid_import_limit_kw is not None and (not np.isfinite(grid_import_limit_kw) or grid_import_limit_kw <= 0):
        raise ValueError("grid_import_limit_kw must be finite and positive when supplied")

    n = 24
    # Variable order: grid import, grid export, charge, discharge, SOC[0..24], peak import.
    gi = slice(0, n)
    ge = slice(n, 2*n)
    ch = slice(2*n, 3*n)
    dis = slice(3*n, 4*n)
    soc = slice(4*n, 4*n + n + 1)
    peak_idx = 4*n + n + 1
    size = peak_idx + 1

    objective = np.zeros(size)
    objective[gi] = buy
    objective[ge] = -sell
    objective[ch] = degradation_cost_per_kwh
    objective[dis] = degradation_cost_per_kwh
    objective[peak_idx] = demand_charge_per_kw

    a_eq = []
    b_eq = []
    # Hourly power balance: grid import - export - charge + discharge = load - PV.
    for t in range(n):
        row = np.zeros(size)
        row[gi.start + t] = 1.0
        row[ge.start + t] = -1.0
        row[ch.start + t] = -1.0
        row[dis.start + t] = 1.0
        a_eq.append(row)
        b_eq.append(float(load[t] - pv[t]))

    # SOC transition: SOC[t+1] = SOC[t] + eta_c*charge - discharge/eta_d.
    for t in range(n):
        row = np.zeros(size)
        row[soc.start + t + 1] = 1.0
        row[soc.start + t] = -1.0
        row[ch.start + t] = -charge_efficiency
        row[dis.start + t] = 1.0 / discharge_efficiency
        a_eq.append(row)
        b_eq.append(0.0)

    # Initial state of charge is known.
    row = np.zeros(size)
    row[soc.start] = 1.0
    a_eq.append(row)
    b_eq.append(initial_soc_fraction * battery_capacity_kwh)
    # Terminal SOC equals initial SOC so the optimiser cannot treat stored
    # energy at the start of the 24-hour horizon as free energy.
    row = np.zeros(size)
    row[soc.stop - 1] = 1.0
    a_eq.append(row)
    b_eq.append(initial_soc_fraction * battery_capacity_kwh)

    a_ub = []
    b_ub = []
    # Peak import variable bounds the grid import each hour.
    for t in range(n):
        row = np.zeros(size)
        row[gi.start + t] = 1.0
        row[peak_idx] = -1.0
        a_ub.append(row)
        b_ub.append(0.0)

    bounds = []
    bounds.extend([(0, grid_import_limit_kw)] * n)  # grid import
    bounds.extend([(0, None)] * n)  # grid export
    bounds.extend([(0, max_charge_kw)] * n)
    bounds.extend([(0, max_discharge_kw)] * n)
    bounds.extend([
        (min_soc_fraction * battery_capacity_kwh,
         max_soc_fraction * battery_capacity_kwh)
    ] * (n + 1))
    bounds.append((0, None))  # peak import

    result = linprog(
        objective,
        A_ub=np.asarray(a_ub), b_ub=np.asarray(b_ub),
        A_eq=np.asarray(a_eq), b_eq=np.asarray(b_eq),
        bounds=bounds, method="highs",
    )
    if not result.success or result.x is None:
        raise RuntimeError(f"Battery dispatch optimisation failed: {result.message}")

    x = result.x
    grid_import = x[gi]
    grid_export = x[ge]
    charge = x[ch]
    discharge = x[dis]
    soc_series = x[soc]
    baseline_import = np.maximum(load - pv, 0.0)
    baseline_export = np.maximum(pv - load, 0.0)
    baseline_cost = float(np.sum(baseline_import * buy - baseline_export * sell)
                          + demand_charge_per_kw * (float(np.max(baseline_import))))
    energy_cost = float(np.sum(grid_import * buy - grid_export * sell))
    degradation_cost = float(np.sum(charge + discharge) * degradation_cost_per_kwh)
    peak_cost = float(np.max(grid_import) * demand_charge_per_kw)
    optimised_total_cost = energy_cost + degradation_cost + peak_cost

    return {
        "baseline_grid_import_kw": baseline_import.round(4).tolist(),
        "optimised_grid_import_kw": grid_import.round(4).tolist(),
        "grid_export_kw": grid_export.round(4).tolist(),
        "battery_charge_kw": charge.round(4).tolist(),
        "battery_discharge_kw": discharge.round(4).tolist(),
        "battery_soc_kwh": soc_series.round(4).tolist(),
        "baseline_cost": baseline_cost,
        "optimised_total_cost": optimised_total_cost,
        "estimated_cost_difference": baseline_cost - optimised_total_cost,
        "baseline_peak_import_kw": float(np.max(baseline_import)),
        "optimised_peak_import_kw": float(np.max(grid_import)),
        "peak_reduction_kw": float(np.max(baseline_import) - np.max(grid_import)),
        "battery_parameters": {
            "capacity_kwh": battery_capacity_kwh,
            "max_charge_kw": max_charge_kw,
            "max_discharge_kw": max_discharge_kw,
            "charge_efficiency": charge_efficiency,
            "discharge_efficiency": discharge_efficiency,
            "initial_soc_fraction": initial_soc_fraction,
            "terminal_soc_fraction": initial_soc_fraction,
            "min_soc_fraction": min_soc_fraction,
            "max_soc_fraction": max_soc_fraction,
            "degradation_cost_per_kwh": degradation_cost_per_kwh,
            "demand_charge_per_kw": demand_charge_per_kw,
            "grid_import_limit_kw": grid_import_limit_kw,
        },
        "solver": "scipy.optimize.linprog(method='highs')",
        "note": "Optimised scenario estimate under stated assumptions; not measured savings or a battery control command.",
    }


def make_demo_site_profile() -> dict[str, list[float]]:
    """Return a clearly synthetic 24-hour site load/PV/tariff profile."""
    hour = np.arange(24)
    load = 1.1 + 0.18 * np.sin((hour - 7) / 24 * 2 * np.pi) + 0.55 * np.exp(-0.5 * ((hour - 19) / 2.2) ** 2)
    load = np.maximum(load, 0.35)
    pv = 2.4 * np.maximum(0.0, np.sin(np.pi * (hour - 6) / 12))
    tariff = np.array([3.5 if h < 6 or h >= 23 else 5.0 if h < 17 else 8.0 if h < 22 else 5.0 for h in hour])
    return {"load_kw": load.tolist(), "pv_kw": pv.tolist(), "import_tariff": tariff.tolist()}
