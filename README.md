# WarriWorks 2.0 — Django API + Next.js frontend

A modular-monolith rebuild foundation using Django 6.1.3 + Django REST Framework, PostgreSQL 18, Next.js 16.4.6 App Router, TypeScript and Tailwind CSS 4.3.5. The visual direction follows the supplied WarriWorks brief: forest green `#0F3826`, primary green `#1E6B44`, warm off-white `#FBFAF6`, Fraunces editorial headings and Work Sans interface typography.

## Architecture
- `frontend/`: Next.js app with responsive homepage, artisan discovery, login/register and customer/artisan workspaces.
- `backend/`: Django REST API, custom user model, artisan profiles, requests, quotes, payments and reviews.
- `backend/apps/accounts/`: email-based authentication and legacy Werkzeug scrypt hasher.
- `backend/apps/marketplace/`: artisan and service-category models.
- `backend/apps/workflow/`: request lifecycle, quote acceptance, payment records and completion/review rules.

TanStack Router is intentionally not included: Next.js App Router is already the routing solution. TanStack Query is installed for future server-state caching; the first screens currently use a small fetch helper.

## Run locally
1. Copy `.env.example` to `.env` and set a strong `POSTGRES_PASSWORD` and `DJANGO_SECRET_KEY`.
2. Run `docker compose up --build`.
3. Backend: `http://localhost:8000`; API: `http://localhost:8000/api/`; admin: `http://localhost:8000/admin/`.
4. Frontend: `http://localhost:3000`.
5. Create an administrator: `docker compose exec backend python manage.py createsuperuser`.

For local Python-only development, install `backend/requirements.txt`, set `DJANGO_USE_SQLITE=true`, and run `python manage.py migrate` then `python manage.py runserver` from `backend/`. For frontend, run `npm install && npm run dev` from `frontend/`.

## JSON migration
Copy the legacy `artisans.json`, `artisan_accounts.json`, `customer_accounts.json`, `requests.json` and `ratings.json` into `backend/` (the archive includes the copies we found). After migrations are generated/applied, run:

`python manage.py import_legacy_json --source .`

The importer is repeatable for users/profiles and avoids blindly inventing account links. Legacy Werkzeug `scrypt:32768:8:1` password hashes are imported in a compatible format; Django upgrades them to its preferred password hash after a successful login. If an email is shared by a customer and artisan account, or a request has no reliable customer link, the importer warns instead of merging records unsafely. Review warnings and reconcile skipped records before production cutover. Keep the original JSON backup read-only until counts and sample records have been verified.

## Important implementation boundaries
- Paystack transaction initialization and server-side verification, signed webhooks, milestone allocation and transfer-worker scaffolding are present. This integration remains unverified in a live/staging runtime; payout onboarding, reconciliation, refunds and robust failure/reversal handling must be completed before production.
- Artisan discovery returns verified profiles only. Existing directory-only artisan records without linked accounts are not auto-promoted into login-capable profiles.
- Request creation, artisan acceptance, quote submission/acceptance and completion are represented in the API. Discovery, login/register, dashboard reads and a basic request/payment journey are present. Artisan self-profile editing is available at `/artisan/profile`; broader quote revision, customer-side timelines and full operational screens still need completion.
- Appointment scheduling, notifications, disputes/refunds, portfolio uploads and complete admin workflows remain outstanding before the old app can be retired.
- Legacy data has inconsistent fields and duplicate emails. Do not run an irreversible production migration without reviewing importer output and testing a restore.

## Stabilisation roadmap
See [`COMPLETION_ROADMAP.md`](./COMPLETION_ROADMAP.md) for the phased delivery order, acceptance criteria and current validation blockers.

## Before production
Set `DJANGO_DEBUG=false`, configure HTTPS and trusted origins, use a strong secret, set real allowed hosts, configure secure cookies, email delivery, object storage, backups, monitoring and a real payment provider. Add automated API and browser tests. Review Django's deployment checklist.

## Flexible milestone payments (new)

WarriWorks uses a default 70/20/10 schedule. A higher first tranche (up to 80% in the initial policy) must be approved by a WarriWorks staff account and accepted by the customer before checkout. The payment schedule is copied to payment milestones after Paystack verifies the full NGN charge. Do not edit paid schedules in place; use an approved, mutually accepted change order (the full change-order acceptance UI is not part of this release).

### Backend setup

1. Copy `.env.example` values into the backend runtime environment. Set a real `DJANGO_SECRET_KEY`, database settings and a Paystack **test** secret key. Never put `PAYSTACK_SECRET_KEY` in the frontend environment.
2. From `backend/`, install `requirements.txt` and run `python manage.py makemigrations workflow` followed by `python manage.py migrate`.
3. Create an admin account. Review and approve exception schedules in Django admin (`Quote.schedule_approved`).
4. Configure the Paystack webhook URL as `https://YOUR_API_HOST/api/webhooks/paystack/` in the Paystack dashboard. Subscribe to `charge.success`, `transfer.success`, `transfer.failed`, and `transfer.reversed`.
5. Set `PAYSTACK_CALLBACK_URL` to the deployed frontend `/payment/return` URL.
6. Provision and verify an artisan `ArtisanPayoutAccount` with a valid Paystack `recipient_code` before running the payout worker. The payout account record is intentionally an operations-provisioned integration point in this release; self-service bank resolution and encrypted account onboarding are not yet implemented.
7. Run the protected worker/scheduler: `python manage.py process_disbursements`. It submits queued transfers; final settlement is only recorded from verified Paystack transfer webhooks.

### Connected frontend/backend flow

The Next.js job detail screen calls the Django `/api/quotes/` and `/api/quotes/{id}/accept/` endpoints, then `/api/payments/initialize/`. Django initializes Paystack and returns a checkout URL. The browser redirects to Paystack. Paystack returns to `/payment/return`, where the frontend calls `/api/payments/verify/`; Django independently verifies the transaction with Paystack. Payment details are read from `/api/payments/{id}/`. API base URL is configured by `frontend/.env.local` using `NEXT_PUBLIC_API_URL`; CORS and CSRF trusted origins must include the deployed frontend origin.

### Important launch limitations

- The release worker requires a verified Paystack transfer recipient code for the artisan. Self-service account resolution, encryption/key rotation and recipient onboarding still need implementation before unrestricted production use.
- Milestone evidence currently accepts secure evidence URLs, and approval is staff-only. A full customer/admin dispute centre, refund workflow, signed change-order acceptance UI, automated recurring worker and reconciliation dashboard remain follow-on work.
- This is staged payment orchestration, not a representation that WarriWorks is a regulated escrow provider. Confirm Paystack approval, available-balance/settlement arrangements and Nigerian regulatory/legal requirements before live customer funds are accepted.
- Do not deploy with test credentials, `DEBUG=true`, default secret keys or permissive hosts. Test duplicate webhooks, duplicate payment attempts, pending transfers, transfer failures/reversals and database concurrency before launch.

## Manual artisan verification
The MVP uses a manual, admin-controlled artisan verification workflow with no paid KYC provider. See [`MANUAL_ARTISAN_VERIFICATION.md`](./MANUAL_ARTISAN_VERIFICATION.md) for the implementation, endpoints, privacy limits, setup and rollout plan.
