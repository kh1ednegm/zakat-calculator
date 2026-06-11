# حاسبة الزكاة - Arabic Zakat Calculator (MVP V1)

تطبيق ويب عربي (RTL) لحساب زكاة الأموال والذهب وفق طريقتين فقهيتين معتبرتين، مع حسابات مستخدمين وتقارير PDF.

> هذه الحاسبة أداة مساعدة لحساب الزكاة وفق آراء فقهية معتبرة ولا تغني عن استشارة أهل العلم عند الحاجة.

## المزايا

- إنشاء حساب وتسجيل دخول (بريد إلكتروني / كلمة مرور مشفرة bcrypt)
- تسجيل المدخرات والذهب والديون والسحوبات (إضافة / تعديل / حذف)
- **الطريقة الأولى - الحول المستقل لكل مال**: لكل إيداع وكل قطعة ذهب حول هجري مستقل؛ لا تدخل في الوعاء إلا الأصول التي أتمت سنة هجرية كاملة (مكتبة `hijridate`)
- **الطريقة الثانية - موعد زكاة موحد**: تجمع كل الأصول في تاريخ سنوي واحد يختاره المستخدم
- نسبة الزكاة: **2.5٪** | النصاب = **85 جرام × سعر جرام الذهب** | تقييم الذهب بسعر السوق الحالي مع تعديل العيار
- تقرير PDF شامل (مدخرات، ذهب، ديون، نصاب، نتائج الطريقتين)
- واجهة Bootstrap 5 RTL متجاوبة مع الجوال

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic 2 |
| Database | Supabase PostgreSQL (SQLite fallback for local dev) |
| Frontend | Jinja2 + Bootstrap 5 RTL (Arabic only) |
| PDF | reportlab + arabic-reshaper + python-bidi |
| Deployment | Render (free) + Supabase (free) |

## Project Structure

```
app/
  main.py            # FastAPI entrypoint
  config.py          # Settings (env vars)
  security.py        # bcrypt hashing, CSRF
  deps.py            # Auth/session dependencies, Jinja2 env
  database/          # Engine + session
  models/            # SQLAlchemy models (users, user_settings, savings, gold_assets, debts, withdrawals)
  schemas/           # Pydantic validation
  repositories/      # User-scoped CRUD (data isolation)
  services/          # zakat_service (engine), pdf_service, auth_service
  routers/           # Pages & form handlers
  templates/         # Arabic RTL Jinja2 templates
  static/            # CSS + fonts
alembic/             # Migrations
supabase/            # schema.sql + rls_policies.sql
tests/               # pytest suite
```

## Local Development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit values
alembic upgrade head          # creates tables (SQLite by default)
uvicorn app.main:app --reload
```

Open http://localhost:8000

Or with Docker:

```bash
docker compose up --build
```

## Running Tests

```bash
pytest
```

Covers: Nisab calculation, gold valuation (karat purity), Method 1 (independent hawl, FIFO withdrawals, debts), Method 2 (unified date aggregation).

## Supabase Setup Guide

1. Create a free project at https://supabase.com (choose a strong database password).
2. Go to **Project Settings > Database > Connection string > URI** and copy it.
3. Set `DATABASE_URL` in `.env` using the `postgresql+psycopg2://` scheme:
   `postgresql+psycopg2://postgres:YOUR_PASSWORD@db.YOUR_PROJECT_REF.supabase.co:5432/postgres`
4. Create the schema, either:
   - Run `alembic upgrade head` locally with the Supabase `DATABASE_URL` (recommended), or
   - Paste `supabase/schema.sql` into the Supabase **SQL Editor** and run it.
5. Apply Row Level Security: paste `supabase/rls_policies.sql` into the SQL Editor and run it.

> **Note on auth & RLS:** the application performs email/password auth itself (bcrypt-hashed passwords in the `users` table) and enforces per-user data isolation in every repository query. The RLS policies additionally lock down the tables for any access through Supabase's auto-generated APIs (`anon` / `authenticated` roles), so users can only ever reach their own rows.

## Render Deployment (Free Tier)

1. Push this repository to GitLab/GitHub.
2. On https://render.com create a **New Web Service** and connect the repo.
3. Either select **Docker** as the environment (the included `Dockerfile` is used, fonts downloaded automatically), or use a native Python environment with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `DATABASE_URL` = your Supabase URI (with `postgresql+psycopg2://`)
   - `SECRET_KEY` = long random string (`python -c "import secrets; print(secrets.token_hex(32))"`)
   - `ENV` = `production`
5. Deploy. Migrations run automatically on start.

## Security

- Passwords hashed with **bcrypt** (passlib)
- **CSRF** protection on every form (session-bound token, constant-time comparison)
- Signed, HTTP-only **session cookies** (HTTPS-only in production, SameSite=Lax)
- Input validation with **Pydantic** on all forms
- SQL injection protected via **SQLAlchemy ORM** parameterized queries
- Per-user data isolation in repositories + **Supabase RLS** policies

## PDF Arabic Font

PDF reports use the **Amiri** font for proper Arabic shaping. The Dockerfile downloads it automatically. For local dev, download [Amiri-Regular.ttf](https://github.com/google/fonts/raw/main/ofl/amiri/Amiri-Regular.ttf) into `app/static/fonts/`. Without it, the PDF falls back to Helvetica (Arabic text will not render correctly).
