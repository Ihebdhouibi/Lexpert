**Task id:** `DSP-02`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `DSP-01`
**Branch:** `feature/dsp-02-dispute-mediation`
**Labels:** `admin`, `escrow`, `backend`

## Goal

The admin's power to resolve a disputed consultation: pay the professional, refund the client, or split it. The feasibility study leaves partial release and mediation as policy to define; this issue defines it as a mechanism with an explicit, audited human decision.

## Requirements

1. `GET /api/v1/admin/disputes` — a paginated queue of open disputes, oldest first, filterable by status and reason category, showing how long each has been open.
2. `GET /api/v1/admin/disputes/{id}` — the dispute, the consultation, both parties, the session participation record from CON-02, the amounts, and the audit trail. The admin decides from evidence, so it must all be on one screen.
3. `POST /api/v1/admin/disputes/{id}/resolve` taking an outcome — release in full, refund in full, or a partial split with an explicit professional amount — plus a required resolution note.
4. A partial split is validated to sum exactly to the total held. A split that does not balance is refused; there is no rounding accommodation.
5. Resolution transitions `UNDER_REVIEW -> RELEASED_TO_PRO` or `UNDER_REVIEW -> REFUNDED` through the ESC-03 transition function, posting the corresponding ledger entries and appending the audit entry with the admin as actor and the note as the reason.
6. For a partial outcome, document and implement the ledger posting pattern in `ledger.md` **before** writing the code, since it is the only posting that splits a hold three ways.
7. Resolving an already-resolved dispute is a conflict. A consultation not in `UNDER_REVIEW` cannot be resolved.
8. Both parties are notified of the outcome with the resolution note.
9. Admin-only, via the router-level dependency.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: release in full pays the professional and the platform per the original split, with balanced ledger entries.
- Integration test: refund in full returns everything to the client and leaves the platform with nothing.
- Integration test: a partial split posts the exact stated amounts and balances.
- Integration test: a partial split whose amounts do not sum to the total is refused.
- Integration test: a resolution without a note is refused.
- Integration test: resolving twice is a conflict, and the second attempt posts no ledger entries.
- Integration test: resolving a consultation in `HOLD_WINDOW` (not yet disputed) is refused.
- Integration test: a non-admin is refused on every endpoint.
- Integration test: each outcome appends exactly one audit entry with the admin actor and the note.
- Integration test: both parties are notified.
- Integration test: after each outcome, the ledger total across all accounts is still zero.

## Deliverables

- `lexpert_api/admin/disputes_router.py` and the mediation service.
- The partial-split posting pattern documented in `docs/technical_docs/ledger.md`.
- `apps/api/tests/admin/test_dispute_mediation.py`.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/dsp-02-dispute-mediation`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
