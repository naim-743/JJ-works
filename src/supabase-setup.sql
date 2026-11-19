-- JJ Works flats database (Supabase). Run once in the Supabase SQL editor.
-- Sellers post instantly; only the admin (jjworks.info@gmail.com) can hide posts or see seller contacts.

-- ---------- Tables ----------
create table if not exists public.listings (
  id            bigint generated always as identity primary key,
  code          text generated always as ('F-' || lpad(id::text, 3, '0')) stored,
  created_at    timestamptz not null default now(),
  location      text not null check (char_length(location) between 3 and 200),
  size_sqft     integer not null check (size_sqft between 100 and 100000),
  price_bdt     bigint not null check (price_bdt between 0 and 100000000000),
  negotiable    boolean not null default false,
  bedrooms      integer not null check (bedrooms between 0 and 20),
  bathrooms     integer not null check (bathrooms between 0 and 20),
  floor         integer not null check (floor between 0 and 100),
  total_floors  integer not null check (total_floors between 1 and 100),
  parking       boolean not null default false,
  lift          boolean not null default false,
  generator     boolean not null default false,
  details       text check (char_length(details) <= 2000),
  photo_path    text not null,
  lang          text,
  hidden        boolean not null default false,
  sold          boolean not null default false
);

-- Seller's private contact details: never readable by the public.
create table if not exists public.listing_contacts (
  listing_id  bigint primary key references public.listings(id) on delete cascade,
  name        text not null check (char_length(name) between 1 and 120),
  phone       text not null check (char_length(phone) between 6 and 30),
  email       text check (char_length(email) <= 200),
  address     text not null check (char_length(address) between 1 and 300)
);

alter table public.listing_contacts add column if not exists edit_key text;

alter table public.listings enable row level security;
alter table public.listing_contacts enable row level security;

-- ---------- Admin check ----------
create or replace function public.is_admin() returns boolean
language sql stable as $$
  select coalesce(auth.jwt() ->> 'email', '') = 'jjworks.info@gmail.com'
$$;

-- ---------- Row security ----------
drop policy if exists "Public can read visible listings" on public.listings;
create policy "Public can read visible listings" on public.listings
  for select using (hidden = false or public.is_admin());

drop policy if exists "Admin can update listings" on public.listings;
create policy "Admin can update listings" on public.listings
  for update using (public.is_admin()) with check (public.is_admin());

drop policy if exists "Admin can delete listings" on public.listings;
create policy "Admin can delete listings" on public.listings
  for delete using (public.is_admin());

drop policy if exists "Admin can read seller contacts" on public.listing_contacts;
create policy "Admin can read seller contacts" on public.listing_contacts
  for select using (public.is_admin());

-- Table permissions (row security above still decides which rows).
revoke all on public.listings, public.listing_contacts from anon, authenticated;
grant select on public.listings to anon, authenticated;
grant update (hidden, sold) on public.listings to authenticated;
grant delete on public.listings to authenticated;
grant select on public.listing_contacts to authenticated;

-- No insert policies: new posts only come in through submit_listing() below.

-- ---------- Posting a flat ----------
drop function if exists public.submit_listing(jsonb);
create or replace function public.submit_listing(p jsonb) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  new_id   bigint;
  new_code text;
  new_key  text := replace(gen_random_uuid()::text, '-', '') || replace(gen_random_uuid()::text, '-', '');
begin
  if coalesce(p ->> 'website', '') <> '' then          -- spam-bot honeypot
    raise exception 'rejected';
  end if;
  if (select count(*) from listings where created_at > now() - interval '10 minutes') >= 20 then
    raise exception 'too many posts, try again later';
  end if;
  if coalesce(p ->> 'photo_path', '') !~ '^[a-z0-9-]{20,60}\.jpg$' then
    raise exception 'photo missing';
  end if;

  insert into listings (location, size_sqft, price_bdt, negotiable, bedrooms, bathrooms,
                        floor, total_floors, parking, lift, generator, details, photo_path, lang)
  values (trim(p ->> 'location'), (p ->> 'size_sqft')::int, (p ->> 'price_bdt')::bigint,
          coalesce((p ->> 'negotiable')::boolean, false),
          (p ->> 'bedrooms')::int, (p ->> 'bathrooms')::int,
          (p ->> 'floor')::int, (p ->> 'total_floors')::int,
          coalesce((p ->> 'parking')::boolean, false), coalesce((p ->> 'lift')::boolean, false),
          coalesce((p ->> 'generator')::boolean, false),
          nullif(trim(p ->> 'details'), ''), p ->> 'photo_path', p ->> 'lang')
  returning id, code into new_id, new_code;

  insert into listing_contacts (listing_id, name, phone, email, address, edit_key)
  values (new_id, trim(p ->> 'name'), trim(p ->> 'phone'),
          nullif(trim(p ->> 'email'), ''), trim(p ->> 'address'), new_key);

  return jsonb_build_object('code', new_code, 'key', new_key);
