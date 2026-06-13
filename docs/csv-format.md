# CSV Format

The MVP uses box-score CSV uploads.

## Required Columns

```txt
game_date
opponent
player
minutes
points
rebounds
assists
steals
blocks
turnovers
fgm
fga
three_pm
three_pa
ftm
fta
```

## Example

```csv
game_date,opponent,player,minutes,points,rebounds,assists,steals,blocks,turnovers,fgm,fga,three_pm,three_pa,ftm,fta
2026-02-12,Ajax Wolves,Alex,31,18,5,7,2,1,3,7,14,2,5,2,3
```

## Validation Rules

- Required columns must be present.
- `game_date` must be a valid date.
- Numeric stat fields must be numbers.
- Shot makes cannot be greater than attempts.
- Minutes cannot be negative.
- Turnovers cannot be negative.
- A player name cannot be empty.

Good validation is a strong project feature because it shows the app handles messy real-world data.
