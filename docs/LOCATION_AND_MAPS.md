# Locations, matching and Maps

No ERD changes. The existing text columns store a compact tagged JSON array:

`BS1:[country_code, area_id, city_id, latitude, longitude, street_description, precision]`

For example the country code is `PH`; city/area IDs identify catalog entries. Custom cities use a `~` name. Coordinates are rounded to 5 decimal places; precision is `city`, `pin`, `gps`, `facility` or `legacy`. Existing plain strings and old `latitude,longitude` strings remain supported. Forms validate relationships, coordinate ranges, paired coordinates and original column lengths. Legacy rows are not rewritten until the user saves a selection.

The shared module is a utility package under `apps/`, not a Django database app. Profile/request/facility Python behavior remains in its feature app. Templates and static assets follow the existing separate feature folders.

When both locations have coordinates, matching uses straight-line Haversine distance and the donor's existing `match_radius_km`. This supports nearby cities across locality boundaries. Without coordinates, existing normalized exact locality behavior is preserved. Blood compatibility, availability, request dates/statuses and privacy preferences still apply. City centers are approximate: a donor near one side of a large city can produce different results until they choose a specific point.

The bundled derived catalog includes 249 countries and 27,638 cities/municipalities, including all 1,656 Philippine city/municipality entries from the packaged PSGC snapshot. Other countries cover major settlements, not every town. Areas vary by country. Metro Cebu independent cities are grouped geographically under Cebu. An unlisted city requires a name and a point; no live geocoding or new entity is added.

Google Maps is selected with `GOOGLE_MAPS_BROWSER_KEY`; `GOOGLE_MAPS_MAP_ID` defaults to `DEMO_MAP_ID`. The adapter uses Maps JavaScript API and AdvancedMarkerElement. No Places, Geocoding or Routes billing dependency. Without a key, locally bundled Leaflet loads OpenStreetMap background tiles. Maps load on demand in the explorer to avoid unnecessary API loads for List view. Detail/picker maps load where they are shown. Browser GPS is requested only after pressing Use my location.

Facility addresses now contain collection points. Staff can add/edit them in the app or admin; verification is admin-managed. A request can explicitly reuse a selected facility's point, or an owner can edit an active request point later. The donation form starts with the request's facility. Existing real facility rows are not automatically changed.

Community request pins are authenticated, de-identified collection locations. No patient names, private documents, donor profile points or contact details are serialized. Pin detail links follow the original request access rule. An authenticated user can inspect blood needs and collection points even if not eligible; eligibility is still required to offer.

Map data endpoint: `GET /requests/map-data/` (login required, private/no-store), shares filters with list. Geographic catalog: `GET /locations/options/?country=PH&province=0702200000` (public reference data). Facility options: `GET /facilities/options/` (login required).

Google Cloud setup and upgrade steps: START_HERE.md sections 7–8. Attribution/licenses: docs/licenses/GEOGRAPHIC_DATA.md. The unchanged ERD text lengths limit long freeform street descriptions; shortening is reported as a form validation message.
