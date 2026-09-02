**Task id:** `SCH-04`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `SCH-02`, `PRO-04`
**Branch:** `feature/sch-04-booking-calendar-ui`
**Labels:** `frontend`, `scheduling`

## Goal

The slot picker on the professional's profile page: choose a duration, see available times in your own timezone, pick one, and carry it into checkout. A diaspora client must never have to do timezone arithmetic in their head.

## Requirements

1. Duration selector from the allowed set, showing the price for each so the choice is informed.
2. A date strip or small calendar with the days that have slots, and the slot list for the selected day.
3. Times are rendered in the **client's** detected timezone, with the zone named explicitly and the professional's local time shown alongside when the two differ. Allow overriding the detected zone.
4. Loading, empty (no availability in this range) and error states, each with useful French copy — an empty state should suggest looking further ahead.
5. Selecting a slot shows a confirmation summary: professional, date and time in both zones, duration, and the price breakdown (rate x duration + commission = total), then continues into the ESC-08 checkout.
6. The escrow explanation and the MVP simulation notice appear on this summary, because this is the last screen before a client commits.
7. If the chosen slot is gone by the time checkout is submitted, the resulting conflict from ESC-03 is handled here: an explicit French message and a refreshed slot list, never a silent failure or a double booking.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Component test: duration selection refetches slots and updates the displayed prices.
- Component test: slots render in a client timezone different from the professional's, and both times are shown.
- Component test: overriding the timezone re-renders the same slots at the new local times.
- Component test: loading, empty and error states each render.
- Component test: the summary shows the exact breakdown the API returns, with no client-side price arithmetic of its own.
- Component test: a 409 slot-taken response renders the conflict message and refetches the slots.
- Component test: the simulation notice is present on the summary.
- Manual: pick a slot as a client in `Europe/Paris` against a professional in `Africa/Tunis` and confirm the displayed times are correct on both sides of a DST boundary.

## Deliverables

- `apps/web/src/features/client/booking/` with the duration selector, calendar, slot list and summary.
- A timezone display helper, tested.
- Booking keys in `fr.ts`.
- Component tests covering every item above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/sch-04-booking-calendar-ui`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
