# Frontend

React + TypeScript frontend for CourtIQ.

The current frontend is an MVP workspace, not a landing page. It connects to the FastAPI backend and supports the first product workflow:

1. Create/select a team.
2. Upload a box-score CSV.
3. View team analytics.
4. Select a player.
5. View player analytics.

## Local Run

From `frontend/`:

```bash
PATH=/Users/alexandrubogdan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:/Users/alexandrubogdan/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin:$PATH \
/Users/alexandrubogdan/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pnpm dev
```

Then open:

```txt
http://127.0.0.1:5173
```

The backend should be running at:

```txt
http://127.0.0.1:8000
```

To override the API URL, set:

```txt
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Build

```bash
PATH=/Users/alexandrubogdan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:/Users/alexandrubogdan/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin:$PATH \
/Users/alexandrubogdan/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/pnpm build
```

## Structure

```txt
src/
├── api/
│   └── client.ts
├── components/
│   ├── charts/
│   ├── layout/
│   └── tables/
├── types/
│   └── api.ts
├── App.tsx
└── styles.css
```
