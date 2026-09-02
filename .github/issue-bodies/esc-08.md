**Task id:** `ESC-08`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `ESC-03`, `SCH-04`
**Branch:** `feature/esc-08-checkout-ui`
**Labels:** `frontend`, `escrow`

## Goal

The screens where a client confirms a booking and the funds are held. In the MVP there is no real payment, and this screen carries the responsibility of saying so unambiguously while still demonstrating the real flow.

## Requirements

1. A checkout summary: professional, date and time in the client's timezone, duration, and the price breakdown exactly as the API returned it (rate x duration, commission, total). No client-side price arithmetic.
2. A clear French explanation of the escrow: the money is held, the professional is paid one hour after the consultation, a dispute can be raised in that hour.
3. An unmissable simulation notice — a distinct banner, not fine print — stating that this is a demonstration, that no real payment is taken and no card is charged. It must be impossible to reach the confirm button without having seen it.
4. A simulated payment step that visibly stands in for a real one, without imitating a card form. Do **not** build a fake card-number input: a screen that collects card-shaped data under false pretenses is the one thing this MVP must not do.
5. Explicit consent checkboxes before confirming: the cancellation policy (linking to the ESC-07 copy) and the platform terms. Unchecked means the confirm button stays disabled.
6. On confirm, call `POST /consultations` and handle every documented outcome: success goes to a confirmation screen; a slot conflict returns to the calendar with a French explanation; a provider decline explains and offers a retry; a network failure is distinguishable from a decline.
7. Double-submit protection: the confirm button disables on click and the request carries an idempotency-safe path, so a double click cannot create two consultations.
8. A confirmation screen: what was booked, when, what happens next, and how to join the consultation.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Component test: the summary renders the API's breakdown verbatim, and no arithmetic is performed client-side (assert against a breakdown whose numbers do not follow the naive formula).
- Component test: the simulation banner is present and is not visually dismissible before confirming.
- Component test: confirm is disabled until both consents are checked.
- Component test: a successful confirm calls the endpoint once and navigates to the confirmation screen.
- Component test: a double click results in exactly one request.
- Component test: a 409 conflict, a provider decline and a network error each render their own distinct French message.
- Component test: no input in the flow collects card-like data (assert on the rendered form fields).
- Manual: complete a booking end to end against a running local stack and confirm the consultation appears as `FUNDS_HELD` with a balanced ledger transaction.

## Deliverables

- `apps/web/src/features/client/checkout/` with the summary, simulation notice, consent panel and confirmation screen.
- Checkout keys in `fr.ts`, including the escrow explanation and the simulation notice.
- Component tests covering every item above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-08-checkout-ui`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
