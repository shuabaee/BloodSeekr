# BloodSeekr: run and demonstrate

## 1. Extract and restore your private configuration

1. Extract BloodSeekr-Final-Project.zip into a **new folder**, separate from your working copy. Its root folder is BloodSeekr-Final.
2. Copy the `.env` from your existing working project into BloodSeekr-Final, beside `manage.py`. Keep your original `DJANGO_SECRET_KEY` and `DATABASE_URL`. Add the optional Maps variables only if you want Google Maps (section 7). These credentials are intentionally excluded from the ZIP.
3. If you already have uploaded files in an existing `media/` directory, copy that directory into the new folder too. Attachment references use the same database and need their corresponding local files.
4. Open PowerShell in BloodSeekr-Final. The following commands use the virtual environment's Python directly, so PowerShell activation policy cannot block them.

## 2. Exact Windows commands

Python 3.12 or later is suitable for the supplied dependency range. The original requirements.txt is unchanged; the current version was validated against Django 6.1.1 (the earlier baseline was also tested on 5.2.17).

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py showmigrations
.\.venv\Scripts\python.exe manage.py migrate --plan
```

Expected: system check passes; no model changes; your previously applied migrations show `[X]`; no new migration operations are planned. **No new migrations were created in this deliverable.** If the plan is empty, no database migration is required. You can confirm the no-op using:

```powershell
.\.venv\Scripts\python.exe manage.py migrate
```

If your existing database instead shows pending original migrations, compare them with the preserved migration history before applying them. Do not reset migrations, use `--fake`, flush the database or recreate the Supabase project.

Add missing compatibility data and run isolated tests:

```powershell
.\.venv\Scripts\python.exe manage.py seed_blood_data
.\.venv\Scripts\python.exe manage.py test --settings=config.test_settings
```

Add fictional facilities only if you want class demo data:

```powershell
.\.venv\Scripts\python.exe manage.py seed_demo_facilities
```

Use your existing administrator. If you do not have one:

```powershell
.\.venv\Scripts\python.exe manage.py createsuperuser
```

Start the app:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
```

Open http://127.0.0.1:8000/ and http://127.0.0.1:8000/admin/.

On macOS/Linux, use `python3 -m venv .venv` and `.venv/bin/python` in place of `.\.venv\Scripts\python.exe`.

## 3. Complete workflow to demonstrate

1. Register a requester account and a donor account. Use separate browser profiles or an incognito window so both sessions stay signed in.
2. Update both accounts' first/last name, email and phone. On the donor account select **O-**, a valid date of birth and **Available to donate**. Choose **Philippines → Cebu → Cebu City**, then use GPS or click the map near the collection center. Save the profile. City centers are approximate; a precise pin makes radius matching more useful.
3. In donor Settings, choose a matching radius such as 25 km and enable emergency notifications. Keep donor profile visible for the discovery screenshot.
4. In the requester account, create a request for **A+**, **1 unit**, a needed date of today or later, and a collection facility. Click **Use facility location** to fill its saved address/pin, then confirm the point. Choose urgency. Upload `docs/DEMO_SUPPORTING_DOCUMENT.pdf` or another test PDF if demonstrating attachments. New requests and documents start with pending verification.
5. In admin, review the donor Profile, Blood request and Request attachment. Only staff can verify them. Mark them verified after reviewing your demonstration data. Unverified profiles/requests may participate in coordination; facilities still confirm screening.
6. In **Blood requests → My matches**, toggle **Map** to see pins and the matching radius. Switch back to **List**, or open a pin popup. Open the request and click **Offer to donate**. Add a coordination note. A notification appears for the requester.
7. In the requester's My requests, open the request and **Accept** the offer. The request becomes in progress; the donor receives an update. Accepted offers reveal relevant contact information for coordination.
8. Click **Record donation**. You may first save a scheduled record with pending screening and zero donated units. Later update the same record to passed screening, completed status, a date of today or earlier and 1.00 units donated.
9. The donor response becomes completed and the request becomes fulfilled when completed, passed donation units reach the requested amount. The donor sees their donation history and a notification.
10. In Notifications, mark one notification or all as read. Confirm the navigation badge updates.
11. Test **Decline**, **Withdraw offer** and **Cancel request** on separate demo requests. Each donor has one response per request; a withdrawn/declined response is retained rather than creating duplicates.
12. Click Logout. Protected pages redirect to login. Logout uses a POST form with CSRF protection.

## 4. Exact Supabase verification

