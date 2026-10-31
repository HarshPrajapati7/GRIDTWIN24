import pytest
from gridtwin.dispatch import schedule_flexible_loads

def test_schedule_shifts_task_to_cheaper_window():
    base = [1.0] * 24
    tariff = [8.0] * 24
    for h in range(0, 6): tariff[h] = 2.0
    result = schedule_flexible_loads(base, tariff, [{"name":"pump", "power_kw":1, "duration_hours":2, "earliest_start":0, "latest_start":20, "baseline_start":18}])
    assert result["tasks"][0]["start_hour"] == 0
    assert result["scheduled_cost"] < result["baseline_cost"]

def test_rejects_wrong_horizon():
    with pytest.raises(ValueError):
        schedule_flexible_loads([1]*23, [2]*24, [])


def test_rejects_non_finite_load_and_invalid_capacity():
    with pytest.raises(ValueError, match="finite values"):
        schedule_flexible_loads([1.0] * 23 + [float("nan")], [2.0] * 24, [])
    with pytest.raises(ValueError, match="capacity_kw must be finite and positive"):
        schedule_flexible_loads([1.0] * 24, [2.0] * 24, [], capacity_kw=0)
