# Frontend

React + TypeScript frontend for CourtIQ.

The frontend should come after the backend can return real analytics data. For the MVP, focus on a practical coach/player workflow instead of a marketing page.

## MVP Screens

1. Upload game CSV.
2. Team dashboard.
3. Player profile.
4. Player comparison.

## Recommended Structure

```txt
src/
├── api/
├── components/
│   ├── charts/
│   ├── forms/
│   ├── layout/
│   └── tables/
├── pages/
└── types/
```

Use Recharts or ECharts when the backend analytics are ready.