1. Open your **existing** Supabase project. Do not create a replacement database.
2. Open **Table Editor** and choose the `public` schema. Refresh after saving records in Django.
3. Confirm these tables exist: `auth_user`, `profile`, `user_settings`, `blood_type`, `blood_compatibility`, `facility`, `blood_request`, `request_attachment`, `notification`, `donor_response`, `donation_record`. Django's system tables should remain as well.
4. Find your registered username in `auth_user`. Its ID should match `profile.user_id` and `user_settings.user_id`.
5. Confirm Profile blood type uses `blood_type_code`, and settings include `match_radius_km`.
6. In `blood_type`, expect the eight ABO/Rh codes. After seeding, `blood_compatibility` has 64 pairs if all lookup pairs were previously missing. The standard red-cell matrix has 27 compatible pairs; existing custom pair values are preserved.
7. New location values may start with `BS1:`. This is the intentionally encoded location in the existing column, not a new entity. Check the decoded point using `docs/VERIFY_SUPABASE.sql`; the app shows the human-readable address. Existing plain locations remain valid. Confirm `blood_request.requester_id`, `required_blood_type_code`, optional `facility_id`, patient name, units, urgency, needed date, location, verification status and request status match your demo.
8. Confirm the uploaded document in `request_attachment`: its `blood_request_id`, `uploaded_by_user_id`, document type, pending/verified status and relative storage reference in `file_url`. The bytes live in the private local `media/` directory, not the PostgreSQL table.
9. Confirm donor and requester notification rows in `notification`; mark one read in the application and refresh to see `is_read=true`.
10. Confirm one `donor_response` row for each `(blood_request_id, donor_user_id)` pair. On accepting/completing, its response status changes.
11. Confirm one `donation_record` at most per `donor_response_id`, with facility, date, decimal units and statuses. Completed units trigger request fulfillment when sufficient.
12. Open SQL Editor and run the **read-only** queries in `docs/VERIFY_SUPABASE.sql` to inspect migration history, foreign keys, unique constraints, row counts and duplicate checks. Do not include credentials or identifiable medical details in class screenshots.

The development environment could not reach your live Supabase database. The shipped schema was verified against the original models/migrations and approved ERD; no remote data was changed here.

## 5. Class screenshot checklist

- [ ] Folder structure showing the ten feature apps under `apps/` and separate template/static feature folders.
- [ ] Successful `manage.py check`, `makemigrations --check --dry-run`, and isolated tests.
- [ ] `showmigrations` with the original migrations applied.
- [ ] Registration page and successful login.
- [ ] Home dashboard showing blood type, availability, request counts and matches.
- [ ] Profile with updated personal details, blood type, location, availability and verification status.
- [ ] Settings with notification switches, visibility and matching radius.
- [ ] Create request form with meaningful valid data and optional supporting document.
- [ ] My requests and request detail page with status and verification.
- [ ] Supporting document link and staff attachment verification.
- [ ] Donor's matching request and submitted offer.
- [ ] Requester's accepted response and donation recording form.
- [ ] Completed donation history and fulfilled request.
- [ ] Notifications before and after marking as read.
- [ ] Collection facility list, detail, contact/directions and active linked requests.
- [ ] Staff add/edit facility with collection pin.
- [ ] Country → province/state → city selectors and saved GPS/selected pin.
- [ ] Blood requests in Map view, pin popup and My matches radius.
- [ ] Request form using a facility pin, and owner Edit point page.
- [ ] Supabase Table Editor rows/relationships for the workflow, using synthetic class data.
- [ ] Narrow/mobile viewport showing usable navigation and forms.

## 6. Limitations and operational choices

