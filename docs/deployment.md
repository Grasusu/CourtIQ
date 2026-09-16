# Deployment Plan

Recommended low-cost setup:

```txt
Vercel frontend
   |
Render FastAPI backend
   |
Supabase PostgreSQL
```

Supabase Storage can be added later for uploaded CSV files. For the first public demo, local Render disk storage is enough as long as demo uploads are not treated as permanent files.

## Accounts Needed

- GitHub account with this repository pushed.
- Supabase account for Postgres.
- Render account for the FastAPI backend.
- Vercel account for the React frontend.

You do not need AWS credits for this version.

## 1. Supabase

1. Create a Supabase project.
2. Open project settings and copy the Postgres connection string.
3. Use the SQLAlchemy/psycopg format in Render:

```txt
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

Keep this value private. Do not commit it.

## 2. Render Backend

Use `render.yaml` from the repository root or create the service manually.

Manual settings:

```txt
Service type: Web Service
Root directory: backend
Build command: pip install -r requirements.txt
Start command: sh start.sh
Health check path: /health
```

Environment variables:

```txt
DATABASE_URL=postgresql+psycopg://...
JWT_SECRET_KEY=<long random secret>
CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
LOCAL_UPLOAD_DIR=local_uploads
```

`start.sh` runs Alembic migrations before starting the API.

## 3. Vercel Frontend

Import the repo in Vercel and point the project to `frontend/`.

Settings:

```txt
Framework: Vite
Build command: pnpm build
Output directory: dist
Install command: pnpm install --frozen-lockfile
```

Environment variable:

```txt
VITE_API_BASE_URL=https://your-render-api.onrender.com
```

After Vercel gives you the frontend URL, add it to `CORS_ALLOWED_ORIGINS` in Render and redeploy the backend.

## 4. Later: Supabase Storage

The current app has a local upload storage adapter. A future `SupabaseUploadStorage` adapter can replace local disk storage and save CSV files in a private Supabase Storage bucket.

Do this after the public demo works with Vercel + Render + Supabase Postgres.
