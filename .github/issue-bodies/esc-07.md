**Task id:** `ESC-07`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `ESC-03`
**Branch:** `feature/esc-07-cancellation-policy`
**Labels:** `escrow`, `backend`

## Goal

Encode the rules from feasibility study section 5.2 for what happens when a consultation does not go ahead: who cancelled, how late, who failed to show, and therefore what portion of the held funds is refunded or retained. These are business policy, so they belong in one declarative, testable place rather than scattered across endpoints.

## Requirements

1. A pure policy function taking who is cancelling, the time until the scheduled start, the consultation state and the amounts, and returning an outcome: refund in full, refund partially with a stated retained amount, or no refund.
2. A cancellation while the consultation is still `PENDING_ACCEPTANCE` always refunds in full, whoever initiates it: the professional has not committed any time yet, so there is nothing to compensate. ESC-10 owns the endpoints for that state; this issue owns the rule.
3. Tiered client cancellation: free outside a configurable window (for example more than 24 hours before), a configurable retained percentage inside it, and a different tier very close to the start. All thresholds and percentages come from settings, not from literals in the code.
4. Professional cancellation always refunds the client in full, at any notice. The study is explicit that the platform protects the client here.
5. No-show handling: a professional no-show refunds the client in full; a client no-show retains per policy. A no-show is determined from the CON-02 participation record, not asserted by either party.
6. A grace period after the scheduled start before a no-show can be declared, from settings.
7. Endpoints: `POST /api/v1/consultations/{id}/cancel` for the client and the professional, which computes the outcome, performs the refund through the provider, posts the ledger entries and transitions to `CANCELLED` or `REFUNDED`.
8. Retained amounts are split between professional and platform per a documented rule, and the ledger postings for every outcome are documented in `ledger.md` before the code is written.
9. The policy function is pure and has no database or provider access, so the whole matrix can be tested exhaustively.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: a table-driven matrix over {client, professional} x {well before, inside window, just before, after start} x {PENDING_ACCEPTANCE, FUNDS_HELD} asserting the expected outcome for every cell. Every cell is populated; none is left implicit.
- Unit test: every `PENDING_ACCEPTANCE` cell refunds in full, for both initiators and at every notice level.
- Unit test: each tier boundary is tested on both sides and exactly at the boundary.
- Unit test: a professional cancellation refunds in full even one minute before the start.
- Unit test: outcome amounts always sum to the total held, with no millime lost or created.
- Integration test: a client cancellation inside the window refunds the correct partial amount, posts balanced ledger entries, and audits the transition.
- Integration test: cancelling a consultation already `IN_SESSION` is refused.
- Integration test: cancelling an already-cancelled consultation is refused.
- Integration test: a third party cannot cancel someone else's consultation.
- Integration test: a client no-show inside the grace period cannot yet be declared; after it, it can.
- Integration test: a professional no-show refunds the client fully and records the outcome.
- Integration test: after every cancellation path, the ledger total across all accounts is still zero.

## Deliverables

- `lexpert_api/escrow/policy.py` — the pure policy function and its outcome type.
- The cancel endpoint and the no-show determination service.
- New settings for the windows, percentages and grace period, added to `.env.example`.
- `apps/api/tests/escrow/test_cancellation_policy.py` with the full matrix.
- `docs/technical_docs/cancellation_policy.md` — the policy in prose, as the reference for the French copy in the UI.

## Notes

The specific windows and percentages are business decisions the feasibility study leaves open. Implement the mechanism with defaults, list the exact numbers you chose in the PR description, and expect them to be adjusted in review rather than treated as settled.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-07-cancellation-policy`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
