# Changed files: locations, facilities, maps and UI

This update continues the delivered working project. All original models, requirements and migrations are unchanged byte-for-byte. **No new migrations or database entities.** The earlier implementation file list is retained in `CHANGED_FILES_V1.md`.

## Features changed

- Shared location catalog, country/area/city selectors, GPS/pin picking, original-column validation and readable address decoding.
- Radius matching across city boundaries, while preserving plain-text legacy locations.
- Collection-facility contact/direction/detail workflows, staff add/edit, pinned addresses, request prefill and donation defaults.
- Authenticated request explorer with filters, de-identified map pins and list/map views; owner edits active collection points.
- Optional Google Maps, key-free Leaflet map, origin-only external referrer policy and geographic attribution.
- Responsive sidebar/mobile navigation, forms, cards, dashboard/profile/settings and read feedback.
- 19 new regression tests, browser workflows and refreshed setup/Supabase/submission documentation.

## Modified in this update

- `.env.example`
- `README.md`
- `START_HERE.md`
- `apps/blood_data/services.py`
- `apps/blood_requests/admin.py`
- `apps/blood_requests/forms.py`
- `apps/blood_requests/urls.py`
- `apps/blood_requests/views.py`
- `apps/facilities/admin.py`
- `apps/facilities/management/commands/seed_demo_facilities.py`
- `apps/facilities/urls.py`
- `apps/facilities/views.py`
- `apps/notifications/context_processors.py`
- `apps/profile/admin.py`
- `apps/profile/forms.py`
- `config/settings.py`
- `config/urls.py`
- `docs/CHANGED_FILES.md`
- `docs/TEST_REPORT.md`
- `docs/VERIFY_SUPABASE.sql`
- `static/css/shared/site.css`
- `templates/blood_requests/card.html`
- `templates/blood_requests/detail.html`
- `templates/blood_requests/form.html`
- `templates/blood_requests/list.html`
- `templates/donations/form.html`
- `templates/facilities/detail.html`
- `templates/facilities/list.html`
- `templates/home/home.html`
- `templates/profile/profile.html`
- `templates/shared/base.html`
- `templates/shared/navigation.html`
- `templates/shared/pagination.html`
- `templates/user_settings/settings.html`

## Added in this update

- `apps/blood_data/templatetags/__init__.py`
- `apps/blood_data/templatetags/locations.py`
- `apps/blood_requests/test_locations.py`
- `apps/facilities/forms.py`
- `apps/facilities/services.py`
- `apps/shared/__init__.py`
- `apps/shared/data/places.json`
- `apps/shared/locations.py`
- `apps/shared/views.py`
- `apps/shared/widgets.py`
- `docs/BROWSER_TEST_RESULTS.json`
- `docs/CHANGED_FILES_V1.md`
- `docs/LOCATION_AND_MAPS.md`
- `docs/licenses/GEOGRAPHIC_DATA.md`
- `docs/licenses/geonamescache-LICENSE`
- `docs/licenses/psgc-LICENSE`
- `docs/licenses/pycountry-LICENSE.txt`
- `docs/screenshots/REQUEST_LIST_DESKTOP.png`
- `static/css/shared/location.css`
- `static/js/blood_requests/explorer.js`
- `static/js/blood_requests/facility.js`
- `static/js/shared/locations.js`
- `static/js/shared/maps.js`
- `static/vendor/leaflet/LICENSE`
- `static/vendor/leaflet/images/layers-2x.png`
- `static/vendor/leaflet/images/layers.png`
- `static/vendor/leaflet/images/marker-icon-2x.png`
- `static/vendor/leaflet/images/marker-icon.png`
- `static/vendor/leaflet/images/marker-shadow.png`
- `static/vendor/leaflet/leaflet.css`
- `static/vendor/leaflet/leaflet.js`
- `templates/blood_requests/location_form.html`
- `templates/facilities/form.html`
- `templates/shared/location_widget.html`
- `templates/shared/map_assets.html`

## Schema and dependency verification

- `apps/blood_data/migrations/0001_initial.py` unchanged
- `apps/blood_data/migrations/__init__.py` unchanged
- `apps/blood_data/models.py` unchanged
- `apps/blood_requests/migrations/0001_initial.py` unchanged
- `apps/blood_requests/migrations/__init__.py` unchanged
- `apps/blood_requests/models.py` unchanged
- `apps/donations/migrations/0001_initial.py` unchanged
- `apps/donations/migrations/__init__.py` unchanged
- `apps/donations/models.py` unchanged
- `apps/facilities/migrations/0001_initial.py` unchanged
- `apps/facilities/migrations/__init__.py` unchanged
- `apps/facilities/models.py` unchanged
- `apps/home/migrations/__init__.py` unchanged
- `apps/home/models.py` unchanged
- `apps/login/migrations/__init__.py` unchanged
- `apps/login/models.py` unchanged
- `apps/notifications/migrations/0001_initial.py` unchanged
- `apps/notifications/migrations/__init__.py` unchanged
- `apps/notifications/models.py` unchanged
- `apps/profile/migrations/0001_initial.py` unchanged
- `apps/profile/migrations/0002_remove_profile_last_donation_date.py` unchanged
- `apps/profile/migrations/0003_profile_is_verified_alter_profile_blood_type_and_more.py` unchanged
- `apps/profile/migrations/__init__.py` unchanged
- `apps/profile/models.py` unchanged
- `apps/register/migrations/__init__.py` unchanged
- `apps/register/models.py` unchanged
- `apps/user_settings/migrations/0001_initial.py` unchanged
- `apps/user_settings/migrations/0002_remove_usersettings_updated_at_and_more.py` unchanged
- `apps/user_settings/migrations/__init__.py` unchanged
- `apps/user_settings/models.py` unchanged
- `requirements.txt` unchanged

## UI refresh and new features
- New design system: `static/css/shared/{tokens,layout,components,auth}.css`, SVG icon sprite, `static/js/shared/ui.js`.
- New: dashboard "Needs your attention", profile strength meter, blood type guide (`/blood-guide/`),
  donation summary, 8-week wait estimate and CSV export, request progress/timeline/share, password reset and change,
  grouped notifications, confirm dialogs, friendly 403/404/500 pages.
- Tests: 70 (was 60). See `docs/ARCHITECTURE.md` for slice boundaries.

## Round 2
- Removed supporting-document upload/download and the "awaiting verification" step from blood requests (new requests are posted immediately; staff can still reject abusive ones in admin). No schema change.
- Settings and password pages are centered.
- All sizes are rem-based and the root size grows with the viewport, so zooming out scales the UI instead of leaving it small.
