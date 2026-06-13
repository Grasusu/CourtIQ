import pytest

from app.analytics.metrics import (
    assist_to_turnover_ratio,
    best_worst_performance,
    consistency_score,
    effective_field_goal_percentage,
    points_per_minute,
    recent_rolling_average,
    true_shooting_percentage,
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
