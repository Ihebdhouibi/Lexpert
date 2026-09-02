**Task id:** `ESC-05`
**Milestone:** MVP
**Size:** S (half a day or less)
**Depends on:** `PRO-01`
**Branch:** `feature/esc-05-price-computation`
**Labels:** `escrow`, `backend`, `good-first-issue`

## Goal

One function that turns an hourly rate and a duration into the three numbers everything else uses: what the client pays, what the professional earns, and what the platform keeps. Small, pure, and worth getting exactly right — rounding errors here become ledger imbalances in ESC-03.

## Requirements

1. A pure function `compute_price(hourly_rate_millimes, duration_minutes, commission_bps) -> PriceBreakdown` with fields `total`, `professional_amount` and `platform_commission`, all integer millimes.
2. The invariant, asserted in the function itself: `professional_amount + platform_commission == total`, always. Any rounding remainder is assigned deliberately to one side (document which and why) rather than left to float.
3. Rounding is explicit and documented: the total is derived from the rate and the duration with a stated rule, and the commission is computed from the total in basis points with a stated rounding direction.
4. Integer arithmetic only. No `float` anywhere in the module, and no `Decimal` conversion that could reintroduce fractions into a stored amount.
5. Reject invalid input rather than coercing it: a non-positive rate, a duration not in the allowed set, a commission outside 0..10000.
6. `GET /api/v1/professionals/{id}/pricing?duration=` returning the breakdown, so the web app displays the server's numbers rather than recomputing them.
7. The commission rate comes from `LEXPERT_PLATFORM_COMMISSION_BPS`. The breakdown stored on a consultation is the one computed at booking time; a later change to the platform rate must not alter an existing consultation.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: a clean case (60000 millimes per hour, 60 minutes, 1500 bps) produces the documented breakdown.
- Unit test: a case with a rounding remainder (a rate and duration that do not divide evenly) still satisfies the sum invariant, with the remainder on the documented side.
- Property test: across a wide range of rates, durations and commission rates, `professional_amount + platform_commission == total` and all three are non-negative integers.
- Unit test: a 15-minute duration is a quarter of the hourly rate, exactly.
- Unit test: 0 bps gives the professional everything; 10000 bps gives them nothing and still balances.
- Unit test: each invalid input raises with its documented code.
- Unit test: `grep` the module for `float` finds nothing.
- Integration test: changing the platform commission setting does not change the amounts on an already-booked consultation.

## Deliverables

- `lexpert_api/escrow/pricing.py` with `compute_price` and `PriceBreakdown`.
- The pricing endpoint.
- `apps/api/tests/escrow/test_pricing.py` including the property test.
- A `## Pricing` section in `docs/technical_docs/ledger.md` stating the rounding rule.

## Notes

Good first issue: small, self-contained, pure, and heavily tested. It is also on the critical path for ESC-03, so it is a useful early win.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-05-price-computation`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
