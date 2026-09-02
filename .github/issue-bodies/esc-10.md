**Task id:** `ESC-10`
**Milestone:** MVP
**Size:** L (3 days or more)
**Depends on:** `ESC-03`, `SCH-02`
**Branch:** `feature/esc-10-request-acceptance`
**Labels:** `escrow`, `backend`, `api`

## Goal

A consultation is requested by the client and must be accepted by the professional before it is confirmed. This issue builds that handshake: the request endpoint, the professional's accept and decline endpoints, and the job that expires a request the professional never answers -- each refunding the client in full where the consultation does not go ahead.

## Requirements

1. The states `PENDING_ACCEPTANCE`, `DECLINED` and `EXPIRED` come from ESC-03's state machine. This issue builds the endpoints and the job that drive them; it does not redefine the machine.
2. `POST /api/v1/consultations` (client) validates the slot, computes the price, authorizes the escrow hold, and lands the consultation in `PENDING_ACCEPTANCE`. The client's funds are held from this moment, so the professional is accepting a consultation that is already funded.
3. `POST /api/v1/consultations/{id}/accept` (professional only, own consultation only) transitions `PENDING_ACCEPTANCE -> FUNDS_HELD`. This is the point the consultation is confirmed and the slot is committed.
4. `POST /api/v1/consultations/{id}/decline` (professional only) takes an optional reason from a fixed set of French-labelled categories plus free text, refunds the client **in full** through the provider, posts the reversing ledger entries, and transitions to `DECLINED`. A decline never costs the client anything.
5. A response deadline on every request: `acceptance_deadline_at = requested_at + LEXPERT_ACCEPTANCE_WINDOW_HOURS`, from settings, and additionally capped so the deadline never falls after the consultation's own scheduled start.
6. An expiry job, built on the ESC-06 pattern: select `PENDING_ACCEPTANCE` consultations past their deadline with `SELECT ... FOR UPDATE SKIP LOCKED`, refund each in full, transition to `EXPIRED`, process each independently so one failure does not stop the batch, and make it idempotent so a second run is a no-op.
7. A pending request **holds its slot**: the slot is not offered to another client while a request for it is awaiting acceptance. The ESC-03 overlap constraint must treat `PENDING_ACCEPTANCE` as non-terminal, and SCH-02 must exclude it.
8. A client can withdraw a request while it is still `PENDING_ACCEPTANCE`, refunded in full, transitioning to `CANCELLED`. Withdrawing after acceptance goes through the ESC-07 cancellation policy instead, because by then the professional has committed the time.
9. A professional can only accept if their verification is still `APPROVED` and their profile still published. A professional suspended between request and acceptance cannot accept; the request expires and the client is refunded.
10. Every transition goes through the ESC-03 transition function, so the ledger posting and the ESC-04 audit entry happen for each of accept, decline, expire and withdraw, with the correct actor.
11. Notifications on each event, through the NOT-01 interface: request received (professional), accepted, declined, expired and withdrawn (the counterparty). Wired fully in NOT-02.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: a request lands in `PENDING_ACCEPTANCE` with a hold authorized, a balanced ledger transaction and an audit entry.
- Integration test: accept moves to `FUNDS_HELD`; the amounts are unchanged and no second hold is authorized.
- Integration test: decline refunds the client in full, leaves the platform with nothing, and the ledger nets to zero for that consultation.
- Integration test: the same for expiry, with actor `SYSTEM`, and for withdrawal, with actor `CLIENT`.
- Integration test with a frozen clock: the expiry job expires a request one second past its deadline and leaves one a second before it alone. Test the exact boundary instant too.
- Integration test: the acceptance deadline is capped at the scheduled start when the configured window would run past it.
- Integration test: running the expiry job twice refunds once; the second run posts no further ledger entries.
- Concurrency test: two workers over the same expired set expire each consultation exactly once.
- Concurrency test: an accept and the expiry job racing on the same consultation produce exactly one outcome, never both a `FUNDS_HELD` and an `EXPIRED`.
- Concurrency test: accept and decline racing produce one outcome and one rejection.
- Integration test: while a request is `PENDING_ACCEPTANCE`, its slot is absent from `GET /professionals/{id}/slots`, and a second request for it is refused with a conflict.
- Integration test: after a decline or an expiry, that slot becomes bookable again.
- Integration test: a different professional cannot accept or decline; a client cannot accept their own request.
- Integration test: accepting an already-accepted, declined or expired consultation is refused, each with its documented code.
- Integration test: a professional whose verification was revoked after the request cannot accept.
- Integration test: withdrawal after acceptance is routed to the ESC-07 policy, not refunded unconditionally.
- Integration test: after every path, the ledger total across all accounts is still zero.

## Deliverables

- The request, accept, decline and withdraw endpoints in `lexpert_api/booking/router.py`, with their service functions.
- `lexpert_api/booking/jobs/expire_requests.py` and its CLI entry point.
- The decline-reason categories with French labels in `fr.ts`.
- `LEXPERT_ACCEPTANCE_WINDOW_HOURS` added to `.env.example`.
- `apps/api/tests/booking/test_request_acceptance.py` and `test_request_expiry.py`, including the concurrency and boundary tests.
- The handshake documented in `docs/technical_docs/escrow_lifecycle.md`, with the diagram updated.

## Notes

**A design decision worth confirming before implementing.** The escrow hold is authorized when the client *requests*, not when the professional accepts. That keeps the feasibility study's promise that the professional sees funds confirmed before committing time, and it needs no second client action after acceptance. The cost is that a client's funds are held briefly for a consultation that may be declined -- which is why a decline, an expiry and a withdrawal all refund in full, and why the acceptance window is short.

The alternative -- request first, pay after acceptance -- means the professional accepts an unfunded consultation and the client has to return to pay, which loses the escrow guarantee and adds a drop-off point. If the owner prefers it, say so on this issue before starting: it changes ESC-03, ESC-08 and this issue together, and is much cheaper to change now than later.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-10-request-acceptance`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
