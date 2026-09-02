**Task id:** `KYC-06`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `KYC-04`, `AUT-03`
**Branch:** `feature/kyc-06-admin-review-api`
**Labels:** `admin`, `kyc-pro`, `backend`

## Goal

The API an admin uses to work through submitted verification files and decide them. Manual review is the compliance control the whole regulated-professions story rests on, so it has to be recorded properly and impossible to bypass.

## Requirements

1. `GET /api/v1/admin/verification` — a paginated queue, filterable by status and vertical, sortable by submission date, defaulting to pending files oldest first.
2. `GET /api/v1/admin/verification/{id}` — the full file: fields, documents with read URLs, current violations, the applicant's account details, and the event history.
3. `POST /api/v1/admin/verification/{id}/claim` transitioning `SUBMITTED -> UNDER_REVIEW` and recording the reviewer, so two admins do not review the same file. Claiming an already-claimed file is a conflict.
4. `POST .../approve`, `POST .../reject` (reason required, minimum length enforced), `POST .../request-info` (message required). All go through the KYC-01 state machine.
5. Approving sets the professional's verification to `APPROVED`, which is what makes them visible to PRO-02 search and bookable. Nothing else grants that.
6. Every decision appends a `VerificationEvent` with the reviewer, the timestamp, the transition and the reason or message. Events are append-only; there is no edit or delete endpoint.
7. Each decision triggers a notification to the professional through the AUT-02 interface.
8. The whole router is admin-only via the router-level dependency from AUT-03.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: the queue returns pending files oldest first and honours the status and vertical filters.
- Integration test: a professional-role user is refused on every admin endpoint.
- Integration test: claim, then approve; the professional's status is `APPROVED` and two events exist.
- Integration test: a second admin claiming a claimed file gets a conflict.
- Integration test: reject without a reason, and with a one-character reason, are both refused.
- Integration test: `request-info` without a message is refused.
- Integration test: approving a file that is still `SUBMITTED` (unclaimed) is refused by the state machine.
- Integration test: an approved professional appears in the PRO-02 search query; the same professional before approval does not.
- Integration test: each decision calls the notification interface once.
- Integration test: the detail response's document URLs are fetchable by the admin.

## Deliverables

- `lexpert_api/admin/verification_router.py` and its schemas.
- `apps/api/tests/admin/test_verification_review.py`.
- OpenAPI documentation for the six endpoints.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/kyc-06-admin-review-api`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
