from __future__ import annotations
from pathlib import Path
import pandas as pd


def load_hourly_series(
    path: str | Path,
    timestamp_col: str = "timestamp",
    demand_col: str = "demand",
    timezone: str | None = None,
) -> pd.Series:
    """Load a clean, continuous hourly demand series indexed in UTC.

    Naive timestamps require an explicit source timezone. Short internal gaps
    up to two hours may be interpolated; longer or boundary gaps are rejected
    because dropping them would make lag features span non-hourly intervals.
    Duplicate timestamps are averaged and reported by the caller if desired.
    """
    frame = pd.read_csv(path)
    missing = [c for c in (timestamp_col, demand_col) if c not in frame.columns]
    if missing:
        raise ValueError(f"Missing required CSV columns: {missing}. Available: {list(frame.columns)}")
    frame = frame[[timestamp_col, demand_col]].copy()

    try:
        parsed = pd.to_datetime(frame[timestamp_col], errors="coerce")
        parsed_tz = parsed.dt.tz
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError("Timestamps use mixed or inconsistent timezone formats; normalise them before modelling.") from exc

    if parsed_tz is None:
        if not timezone:
            raise ValueError("Naive timestamps detected. Set the source timezone explicitly (for example Asia/Kolkata); do not assume UTC.")
        try:
            parsed = parsed.dt.tz_localize(timezone, ambiguous="raise", nonexistent="raise").dt.tz_convert("UTC")
        except Exception as exc:
            raise ValueError(f"Could not localise timestamps using timezone {timezone!r}: {exc}") from exc
    else:
        parsed = parsed.dt.tz_convert("UTC")

    frame[timestamp_col] = parsed
    frame[demand_col] = pd.to_numeric(frame[demand_col], errors="coerce")
    frame = frame.dropna(subset=[timestamp_col, demand_col])
    if frame.empty:
        raise ValueError("No valid timestamp/demand rows found")

    # Average duplicate observations at the same instant, then enforce a
    # continuous UTC hourly index. Duplicate handling is explicit and stable.
    series = frame.groupby(timestamp_col)[demand_col].mean().sort_index()
    series = series.resample("1h").mean()
    filled = series.interpolate(method="time", limit=2, limit_area="inside")
    unresolved = int(filled.isna().sum())
    if unresolved:
        raise ValueError(
            f"{unresolved} hourly gaps remain after interpolating internal gaps up to 2 hours. "
            "Inspect the source data or define an explicit gap-handling policy before forecasting."
        )
    if len(filled) < 24:
        raise ValueError("At least 24 continuous hourly observations are required")
    if not filled.index.is_monotonic_increasing or not filled.index.is_unique:
        raise ValueError("Hourly timestamps must be sorted and unique after normalisation")
    filled.name = "demand"
    return filled.astype(float)
