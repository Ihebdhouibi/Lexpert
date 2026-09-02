**Task id:** `DSP-01`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `CON-02`, `ESC-06`
**Branch:** `feature/dsp-01-raise-dispute`
**Labels:** `escrow`, `backend`

## Goal

Let a client contest a consultation during the one-hour hold window, which pauses the auto-release and routes the consultation to human mediation. This window is the reason the escrow exists at all, so the timing rules have to be exact.

## Requirements

1. `Dispute`: id, consultation id, raised-by user id, reason category, a free-text description, status (`OPEN`, `RESOLVED`), the resolution outcome, resolver id, raised_at, resolved_at.
2. Reason categories as an enum: professional did not attend, consultation cut short, service not as described, technical failure, other. Each with a French label.
3. `POST /api/v1/consultations/{id}/dispute`, permitted to the **client only**, and only while the consultation is in `HOLD_WINDOW` and the window has not expired. Per the feasibility study's recommendation, a dispute must be raised inside the hour.
4. Raising a dispute transitions `HOLD_WINDOW -> UNDER_REVIEW`, which is what stops the ESC-06 auto-release. The two must be verified to interact correctly under a race: a dispute landing in the same instant the sweeper runs must produce one outcome, not both.
5. One open dispute per consultation. A second attempt is a conflict.
6. A dispute cannot be raised on a consultation already released, refunded or cancelled; each returns its own documented code.
7. The description is free text written by a client and may contain sensitive detail. It must never be logged, and it is readable only by the client, the professional and admins.
8. `GET /api/v1/consultations/{id}/dispute` for the parties and admins.
9. Raising a dispute notifies the professional and the admin queue through the notification interface.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: a client raises a dispute in `HOLD_WINDOW`; the status becomes `UNDER_REVIEW` and an audit entry is written.
- Integration test: with the clock frozen one second before expiry, a dispute is accepted; one second after, it is refused.
- Race test: the auto-release job and a dispute request against the same consultation produce exactly one of the two outcomes, never a release **and** an `UNDER_REVIEW`, and the ledger reflects only what happened.
- Integration test: a professional cannot raise a dispute.
- Integration test: a second dispute on the same consultation is a conflict.
- Integration test: disputing a `RELEASED_TO_PRO` consultation is refused with its own code, and likewise for `REFUNDED` and `CANCELLED`.
- Integration test: a third party cannot read the dispute.
- Test asserting the description does not appear in any captured log line.
- Integration test: raising a dispute calls the notification interface for the professional.

## Deliverables

- `lexpert_api/disputes/models.py`, `service.py`, `router.py`, `schemas.py`.
- The Alembic migration.
- `apps/api/tests/disputes/test_raise_dispute.py` including the race test.
- Reason categories with French labels in `fr.ts`.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/dsp-01-raise-dispute`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
