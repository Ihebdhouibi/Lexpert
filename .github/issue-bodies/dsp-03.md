**Task id:** `DSP-03`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `DSP-02`, `CON-03`, `ESC-12`
**Branch:** `feature/dsp-03-dispute-ui`
**Labels:** `frontend`, `admin`

## Goal

The client's route to raising a dispute in the hour after a consultation, and the admin's screen for resolving it. The client-side flow has a hard deadline, so the remaining time has to be visible and honest.

## Requirements

1. On the client's consultation detail, during `HOLD_WINDOW`, a clear dispute entry point with a **live countdown** of the time remaining. When the window expires, the control disappears and the screen explains that the funds have been released.
2. The dispute form: reason category selection with French labels, a description field with a minimum useful length, and a confirmation step that states plainly what happens next (review by the platform, payment paused).
3. After raising it, a status view: raised at, the category, the description, and, once resolved, the outcome and the resolution note in French.
4. The countdown must be derived from the server's stored expiry, not from a client-side clock started at page load. A clock-skewed client must not be shown a wrong deadline.
5. Admin dispute queue and detail screens: the queue with age and category, the detail showing the consultation, both parties, the participation record, the amounts and the audit trail.
6. The admin resolution panel: the three outcomes, with the partial option offering an amount input that validates the split client-side before submitting, a required note, and a confirmation step. The amounts on both sides of the split are shown as the admin types.
7. All copy in French; accessible forms; mobile-first for the client side.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Component test: the countdown renders from a server-provided expiry and reaches zero correctly.
- Component test: with the expiry in the past, the dispute control is absent and the released explanation shows.
- Component test: the form blocks submission without a category or with too short a description.
- Component test: submitting calls the endpoint once and shows the status view.
- Component test: a resolved dispute renders the outcome and the note.
- Component test: the admin queue renders, filters and paginates.
- Component test: the partial-split input rejects amounts that do not sum to the total, before any request is made.
- Component test: resolution requires a note and a confirmation.
- Manual: raise and resolve a dispute end to end against a running local stack, checking the ledger and the audit trail afterwards.

## Deliverables

- `apps/web/src/features/client/disputes/` and `apps/web/src/features/admin/disputes/`.
- A countdown component driven by a server timestamp, tested.
- Dispute keys in `fr.ts`.
- Component tests covering every item above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/dsp-03-dispute-ui`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
