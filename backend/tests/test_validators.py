import csv

import pytest

from app.analytics.validators import validate_csv
from app.analytics.validators import parse_box_score_csv


HEADERS = [
    "game_date",
    "opponent",
    "player",
    "minutes",
    "points",
    "rebounds",
    "assists",
    "steals",
    "blocks",
    "turnovers",
    "fgm",
    "fga",
    "three_pm",
    "three_pa",
    "ftm",
    "fta",
]


def write_csv(path, rows):
    with open(path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS)
        writer.writerows(rows)


def test_validate_csv_accepts_valid_box_score(tmp_path):
    csv_path = tmp_path / "valid.csv"
    write_csv(
        csv_path,
        [["2026-02-12", "Ajax Wolves", "Alex", 31, 18, 5, 7, 2, 1, 3, 7, 14, 2, 5, 2, 3]],
    )

    assert validate_csv(csv_path) is None


def test_parse_box_score_csv_returns_typed_rows(tmp_path):
    csv_path = tmp_path / "valid.csv"
    write_csv(
        csv_path,
        [["2026-02-12", "Ajax Wolves", "Alex", 31, 18, 5, 7, 2, 1, 3, 7, 14, 2, 5, 2, 3]],
    )

    rows = parse_box_score_csv(csv_path)

    assert len(rows) == 1
    assert rows[0].player == "Alex"
    assert rows[0].points == 18
    assert rows[0].minutes == 31.0


@pytest.mark.parametrize(
    "row, expected_message",
    [
        (
            ["2026-02-12", "Ajax Wolves", "Alex", -1, 18, 5, 7, 2, 1, 3, 7, 14, 2, 5, 2, 3],
            "Minutes cannot be negative",
        ),
        (
            ["2026-02-12", "Ajax Wolves", "Alex", 31, 18, 5, 7, 2, 1, -1, 7, 14, 2, 5, 2, 3],
            "Turnovers cannot be negative",
        ),
        (
            ["2026-02-12", "Ajax Wolves", "Alex", 31, 18, 5, 7, 2, 1, 3, 15, 14, 2, 5, 2, 3],
            "Field goals made cannot exceed attempts",
        ),
        (
            ["2026-02-12", "Ajax Wolves", "Alex", 31, 18, 5, 7, 2, 1, 3, 7, 14, 6, 5, 2, 3],
            "Three-pointers made cannot exceed attempts",
        ),
        (
            ["2026-02-12", "Ajax Wolves", "Alex", 31, 18, 5, 7, 2, 1, 3, 7, 14, 2, 5, 4, 3],
            "Free throws made cannot exceed attempts",
        ),
    ],
)
def test_validate_csv_rejects_invalid_stat_rules(tmp_path, row, expected_message):
    csv_path = tmp_path / "invalid.csv"
    write_csv(csv_path, [row])

    with pytest.raises(ValueError, match=expected_message):
        validate_csv(csv_path)


def test_validate_csv_rejects_invalid_date(tmp_path):
    csv_path = tmp_path / "invalid_date.csv"
    write_csv(
        csv_path,
        [["2026-02-30", "Ajax Wolves", "Alex", 31, 18, 5, 7, 2, 1, 3, 7, 14, 2, 5, 2, 3]],
    )

    with pytest.raises(ValueError, match="Invalid data in row"):
        validate_csv(csv_path)


def test_validate_csv_rejects_missing_columns(tmp_path):
    csv_path = tmp_path / "missing_columns.csv"
    with open(csv_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(HEADERS[:-1])
        writer.writerow(["2026-02-12", "Ajax Wolves", "Alex", 31, 18, 5, 7, 2, 1, 3, 7, 14, 2, 5, 2])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_csv(csv_path)