- Live Supabase connectivity and migration state could not be inspected here. Tests use an isolated SQLite database and the existing migrations. Validate PostgreSQL through the steps above before submission.
- Country/province/city selection now provides approximate city coordinates; map selection or GPS provides a more specific point. Radius matching uses straight-line Haversine distance when both locations have coordinates. Old plain-text locations remain supported through same-city matching until edited. No background conversion of existing rows is performed.
- The bundled catalog covers 249 countries, 1,656 Philippine cities/municipalities, and major towns/cities worldwide. It is a snapshot, not every settlement or barangay. Use **My city is not listed**, enter the city name and pick a point when necessary. Sources and licenses are in `docs/licenses/GEOGRAPHIC_DATA.md`.
- City-center/area-centroid pins are approximate and do not identify a facility entrance. Move the pin or use GPS for that purpose. GPS needs browser permission and a secure origin (HTTPS or localhost). Radius is not driving distance; routes come from the directions link.
- Google Maps integration is optional and requires your own restricted browser API key. The standard Leaflet/OpenStreetMap map works without a key. Both need internet for the background map. The local city dropdowns and entered coordinates remain usable if the map service is unavailable. Live Google Maps billing/key authorization was not verified without your key.
- To preserve the approved ERD, structured location data uses a compact `BS1:` JSON value in the existing `profile.location`, `blood_request.location` and `facility.address` text columns. Country/area/city codes, coordinates, street description and point quality are encoded there; `facility.city` remains readable text. Forms, templates, admin and map services decode it. Existing column lengths are enforced; long street descriptions may need shortening. No new tables, columns or migrations were added.
- Blood compatibility is red-cell coordination data, sourced from American Red Cross guidance. This app does not model plasma, platelets, appointment scheduling or clinical eligibility. Facilities confirm screening and crossmatching.
- Verification is staff-driven through existing Django admin fields; users cannot self-verify. Staff can add/edit real facilities in the app or admin, including a collection pin and contact details. Facility verification stays in admin. The optional demo facilities are fictional and explicitly unverified.
- Email defaults to Django's console backend. Real delivery requires SMTP settings in `.env`. In-app notifications work independently. Emergency matching notifications respect the emergency preference; hiding a donor profile hides discovery but still lets that donor view/respond to matches.
- Documents are private local files with references in the existing `file_url` column. Back up `media/` with your database references. Existing external URL references are preserved, but the private download endpoint handles locally uploaded `request_documents/` paths only. No Supabase Storage integration is added.
- Completed donation records are read-only in the normal app; scheduled/cancelled records can be updated while the accepted response/request remains eligible. Staff use the application recording workflow too. Historical corrections would need a separately approved administration workflow.
- Closed requests cannot be reopened through normal forms. Withdrawn or declined responses cannot be submitted again for the same request; the unique ERD relationship is preserved.
- Matching is appropriate for classroom datasets and does some per-record evaluation; large-scale search optimization, external messaging, deployment and advanced clinical rules are outside this final-project scope.

## 7. Optional Google Maps setup

The app works immediately with the standard Leaflet/OpenStreetMap map. To switch to Google Maps:

1. In your Google Cloud project, enable billing and **Maps JavaScript API**. Create a browser API key.
2. Set application restrictions to **Websites / HTTP referrers**. Allow `http://localhost:8000/*` and `http://127.0.0.1:8000/*` for local development, plus your exact HTTPS production host when deployed. Restrict the key to Maps JavaScript API. Set billing alerts/quotas in your Cloud project.
3. Add to your private `.env`:

```dotenv
GOOGLE_MAPS_BROWSER_KEY=your_restricted_browser_key
GOOGLE_MAPS_MAP_ID=DEMO_MAP_ID
```

4. Restart Django and reload the page. Open Blood requests → Map. The shared adapter selects Google Maps when a key is configured; otherwise it uses Leaflet. Picker, request detail and facility detail maps use the same adapter.
5. `DEMO_MAP_ID` supports trying advanced markers; use a Maps JavaScript map ID from your own Cloud project for deployment. A map ID is not an API key. No Places, Geocoding or Routes API is required: the bundled city catalog supplies dropdowns and coordinates, and directions open Google Maps in a separate tab.

A browser Maps key is intentionally sent to the browser. Protect it with website/API restrictions. Never reuse a server key or your Django secret. Keep `.env` private. Google's instructions: https://developers.google.com/maps/documentation/javascript/get-api-key and https://developers.google.com/maps/documentation/javascript/advanced-markers/start

## 8. Upgrading existing locations and facilities

- Copy your existing `.env` and `media/` into the extracted new project; use the same Supabase database. No migration is needed for these improvements.
- Existing donor locations are preserved. Edit Profile once, choose country/area/city and confirm a point to enable distance-based matches across nearby cities.
- Staff edit existing real facilities to save collection entrance pins. The display city is populated from the selected city. Verify facilities in admin after checking the information.
- An owner can open an active request → **Edit point** to update its facility/location. Donors who already responded receive an in-app collection-location notification. Closed request locations cannot be changed.
- The optional `seed_demo_facilities` command adds fictional mapped facilities; if a prior BloodSeekr demo row still has its original `Demo address…`, it updates only that demo row's address. Existing real facility addresses are not rewritten.
- Community pins show blood need, urgency and collection location. Patient names and contact details are omitted; request-detail access still requires ownership, staff status, an existing response or donor eligibility. Donor profile coordinates are not included in community pins.

## 9. Changed files and verification

See `docs/CHANGED_FILES.md` for every changed/new path, `docs/TEST_REPORT.md` for the test results and `docs/LOCATION_AND_MAPS.md` for the encoding and matching behavior. The original models, requirements and migrations remain byte-for-byte unchanged. No new migrations were created.
