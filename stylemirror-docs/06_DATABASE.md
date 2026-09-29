# 06 — Database (SQLite for MVP, Postgres-compatible)

Use SQLAlchemy models so you can switch `DATABASE_URL` to Supabase Postgres later. SQLite note: replace `gen_random_uuid()` with a Python `uuid4()` default and `timestamptz` with `DateTime`.

```sql
create table styles (
  id text primary key,            -- 'H01', 'B12'
  type text check (type in ('hair','beard')) not null,
  name text not null,
  prompt_hint text not null,
  thumb_url text not null,
  ref_front_url text, ref_side_url text, ref_back_url text,
  sort_order int default 0,
  is_active boolean default true
);

create table photos (
  id uuid primary key default gen_random_uuid(),
  user_id uuid null,               -- null = anonymous
  session_id text not null,
  storage_path text not null,
  sha256 text not null,
  face_meta jsonb,                 -- bbox, yaw, blur score
  created_at timestamptz default now(),
  expires_at timestamptz not null  -- now() + 24h
);

create table generations (
  id uuid primary key default gen_random_uuid(),
  photo_id uuid references photos(id) on delete cascade,
  hair_style_id text references styles(id),
  beard_style_id text references styles(id),
  view text default 'front',
  status text default 'queued',
  result_path text,
  identity_score real,
  provider text, latency_ms int, cost_usd numeric(8,4),
  error text,
  created_at timestamptz default now()
);

create unique index generations_cache_idx on generations
  (photo_id, coalesce(hair_style_id,''), coalesce(beard_style_id,''), view);
```

## Phase 2 Tables
```sql
create table users (id uuid primary key, email text unique, created_at timestamptz default now());
create table looks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  generation_id uuid references generations(id) on delete cascade,
  share_id text unique, created_at timestamptz default now()
);
```

## Cleanup Job
Background task in `services/cleanup.py` (started in FastAPI lifespan, runs every 15 min): delete `photos` rows (cascades to `generations`) and their storage files where `expires_at < now()`.

## Storage Layout
```
photos/{photo_id}/original.jpg
photos/{photo_id}/out/{generation_id}.jpg
```
Local `storage/` folder (git-ignored), served only through `/v1/files/{path}` with short-lived signed tokens. If moved to Supabase/Firebase Storage later, add a lifecycle rule as a second 24 h safety net.

## Seeding
`scripts/seed_styles.py` reads the catalog in `03_STYLE_CATALOG.md` and upserts into `styles`.
