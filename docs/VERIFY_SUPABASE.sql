-- Read-only checks. Run in your existing Supabase SQL Editor.
-- Application/Django auth tables:
SELECT tablename FROM pg_tables
WHERE schemaname = 'public' AND tablename IN
('auth_user','profile','user_settings','blood_type','blood_compatibility','facility',
 'blood_request','request_attachment','notification','donor_response','donation_record')
ORDER BY tablename;

-- Preserve the original profiles app label in migration history.
SELECT app, name, applied FROM public.django_migrations
WHERE app IN ('profiles','user_settings','blood_data','facilities','blood_requests','notifications','donations')
ORDER BY app, name;

-- Existing foreign keys, composite key, one-to-one and unique constraints:
SELECT c.relname AS table_name, con.conname AS constraint_name,
       con.contype AS constraint_type, pg_get_constraintdef(con.oid) AS definition
FROM pg_constraint con
JOIN pg_class c ON c.oid = con.conrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname='public' AND c.relname IN
('profile','user_settings','blood_type','blood_compatibility','facility','blood_request',
 'request_attachment','notification','donor_response','donation_record')
ORDER BY c.relname, con.conname;

-- These duplicate checks should return no rows.
SELECT blood_request_id, donor_user_id, COUNT(*)
FROM public.donor_response GROUP BY blood_request_id, donor_user_id HAVING COUNT(*) > 1;
SELECT donor_response_id, COUNT(*)
FROM public.donation_record GROUP BY donor_response_id HAVING COUNT(*) > 1;
SELECT user_id, COUNT(*) FROM public.profile GROUP BY user_id HAVING COUNT(*) > 1;
SELECT user_id, COUNT(*) FROM public.user_settings GROUP BY user_id HAVING COUNT(*) > 1;

-- Aggregate counts without displaying personal/medical information.
SELECT 'blood_type' AS table_name, COUNT(*) AS rows FROM public.blood_type
UNION ALL SELECT 'blood_compatibility',COUNT(*) FROM public.blood_compatibility
UNION ALL SELECT 'facility',COUNT(*) FROM public.facility
UNION ALL SELECT 'blood_request',COUNT(*) FROM public.blood_request
UNION ALL SELECT 'request_attachment',COUNT(*) FROM public.request_attachment
UNION ALL SELECT 'donor_response',COUNT(*) FROM public.donor_response
UNION ALL SELECT 'notification',COUNT(*) FROM public.notification
UNION ALL SELECT 'donation_record',COUNT(*) FROM public.donation_record;
SELECT is_compatible,COUNT(*) FROM public.blood_compatibility GROUP BY is_compatible;

-- New tagged locations live in the EXISTING columns. Synthetic demo data only.
-- For values produced by the app, inspect codes and coordinates without schema writes.
SELECT id,
       (substring(location from 5)::jsonb)->>0 AS country_code,
       (substring(location from 5)::jsonb)->>1 AS area_id,
       (substring(location from 5)::jsonb)->>2 AS city_id,
       (substring(location from 5)::jsonb)->>3 AS latitude,
       (substring(location from 5)::jsonb)->>4 AS longitude,
       (substring(location from 5)::jsonb)->>6 AS point_quality
FROM public.blood_request WHERE location LIKE 'BS1:%';

SELECT id, city, is_verified,
       (substring(address from 5)::jsonb)->>3 AS latitude,
       (substring(address from 5)::jsonb)->>4 AS longitude
FROM public.facility WHERE address LIKE 'BS1:%';
