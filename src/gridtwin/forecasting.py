from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.inspection import permutation_importance

HORIZON = 24
MIN_HISTORY = 168  # one full week for weekly seasonal context


def _feature_row(history: pd.Series, target_time: pd.Timestamp, horizon: int) -> dict[str, float]:
    vals = history.astype(float).to_numpy()
    if len(vals) < MIN_HISTORY:
        raise ValueError(f"Need at least {MIN_HISTORY} hourly observations; got {len(vals)}")
    tail = vals[-168:]
    ts = pd.Timestamp(target_time)
    hour = ts.hour
    dow = ts.dayofweek
    doy = ts.dayofyear
    last24 = vals[-24:]
    return {
        "lag_1": float(vals[-1]),
        "lag_2": float(vals[-2]),
        "lag_3": float(vals[-3]),
        "lag_24": float(vals[-24]),
        "lag_48": float(vals[-48]),
        "lag_168": float(vals[-168]),
        "mean_24": float(np.mean(last24)),
        "std_24": float(np.std(last24)),
        "min_24": float(np.min(last24)),
        "max_24": float(np.max(last24)),
        "mean_168": float(np.mean(tail)),
        "std_168": float(np.std(tail)),
        "trend_24_vs_168": float(np.mean(last24) - np.mean(tail)),
        "hour": float(hour),
        "dayofweek": float(dow),
        "dayofyear_sin": float(np.sin(2 * np.pi * doy / 365.25)),
        "dayofyear_cos": float(np.cos(2 * np.pi * doy / 365.25)),
        "hour_sin": float(np.sin(2 * np.pi * hour / 24)),
        "hour_cos": float(np.cos(2 * np.pi * hour / 24)),
        "is_weekend": float(dow >= 5),
        "horizon": float(horizon),
    }


def build_supervised(series: pd.Series, max_horizon: int = HORIZON) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """Create direct multi-horizon training rows without using future inputs.

    Each row's features use observations only up to its forecast origin. The
    target is the demand at origin + horizon. Returned target_times support
    strict temporal splitting.
    """
    s = series.sort_index().astype(float)
    x_rows, y_rows, target_times = [], [], []
    values = s.to_numpy()
    index = s.index
    for origin in range(MIN_HISTORY - 1, len(s) - max_horizon):
        hist = s.iloc[: origin + 1]
        for h in range(1, max_horizon + 1):
            target_pos = origin + h
            row = _feature_row(hist, index[target_pos], h)
            x_rows.append(row)
            y_rows.append(float(values[target_pos]))
            target_times.append(index[target_pos])
    if not x_rows:
        raise ValueError("Not enough data to create supervised training rows")
    X = pd.DataFrame(x_rows).replace([np.inf, -np.inf], np.nan).fillna(0.0)
    y = pd.Series(y_rows, name="target")
    t = pd.Series(pd.to_datetime(target_times, utc=True), name="target_time")
    return X, y, t


def _seasonal_naive(history: pd.Series, target_time: pd.Timestamp) -> float:
    lookup = pd.Timestamp(target_time) - pd.Timedelta(hours=24)
    if lookup in history.index:
        return float(history.loc[lookup])
    lookup = pd.Timestamp(target_time) - pd.Timedelta(hours=168)
    if lookup in history.index:
        return float(history.loc[lookup])
    return float(history.iloc[-1])


def _metrics(actual: np.ndarray, pred: np.ndarray, peak_threshold: float) -> dict[str, float]:
    mae = float(mean_absolute_error(actual, pred))
    rmse = float(np.sqrt(mean_squared_error(actual, pred)))
    denom = float(np.sum(np.abs(actual)))
    wape = float(np.sum(np.abs(actual - pred)) / denom * 100) if denom else float("nan")
    # Use one threshold fixed from training history for both actual and predicted
    # values; do not derive a separate threshold from held-out labels/predictions.
    actual_peak = actual >= peak_threshold
    pred_peak = pred >= peak_threshold
    tp = int(np.sum(actual_peak & pred_peak))
    fn = int(np.sum(actual_peak & ~pred_peak))
    fp = int(np.sum(~actual_peak & pred_peak))
    peak_recall = float(tp / (tp + fn)) if (tp + fn) else float("nan")
    peak_precision = float(tp / (tp + fp)) if (tp + fp) else float("nan")
    return {
        "mae": mae,
        "rmse": rmse,
        "wape_pct": wape,
        "peak_recall_above_training_p90": peak_recall,
        "peak_precision_above_training_p90": peak_precision,
        "peak_threshold_training_p90": float(peak_threshold),
    }


@dataclass
class ForecastResult:
    forecast: pd.DataFrame
    validation: pd.DataFrame
    feature_importance: pd.DataFrame
    metrics: dict[str, Any]
    validation_residuals: np.ndarray
    interval_calibrated: bool
    model: Any


