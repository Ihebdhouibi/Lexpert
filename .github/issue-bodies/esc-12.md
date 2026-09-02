**Task id:** `ESC-12`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `ESC-10`, `ESC-08`
**Branch:** `feature/esc-12-client-consultations`
**Labels:** `frontend`, `escrow`

## Goal

The client's view of their own consultations: what they have requested, what has been accepted, what is coming up, and where their money is. DSP-03 and CON-03 both assume a client consultation detail screen exists; this is the issue that creates it.

## Requirements

1. A consultations list under the client portal, grouped into awaiting acceptance, upcoming, and past, each entry showing the professional, the date and time in the client's timezone, the duration and the total paid.
2. Status in plain French from the client's point of view -- awaiting the professional's answer, confirmed, in progress, being reviewed, paid out, refunded -- never the internal state name.
3. For a `PENDING_ACCEPTANCE` request: the acceptance deadline countdown, an explanation that the money is held and fully refunded if the professional does not accept, and a withdraw action with confirmation.
4. For a confirmed consultation: a join control active only inside the join window, with a countdown, and a cancel action that shows the ESC-07 policy outcome -- what will be refunded and what retained -- **before** the client confirms.
5. For a consultation in `HOLD_WINDOW`: the release countdown and the dispute entry point from DSP-03.
6. A detail view with the money timeline in client-readable French: held on this date, consultation on this date, released or refunded on this date and why.
7. The rating prompt from DSP-04 appears here once a consultation is released.
8. An empty state pointing a new client at search.
9. The MVP simulation notice wherever an amount is shown.
10. Mobile-first, French throughout, accessible.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Component test: the three groups render and each status maps to its French client-facing label, with no internal state name reaching the DOM.
- Component test: a pending request shows the deadline countdown and the withdraw action; withdrawing calls the endpoint once after confirmation.
- Component test: the cancel flow shows the policy outcome returned by the API before confirmation, and does not compute it client-side.
- Component test: the join control respects the window, with the clock controlled.
- Component test: a `HOLD_WINDOW` consultation shows the release countdown and the dispute entry point.
- Component test: the money timeline renders each event in French.
- Component test: the rating prompt appears only for a released consultation.
- Component test: the empty state renders and links to search.
- Component test: times render in the client's timezone including across a DST boundary.
- Manual: walk the whole client side on a 375px viewport, keyboard only.

## Deliverables

- `apps/web/src/features/client/consultations/` with the list and detail views.
- The client-facing status label mapping, tested.
- Client consultation keys in `fr.ts`.
- Component tests covering every item above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-12-client-consultations`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
