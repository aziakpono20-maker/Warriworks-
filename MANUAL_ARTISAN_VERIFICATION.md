# WarriWorks — Manual Artisan Verification (MVP)

**Decision:** Manual verification only. Initial implementation/operations budget: **₦0–₦50,000**. No external KYC API, provider subscription, customer KYC or automated NIN/BVN lookup is included.

## What this release does

- Adds a dedicated Django app at `backend/apps/verification/`.
- Lets authenticated artisan accounts submit a verification application.
- Collects legal name, phone, operating address, ID category, optional last four ID characters, inspection method and explicit consent.
- Does **not** upload or retain ID images, full NIN/BVN numbers or biometric images. Admin arranges an in-person or live-video inspection and records the outcome.
- Gives admins a queue, a six-part manual checklist, review notes, approve/reject/request-information/suspend actions and audit history.
- Synchronises approved/rejected/suspended outcomes to the existing `ArtisanProfile.verified` and `verification_status` fields. Existing profile and marketplace models are extended rather than duplicated.
- Adds artisan and admin Next.js pages:
  - `/artisan/verification`
  - `/admin/verifications`

## Manual checklist (all six required for approval)

1. Phone confirmed by an admin call.
2. Government-issued ID visually inspected in person or over a live video call.
3. Person visually matched to the inspected ID during the same session.
4. Professional skills and portfolio reviewed.
5. Operating location checked using the documented method.
6. At least one professional reference checked.

These checks record a manual review only. They do not prove that a government identity database was queried or that an ID was independently authenticated. Public-facing copy must not claim NIMC/NIN database verification.

## API routes

Artisan (authenticated `role=artisan`):

- `GET /api/verification/artisan/` — current status.
- `POST /api/verification/artisan/` — initial application.
- `POST /api/verification/artisan/resubmit/` — resubmit after rejection or request for more information.

Admin (authenticated superuser, staff user or `role=admin`):

- `GET /api/verification/admin/` — paginated queue; optional `?status=pending`.
- `GET /api/verification/admin/{id}/` — application detail.
- `POST /api/verification/admin/{id}/review/` — update checklist booleans and notes.
- `POST /api/verification/admin/{id}/approve/` — approval; blocked until all six checks are true.
- `POST /api/verification/admin/{id}/reject/` — rejection; requires `reason`.
- `POST /api/verification/admin/{id}/request-info/` — request more information; requires `reason`.
- `POST /api/verification/admin/{id}/suspend/` — suspend; requires `reason`.
- `GET /api/verification/admin/{id}/audit/` — audit history.

## Status lifecycle

`pending` → `under_review` → `approved` / `rejected` / `more_info_required` / `suspended`.

Rejected and more-information applications can be resubmitted. Artisan accounts cannot change their own status or checklist. Admin decisions and checklist updates are recorded in `VerificationAuditLog`.

## Privacy and security safeguards

- The form explicitly records consent and consent timestamp.
- The MVP deliberately avoids ID image upload, full ID numbers, BVN and biometric-image storage. Only ID type and optional last four characters are recorded.
- Admin endpoints require an authenticated admin role or Django staff/superuser status.
- Admin actions are logged. Audit entries are read-only in Django admin.
- Never expose verification application details or audit logs on public artisan endpoints.
- Publish a privacy notice, define retention/deletion periods for the collected application data, restrict admin access and provide a privacy-request channel before public launch.
- Do not describe a manually inspected ID as “NIN verified” or “government verified”. Use “identity document reviewed” and explain the scope of the review.

## Setup and migrations

The supplied archive has no existing migration files for its Django apps. After installing backend requirements and setting environment variables, generate the initial migrations for the existing apps together (not just this new app), inspect them, then apply them:

```bash
cd backend
python manage.py makemigrations accounts marketplace workflow verification
python manage.py migrate
python manage.py check
```

Run tests and frontend checks:

```bash
python manage.py test
cd ../frontend
npm install
npm run typecheck
npm run build
```

Create an admin user with `role=admin` (or Django staff/superuser) before using `/admin/verifications`. Confirm the configured session/CSRF flow works in the deployment environment.

## Rollout plan

- Days 1–2: inspect existing data, generate/review migrations, confirm admin accounts and publish privacy notice.
- Days 3–7: integrate artisan submission, admin review and profile status into the existing app.
- Days 8–10: test ownership, role restrictions, approval gating, resubmission, audit records and regression of registration/payments/marketplace.
- Days 11–14: pilot with 10–20 artisans, review completion time and support issues, then widen onboarding.

## Budget allocation (maximum ₦50,000)

| Workstream | Budget ceiling |
|---|---:|
| Backend verification functionality | ₦12,000 |
| Artisan frontend form/status | ₦8,000 |
| Admin review dashboard | ₦10,000 |
| Testing and bug fixes | ₦5,000 |
| Security/privacy setup | ₦5,000 |
| Operational verification expenses | ₦5,000 |
| Contingency | ₦5,000 |
| **Total** | **₦50,000** |

These are planning allocations, not vendor quotes. Reuse existing hosting, database, authentication and deployment infrastructure; do not spend the full amount automatically.

## Known implementation limits before production

- No email/SMS notifications are wired for status changes; admins must communicate outcomes through the existing support process until notifications are implemented.
- The admin checklist records review outcomes; it does not capture uploaded documents or retain selfie evidence by design.
- No government registry/API lookup is performed.
- Full Django migrations, backend tests, Next.js typecheck/build and end-to-end browser testing must be run in an environment with project dependencies installed before deployment.
- The public badge should be accompanied by a clear explanation of the manual checks completed; it is not a guarantee of workmanship or future conduct.