def fit_evaluate_forecast(series: pd.Series, horizon: int = HORIZON, test_fraction: float = 0.2) -> ForecastResult:
    """Fit a global horizon-conditioned model, evaluate rolling 24h origins,
    and issue the next-day forecast. A seasonal-naive benchmark is always
    computed. The interval is empirical and withheld when calibration is weak.
    """
    s = series.sort_index().astype(float)
    if len(s) < MIN_HISTORY + horizon + 48:
        raise ValueError(f"Need at least {MIN_HISTORY + horizon + 48} hourly points for evaluation")
    X, y, target_times = build_supervised(s, horizon)
    split_idx = int(len(s) * (1 - test_fraction))
    cutoff = s.index[split_idx]
    train_mask = target_times < cutoff
    X_train, y_train = X.loc[train_mask], y.loc[train_mask]
    if len(X_train) < 500:
        raise ValueError("Insufficient training examples after temporal split")

    model = HistGradientBoostingRegressor(
        learning_rate=0.06, max_iter=140, max_leaf_nodes=15,
        l2_regularization=1.0, random_state=42
    )
    model.fit(X_train, y_train)

    val_actual, val_pred, val_naive, val_residuals, val_times = [], [], [], [], []
    # Rolling-origin evaluation: each origin is at least 24h apart. At each
    # origin, only history available up to that origin is used as features.
    origins = list(range(split_idx, len(s) - horizon, horizon))
    for origin in origins:
        hist = s.iloc[: origin + 1]
        for h in range(1, horizon + 1):
            target_time = s.index[origin] + pd.Timedelta(hours=h)
            row = pd.DataFrame([_feature_row(hist, target_time, h)])
            pred = max(0.0, float(model.predict(row)[0]))
            actual = float(s.loc[target_time])
            naive = max(0.0, _seasonal_naive(hist, target_time))
            val_actual.append(actual); val_pred.append(pred); val_naive.append(naive)
            val_residuals.append(actual - pred); val_times.append(target_time)

    actual_arr = np.asarray(val_actual, dtype=float)
    pred_arr = np.asarray(val_pred, dtype=float)
    naive_arr = np.asarray(val_naive, dtype=float)
    residuals = np.asarray(val_residuals, dtype=float)
    validation = pd.DataFrame({
        "timestamp": pd.to_datetime(val_times, utc=True),
        "actual": actual_arr,
        "model_forecast": pred_arr,
        "seasonal_naive": naive_arr,
    })
    peak_threshold = float(s.iloc[:split_idx].quantile(0.90))
    model_metrics = _metrics(actual_arr, pred_arr, peak_threshold)
    baseline_metrics = _metrics(actual_arr, naive_arr, peak_threshold)
    # Evaluate interval calibration on a later, disjoint slice of the
    # rolling-origin residuals. We do not report the in-sample calibration
    # coverage as evidence of interval quality.
    calibrated = len(residuals) >= 72
    interval_validation_coverage = float("nan")
    interval_calibration_n = 0
    interval_validation_n = 0
    if calibrated:
        split_resid = max(36, int(len(residuals) * 0.60))
        split_resid = min(split_resid, len(residuals) - 24)
        calibration_residuals = residuals[:split_resid]
        interval_validation_residuals = residuals[split_resid:]
        cal_lo, cal_hi = np.quantile(calibration_residuals, [0.10, 0.90])
        interval_validation_coverage = float(np.mean(
            (interval_validation_residuals >= cal_lo) &
            (interval_validation_residuals <= cal_hi)
        ))
        interval_calibration_n = int(len(calibration_residuals))
        interval_validation_n = int(len(interval_validation_residuals))
        # For the next-day operational band, refit the empirical residual
        # quantiles using all out-of-sample rolling-origin residuals.
        lo_resid, hi_resid = np.quantile(residuals, [0.10, 0.90])
    else:
        lo_resid, hi_resid = np.nan, np.nan

    # Feature explanations are calculated on held-out supervised rows. This is
    # global permutation importance (not a causal explanation of one hour).
    X_eval = X.loc[~train_mask]
    y_eval = y.loc[~train_mask]
    if len(X_eval) > 1200:
        sampled_idx = X_eval.sample(n=1200, random_state=42).index
        X_eval, y_eval = X_eval.loc[sampled_idx], y_eval.loc[sampled_idx]
    if len(X_eval) >= 24:
        perm = permutation_importance(
            model, X_eval, y_eval, n_repeats=3,
            scoring="neg_mean_absolute_error", random_state=42, n_jobs=-1,
        )
        feature_importance = pd.DataFrame({
            "feature": X_eval.columns,
            "mae_increase": perm.importances_mean,
            "std": perm.importances_std,
        }).sort_values("mae_increase", ascending=False).reset_index(drop=True)
    else:
        feature_importance = pd.DataFrame(columns=["feature", "mae_increase", "std"])

    # Refit on all available observations for tomorrow's operational forecast.
    model.fit(X, y)
    origin_time = s.index[-1]
    rows = []
    hist = s.copy()
    for h in range(1, horizon + 1):
        target_time = origin_time + pd.Timedelta(hours=h)
        row = pd.DataFrame([_feature_row(hist, target_time, h)])
        point = max(0.0, float(model.predict(row)[0]))
        if calibrated:
            lower = max(0.0, point + float(lo_resid))
            upper = max(lower, point + float(hi_resid))
        else:
            lower, upper = np.nan, np.nan
        rows.append({"timestamp": target_time, "forecast": point, "lower": lower, "upper": upper, "peak_threshold": peak_threshold, "peak_flag": bool(point >= peak_threshold)})
    forecast = pd.DataFrame(rows)
    metrics = {
        "model": model_metrics,
        "seasonal_naive": baseline_metrics,
        "validation_origins": len(origins),
        "validation_points": len(actual_arr),
        "peak_threshold_training_p90": peak_threshold,
        "interval_calibrated": calibrated,
        "interval_method": "pooled rolling-origin residual 10th-90th percentiles" if calibrated else "withheld: insufficient calibration residuals",
        "interval_nominal_level": "80% empirical central interval" if calibrated else None,
        "interval_calibration_samples": interval_calibration_n,
        "interval_validation_samples": interval_validation_n,
        "interval_validation_coverage": interval_validation_coverage if calibrated else None,
        "interval_note": "Coverage measured on a later disjoint residual slice; future coverage is not guaranteed." if calibrated else "Insufficient out-of-sample residuals; interval withheld.",
        "validation_start": str(s.index[split_idx]),
        "validation_end": str(s.index[-1]),
    }
    return ForecastResult(forecast, validation, feature_importance, metrics, residuals, calibrated, model)
