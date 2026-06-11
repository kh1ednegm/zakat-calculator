-- Row Level Security (RLS) policies for the Zakat Calculator tables.
--
-- Notes:
-- * The FastAPI app connects with the postgres role, which bypasses RLS.
--   Application-level isolation is enforced in app/repositories (every query
--   filters by user_id).
-- * These policies protect the data when it is accessed through Supabase's
--   auto-generated APIs (PostgREST / supabase-js) with the anon or
--   authenticated roles, ensuring users can only ever access their own rows.
-- * auth.uid() returns the Supabase Auth user id; it is compared with the
--   user_id column (cast to text since the app stores string UUIDs).

alter table users enable row level security;
alter table user_settings enable row level security;
alter table savings enable row level security;
alter table gold_assets enable row level security;
alter table debts enable row level security;
alter table withdrawals enable row level security;

-- users: a user can only see and manage their own row
create policy users_select_own on users
    for select to authenticated using (id = auth.uid()::text);
create policy users_update_own on users
    for update to authenticated using (id = auth.uid()::text);
create policy users_delete_own on users
    for delete to authenticated using (id = auth.uid()::text);

-- user_settings
create policy user_settings_select_own on user_settings
    for select to authenticated using (user_id = auth.uid()::text);
create policy user_settings_insert_own on user_settings
    for insert to authenticated with check (user_id = auth.uid()::text);
create policy user_settings_update_own on user_settings
    for update to authenticated using (user_id = auth.uid()::text);
create policy user_settings_delete_own on user_settings
    for delete to authenticated using (user_id = auth.uid()::text);

-- savings
create policy savings_select_own on savings
    for select to authenticated using (user_id = auth.uid()::text);
create policy savings_insert_own on savings
    for insert to authenticated with check (user_id = auth.uid()::text);
create policy savings_update_own on savings
    for update to authenticated using (user_id = auth.uid()::text);
create policy savings_delete_own on savings
    for delete to authenticated using (user_id = auth.uid()::text);

-- gold_assets
create policy gold_assets_select_own on gold_assets
    for select to authenticated using (user_id = auth.uid()::text);
create policy gold_assets_insert_own on gold_assets
    for insert to authenticated with check (user_id = auth.uid()::text);
create policy gold_assets_update_own on gold_assets
    for update to authenticated using (user_id = auth.uid()::text);
create policy gold_assets_delete_own on gold_assets
    for delete to authenticated using (user_id = auth.uid()::text);

-- debts
create policy debts_select_own on debts
    for select to authenticated using (user_id = auth.uid()::text);
create policy debts_insert_own on debts
    for insert to authenticated with check (user_id = auth.uid()::text);
create policy debts_update_own on debts
    for update to authenticated using (user_id = auth.uid()::text);
create policy debts_delete_own on debts
    for delete to authenticated using (user_id = auth.uid()::text);

-- withdrawals
create policy withdrawals_select_own on withdrawals
    for select to authenticated using (user_id = auth.uid()::text);
create policy withdrawals_insert_own on withdrawals
    for insert to authenticated with check (user_id = auth.uid()::text);
create policy withdrawals_update_own on withdrawals
    for update to authenticated using (user_id = auth.uid()::text);
create policy withdrawals_delete_own on withdrawals
    for delete to authenticated using (user_id = auth.uid()::text);
