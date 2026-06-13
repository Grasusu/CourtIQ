"""Basketball metric calculations for CourtIQ.

These functions are intentionally framework-free so they can be tested without
FastAPI, a database, or uploaded files.
"""

from __future__ import annotations

from math import isclose, sqrt
from statistics import mean


def points_per_minute(points: float, minutes: float) -> float:
    """Return points scored per minute played."""
    if minutes <= 0:
        return 0.0

    return points / minutes


def assist_to_turnover_ratio(assists: float, turnovers: float) -> float:
    """Return assist-to-turnover ratio.

    A player with assists and zero turnovers has an infinite ratio, which is a
    common way to represent perfect turnover protection for that sample.
    """
    if turnovers == 0:
        return float("inf") if assists > 0 else 0.0

    return assists / turnovers


def effective_field_goal_percentage(
    field_goals_made: float,
    field_goal_attempts: float,
    three_pointers_made: float,
) -> float:
    """Return effective field goal percentage."""
    if field_goal_attempts <= 0:
        return 0.0

    return (field_goals_made + 0.5 * three_pointers_made) / field_goal_attempts


def true_shooting_percentage(points: float, field_goal_attempts: float, free_throw_attempts: float) -> float:
    """Return true shooting percentage.

    Formula: points / (2 * (FGA + 0.44 * FTA)).
    """
    denominator = 2 * (field_goal_attempts + 0.44 * free_throw_attempts)
    if denominator <= 0:
        return 0.0

    return points / denominator


def recent_rolling_average(values: list[float], window: int) -> list[float | None]:
    """Return rolling averages with None before the window is full."""
    if window <= 0:
        raise ValueError("window must be greater than 0")

    averages: list[float | None] = []
    for index in range(len(values)):
        if index + 1 < window:
            averages.append(None)
            continue

        window_values = values[index + 1 - window : index + 1]
        averages.append(mean(window_values))

    return averages


def best_worst_performance(values: list[float]) -> tuple[float | None, float | None]:
    """Return best and worst values from a performance series."""
    if not values:
        return None, None

    return max(values), min(values)


def consistency_score(values: list[float]) -> float:
    """Return a 0-1 score where stable performances are closer to 1."""
    if not values:
        return 0.0

    average = mean(values)
    if isclose(average, 0.0):
        return 1.0 if all(isclose(value, 0.0) for value in values) else 0.0

    variance = mean([(value - average) ** 2 for value in values])
    standard_deviation = sqrt(variance)
    coefficient_of_variation = standard_deviation / abs(average)

    return max(0.0, min(1.0, 1.0 - coefficient_of_variation))
