# WarriWorks payment policy — release 2.0

## Commercial rules
- Default milestone schedule: 70% initial mobilisation, 20% verified progress, 10% completion retention.
- Alternative schedule: initial tranche may be adjusted above 70% up to 80%, with the progress tranche adjusted accordingly. Completion retention may never be below 10%.
- Artisan must provide a reason for initial mobilisation above 70%; WarriWorks staff must approve it; customer must accept the exact schedule before payment.
- Milestone percentages must total 100%. Monetary allocations are calculated in integer kobo, with any rounding remainder assigned to the final milestone.
- Quotation scope, cost breakdown, payment schedule and release conditions are displayed before customer acceptance. After payment, the schedule is locked; a new schedule must be handled through a mutually accepted change order (change-order API/UI is a follow-on item in this build).
- Customer charge success and artisan transfer success are distinct. The platform records a customer payment only after server-side Paystack verification, and records an artisan payout only after the Paystack transfer-success webhook.
- Progress release requires evidence and WarriWorks staff approval. Final release requires customer completion confirmation, previous milestone settlement, and a verified artisan Paystack recipient.
- Failed, pending or reversed transfers are not marked successful. Do not retry an uncertain transfer with a new reference; reconcile the original reference first.

## Supported schedule validation
- 70/20/10 is the default.
- 75/15/10 and 80/10/10 are examples of allowed exception schedules, subject to approval.
- Initial allocation above 80%, retention below 10%, zero/negative milestone percentages or a schedule not totalling 100% are rejected.

## Operational readiness
- A Paystack transfer recipient must be provisioned and verified for each artisan before any payout is processed. This code release stores the Paystack recipient code and account display metadata; it does not yet provide self-service bank-account resolution, encrypted account-number capture or recipient onboarding UI.
- A staff-only milestone approval endpoint is provided. A production admin console for evidence review and disputes is still required.
- This is not represented as regulated escrow. Confirm provider approval, settlement and balance arrangements, and applicable Nigerian regulatory/legal requirements before live launch.
