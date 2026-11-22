# WarriWorks 2.0 — Stabilisation and completion roadmap

**Working baseline:** `WarriWorks_2_0_Manual_Artisan_Verification_Updated.zip`  
**Architecture to preserve:** Django REST Framework modular monolith + Next.js App Router frontend.  
**Product decisions:** manual artisan verification only; no customer KYC; retain the current flexible milestone-payment policy; do not describe the product as regulated escrow.

## Delivery sequence and acceptance criteria

### Phase 0 — Foundation and release safety (Critical)
- Generate and review initial migrations for `accounts`, `marketplace`, `workflow`, and `verification` using the project's pinned Django version.
- Apply migrations to a new empty PostgreSQL database and to a restored staging copy; confirm migration consistency and rollback procedure.
- Run Django checks, API tests, frontend typecheck/build, and a clean Docker Compose boot.
- Fix all runtime errors before feature work is merged. Never generate migrations against production data as the first test.
- Add environment validation: production must fail closed without a strong secret, allowed hosts, HTTPS origins, database credentials, and Paystack keys where payments are enabled.

**Acceptance:** clean install from an empty database; `manage.py check`, all tests, frontend typecheck/build and container health checks pass.

### Phase 1 — Core account and service journey (Critical)
- Artisan profile editing is now introduced at `/artisan/profile` and `PATCH /api/artisans/me/`.
- Keep `verified`, `verification_status`, user role, and payout verification server-controlled. The artisan can edit only their public professional details.
- Finish customer request creation, artisan acceptance, quote/revision, customer quote acceptance and clear status history.
- Add an event timeline using immutable status events rather than relying only on the current status field.

**Acceptance:** a customer can create a request, the assigned artisan can respond and quote, the customer can accept/revise, and both sides see the same chronological history. Unauthorized users cannot edit another user's records.

### Phase 2 — Paystack onboarding and payment integrity (Critical)
- Complete artisan bank onboarding with bank resolution and account-name confirmation. Store account details encrypted with a managed key; never expose account numbers or Paystack secret keys to the browser.
- Create/verify Paystack transfer recipients server-side and support safe recipient updates/revocation.
- Make webhook handling idempotent and concurrency-safe. Verify signatures against the raw request body and reconcile charge and transfer state against Paystack before final ledger changes.
- Handle duplicate, late, failed, pending and reversed transfers; provide a retry/reconciliation queue rather than silently marking uncertain transfers as failed.
- Ensure first milestone disbursement can be queued after payout onboarding if payment was already verified.
- Validate milestone percentages sum to 100, prevent duplicate checkout/payment for a quote, and make ledger entries immutable.
- Run only Paystack test-mode end-to-end scenarios until Paystack account approval, legal review and operational reconciliation are complete.

**Acceptance:** each test payment and transfer has a unique reference, verified provider state, balanced milestone allocations, immutable ledger history and correct retry/reversal behaviour.

### Phase 3 — Notifications and operations (High)
- Add an in-app notification record and user notification inbox first.
- Trigger notifications from committed workflow events: request received, request accepted, quote submitted/revised, quote accepted, payment confirmed, milestone evidence submitted/approved, transfer result, completion request and dispute updates.
- Add email delivery with retry and delivery logs. Add WhatsApp only after explicit opt-in, approved template/message design and provider configuration.
- Complete admin moderation: artisan/profile review, service request oversight, user restrictions, content/report handling, dispute queue, payment reconciliation and audit trail.

**Acceptance:** no important workflow transition is invisible to the affected user or admin; notification retries do not duplicate the underlying action.

### Phase 4 — Disputes, refunds and trust (High)
- Add dispute creation with reason, evidence, deadline, status and assigned reviewer.
- Freeze only the affected unpaid milestone(s) while a dispute is open; preserve already settled transfers and show the actual state clearly.
- Define staff resolution outcomes: release, partial release, refund request, cancellation or further evidence.
- Implement refunds through supported Paystack APIs with idempotency, ledger entries, webhook reconciliation and customer-visible status. Do not promise a refund until provider confirmation.
- Add role-based permissions and a full audit log for every admin action.

**Acceptance:** customer, artisan and staff see consistent dispute states; disputed funds cannot be released accidentally; refunds are provider-confirmed and auditable.

### Phase 5 — Portfolio, migration and automated quality (Medium)
- Add portfolio media upload with type/size limits, private upload handling, malware scanning where supported, safe image transformation and ownership checks.
- Extend legacy importer for appointments, quotes and payment history only after mapping each legacy field and resolving duplicate/ambiguous identities. Preserve source IDs and produce import/reconciliation reports.
- Add Playwright journeys for registration/login, search, request, quote, payment return, verification application, admin review and dispute flows.
- Add API permission, webhook signature/idempotency, concurrency, importer repeatability, upload validation and security regression tests.

**Acceptance:** repeatable migration with count reconciliation and no silent merges; browser journeys pass in CI; uploads are private-by-default and validated.

## Current change in this working copy
- Added artisan self-profile GET/PATCH endpoint at `/api/artisans/me/`.
- Added a profile editing screen at `/artisan/profile` and linked it from the artisan workspace.
- Editable fields: display name, primary skill, location, bio, years of experience, availability and phone visibility preference.
- Verification state is read-only and cannot be changed through the profile endpoint.
- Added API tests for profile read/update, role restriction and verification-state protection.

## Known execution blockers in this environment
- The archive contains no initial Django migration files.
- Django is not installed in the available runtime and frontend dependencies are not installed. Network/package installation is unavailable in this execution environment.
- Therefore migrations have **not** been generated or applied, Django tests have **not** been executed, and Next.js typecheck/build has **not** been executed. Python syntax compilation alone is not a substitute for those checks.
- Do not treat this archive as production-ready until Phase 0 and the payment safety acceptance criteria pass in a real development/staging environment.
