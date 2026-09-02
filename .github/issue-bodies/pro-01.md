**Task id:** `PRO-01`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `KYC-06`, `FND-07`
**Branch:** `feature/pro-01-profile-model`
**Labels:** `backend`, `database`

## Goal

Model what a client sees when they look at a professional, and the hourly rate that drives every price the platform computes. The rate is the input to the escrow amount, so its type and constraints matter more than the rest of the profile.

## Requirements

1. `ProfessionalProfile`: user id, vertical, display title, French biography, specialities (from FND-07, at least one), spoken languages, city or governorate, years of experience, hourly rate in millimes, default consultation duration in minutes, `is_published`, timestamps.
2. The hourly rate is an **integer number of millimes**. Never a float. Constrain it to a sane range from settings (a floor and a ceiling) and reject anything outside it with a clear code.
3. Allowed consultation durations are a fixed set (for example 15, 30, 45, 60 minutes) defined once and shared with SCH-02 and ESC-05. Do not accept an arbitrary integer.
4. A profile can only be published when the owner's verification is `APPROVED` and the profile is complete (biography, at least one speciality, a rate, a city). Enforce in the service layer, not only in the UI.
5. Unpublishing is always allowed and immediately removes the professional from search, but must not affect consultations already booked.
6. `GET /api/v1/professionals/{id}` — the public profile. It returns 404 unless the profile is published **and** verification is `APPROVED`. It never exposes the email, the phone, or anything from the verification file.
7. `GET /api/v1/professionals/me` and `PUT /api/v1/professionals/me` for the owner, guarded by `require_verified_professional`.
8. Revoking a verification (an admin moving an approved file back to `REJECTED`) must unpublish the profile. Cover this with a test even though the admin path for it is thin in the MVP.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: an approved professional creates, completes and publishes a profile.
- Integration test: publishing with verification `SUBMITTED` is refused.
- Integration test: publishing an incomplete profile is refused, naming the missing fields.
- Integration test: a rate of 0, a negative rate, and a rate above the ceiling are all refused.
- Unit test: the rate column round-trips large values exactly, with no floating-point drift.
- Integration test: an unsupported duration (for example 37 minutes) is refused.
- Integration test: the public endpoint returns 404 for an unpublished profile and for a published profile whose verification is not approved.
- Integration test: the public response contains no email, phone, or verification field.
- Integration test: revoking verification unpublishes the profile.
- Integration test: unpublishing leaves an already-booked consultation intact.

## Deliverables

- `lexpert_api/profiles/models.py`, `service.py`, `router.py`, `schemas.py`.
- The Alembic migration.
- `apps/api/tests/profiles/test_profile.py`.
- The shared duration and rate-bound constants, referenced by SCH and ESC.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/pro-01-profile-model`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
