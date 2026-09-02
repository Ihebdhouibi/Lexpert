**Task id:** `BETA-03`
**Milestone:** Beta
**Size:** L (3 days or more)
**Depends on:** `BETA-01`
**Branch:** `feature/beta-03-diaspora-fx`
**Labels:** `escrow`, `compliance`, `backend`

## Goal

Let a Tunisian abroad pay a professional at home. The feasibility study identifies the diaspora as a major demand segment and BCT foreign-exchange controls as the obstacle, so this is a compliance issue with a technical component rather than the reverse.

## Requirements

1. **Gate:** written confirmation of a compliant cross-border flow, from the same advisory work as BETA-01. This cannot be designed from the technical side alone.
2. Multi-currency pay-in with the exchange rate captured at booking and stored on the consultation, so the client's total is fixed at the moment they agree to it.
3. Ledger support for a second currency without breaking the balance invariant: entries balance within a currency, and conversion is an explicit two-transaction operation with the rate recorded.
4. Payout to the professional in dinars regardless of the pay-in currency.
5. Whatever declarations or limits the confirmed flow requires, enforced in code and surfaced to the client before they pay.
6. Startup Act status, if obtained, may change what is permitted — keep the constraints configurable rather than hard-coded.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Test: a multi-currency consultation stores the rate and the total does not move afterwards.
- Test: the ledger balances within each currency, and a conversion is two balanced transactions with the rate recorded.
- Property test: the balance invariant holds per currency across generated transactions.
- Test: a payout is in dinars for a foreign-currency pay-in, and the amounts reconcile.
- Test: each configured limit or declaration requirement is enforced and surfaced.
- Sandbox end-to-end for at least one foreign currency.

## Deliverables

- Multi-currency ledger support and its migration.
- Rate capture and the conversion posting pattern documented in `ledger.md`.
- The compliance constraints as configuration.
- Tests as listed above, and the legal confirmation referenced from the PR.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/beta-03-diaspora-fx`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
