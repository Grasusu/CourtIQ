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

## 4. Supabase Storage

The backend includes both local and Supabase upload storage adapters. To enable persistent CSV storage:

1. In Supabase, open Storage and create a private bucket named `courtiq-uploads`.
2. In Supabase project settings, create or copy a server-side secret key.
3. Add the following environment variables to the Render backend:

```txt
UPLOAD_STORAGE_BACKEND=supabase
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_SECRET_KEY=sb_secret_...
SUPABASE_STORAGE_BUCKET=courtiq-uploads
```

4. Redeploy the Render service and test one CSV upload.

The secret key bypasses Storage RLS and must exist only in Render. Never add it to Vercel, the frontend, GitHub, or a local file that is committed.

Stored object paths are isolated by CourtIQ user and team:

```txt
users/{owner_id}/teams/{team_id}/{generated_file_id}.csv
```

If `UPLOAD_STORAGE_BACKEND` is omitted or set to `local`, the backend continues to use `LOCAL_UPLOAD_DIR`.
