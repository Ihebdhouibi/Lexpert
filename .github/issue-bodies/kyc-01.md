**Task id:** `KYC-01`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `AUT-01`, `FND-07`
**Branch:** `feature/kyc-01-data-model`
**Labels:** `kyc-pro`, `database`, `backend`

## Goal

Model the professional verification file that all three verticals share, with the per-regulator fields kept where they can vary independently, and the review state machine that governs how a file moves from draft to approved. This is the schema every other KYC issue builds on.

## Requirements

1. `VerificationFile`: id, user id (unique — one file per professional), vertical, status, submitted_at, reviewed_at, reviewer id, rejection reason, more-info message, timestamps.
2. `VerificationField`: the regulator-specific values, stored as a validated JSON column or a per-vertical detail table. Choose one and justify the choice in the PR description; both are defensible, but a mix is not.
3. `VerificationDocument`: id, file id, document type, storage key, original filename, content type, byte size, checksum, uploaded_at. **The document bytes never live in the database.**
4. Document types as an enum covering what all three verticals need: `NATIONAL_ID`, `DIPLOMA`, `REGULATOR_CERTIFICATE`, `PROOF_OF_ADDRESS`, `OTHER`.
5. The review state machine with exactly these legal transitions: `DRAFT -> SUBMITTED`, `SUBMITTED -> UNDER_REVIEW`, `UNDER_REVIEW -> APPROVED`, `UNDER_REVIEW -> REJECTED`, `UNDER_REVIEW -> MORE_INFO_REQUESTED`, `MORE_INFO_REQUESTED -> SUBMITTED`, `REJECTED -> SUBMITTED` (a resubmission after fixing the file). Every other transition is refused.
6. Transitions go through one service function that validates the transition, requires a reason on `REJECTED` and a message on `MORE_INFO_REQUESTED`, and appends a `VerificationEvent` audit row. Direct status writes are not allowed anywhere else.
7. An index supporting the admin queue query: files in `SUBMITTED` or `UNDER_REVIEW`, oldest first.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: a table-driven test over the full transition matrix asserts every legal transition is allowed and **every** illegal one raises.
- Unit test: `REJECTED` without a reason is refused; `MORE_INFO_REQUESTED` without a message is refused.
- Unit test: each transition appends exactly one `VerificationEvent` with the actor, the from- and to-status, and the timestamp.
- Integration test: two files for the same user violate the uniqueness constraint.
- Integration test: the admin queue query returns pending files oldest first and excludes approved and rejected ones.
- `alembic upgrade head` then `--autogenerate` produces an empty migration.

## Deliverables

- `lexpert_api/verification/models.py`, `state_machine.py`, `service.py`.
- The Alembic migration for the four tables.
- `apps/api/tests/verification/test_state_machine.py` with the transition matrix.
- A transition diagram in `docs/technical_docs/kyc_review_workflow.md`.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/kyc-01-data-model`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
