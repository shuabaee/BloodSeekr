# BloodSeekr verification report

Date: October 6, 2026. Source: the attached BloodSeekr-ERD-Models.zip, approved GABISON_ERD.pdf and CSIT327 vertical slicing/Supabase guide.

## Results

- Final suite: **60 tests passed** on Django **6.1.1**, using isolated in-memory SQLite and the project's original migrations.
- Earlier baseline suite: 36 tests passed on Django 5.2.17 before the final five edge-case additions.
- `python manage.py check`: no issues with the normal project configuration.
- `python manage.py makemigrations --settings=config.test_settings --check --dry-run`: no changes detected.
- All original migrations applied successfully to the isolated local database.
- Byte comparison: all **20** original application migration/package files are unchanged (10 numbered migrations and 10 package initializers).
- All original model definitions and requirements.txt are unchanged.
- `compileall` passed for feature apps and project configuration.
- `collectstatic --dry-run` passed.
- Major page templates and staff admin screens rendered successfully in tests.
- Live HTTP smoke through a running Django development server passed registration, login, profile, settings, request creation, matching, offer, acceptance, completed donation, automatic fulfillment, notification marking and logout. Requests used real HTTP sessions and CSRF tokens, with synthetic data in a separate local SQLite database.

## Location, facilities, maps and UI update

- Added 19 regression tests: valid geographic hierarchy, city fallback coordinates, custom cities, malformed coordinates/tagged values, original column lengths, cross-city distance matching, legacy locality compatibility, catalog filtering, map authentication/de-identification, filter/unpinned behavior, radius preferences, facility prefill and staff ownership, active owner point updates/notifications and closed-request protection.
- Added legacy preservation checks: changing profile/facility contact details alone keeps existing plain location/address values and facility city unchanged.
- Both Community and facility-linked request cards enforce the existing patient-detail access rule. Ineligible viewers see the blood need and collection point without patient names.
- Real browser workflows passed on Chromium, desktop 1440×1000 and mobile 390×844: login/logout, country/province/city cascade, GPS profile save, settings radius, facility-linked request/document creation, matching map pins/popups, list/map toggle, donor offer, acceptance, completed donation with default facility, automatic fulfillment, staff facility creation, notification marking and mobile layout without horizontal overflow.
- Additional focused browser checks passed registration, an actual map click persisted to the profile, presence of the matching-radius circle, and fallback to Leaflet after a rejected Google script load.
- No JavaScript page errors in those workflows. Browser tests used synthetic data in a separate local SQLite database; no Supabase writes.
- Referrer-Policy response now uses `strict-origin-when-cross-origin`: external maps receive the origin needed for service authorization/attribution, without request paths or patient information.
- The new location/maps package, facility forms and frontend require no extra pip dependency. Derived geography data and Leaflet are bundled with attribution/licenses.

## Coverage

| Workflow | Validated behavior |
|---|---|
| Registration | Django User creation, email/username validation, profile/settings defaults |
| Login/logout | Successful authentication, safe next redirect, external redirect rejection, POST logout |
| Profile | Existing update flow, blood-type FK, no user self-verification, changed blood type clears verification |
| Settings | Notification and visibility updates; radius bounds |
| Request creation | Request owner, pending verification, open status; positive units, future/today needed date, urgency validation |
| Request access | Owner and eligible donor access; unrelated users denied; authenticated page protection |
| Matching | Blood compatibility direction, explicit false pairs, availability, self-exclusion, locality/radius, expired/closed requests |
| Privacy/preferences | Hidden donors omitted from discovery while retaining voluntary response; emergency alert preference |
| Donor response | Offer, duplicate prevention at view and database level, accept, decline, withdraw, permission checks |
| Documents | Private storage reference, file signature validation, owner download, donor download/upload denial |
| Notifications | Matching request, response, status, donation events; own-item and bulk read controls |
| Donations | Accepted response required, authorized recorder, valid screening/units/date, scheduled record updates, one-to-one uniqueness |
| Fulfillment | Completed passed units fulfill request; response becomes completed; completed record prevents withdrawal |
| Verification | Staff review updates and notification; rejected requests cannot record donations |
| Facilities/dashboard | List/detail and dashboard rendering; donor history visibility |
| Security | CSRF enforcement on mutations, ownership, POST-only state changes |
| Lookup seed | Idempotent; existing custom compatibility values remain unchanged |

## Reproduce safely

```powershell
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py test --settings=config.test_settings
```

The explicit test settings override database configuration with an isolated SQLite database. Do not omit this setting when reproducing tests against a Supabase-connected project.

## Unverified here

- Live Supabase connectivity, remote migration application state and PostgreSQL-specific concurrent execution. A read-only connection attempt failed due to environment connectivity; no remote migrations or data writes were performed.
- Google Maps live key authorization/billing: no private Google Maps key was supplied. Google script failure fallback is tested.
- External OpenStreetMap background availability was not fully verified in the restricted browser environment. The test transport proxy received blocked tile images; it is not part of the delivered application. The shipped browser loads tiles directly and uses origin-only cross-site referrers. Verify provider backgrounds locally; pin positions, map interactions and frontend behavior were tested.
- Real SMTP delivery. Tests use Django's in-memory backend; normal configuration defaults to console output until SMTP is configured.
