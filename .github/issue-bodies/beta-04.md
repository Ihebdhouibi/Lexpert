**Task id:** `BETA-04`
**Milestone:** Beta
**Size:** L (3 days or more)
**Depends on:** `BETA-01`, `PRO-02`
**Branch:** `feature/beta-04-subscriptions`
**Labels:** `backend`, `frontend`, `escrow`

## Goal

The second and third revenue streams from the business model: a premium plan for professionals with better visibility, analytics and a lower commission, and paid promotion in search results.

## Requirements

1. Subscription plans with a recurring charge through the payment partner, a lifecycle (active, past due, cancelled) and a lower commission rate applied to consultations booked while active.
2. The commission rate used for a consultation is the one in force at booking, stored on the consultation, so a later plan change does not retroactively alter a held or released amount.
3. Featured placement in PRO-02 search results, clearly and honestly labelled as promoted. An unlabelled paid ranking is a trust problem for a platform selling trust.
4. A professional analytics view: consultation volume, earnings over time, conversion from profile views to bookings.
5. Plan changes, cancellation and dunning, each with the corresponding notifications.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Test: an active subscription applies the reduced commission to a new booking, and the stored breakdown reflects it.
- Test: cancelling a plan does not change the commission on an existing consultation.
- Test: a past-due subscription reverts to the standard commission.
- Test: featured results are ranked ahead and are labelled in the response.
- Test: the analytics figures match the underlying ledger and consultation data.
- Component test: promoted results are visibly labelled.

## Deliverables

- Subscription models, the billing integration and its migration.
- Featured placement in the search query, with labelling.
- The analytics endpoint and view.
- Tests as listed above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/beta-04-subscriptions`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
