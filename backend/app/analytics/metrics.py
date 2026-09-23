"""Basketball metric calculations for CourtIQ.

These functions are intentionally framework-free so they can be tested without
FastAPI, a database, or uploaded files.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, sqrt
from statistics import mean


@dataclass(frozen=True)
class PerformanceForecast:
    projected_value: float
    interval_low: float
    interval_high: float
    trend_per_game: float
    confidence: str
    sample_size: int


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


def weighted_linear_forecast(values: list[float], max_window: int = 8) -> PerformanceForecast | None:
    """Forecast the next value with a recency-weighted linear regression.

    Recent games receive more weight. The interval uses weighted residual error,
    so volatile players receive a visibly wider prediction range.
    """
    if max_window < 3:
        raise ValueError("max_window must be at least 3")
    if len(values) < 3:
        return None

    sample = values[-max_window:]
    count = len(sample)
    x_values = [float(index) for index in range(count)]
    weights = [float(index + 1) for index in range(count)]
    total_weight = sum(weights)
    x_mean = sum(weight * value for weight, value in zip(weights, x_values, strict=True)) / total_weight
    y_mean = sum(weight * value for weight, value in zip(weights, sample, strict=True)) / total_weight
    denominator = sum(
        weight * (x_value - x_mean) ** 2
        for weight, x_value in zip(weights, x_values, strict=True)
    )
    slope = 0.0 if isclose(denominator, 0.0) else sum(
        weight * (x_value - x_mean) * (y_value - y_mean)
        for weight, x_value, y_value in zip(weights, x_values, sample, strict=True)
    ) / denominator
    intercept = y_mean - slope * x_mean
    projected = max(0.0, intercept + slope * count)
    weighted_error = sum(
        weight * (y_value - (intercept + slope * x_value)) ** 2
        for weight, x_value, y_value in zip(weights, x_values, sample, strict=True)
    ) / total_weight
    residual_error = sqrt(weighted_error)
    interval_radius = max(2.0, 1.64 * residual_error * sqrt(1 + 1 / count))
    relative_error = residual_error / max(abs(y_mean), 1.0)

    if count >= 7 and relative_error <= 0.2:
        confidence = "high"
    elif count >= 5 and relative_error <= 0.35:
        confidence = "medium"
    else:
        confidence = "low"

    return PerformanceForecast(
        projected_value=round(projected, 2),
        interval_low=round(max(0.0, projected - interval_radius), 2),
        interval_high=round(projected + interval_radius, 2),
        trend_per_game=round(slope, 2),
        confidence=confidence,
        sample_size=count,
    )


def percentile_rank(value: float, cohort: list[float]) -> int:
    """Return a tie-aware 0-100 percentile rank within a cohort."""
    if not cohort:
        return 0
    if len(cohort) == 1:
        return 50

    below = sum(candidate < value for candidate in cohort)
    equal = sum(isclose(candidate, value) for candidate in cohort)
    rank = (below + max(0, equal - 1) / 2) / (len(cohort) - 1)
    return round(max(0.0, min(1.0, rank)) * 100)


def recent_form_delta(values: list[float], window: int = 3) -> float:
    """Compare the latest sample with the immediately preceding sample."""
    if window <= 0:
        raise ValueError("window must be greater than 0")
    if len(values) < 4:
        return 0.0

    recent = values[-window:]
    previous = values[-(window * 2):-window]
    if not previous:
        previous = values[:-window]

    return round(mean(recent) - mean(previous), 2)


def latest_standard_score(values: list[float]) -> float | None:
    """Measure how unusual the latest value is against earlier performances."""
    if len(values) < 4:
        return None

    baseline = values[:-1]
    baseline_mean = mean(baseline)
    variance = mean([(value - baseline_mean) ** 2 for value in baseline])
    standard_deviation = sqrt(variance)
    if isclose(standard_deviation, 0.0):
        if isclose(values[-1], baseline_mean):
            return 0.0
        return 3.0 if values[-1] > baseline_mean else -3.0

    return round((values[-1] - baseline_mean) / standard_deviation, 2)
