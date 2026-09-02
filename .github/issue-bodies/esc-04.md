**Task id:** `ESC-04`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `ESC-03`
**Branch:** `feature/esc-04-audit-log`
**Labels:** `escrow`, `compliance`, `database`

## Goal

An append-only record of every escrow state transition: who, when, from what state to what state, why, and which ledger transaction it produced. The feasibility study lists this under financial traceability, and it is the artifact a payment partner or a regulator will ask to see.

## Requirements

1. `EscrowAuditEntry`: id, consultation id, sequence number within that consultation, from status, to status, actor type (`CLIENT`, `PROFESSIONAL`, `ADMIN`, `SYSTEM`), actor id, reason, ledger transaction id, provider reference, occurred_at, and a JSON snapshot of the amounts at that moment.
2. Append-only at the **database** level: a trigger or rule refusing `UPDATE` and `DELETE`, as with the ledger.
3. Written inside the same transaction as the transition it records, so a transition without an audit entry is impossible. Not a listener, not a background task.
4. The sequence number is contiguous per consultation and gapless, so a missing entry is detectable.
5. A tamper-evidence chain: each entry stores a hash over its own content plus the previous entry's hash for that consultation. Any retro-edit of an earlier entry breaks verification for every entry after it.
6. `GET /api/v1/admin/consultations/{id}/audit` for admins, and a verification function that walks a consultation's chain and reports whether it is intact.
7. The reason field carries operational context only. **No consultation content, no health, legal or financial detail.** Say so in the model docstring.
8. A test that enumerates every call site of `transition()` and asserts an audit entry results — so a future transition path cannot skip the log.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: every transition in the happy path produces exactly one entry, sequence numbers 1..n with no gaps.
- Integration test: `UPDATE` and `DELETE` on the audit table, via raw SQL, are refused.
- Integration test: a transition whose surrounding database transaction rolls back leaves **no** audit entry and no status change.
- Unit test: the hash chain verifies on an intact chain.
- Integration test: mutating an entry's content in the database (with the trigger temporarily disabled, inside the test) makes verification fail from that point on.
- Integration test: each actor type is recorded correctly, including `SYSTEM` for the ESC-06 auto-release.
- Integration test: the admin endpoint returns the full chain; a client is refused.
- The call-site coverage test fails when a transition path without an audit entry is introduced.

## Deliverables

- `lexpert_api/escrow/audit.py` and its models.
- The Alembic migration with the append-only trigger.
- The admin audit endpoint.
- `apps/api/tests/escrow/test_audit.py` covering every item above.
- A `## Audit trail` section in `docs/technical_docs/escrow_lifecycle.md`.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-04-audit-log`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
