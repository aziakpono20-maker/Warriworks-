# Payment implementation handoff for the developer

## Frontend to backend contract

| Frontend action | Django endpoint | Result |
|---|---|---|
| Submit artisan quote | `POST /api/quotes/` | Stores amount, cost breakdown, milestone schedule and exception reason |
| Approve exception schedule | `POST /api/quotes/{id}/approve_schedule/` | Staff-only; sets `schedule_approved` |
| Customer accepts quote | `POST /api/quotes/{id}/accept/` | Locks accepted quote and moves request to `payment_pending` |
| Initialise checkout | `POST /api/payments/initialize/` | Returns Paystack `checkout_url` |
| Paystack callback | `GET /payment/return?reference=...` | Next.js calls server verification endpoint |
| Verify payment | `POST /api/payments/verify/` | Django calls Paystack verify API; never trusts browser status |
| View payment | `GET /api/requests/{id}/payment/` | Payment and milestone status for customer/artisan job page |
| View payment by ID | `GET /api/payments/{id}/` | Payment detail and milestone detail |
| Paystack webhook | `POST /api/webhooks/paystack/` | Signed webhook handling for charge and transfer events |
| Submit progress evidence | `POST /api/milestones/{id}/submit-evidence/` | Assigned artisan submits evidence URLs |
| Approve milestone | `POST /api/milestones/{id}/approve/` | Staff-only; creates a queued disbursement when payout recipient exists |
| Submit transfers | `python manage.py process_disbursements` | Background command sends queued transfer requests |

## Frontend configuration

Set `NEXT_PUBLIC_API_URL` to the Django API root, e.g. `https://api.example.com/api`. Ensure Django `CORS_ALLOWED_ORIGINS` and `CSRF_TRUSTED_ORIGINS` include the exact frontend origin. The current app uses session authentication and CSRF cookies.

## Backend configuration

Set `PAYSTACK_SECRET_KEY` only in the backend environment. Set `PAYSTACK_CALLBACK_URL` to the public frontend payment return URL. Configure the Paystack webhook URL at `/api/webhooks/paystack/` and subscribe to `charge.success`, `transfer.success`, `transfer.failed`, `transfer.reversed`.

## Schema and deployment

This repository did not contain committed Django migration files before this update. The Docker Compose backend command runs `makemigrations` for accounts, marketplace and workflow before `migrate`. For a non-Docker deployment, run:

```bash
cd backend
python manage.py makemigrations accounts marketplace workflow
python manage.py migrate
```

Run `python manage.py check` and the frontend `npm run typecheck` / `npm run build` in an environment with dependencies installed before deployment.

## Important known gaps

- Artisan payout recipient onboarding/account resolution and encryption of raw bank account numbers are not implemented. Only the Paystack recipient token and non-sensitive account metadata are stored; provision recipient tokens securely before enabling the worker.
- Evidence is submitted as URLs; a production upload/storage workflow and evidence moderation screen are needed.
- Change-order records exist, but the full dual-party approval endpoints/UI are not implemented. Do not change a paid schedule directly in admin.
- No automated Celery/Redis scheduler is bundled. Run the disbursement command as a protected worker/job, and add transfer reconciliation before production.
- Refund and dispute case management, fee/deduction rules, customer support escalation, and full financial reporting are not yet implemented.
