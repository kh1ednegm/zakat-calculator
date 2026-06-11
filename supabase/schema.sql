-- Zakat Calculator - database schema for Supabase PostgreSQL
-- Run this in the Supabase SQL Editor, OR simply run `alembic upgrade head`
-- from the application (recommended - keeps schema in sync with migrations).

create table if not exists users (
    id varchar(36) primary key,
    email varchar(255) not null unique,
    password_hash varchar(255) not null,
    full_name varchar(120) not null,
    created_at timestamp not null default current_timestamp
);
create index if not exists ix_users_email on users (email);

create table if not exists user_settings (
    user_id varchar(36) primary key references users (id) on delete cascade,
    gold_price_per_gram numeric(12, 2) not null default 0,
    currency varchar(10) not null default 'ر.س',
    zakat_date date,
    preferred_method integer not null default 1
);

create table if not exists savings (
    id varchar(36) primary key,
    user_id varchar(36) not null references users (id) on delete cascade,
    amount numeric(14, 2) not null,
    date date not null,
    description varchar(255)
);
create index if not exists ix_savings_user_id on savings (user_id);

create table if not exists gold_assets (
    id varchar(36) primary key,
    user_id varchar(36) not null references users (id) on delete cascade,
    weight_grams numeric(10, 3) not null,
    karat integer not null,
    purchase_date date not null,
    description varchar(255)
);
create index if not exists ix_gold_assets_user_id on gold_assets (user_id);

create table if not exists debts (
    id varchar(36) primary key,
    user_id varchar(36) not null references users (id) on delete cascade,
    amount numeric(14, 2) not null,
    due_date date not null,
    description varchar(255)
);
create index if not exists ix_debts_user_id on debts (user_id);

create table if not exists withdrawals (
    id varchar(36) primary key,
    user_id varchar(36) not null references users (id) on delete cascade,
    amount numeric(14, 2) not null,
    date date not null,
    description varchar(255)
);
create index if not exists ix_withdrawals_user_id on withdrawals (user_id);
