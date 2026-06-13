# Analytics

This is the brain of CourtIQ.

Start here before building a large frontend or cloud setup. These modules should be plain Python and easy to unit test.

## MVP Files To Add Next

```txt
metrics.py
trends.py
validators.py
summaries.py
```

## MVP Metrics

- Points per minute.
- Assist/turnover ratio.
- Effective field goal percentage.
- True shooting percentage.
- Recent rolling averages.
- Best and worst games.
- Consistency score.

## Design Rule

Analytics functions should accept normal Python data structures and return normal Python data structures. They should not depend directly on FastAPI request objects.
