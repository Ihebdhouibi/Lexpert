**Task id:** `ESC-02`
**Milestone:** MVP
**Size:** L (3 days or more)
**Depends on:** `FND-03`
**Branch:** `feature/esc-02-ledger`
**Labels:** `escrow`, `database`, `backend`

## Goal

The financial record of the platform: every movement of value recorded as balanced double-entry postings, from which every balance is derived rather than stored. The feasibility study calls for an immutable record of every escrow transition for financial traceability; this is that record's foundation.

## Requirements

1. `LedgerAccount`: id, type (`CLIENT`, `ESCROW_HOLD`, `PROFESSIONAL_PAYABLE`, `PLATFORM_REVENUE`, `EXTERNAL`), owner reference where applicable, currency. One escrow-hold account per consultation keeps holds individually traceable.
2. `LedgerTransaction`: id, an idempotency key (unique), a kind, a reference to the consultation, a description, created_at. `LedgerEntry`: transaction id, account id, a signed integer amount in millimes.
3. **Both tables are append-only.** No `UPDATE` and no `DELETE`, enforced by a database trigger or rule, not merely by convention in the service layer. A correction is a new, reversing transaction.
4. The core invariant: the entries of a transaction sum to exactly zero. Enforce it in the posting function **and** with a database constraint or trigger, so no code path can write an unbalanced transaction.
5. One `post_transaction(kind, entries, idempotency_key, ...)` function is the only way to write to the ledger. Replaying an idempotency key returns the existing transaction without writing.
6. Balance queries derived by summation, with an index that makes per-account summation fast. Do not cache a balance column in the MVP; a stored balance that can disagree with the entries is worse than a slower query.
7. Amounts are integer millimes throughout. A non-integer amount is a programming error and must raise, not round.
8. A reversal helper that posts the exact inverse of a prior transaction, referencing it, for corrections and for refunds.
9. The ledger module exposes only `post_transaction`, the balance queries and the reversal helper. Nothing outside `escrow` may import the models.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: a balanced two-entry transaction posts and both entries persist.
- Unit test: an unbalanced transaction is refused by the posting function.
- Integration test: an unbalanced transaction inserted **directly via SQL**, bypassing the service, is refused by the database. This is the test that proves the invariant is real.
- Integration test: an `UPDATE` and a `DELETE` against either ledger table are refused by the database.
- Unit test: replaying an idempotency key returns the original transaction and adds no rows.
- Unit test: a balance equals the sum of its account's entries, across several transactions.
- Unit test: a float or Decimal-with-fraction amount raises rather than rounding.
- Unit test: a reversal produces exactly inverse entries and references the original.
- Property test: over a few hundred randomly generated valid transactions, the sum of **all** entries across all accounts is always zero.
- Integration test: two concurrent posts with the same idempotency key result in exactly one transaction.
- Performance check: with 100000 entries, a per-account balance query uses the index; paste the plan in the PR.

## Deliverables

- `lexpert_api/escrow/ledger/` with `models.py`, `posting.py`, `balances.py`.
- The Alembic migration including the append-only and balance constraints or triggers.
- `apps/api/tests/escrow/test_ledger.py` covering every item above, including the raw-SQL bypass attempts.
- `docs/technical_docs/ledger.md` with the account types and the posting patterns for hold, release, refund and commission.

## Notes

The raw-SQL bypass tests are the point of this issue. A balance invariant enforced only in Python is an invariant that holds until the first migration script or admin fix-up query, and the whole value of a ledger is that it cannot be quietly wrong.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-02-ledger`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
