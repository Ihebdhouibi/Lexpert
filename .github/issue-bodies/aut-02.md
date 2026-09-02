**Task id:** `AUT-02`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `AUT-01`
**Branch:** `feature/aut-02-verification-reset`
**Labels:** `auth`, `backend`

## Goal

Confirm that a new account's email and phone belong to the person registering, and let someone who has forgotten their password recover it. Phone verification matters more than usual here: SMS is the channel with the highest open rate in Tunisia and is what consultation reminders will use.

## Requirements

1. Single-use, expiring tokens for email verification (link) and phone verification (6-digit code). Store hashes, not the raw values.
2. `POST /api/v1/auth/verify-email/request`, `POST /api/v1/auth/verify-email/confirm`, `POST /api/v1/auth/verify-phone/request`, `POST /api/v1/auth/verify-phone/confirm`.
3. `POST /api/v1/auth/password-reset/request` and `POST /api/v1/auth/password-reset/confirm`. The request endpoint responds identically whether or not the email exists.
4. Confirming a password reset revokes every outstanding refresh token for that user.
5. Resend throttling with a cooldown, and a cap on attempts per token before it is invalidated.
6. Until NOT-01 lands, send through a logging stub that records the message and the recipient but **not** the token value. Define the interface here so NOT-01 only swaps the implementation.
7. A professional whose phone is unverified cannot submit a verification file; a client whose phone is unverified cannot confirm a booking. Enforce both as service-layer checks with clear error codes.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: request and confirm email verification; `email_verified_at` is set.
- Integration test: a token cannot be reused, and an expired token is rejected.
- Integration test: a wrong code increments the attempt count and the token dies at the cap.
- Integration test: password reset changes the password and invalidates all refresh tokens.
- Integration test: `password-reset/request` returns the same response for a known and an unknown email.
- Integration test: resending inside the cooldown is rejected.
- Integration test: an unverified-phone professional gets the documented error when submitting a verification file.
- Test asserting the notification stub was called and that the raw token does not appear in captured logs.

## Deliverables

- Verification and reset token models plus their migration.
- The six endpoints and their schemas.
- `lexpert_api/notifications/interface.py` with the send interface and the logging stub.
- Tests as listed above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/aut-02-verification-reset`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
