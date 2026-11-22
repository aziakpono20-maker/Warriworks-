# Build status — 21 November 2026

## Included in this delivery
- Django 6.1.3 + Django REST Framework API foundation.
- PostgreSQL configuration and Docker Compose development environment.
- Custom email-based user model and Werkzeug scrypt compatibility hasher.
- Artisan profiles and categories.
- Service request, quote, payment, milestone, disbursement, payout-recipient, webhook-event, ledger, change-order and review models.
- API endpoints for registration, login, logout, current user, verified artisan discovery, requests, request acceptance/completion, quotes, reviews, Paystack payment initialization/verification, signed Paystack webhooks, payment status, milestone evidence submission and staff milestone approval.
- JSON importer with legacy account hash conversion, idempotent user/profile creation and warnings for ambiguous legacy relationships.
- Next.js 16 App Router + React + TypeScript + Tailwind CSS 4 frontend foundation.
- Editorial homepage based on the supplied design brief, artisan search, sign-in/register, customer and artisan workspace views, and customer request form.

## Validation performed
- All Python files passed Python bytecode syntax compilation.
- All frontend TS/TSX files passed TypeScript syntax transpilation.
- Full Django system checks, migration generation/application and frontend type/build checks could not be run because Django/npm dependencies are not installed and package installation is blocked by network/DNS restrictions.
- The archive is an updated development implementation, not a production-verified payment integration.

## Known incomplete work before retiring the legacy app
- Run `makemigrations` and inspect generated migration files; apply them to an empty test database.
- Fix any framework/runtime integration issues found by Django checks and Next.js type/build checks.
- Complete admin moderation and artisan profile editing/verification workflows.
- Complete self-service artisan bank resolution, encrypted bank-account onboarding and Paystack transfer-recipient creation; build a production admin evidence/dispute console; implement signed dual-party change-order acceptance, refunds, notifications, reconciliation and full request detail timelines.
- Extend importer for all legacy appointment/quote/payment data and resolve skipped records after reviewing warnings.
- Add API permission tests, importer tests, Paystack mocked integration tests, transaction/concurrency tests, and Playwright browser journeys. Verify transfer webhook reconciliation before live use.
- Configure production domains, HTTPS, secure cookies, email, media/object storage, backups, logging, monitoring and deployment pipeline.

## Manual artisan verification update — 21 November 2026
- Added `backend/apps/verification/` with artisan applications, admin-only review endpoints, six required manual checks, decision workflow and audit records.
- Reuses the existing `ArtisanProfile.verified` and `ArtisanProfile.verification_status` fields; no duplicate artisan profile model was introduced.
- Added artisan verification page at `/artisan/verification` and admin review queue at `/admin/verifications`.
- No external KYC provider, paid API, customer KYC, full NIN/BVN collection, ID-image upload or biometric-image storage is included.
- Manual inspection must be described accurately as an identity-document review, not NIMC/government-database verification.
- See `MANUAL_ARTISAN_VERIFICATION.md` for API routes, six-check approval gate, privacy controls, setup, rollout and ₦50,000 maximum budget allocation.
- **Pre-deployment requirement:** generate and inspect initial migrations for all Django apps (`accounts`, `marketplace`, `workflow`, `verification`), apply migrations, then run Django checks/tests and Next.js typecheck/build. These checks have not yet been run in this environment.
