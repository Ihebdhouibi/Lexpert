**Task id:** `ESC-03`
**Milestone:** MVP
**Size:** L (3 days or more)
**Depends on:** `ESC-01`, `ESC-02`, `SCH-02`, `ESC-05`
**Branch:** `feature/esc-03-booking-state-machine`
**Labels:** `escrow`, `backend`, `database`

## Goal

The heart of the product: creating a consultation, holding the funds, and moving it through the lifecycle from the feasibility study's state machine. Every transition is validated, ledger-posted and audited, and no two clients can take the same slot.

## Requirements

1. `Consultation`: id, client id, professional id, scheduled start and end (UTC), duration, timezone captured at booking, status, amounts (professional amount, commission, total), provider hold reference, hold-window expiry, timestamps.
2. Implement exactly these transitions and nothing more. They are the feasibility study's section 5.1 machine plus the request-and-accept handshake the MVP requires, which the study does not model:
    - `BOOKED -> PENDING_ACCEPTANCE` (the client's hold is authorized)
    - `BOOKED -> CANCELLED` (the hold was declined by the provider)
    - `PENDING_ACCEPTANCE -> FUNDS_HELD` (the professional accepted)
    - `PENDING_ACCEPTANCE -> DECLINED` (the professional refused)
    - `PENDING_ACCEPTANCE -> EXPIRED` (no answer before the deadline)
    - `PENDING_ACCEPTANCE -> CANCELLED` (the client withdrew)
    - `FUNDS_HELD -> IN_SESSION`, `FUNDS_HELD -> CANCELLED`, `FUNDS_HELD -> REFUNDED`
    - `IN_SESSION -> SESSION_ENDED`, `SESSION_ENDED -> HOLD_WINDOW`
    - `HOLD_WINDOW -> RELEASED_TO_PRO`, `HOLD_WINDOW -> UNDER_REVIEW`
    - `UNDER_REVIEW -> RELEASED_TO_PRO`, `UNDER_REVIEW -> REFUNDED`
  Every other transition raises. This issue owns the whole machine; ESC-10 builds the endpoints and the expiry job that drive the handshake states, so keep the matrix here and do not duplicate it there.
3. `DECLINED` and `EXPIRED` are terminal, and both require the client to have been refunded in full. A consultation cannot reach either state with funds still held.
4. `RELEASED_TO_PRO`, `REFUNDED`, `CANCELLED`, `DECLINED` and `EXPIRED` are terminal. No transition leaves a terminal state, ever.
5. One `transition(consultation, to_status, actor, reason)` function is the only way status changes. It locks the row (`SELECT FOR UPDATE`), validates the transition, performs the provider call and the ledger posting, appends the audit entry, and commits — all in one database transaction.
6. **Slot concurrency is resolved here.** A database-level exclusion or unique constraint prevents two non-terminal consultations overlapping for the same professional. `PENDING_ACCEPTANCE` counts as non-terminal, so an unanswered request holds its slot. Two simultaneous requests for one slot must yield one success and one conflict error, never two.
7. Request flow: validate the slot against SCH-02, compute amounts via ESC-05, create the consultation as `BOOKED`, call `authorize_hold` with an idempotency key derived from the consultation id, post the hold to the ledger, and transition to `PENDING_ACCEPTANCE` -- awaiting the professional's answer. If the provider declines, the consultation ends `CANCELLED` with the reason and no ledger movement. The accept, decline and expiry paths are ESC-10.
8. Ledger postings per transition, exactly as documented in `ledger.md`: the hold moves value from the client account to the consultation's escrow-hold account; release splits it between professional payable and platform revenue; a refund reverses the hold.
9. The provider call and the ledger post must not be able to disagree. Where the provider succeeds and the local transaction then fails, the idempotency key makes the retry safe; document this recovery path explicitly.
10. Endpoints: `POST /api/v1/consultations` (client requests), `GET /api/v1/consultations` (the caller's own, filtered by status), `GET /api/v1/consultations/{id}` (client, professional or admin only).

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: a table-driven test over the full transition matrix asserts every legal transition is allowed and **every** illegal one raises. This includes every transition out of each terminal state.
- Integration test: a successful request ends `PENDING_ACCEPTANCE`, with a provider hold, a balanced ledger transaction, and an audit entry.
- Integration test: a provider decline leaves the consultation `CANCELLED` and the ledger **empty** for it.
- Integration test: a provider timeout leaves no partially-booked state; retrying with the same key does not double-hold.
- Concurrency test: two parallel requests for the identical slot produce exactly one `PENDING_ACCEPTANCE` consultation and one conflict error. Run it enough times to be meaningful.
- Concurrency test: two parallel transitions of the same consultation produce one success and one rejection, not two.
- Integration test: booking a slot outside availability is refused.
- Integration test: booking inside the minimum-notice window is refused.
- Integration test: a client cannot book on behalf of another client; a professional cannot book their own slot.
- Integration test: after every transition, the ledger's total across all accounts is still zero.
- Integration test: a client requesting another client's consultation gets 404.
- Integration test: the full happy path across all states leaves consistent amounts: professional payable plus platform revenue equals the total held.

## Deliverables

- `lexpert_api/booking/models.py`, `lexpert_api/escrow/state_machine.py`, `lexpert_api/booking/service.py`, `router.py`, `schemas.py`.
- The Alembic migration including the overlap-exclusion constraint.
- `apps/api/tests/escrow/test_state_machine.py` (the matrix), `test_booking_flow.py`, `test_booking_concurrency.py`.
- The state diagram in `docs/technical_docs/escrow_lifecycle.md`, matching the code.

## Notes

This is the largest and most consequential issue in the MVP. Two things earn special care in review: the transition matrix test must be exhaustive rather than representative, and the concurrency tests must actually run in parallel against a real PostgreSQL. A serialised test proves nothing about the constraint. If this issue starts feeling too large to review in one pass, say so on the issue and we will split the transition machinery from the booking endpoint.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-03-booking-state-machine`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
