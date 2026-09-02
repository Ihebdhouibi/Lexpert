**Task id:** `BETA-01`
**Milestone:** Beta
**Size:** L (3 days or more)
**Depends on:** `ESC-01`, `ESC-03`, `CMP-03`
**Branch:** `feature/beta-01-payment-partner`
**Labels:** `escrow`, `backend`, `compliance`

## Goal

Replace the simulator with a real licensed Tunisian payment provider or bank, so that actual money moves through the escrow the MVP modelled. This is the single issue the whole ESC-01 boundary exists to make possible, and it is gated on the feasibility study's payment and BCT memo confirming which provider can legally support delayed release and marketplace payouts.

## Requirements

1. **Gate:** the payment and escrow legal memo from feasibility study section 3.2 must exist and name a provider before this issue starts. Do not begin integration against a provider whose legal fitness is unconfirmed.
2. Implement the chosen provider's adapter against the unchanged `EscrowProvider` protocol, covering pay-in authorization, hold, release to a payee, and refund, with genuine idempotency keys.
3. Run the ESC-01 contract test suite against the new adapter in the provider's sandbox. Passing it unchanged is the acceptance criterion. A change to the protocol required by the provider is a finding to discuss, not a change to make quietly.
4. Webhook handling for the provider's asynchronous outcomes, with signature verification, replay protection and idempotency, following the CON-02 pattern.
5. Reconciliation: a scheduled job comparing the provider's hold and payout state against the local ledger, reporting every discrepancy rather than auto-correcting. A money system that silently self-heals hides the bug that caused the discrepancy.
6. Remove the MVP simulation notices from the UI, in the same change that makes them untrue, and not before.
7. The simulator remains in the codebase and stays the provider used in tests and local development. It must not be deleted.
8. A documented, tested rollback: how to return to the simulator if the provider integration has to be switched off.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- The ESC-01 contract suite passes against the real adapter in sandbox, unchanged.
- Sandbox end-to-end: book, hold, consult, auto-release, and confirm the provider shows the payout and the ledger agrees to the millime.
- Sandbox end-to-end: a refund path, likewise reconciled.
- Sandbox: a partial dispute resolution reconciles.
- Test: an unsigned or replayed provider webhook is rejected.
- Test: a redelivered webhook does not double-release.
- Test: the reconciliation job detects a deliberately introduced discrepancy and reports rather than corrects it.
- Test: switching `LEXPERT_ESCROW_PROVIDER` back to `simulator` restores the MVP behaviour with no code change.
- Confirmation in the PR that the simulation notices were removed in this change.

## Deliverables

- The provider adapter and its webhook handler.
- The reconciliation job and its report.
- The contract suite run output, attached to the PR.
- `docs/technical_docs/escrow_provider_boundary.md` updated with the live provider and the rollback procedure.
- A record of the legal memo that gated this work, referenced from the PR.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/beta-01-payment-partner`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
