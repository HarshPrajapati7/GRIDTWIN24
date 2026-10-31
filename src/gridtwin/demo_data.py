from __future__ import annotations
import numpy as np
import pandas as pd


def make_synthetic_load(days: int = 90, seed: int = 7) -> pd.DataFrame:
    """Generate clearly synthetic hourly load data for software smoke tests."""
    rng = np.random.default_rng(seed)
    idx = pd.date_range("2026-01-01", periods=days * 24, freq="h", tz="UTC")
    hour = idx.hour.to_numpy()
    dow = idx.dayofweek.to_numpy()
    day = np.arange(len(idx)) / 24
    daily = 18 + 6 * np.sin((hour - 8) / 24 * 2 * np.pi) + 3 * np.sin((hour - 18) / 24 * 2 * np.pi)
    evening_peak = 8 * np.exp(-0.5 * ((hour - 19) / 2.0) ** 2)
    weekly = np.where(dow >= 5, -2.5, 1.5)
    seasonal = 2.2 * np.sin(day / 45 * 2 * np.pi)
    noise = rng.normal(0, 1.3, len(idx))
    demand = np.maximum(2, 100 + daily + evening_peak + weekly + seasonal + noise)
    return pd.DataFrame({"timestamp": idx, "demand": demand.round(3)})
