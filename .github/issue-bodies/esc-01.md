**Task id:** `ESC-01`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `FND-05`
**Branch:** `feature/esc-01-escrow-provider`
**Labels:** `escrow`, `backend`

## Goal

Define the seam between Lexpert's escrow policy and whoever actually moves money, and implement the MVP's simulator behind it. Getting this boundary right is what makes the Beta swap to a licensed partner a contained change instead of a rewrite, so it is worth doing carefully even though the simulator itself is simple.

## Requirements

1. An `EscrowProvider` protocol with exactly the operations a licensed provider performs: `authorize_hold(amount, currency, payer_ref, idempotency_key)`, `release(hold_ref, payee_ref, amount, idempotency_key)`, `refund(hold_ref, amount, idempotency_key)`, `get_hold(hold_ref)`.
2. Every operation takes an **idempotency key** and is safe to retry: the same key returns the same result and does not perform the action twice. Real providers work this way and code written against a non-idempotent fake will break on the swap.
3. Operations return a provider-agnostic result object (a reference, a status, an amount) and raise provider-agnostic errors (`ProviderDeclined`, `ProviderUnavailable`, `ProviderInvalidState`). No HTTP status, no provider payload, and no provider vocabulary crosses the boundary.
4. `SimulatedEscrowProvider`: persists its own hold records in its own table, transitions them, honours idempotency keys, and is deterministic.
5. The simulator supports **fault injection** driven by configuration or by the payer reference in tests: a declined authorization, a provider timeout, and a hold that is already released. Without these, the domain layer's error handling is untested and the Beta swap will surface bugs the MVP never exercised.
6. Provider selection by `LEXPERT_ESCROW_PROVIDER` through a factory, with `simulator` the only registered value in the MVP and an unknown value failing at startup.
7. The simulator's own records are the only place the word 'simulated' appears in the escrow module. The domain layer must not know which provider it has.
8. A prominent module docstring stating that no real funds move, why (the feasibility study section 3.2), and what must not leak across the boundary in either direction.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: authorize, then release; the hold's status follows the documented path.
- Unit test: authorize, then refund.
- Unit test: the same idempotency key replayed on each of the three mutating operations returns the identical result and creates no second record.
- Unit test: releasing an already-released hold raises `ProviderInvalidState`.
- Unit test: refunding a released hold raises `ProviderInvalidState`.
- Unit test: each injectable fault raises the mapped provider-agnostic error.
- Unit test: an unknown `LEXPERT_ESCROW_PROVIDER` fails at startup with a clear message.
- A structural test asserting the protocol's signatures, so a change to the interface is a deliberate, visible act.
- `grep -rn "simulat" apps/api/src/lexpert_api` finds matches only in the adapter, its tests, and docstrings — never in the ledger or the state machine.

## Deliverables

- `lexpert_api/escrow/provider.py` (the protocol, the result and error types).
- `lexpert_api/escrow/providers/simulator.py` and its migration.
- `lexpert_api/escrow/providers/factory.py`.
- `apps/api/tests/escrow/test_provider_contract.py` — written so it can later be run against a real provider adapter unchanged.
- `docs/technical_docs/escrow_provider_boundary.md` documenting the seam and the Beta swap procedure.

## Notes

Write the contract test suite so it is parameterised over provider implementations. In the MVP it runs against the simulator only; in Beta the same suite runs against the real adapter in sandbox and is the acceptance criterion for the swap. That is the highest-leverage thing this issue can produce.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-01-escrow-provider`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
