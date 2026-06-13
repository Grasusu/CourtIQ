import csv
from datetime import date


def validate_csv(file_path):
    required_columns = {
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
    }
    numeric_columns = required_columns - {"game_date", "opponent", "player"}

    with open(file_path, mode="r", newline="") as file:
        reader = csv.DictReader(file)

        if not reader.fieldnames:
            raise ValueError("CSV file is missing a header row")

        missing = required_columns - set(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

        for row in reader:
            try:
                date.fromisoformat(row["game_date"])
                if not row["player"].strip():
                    raise ValueError("player cannot be empty")

                values = {column: float(row[column]) for column in numeric_columns}
            except (TypeError, ValueError) as e:
                raise ValueError(f"Invalid data in row: {row}") from e

            if values["minutes"] < 0:
                raise ValueError(f"Minutes cannot be negative: {row}")

            if values["turnovers"] < 0:
                raise ValueError(f"Turnovers cannot be negative: {row}")

            if values["fgm"] > values["fga"]:
                raise ValueError(f"Field goals made cannot exceed attempts: {row}")

            if values["three_pm"] > values["three_pa"]:
                raise ValueError(f"Three-pointers made cannot exceed attempts: {row}")

            if values["ftm"] > values["fta"]:
                raise ValueError(f"Free throws made cannot exceed attempts: {row}")
    