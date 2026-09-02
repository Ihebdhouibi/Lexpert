**Task id:** `KYC-04`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `KYC-02`, `KYC-03`, `AUT-03`
**Branch:** `feature/kyc-04-submission-api`
**Labels:** `kyc-pro`, `api`, `backend`

## Goal

The endpoints a professional uses to fill in, submit and track their verification file. This is where the rule sets from KYC-03 and the state machine from KYC-01 meet.

## Requirements

1. `GET /api/v1/verification/me` returning the file, its status, its fields, its documents, the requirements for its vertical, and the current violations — so the UI can render progress without a second call.
2. `PATCH /api/v1/verification/me` saving field values as a draft. Permitted only in `DRAFT` and `MORE_INFO_REQUESTED`. Partial saves are allowed and are not validated against the rule set.
3. `POST /api/v1/verification/me/submit` running the full rule set. On violations, return 422 with the envelope and every violation in `details`, and do **not** change status. On success, transition to `SUBMITTED`.
4. Submission additionally requires the professional's phone to be verified (AUT-02) and their vertical to be set. A vertical cannot be changed once a file has been submitted.
5. `GET /api/v1/verification/me/events` returning the audit trail so the professional can see what happened and when.
6. Every endpoint is restricted to `role == PROFESSIONAL` and operates only on the caller's own file. There is no endpoint that takes another user's file id.
7. A professional resubmitting after `MORE_INFO_REQUESTED` or `REJECTED` keeps their history; the events are appended, not replaced.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test, one per vertical: fill fields, upload documents, submit successfully, status becomes `SUBMITTED`.
- Integration test: submitting an incomplete file returns 422 with all violations and leaves the status at `DRAFT`.
- Integration test: `PATCH` while `UNDER_REVIEW` is refused.
- Integration test: submitting with an unverified phone is refused with the documented code.
- Integration test: changing the vertical after submission is refused.
- Integration test: a client-role user is refused on every endpoint.
- Integration test: the full round trip `SUBMITTED -> MORE_INFO_REQUESTED -> PATCH -> SUBMITTED` works and the event list shows all four entries.
- Integration test: `GET /verification/me` for a professional with no file returns a sensible empty-draft representation rather than a 404.

## Deliverables

- `lexpert_api/verification/router.py` and `schemas.py`.
- `apps/api/tests/verification/test_submission_api.py`.
- OpenAPI documentation for the five endpoints including the 422 violation shape.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/kyc-04-submission-api`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
