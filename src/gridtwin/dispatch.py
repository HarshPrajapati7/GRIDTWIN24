from __future__ import annotations
from typing import Any
import numpy as np
import pandas as pd


def schedule_flexible_loads(
    base_load_kw: list[float] | np.ndarray,
    tariff_per_kwh: list[float] | np.ndarray,
    tasks: list[dict[str, Any]],
    capacity_kw: float | None = None,
    overload_penalty: float = 1000.0,
) -> dict[str, Any]:
    """Greedy transparent scheduler for 24 hourly, shiftable one-block tasks.

    A task needs: name, power_kw, duration_hours, earliest_start, latest_start.
    start slots are indices 0..23; latest_start is inclusive. This is a
    heuristic scenario tool, not a certified utility dispatch optimiser.
    """
    load = np.asarray(base_load_kw, dtype=float).copy()
    tariff = np.asarray(tariff_per_kwh, dtype=float)
    if len(load) != 24 or len(tariff) != 24:
        raise ValueError("base_load_kw and tariff_per_kwh must each contain 24 values")
    if not np.isfinite(load).all() or not np.isfinite(tariff).all():
        raise ValueError("Load and tariff profiles must contain finite values")
    if np.any(load < 0) or np.any(tariff < 0):
        raise ValueError("Load and tariff must be non-negative")
    if capacity_kw is not None and (not np.isfinite(capacity_kw) or capacity_kw <= 0):
        raise ValueError("capacity_kw must be finite and positive when supplied")
    if not np.isfinite(overload_penalty) or overload_penalty < 0:
        raise ValueError("overload_penalty must be finite and non-negative")
    # Baseline assumes each flexible task starts at its earliest permitted slot.
    # This makes the comparison like-for-like: both cases include task energy.
    baseline_load = load.copy()
    for task in tasks:
        p = float(task["power_kw"])
        d = int(task["duration_hours"])
        e = int(task.get("earliest_start", 0))
        baseline_start = int(task.get("baseline_start", e))
        if p < 0 or d < 1 or d > 24 or e < 0 or e + d > 24 or baseline_start < e or baseline_start > int(task.get("latest_start", 23 - d + 1)) or baseline_start + d > 24:
            raise ValueError(f"Invalid baseline task window or power for {task.get('name', 'unnamed task')}")
        baseline_load[baseline_start:baseline_start+d] += p
    baseline_cost = float(np.sum(baseline_load * tariff))
    schedules = []
    for task in tasks:
        power = float(task["power_kw"])
        duration = int(task["duration_hours"])
        earliest = int(task.get("earliest_start", 0))
        latest = int(task.get("latest_start", 23 - duration + 1))
        if power < 0 or duration < 1 or duration > 24 or earliest < 0 or latest > 23 - duration + 1 or earliest > latest:
            raise ValueError(f"Invalid task window or power for {task.get('name', 'unnamed task')}")
        best = None
        for start in range(earliest, latest + 1):
            end = start + duration
            incremental_kwh = np.zeros(24)
            incremental_kwh[start:end] = power
            candidate_load = load + incremental_kwh
            energy_cost = float(np.sum(incremental_kwh * tariff))
            overload = float(np.sum(np.maximum(candidate_load - capacity_kw, 0))) if capacity_kw is not None else 0.0
            score = energy_cost + overload_penalty * overload
            if best is None or score < best[0]:
                best = (score, start, end, energy_cost, overload, candidate_load)
        assert best is not None
        _, start, end, energy_cost, overload, load = best
        schedules.append({"name": task.get("name", "flexible_load"), "baseline_start_hour": int(task.get("baseline_start", earliest)), "start_hour": start, "end_hour_exclusive": end, "power_kw": power, "incremental_cost": energy_cost, "overload_kw_hours": overload})
    final_cost = float(np.sum(load * tariff))
    return {
        "base_load_kw": np.asarray(base_load_kw, dtype=float).tolist(),
        "baseline_load_with_earliest_tasks_kw": baseline_load.tolist(),
        "scheduled_load_kw": load.tolist(),
        "baseline_cost": baseline_cost,
        "scheduled_cost": final_cost,
        "estimated_cost_difference": baseline_cost - final_cost,
        "tasks": schedules,
        "capacity_kw": capacity_kw,
        "note": "Scenario estimate only. No measured saving is claimed; validate against site meter data and actual tariffs.",
    }
