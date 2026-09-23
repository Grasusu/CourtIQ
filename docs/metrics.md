# Metrics

CourtIQ keeps its analytics explainable. Every number shown in the interface is calculated from recorded box scores, and predictive output includes its sample size and uncertainty.

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

## Predictive Intelligence

### Next-game forecast

The scoring forecast uses weighted least-squares linear regression over at most the latest eight games. Game `n` receives weight `n + 1`, so recent performances influence the result more than older ones.

The displayed range is based on the model's weighted residual error. A volatile scoring history therefore produces a wider range than a stable one. Confidence is reported as low, medium, or high using sample size and residual error; fewer than three games returns an insufficient-data state instead of a prediction.

This is a statistical forecast, not a guaranteed result. Opponent strength, injuries, role changes, and lineup context are not yet modeled.

### Team-relative impact profile

Each player is ranked against teammates with recorded data across five dimensions:

| Dimension | Input signal |
| --- | --- |
| Scoring | Points per minute |
| Playmaking | Assists per minute adjusted by assist/turnover ratio |
| Rebounding | Rebounds per minute |
| Defense | Steals plus blocks per minute |
| Efficiency | True shooting percentage |

Tie-aware percentile ranks produce a 0-100 profile and an explainable role label such as `Primary creator`, `Floor general`, or `Defensive disruptor`.

### Change detection

- Recent form compares the latest three games with the immediately preceding sample.
- Weighted trend reports the expected scoring change per game.
- The latest game is flagged when its standard score is materially different from the prior baseline.
- Recommendations target the player's weakest team-relative dimension and account for a declining forecast.

## Summary Examples

```txt
Alex's scoring efficiency improved over the last 5 games, driven by better three-point shooting and stable turnover volume.
```

```txt
Jordan is rebounding above the team average but has a lower assist/turnover ratio than other guards.
```

The summaries should be simple, explainable, and based on calculated numbers.
