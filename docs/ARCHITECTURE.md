# BloodSeekr architecture (vertical slicing)

Each feature is a slice that owns its Python app, templates, CSS, JS and images:

```
apps/<feature>/            models, forms, views, urls, services.py, templatetags, tests
templates/<feature>/       the feature's pages
static/{css,js,images}/<feature>/
```

`apps/shared` + `templates/shared` + `static/*/shared` hold utilities only (design tokens, layout,
components, icon sprite, `ui.js`, location helpers, error pages). It has no models.

## Rule
A slice never imports another slice's `models`, `views` or `forms`. It calls the other slice's
`services.py` (or a template tag). Django's `User` is the shared account model.

## Allowed dependencies
| Slice | Uses |
|---|---|
| home | blood_requests, notifications, donations, profile, blood_data (services) |
| blood_requests | blood_data, facilities, notifications, profile (services) |
| donations | blood_requests, notifications (services) |
| facilities | blood_requests (services) |
| profile | donations (services) |
| blood_data | none (reference data and the blood type guide) |

## Public service functions
- blood_data: `compatibility_map`, `recipients_for`, `donors_for`, `donor_eligible`, `matching_requests`, `matching_donors`, `blood_types`
- blood_requests: `can_view`, `active_requests`, `attach_progress`, `pending_offers_for`, `dashboard_for`, `timeline`, `get_response`, `lock_for_donation`, `mark_response_completed`, `mark_request_fulfilled`
- donations: `records_for`, `history_for`, `summary_for`
- notifications: `notify`, `notify_matches`, `recent_for`, `unread_count`
- profile: `completeness`
- facilities: `facility_option`, `facility_options`, `get_facility`

No models or migrations were added or changed.
