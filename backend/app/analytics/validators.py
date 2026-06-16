"""CSV validation and parsing for CourtIQ box-score uploads."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path


REQUIRED_COLUMNS = [
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

INTEGER_COLUMNS = {
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
}


@dataclass(frozen=True)
class BoxScoreRow:
    game_date: date
    opponent: str
    player: str
    minutes: float
    points: int
    rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fgm: int
    fga: int
    three_pm: int
    three_pa: int
    ftm: int
    fta: int


def validate_csv(file_path: str | Path) -> None:
    """Validate a CSV file and raise ValueError for bad data."""
    parse_box_score_csv(file_path)


def parse_box_score_csv(file_path: str | Path) -> list[BoxScoreRow]:
    """Validate and parse a box-score CSV into typed rows."""
    path = Path(file_path)
    parsed_rows: list[BoxScoreRow] = []

    with path.open(mode="r", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file is missing a header row")

        missing = set(REQUIRED_COLUMNS) - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        for row_number, row in enumerate(reader, start=2):
            parsed_row = _parse_row(row, row_number)
            _validate_stat_rules(parsed_row, row)
            parsed_rows.append(parsed_row)

    return parsed_rows


def _parse_row(row: dict[str, str], row_number: int) -> BoxScoreRow:
    try:
        game_date = date.fromisoformat(row["game_date"])
        opponent = row["opponent"].strip()
        player = row["player"].strip()

        if not opponent:
            raise ValueError("opponent cannot be empty")

        if not player:
            raise ValueError("player cannot be empty")

        minutes = _parse_float(row["minutes"], "minutes", row_number)
        values = {
            column: _parse_int(row[column], column, row_number)
            for column in INTEGER_COLUMNS
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Invalid data in row {row_number}: {row}") from exc

    parsed_row = BoxScoreRow(
        game_date=game_date,
        opponent=opponent,
        player=player,
        minutes=minutes,
        points=values["points"],
        rebounds=values["rebounds"],
        assists=values["assists"],
        steals=values["steals"],
        blocks=values["blocks"],
        turnovers=values["turnovers"],
        fgm=values["fgm"],
        fga=values["fga"],
        three_pm=values["three_pm"],
        three_pa=values["three_pa"],
        ftm=values["ftm"],
        fta=values["fta"],
    )

    if parsed_row.minutes < 0:
        raise ValueError(f"Minutes cannot be negative: {row}")

    if parsed_row.turnovers < 0:
        raise ValueError(f"Turnovers cannot be negative: {row}")

    for column in INTEGER_COLUMNS - {"turnovers"}:
        if getattr(parsed_row, column) < 0:
            raise ValueError(f"{column} cannot be negative: {row}")

    return parsed_row


def _validate_stat_rules(parsed_row: BoxScoreRow, raw_row: dict[str, str]) -> None:
    if parsed_row.fgm > parsed_row.fga:
        raise ValueError(f"Field goals made cannot exceed attempts: {raw_row}")

    if parsed_row.three_pm > parsed_row.three_pa:
        raise ValueError(f"Three-pointers made cannot exceed attempts: {raw_row}")

    if parsed_row.ftm > parsed_row.fta:
        raise ValueError(f"Free throws made cannot exceed attempts: {raw_row}")


def _parse_float(value: str, column: str, row_number: int) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{column} must be numeric in row {row_number}") from exc


def _parse_int(value: str, column: str, row_number: int) -> int:
    try:
        numeric_value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{column} must be numeric in row {row_number}") from exc

    if not numeric_value.is_integer():
        raise ValueError(f"{column} must be a whole number in row {row_number}")

    return int(numeric_value)
