from gridtwin.demo_data import make_synthetic_load
from gridtwin.data import load_hourly_series
from gridtwin.forecasting import fit_evaluate_forecast
import os
import tempfile

# NOTE: We use TemporaryDirectory + an explicit file path instead of
# NamedTemporaryFile. On Windows a NamedTemporaryFile is opened with an
# exclusive lock, so a second open-by-name (pandas.to_csv) raises
# PermissionError. TemporaryDirectory is the portable idiom and keeps the
# exact same test assertions.


def test_forecast_shape_and_nonnegative():
    df = make_synthetic_load(days=75)
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "load.csv")
        df.to_csv(path, index=False)
        s = load_hourly_series(path)
    result = fit_evaluate_forecast(s)
    assert len(result.forecast) == 24
    assert "peak_flag" in result.forecast.columns
    assert result.forecast["peak_flag"].dtype == bool
    assert (result.forecast["forecast"] >= 0).all()
    assert "seasonal_naive" in result.metrics
    assert "interval_validation_coverage" in result.metrics
    assert len(result.validation) == result.metrics["validation_points"]
    assert not result.feature_importance.empty


def test_naive_timestamps_require_explicit_timezone():
    import pandas as pd
    import pytest
    from gridtwin.data import load_hourly_series
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "naive.csv")
        pd.DataFrame({"timestamp": pd.date_range("2026-01-01", periods=30, freq="h"), "demand": range(30)}).to_csv(path, index=False)
        with pytest.raises(ValueError, match="source timezone explicitly"):
            load_hourly_series(path)
        series = load_hourly_series(path, timezone="Asia/Kolkata")
    assert str(series.index.tz) == "UTC"


def test_long_hourly_gaps_are_rejected():
    import pandas as pd
    import pytest
    from gridtwin.data import load_hourly_series
    idx = list(pd.date_range("2026-01-01", periods=12, freq="h", tz="UTC"))
    idx += list(pd.date_range("2026-01-01 18:00", periods=20, freq="h", tz="UTC"))
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "gaps.csv")
        pd.DataFrame({"timestamp": idx, "demand": [1.0] * len(idx)}).to_csv(path, index=False)
        with pytest.raises(ValueError, match="gaps remain"):
            load_hourly_series(path)
