**Task id:** `KYC-05`
**Milestone:** MVP
**Size:** L (3 days or more)
**Depends on:** `KYC-04`, `AUT-04`, `UX-08`
**Branch:** `feature/kyc-05-onboarding-wizard`
**Labels:** `frontend`, `kyc-pro`

## Goal

The French multi-step form a professional completes to get verified, with the fields and documents that their chosen vertical actually requires, plus the status page they return to while waiting. This screen is the platform's first impression on the supply side, and the feasibility study's cold-start analysis says supply comes first — so it needs to be genuinely easy.

## Requirements

1. A wizard with clear steps: choose vertical, professional details (fields driven by the vertical's requirements from the API), documents, review and submit. Steps are navigable backwards and the current step survives a page reload.
2. The form is **generated from the requirements returned by the API**, not hard-coded per vertical. Adding a field in KYC-03 must not require a change here.
3. Draft autosave via `PATCH`, debounced, with a visible saved indicator. A professional who closes the tab loses nothing.
4. Document upload with drag-and-drop and a file picker, per-file progress, client-side type and size pre-checks matching the server's limits, a thumbnail or filename chip per uploaded document, and delete.
5. Submission renders server violations inline against the field or document they name, plus a summary at the top listing them with anchor links. Do not show a bare "submission failed".
6. A status page for every non-draft state, in French: `SUBMITTED` and `UNDER_REVIEW` explain that review is manual and give an expectation; `MORE_INFO_REQUESTED` shows the admin's message and reopens editing; `REJECTED` shows the reason and offers resubmission; `APPROVED` links onward to profile setup.
7. The events timeline from `GET /verification/me/events`, rendered in French with relative and absolute timestamps.
8. Mobile-first: the whole wizard is completable on a 375px viewport, including document upload from a phone camera roll.
9. Accessibility: each step is a real form with labels, violations are announced via a live region, and focus moves to the first violation on a failed submit.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Component test per vertical: the wizard renders exactly the fields and document slots that vertical requires and no others.
- Test: a field added to the mocked API requirements appears without a code change.
- Test: draft autosave fires after the debounce and the indicator updates.
- Test: a 422 with three violations renders three inline errors against the correct inputs plus a three-item summary.
- Test: a file over the size limit is rejected client-side with a French message, before any request is made.
- Test: each of the five statuses renders its own screen with the right copy and actions.
- Test: `MORE_INFO_REQUESTED` shows the admin message and re-enables editing.
- Test: reloading mid-wizard restores the step and the entered values.
- Manual: complete the wizard end to end for all three verticals at a 375px viewport, keyboard only.

## Deliverables

- `apps/web/src/features/professional/onboarding/` with the wizard, the dynamic form renderer, the uploader and the status screens.
- Onboarding keys in `fr.ts`, including copy for all five statuses.
- Component tests covering every item above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/kyc-05-onboarding-wizard`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