end $$;

-- ---------- Seller edits (need the secret edit key from their edit link) ----------
create or replace function public.seller_listing_id(p_code text, p_key text) returns bigint
language sql stable security definer set search_path = public as $$
  select l.id from listings l join listing_contacts c on c.listing_id = l.id
  where l.code = p_code and c.edit_key is not null and length(p_key) >= 32 and c.edit_key = p_key
$$;
revoke all on function public.seller_listing_id(text, text) from public, anon, authenticated;

create or replace function public.get_my_listing(p_code text, p_key text) returns jsonb
language plpgsql stable security definer set search_path = public as $$
declare lid bigint := seller_listing_id(p_code, p_key); r jsonb;
begin
  if lid is null then raise exception 'not found'; end if;
  select to_jsonb(l) || jsonb_build_object('name', c.name, 'phone', c.phone, 'email', c.email, 'address', c.address)
    into r from listings l join listing_contacts c on c.listing_id = l.id where l.id = lid;
  return r;
end $$;

create or replace function public.update_my_listing(p_code text, p_key text, p jsonb) returns void
language plpgsql security definer set search_path = public as $$
declare lid bigint := seller_listing_id(p_code, p_key);
begin
  if lid is null then raise exception 'not found'; end if;
  if p ? 'photo_path' and coalesce(p ->> 'photo_path', '') !~ '^[a-z0-9-]{20,60}\.jpg$' then
    raise exception 'photo missing';
  end if;
  update listings set
    location = trim(p ->> 'location'), size_sqft = (p ->> 'size_sqft')::int, price_bdt = (p ->> 'price_bdt')::bigint,
    negotiable = coalesce((p ->> 'negotiable')::boolean, false),
    bedrooms = (p ->> 'bedrooms')::int, bathrooms = (p ->> 'bathrooms')::int,
    floor = (p ->> 'floor')::int, total_floors = (p ->> 'total_floors')::int,
    parking = coalesce((p ->> 'parking')::boolean, false), lift = coalesce((p ->> 'lift')::boolean, false),
    generator = coalesce((p ->> 'generator')::boolean, false),
    details = nullif(trim(p ->> 'details'), ''),
    photo_path = coalesce(p ->> 'photo_path', photo_path)
  where id = lid;
  update listing_contacts set name = trim(p ->> 'name'), phone = trim(p ->> 'phone'),
    email = nullif(trim(p ->> 'email'), ''), address = trim(p ->> 'address')
  where listing_id = lid;
end $$;

create or replace function public.set_my_listing_sold(p_code text, p_key text, p_sold boolean) returns void
language plpgsql security definer set search_path = public as $$
declare lid bigint := seller_listing_id(p_code, p_key);
begin
  if lid is null then raise exception 'not found'; end if;
  update listings set sold = p_sold where id = lid;
end $$;

create or replace function public.delete_my_listing(p_code text, p_key text) returns void
language plpgsql security definer set search_path = public as $$
declare lid bigint := seller_listing_id(p_code, p_key);
begin
  if lid is null then raise exception 'not found'; end if;
  delete from listings where id = lid;
end $$;

revoke all on function public.submit_listing(jsonb) from public;
revoke all on function public.get_my_listing(text, text) from public;
revoke all on function public.update_my_listing(text, text, jsonb) from public;
revoke all on function public.set_my_listing_sold(text, text, boolean) from public;
revoke all on function public.delete_my_listing(text, text) from public;
grant execute on function public.submit_listing(jsonb) to anon, authenticated;
grant execute on function public.get_my_listing(text, text) to anon, authenticated;
grant execute on function public.update_my_listing(text, text, jsonb) to anon, authenticated;
grant execute on function public.set_my_listing_sold(text, text, boolean) to anon, authenticated;
grant execute on function public.delete_my_listing(text, text) to anon, authenticated;

-- ---------- Photo storage ----------
insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values ('listing-photos', 'listing-photos', true, 5242880, array['image/jpeg'])
on conflict (id) do update
  set public = true, file_size_limit = 5242880, allowed_mime_types = array['image/jpeg'];

drop policy if exists "Anyone can upload a listing photo" on storage.objects;
create policy "Anyone can upload a listing photo" on storage.objects
  for insert to anon, authenticated
  with check (bucket_id = 'listing-photos');

drop policy if exists "Admin can delete listing photos" on storage.objects;
create policy "Admin can delete listing photos" on storage.objects
  for delete using (bucket_id = 'listing-photos' and public.is_admin());
