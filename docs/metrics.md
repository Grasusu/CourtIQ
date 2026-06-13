# Metrics

These are the first analytics calculations to build.

## Basic Metrics

| Metric | Formula |
| --- | --- |
| Points per minute | `points / minutes` |
| Assist/turnover ratio | `assists / turnovers` |
| Effective FG% | `(fgm + 0.5 * three_pm) / fga` |
| True shooting % | `points / (2 * (fga + 0.44 * fta))` |
| Turnovers per minute | `turnovers / minutes` |

Handle division by zero intentionally. Do not let the API crash because a player had zero attempts or zero turnovers.

## Trend Metrics

- Last 5 game averages.
- Recent average compared with season average.
- Best scoring game.
- Worst efficiency game.
- Consistency score from game-to-game variation.

## Summary Examples

```txt
Alex's scoring efficiency improved over the last 5 games, driven by better three-point shooting and stable turnover volume.
```

```txt
Jordan is rebounding above the team average but has a lower assist/turnover ratio than other guards.
```

The summaries should be simple, explainable, and based on calculated numbers.
