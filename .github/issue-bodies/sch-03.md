**Task id:** `SCH-03`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `SCH-01`, `PRO-03`
**Branch:** `feature/sch-03-availability-ui`
**Labels:** `frontend`, `scheduling`

## Goal

The professional portal screens for setting weekly hours, blocking dates, and configuring buffers and notice. The professional must be able to see immediately what a client will be offered.

## Requirements

1. A weekly schedule editor: per day, add or remove time ranges, with overlap prevented client-side before the request is made and the server error rendered if it still occurs.
2. An exceptions calendar: pick a date, mark it unavailable or set different hours, and see the exceptions listed and removable.
3. A settings panel for buffer minutes, minimum notice and maximum horizon, each with a French explanation of what it does in practice.
4. A preview showing the concrete slots the current configuration produces for the next two weeks, fetched from SCH-02 — so the professional validates the result rather than the configuration.
5. The professional's timezone is displayed prominently on every time input, because everything they enter is in it.
6. Mobile-first: the weekly editor must be usable on a phone. A seven-column grid is not; use a per-day accordion or list.
7. All copy in French; accessible time inputs with labels.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Component test: adding a range that overlaps an existing one is blocked client-side with a French message.
- Component test: adding, editing and removing a range calls the API correctly.
- Component test: a server overlap error is rendered inline.
- Component test: adding and removing an exception works and the list updates.
- Component test: the slot preview refetches when the configuration changes.
- Component test: the timezone label reflects the profile's timezone.
- Manual: configure a full week and one exception on a 375px viewport, keyboard only.

## Deliverables

- `apps/web/src/features/professional/availability/` with the weekly editor, exceptions calendar, settings panel and slot preview.
- Scheduling keys in `fr.ts`.
- Component tests covering every item above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/sch-03-availability-ui`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
