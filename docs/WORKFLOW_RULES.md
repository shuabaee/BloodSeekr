# Workflow and authorization rules

| Entity | Values used by the application |
|---|---|
| Blood request urgency | routine, urgent, emergency |
| Blood request status | open, in_progress, fulfilled, cancelled |
| Request/attachment verification | pending, verified, rejected |
| Donor response | pending, accepted, declined, withdrawn, completed |
| Donation screening | pending, passed, failed |
| Donation status | scheduled, completed, cancelled |

These are form/workflow rules on the existing varchar columns. No schema choices, columns, tables or constraints were added. Existing records with other legacy values are preserved and are not automatically rewritten.

The requester owns creation/status management/attachments and accepts or declines pending offers. Donors may offer only on matching active requests, and may withdraw pending/accepted offers before a donation record exists. Each donor/request pair is unique. A requester or staff member records the donation for an accepted offer. The donation's existing OneToOneField enforces at most one record per offer. Request and response rows are locked in transactions during transitions; original database uniqueness also protects duplicates.

The application can start with pending verification for coordination. Rejected requests cannot receive new offers, be accepted or have donations recorded. Screening must pass before a completed donation can be saved. Completed donations are read-only and aggregate toward fulfillment.

The matching service reads **donor type -> recipient type** from blood_compatibility where is_compatible=true. It checks active users, availability, a set blood type, required type, due date, open/in_progress status and location. It excludes self-donation responses. Missing compatibility data produces no match; run the non-destructive seed command.

Hidden profiles stay out of requester discovery. A private donor can still choose to respond; after accepting an offer, the requester receives the donor's relevant contact information. Medical documents remain visible to their requester and staff, and are downloaded through a permission-checked endpoint instead of a public media route.

Sources for lookup semantics:
- https://www.redcrossblood.org/donate-blood/blood-types.html
- https://www.redcrossblood.org/donate-blood/blood-types/a-blood-type.html
- https://www.redcrossblood.org/donate-blood/blood-types/b-blood-type.html
- https://www.redcrossblood.org/donate-blood/blood-types/ab-blood-type.html

Django's composite-key model is preserved and is not registered in stock Django admin; admin support is limited for composite primary keys. The ORM and idempotent seed command manage compatibility data without inventing a surrogate key.
- https://docs.djangoproject.com/en/5.2/topics/composite-primary-key/
