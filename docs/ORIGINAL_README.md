# BloodSeekr

BloodSeekr is a Django final project reorganized using the CSIT327 vertical-slicing structure and configured for Supabase PostgreSQL.

## Feature slices

- `apps/login/` - login and logout authentication behavior
- `apps/register/` - user registration and validation
- `apps/home/` - authenticated BloodSeekr home/dashboard
- `apps/profile/` - donor profile data, forms, views, and migrations
- `apps/user_settings/` - user preferences/settings data, forms, views, and migrations

Feature HTML is stored under `templates/<feature>/`.
Feature CSS, JavaScript, and images are stored under `static/css/<feature>/`, `static/js/<feature>/`, and `static/images/<feature>/`.

## First-time setup

1. Create and activate a virtual environment.
2. Install requirements:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env`.
4. In Supabase, open **Connect -> Session Pooler -> URI** and copy the exact connection URI.
5. Put that URI in `DATABASE_URL` inside `.env`.
6. Generate a Django secret key and put it in `DJANGO_SECRET_KEY`.
7. Run:
   - `python manage.py check`
   - `python manage.py makemigrations`
   - `python manage.py migrate`
   - `python manage.py runserver`

## Important database note

The Profile slice is now physically located at `apps/profile/`, but its Django app label remains `profiles` so an existing BloodSeekr Supabase database that already has the `profiles_profile` table and `profiles` migration history remains compatible.

Do not commit `.env`.
