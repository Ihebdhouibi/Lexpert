**Task id:** `ESC-09`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `ESC-06`, `PRO-03`
**Branch:** `feature/esc-09-earnings-ui`
**Labels:** `frontend`, `escrow`

## Goal

The professional's view of their money: what is held, what has been released, what was refunded, and why. A professional who cannot see where their money is will not trust the escrow, which makes this screen part of the core value proposition rather than a report.

## Requirements

1. An earnings summary: total held (consultations booked or awaiting release), total released, and total refunded away, each derived from the ledger balances rather than recomputed in the client.
2. A consultation list with the status in French, the client's first name, the date, the gross amount, the commission and the net, filterable by status and date range.
3. A per-consultation detail view showing the money timeline: held on this date, consultation on this date, released or refunded on this date and why. This is the professional-readable projection of the ESC-04 audit trail; it must not expose internal state names or actor ids.
4. For a consultation in `HOLD_WINDOW`, show the release countdown explicitly: when the hold expires and when payment will arrive.
5. An API endpoint to back these views (`GET /api/v1/professionals/me/earnings`) if one does not already exist, returning ledger-derived figures. Add it in this issue rather than assembling the numbers from several calls in the browser.
6. Empty state for a professional with no consultations yet, with a French pointer toward completing their profile and availability.
7. The MVP simulation notice appears here too: these are simulated amounts and no real payout occurs.
8. Mobile-first, since a professional will check this on a phone.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: the earnings endpoint's figures equal the ledger balances for a seeded professional across held, released and refunded consultations.
- Integration test: a professional cannot read another professional's earnings.
- Component test: the summary renders the endpoint's figures without recomputation.
- Component test: status and date filters both narrow the list.
- Component test: a `HOLD_WINDOW` consultation shows a countdown to the stored expiry.
- Component test: the detail timeline renders each money event in French with no internal status names leaking.
- Component test: the empty state renders for a professional with no consultations.
- Component test: the simulation notice is present.
- Manual: check the whole view on a 375px viewport.

## Deliverables

- `GET /api/v1/professionals/me/earnings` and its tests.
- `apps/web/src/features/professional/earnings/` with the summary, list and detail views.
- Earnings keys in `fr.ts`.
- Component tests covering every item above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-09-earnings-ui`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
