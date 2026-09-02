**Task id:** `PRO-03`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `PRO-01`, `AUT-04`
**Branch:** `feature/pro-03-profile-management-ui`
**Labels:** `frontend`

## Goal

The professional portal screens for editing a profile, setting an hourly rate, and publishing. Publishing is the moment a professional becomes bookable, so the screen has to make the preconditions and the consequence obvious.

## Requirements

1. A profile editor in French: title, biography with a character counter, speciality multi-select from the reference data, languages, city, years of experience.
2. A rate editor that takes dinars and millimes in a way a person actually types (`45,500`) and converts to integer millimes for the API, with the conversion covered by tests. Show the computed price for each allowed duration underneath, so the professional sees what a client will pay.
3. A publish control that lists any unmet precondition (verification not approved, missing biography, no speciality, no rate) and stays disabled until all are met. Explain, do not just disable.
4. A live preview of the public profile as a client will see it.
5. An unpublish control with a confirmation that states plainly what happens: the professional disappears from search but existing bookings stand.
6. Dirty-state protection: navigating away with unsaved changes prompts first.
7. All copy in French through the catalogue; accessible labelled form controls.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: the dinar-and-millime input converts to integer millimes correctly, including `45`, `45,5`, `45,500` and `0,001`.
- Unit test: the same conversion rejects more than three decimal places.
- Component test: the publish control is disabled and lists each unmet precondition, for each precondition independently.
- Component test: with everything met, publishing calls the endpoint once and reflects the new state.
- Component test: unpublish requires confirmation.
- Component test: the preview renders the same data the public profile endpoint would return.
- Component test: navigating away dirty prompts; clean does not.
- Manual: complete the whole editor on a 375px viewport, keyboard only.

## Deliverables

- `apps/web/src/features/professional/profile/` with the editor, rate input, publish panel and preview.
- A reusable money input component, tested.
- Profile keys in `fr.ts`.
- Component tests covering every item above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/pro-03-profile-management-ui`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
