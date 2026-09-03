**Task id:** `ESC-11`
**Milestone:** MVP
**Size:** L (3 days or more)
**Depends on:** `ESC-10`, `PRO-03`, `SCH-03`
**Branch:** `feature/esc-11-professional-dashboard`
**Labels:** `frontend`, `escrow`, `consultation`

## Goal

The professional's home in the application: the requests waiting for their answer, the consultations coming up, and the route into each session. Without this a verified professional has nowhere to accept a request from, and the journey cannot be completed.

## Requirements

1. A dashboard landing screen for `/pro` showing, in priority order: requests awaiting acceptance (most urgent first by deadline), today's confirmed consultations, and a summary of what is held and released (reusing the ESC-09 earnings endpoint rather than a second source of truth).
2. A request inbox: each pending request shows the client's first name, the requested date and time **in the professional's timezone**, the duration, what they will earn net of commission, and a live countdown to the acceptance deadline.
3. Accept and decline actions on each request. Decline requires a reason category and asks for confirmation, stating plainly that the client is refunded in full.
4. An upcoming-consultations list with each consultation's status in French, and a join control that becomes active only inside the CON-01 join window -- with a countdown until it does.
5. A consultation detail view: the client's first name, when, how long, the amounts, the consent status from CON-04, and the money timeline. It must not expose the client's contact details.
6. A past-consultations list with the outcome of each (released, refunded, disputed) in client-readable French.
7. Empty states that tell a new professional what to do next: no requests yet because availability is not set, or because the profile is not published -- linking to SCH-03 and PRO-03 respectively. This is the screen a professional sees on day one, and the cold-start problem makes it matter.
8. The countdown to an acceptance deadline is derived from the server's stored deadline, never from a clock started at page load.
9. Polling or refetch-on-focus so a request that arrives while the tab is open becomes visible without a manual reload.
10. Mobile-first: a professional will accept requests from a phone.
11. All copy in French through the catalogue.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Component test: the dashboard renders all three sections against a mocked API, and the request section is ordered by deadline.
- Component test: accept calls the endpoint once and the request leaves the inbox.
- Component test: decline requires a reason and a confirmation, and states the full refund.
- Component test: the deadline countdown renders from a server timestamp and reaches zero; an expired request renders as expired rather than actionable.
- Component test: the join control is inactive outside the window and active inside it, with the clock controlled.
- Component test: each empty state renders with the correct next-step link, for each precondition independently.
- Component test: the detail view shows no client contact detail.
- Component test: times render in the professional's timezone, verified against a client request made in another zone.
- Component test: a 409 on accept (already expired or declined) shows a French message and refetches.
- Manual: accept a real request end to end against a running local stack, then join the consultation from this screen.

## Deliverables

- `apps/web/src/features/professional/dashboard/` with the landing screen, request inbox, upcoming list and consultation detail.
- A reusable server-timestamp countdown component, shared with DSP-03.
- Professional dashboard keys in `fr.ts`.
- Component tests covering every item above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-11-professional-dashboard`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
