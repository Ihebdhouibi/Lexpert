**Task id:** `BETA-02`
**Milestone:** Beta
**Size:** L (3 days or more)
**Depends on:** `BETA-01`
**Branch:** `feature/beta-02-local-wallets`
**Labels:** `escrow`, `frontend`, `backend`

## Goal

Accept the payment methods Tunisians actually use. The feasibility study names low card penetration and a cash culture as headwinds, and local wallets as the mitigation; a card-only checkout will not convert.

## Requirements

1. Support the wallet and card rails the chosen partner exposes, each behind the same pay-in operation so the escrow flow is method-agnostic.
2. Method selection in checkout with the method's real constraints surfaced (limits, fees where the user bears them, expected confirmation time).
3. Asynchronous confirmation: several of these methods confirm out of band, so a booking must be able to sit in a pending-payment state and either progress to `FUNDS_HELD` or expire. This is a genuine addition to the state machine and needs its own transition matrix tests.
4. A pending-payment expiry that releases the held slot, so an abandoned payment does not block a professional's calendar.
5. Per-method failure handling with honest French messaging.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Sandbox test per method: a successful pay-in reaches `FUNDS_HELD`.
- Test: the pending-payment state transitions are exhaustively covered, as in ESC-03.
- Test: an expired pending payment releases the slot and cancels the consultation.
- Test: a slot held by a pending payment is not offered to another client.
- Test per method: a declined or abandoned payment leaves no ledger movement.
- Component test: method selection renders each method's constraints.

## Deliverables

- Per-method support in the provider adapter.
- The pending-payment state and its expiry job.
- Checkout method selection.
- Tests as listed above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/beta-02-local-wallets`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
