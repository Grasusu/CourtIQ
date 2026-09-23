import pytest

from app.analytics.metrics import (
    assist_to_turnover_ratio,
    best_worst_performance,
    consistency_score,
    effective_field_goal_percentage,
    latest_standard_score,
    percentile_rank,
    points_per_minute,
    recent_form_delta,
    recent_rolling_average,
    true_shooting_percentage,
    weighted_linear_forecast,
)


def test_points_per_minute():
    assert points_per_minute(30, 10) == 3.0
    assert points_per_minute(0, 10) == 0.0
    assert points_per_minute(30, 0) == 0.0


def test_assist_to_turnover_ratio():
    assert assist_to_turnover_ratio(10, 5) == 2.0
    assert assist_to_turnover_ratio(10, 0) == float('inf')
    assert assist_to_turnover_ratio(0, 5) == 0.0


def test_effective_field_goal_percentage():
    assert effective_field_goal_percentage(5, 10, 2) == 0.6
    assert effective_field_goal_percentage(0, 10, 0) == 0.0
    assert effective_field_goal_percentage(5, 0, 2) == 0.0


def test_true_shooting_percentage():
    assert true_shooting_percentage(30, 10, 5) == pytest.approx(1.2295, rel=1e-4)
    assert true_shooting_percentage(0, 10, 0) == 0.0
    assert true_shooting_percentage(30, 0, 0) == 0.0


def test_recent_rolling_average():
    assert recent_rolling_average([10, 20, 30, 40], 2) == [None, 15.0, 25.0, 35.0]
    assert recent_rolling_average([10, 20, 30, 40], 3) == [None, None, 20.0, 30.0]
    with pytest.raises(ValueError):
        recent_rolling_average([10, 20, 30], 0)


def test_best_worst_performance():
    assert best_worst_performance([10, 20, 30, 40]) == (40, 10)
    assert best_worst_performance([]) == (None, None)


def test_consistency_score():
    assert consistency_score([10, 10, 10]) == 1.0
    assert consistency_score([10, 20, 30]) < 1.0
    assert consistency_score([]) == 0.0


def test_weighted_linear_forecast_tracks_trend_and_uncertainty():
    forecast = weighted_linear_forecast([10, 12, 14, 16, 18])

    assert forecast is not None
    assert forecast.projected_value == pytest.approx(20.0)
    assert forecast.trend_per_game == pytest.approx(2.0)
    assert forecast.interval_low < forecast.projected_value < forecast.interval_high
    assert forecast.sample_size == 5
    assert weighted_linear_forecast([10, 12]) is None


def test_percentile_form_delta_and_latest_standard_score():
    assert percentile_rank(20, [10, 20, 30]) == 50
    assert percentile_rank(10, [10]) == 50
    assert percentile_rank(10, []) == 0
    assert recent_form_delta([10, 10, 10, 16, 16, 16]) == 6.0
    assert recent_form_delta([10, 12, 14]) == 0.0
    assert latest_standard_score([10, 10, 10, 16]) == 3.0
    assert latest_standard_score([8, 10, 12, 18]) == pytest.approx(4.9, abs=0.1)
