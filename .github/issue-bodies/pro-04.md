**Task id:** `PRO-04`
**Milestone:** MVP
**Size:** L (3 days or more)
**Depends on:** `PRO-02`, `FND-06`
**Branch:** `feature/pro-04-client-discovery-ui`
**Labels:** `frontend`

## Goal

The client-facing discovery experience: a search page with filters and a professional profile page that leads into booking. This is the top of the client funnel and the first thing a prospective client sees, so it carries the trust message from the value proposition.

## Requirements

1. A landing and search page: vertical entry points (medical, legal, financial), a search input, and a filter panel for speciality, city, language and rate range. On mobile the filters live behind a sheet rather than consuming the viewport.
2. Results as cards: name, title, vertical and speciality, city, languages, hourly rate, and the price for the default duration. Loading skeletons, an explicit empty state with a suggestion to widen the filters, and an error state with a retry.
3. Filter and query state lives in the URL, so a search is shareable and the back button behaves.
4. Infinite scroll or an explicit load-more against the cursor pagination from PRO-02. Do not build page-number navigation on a cursor API.
5. A professional profile page: full biography, specialities, languages, experience, rate, the price per allowed duration, and a prominent booking call to action (wired to SCH-04 when it lands, a disabled placeholder until then).
6. A visible trust panel explaining, in French, that the professional is verified against their ordre and that payment is held in escrow until after the consultation. This is the platform's core differentiator; do not bury it.
7. During the MVP, wherever escrow is explained, state plainly that payments are simulated and no real money is taken. One clear, unmissable notice.
8. Mobile-first and accessible: real headings, filters usable by keyboard, results announced to screen readers when they change.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Component test: each filter updates the URL and refetches.
- Component test: loading, empty and error states each render.
- Component test: load-more appends the next cursor page without duplicating rows.
- Component test: reloading a filtered URL restores the exact filter state.
- Component test: the profile page renders every field and the per-duration prices, computed from the same helper the API uses.
- Component test: the escrow-simulation notice is present on both the profile page and any price display.
- Component test: a 404 from the profile endpoint renders a not-found screen, not a crash.
- Manual: search, filter and open a profile on a 375px viewport, keyboard only.

## Deliverables

- `apps/web/src/features/client/search/` and `apps/web/src/features/client/professional/`.
- Card, filter-panel and trust-panel components.
- Search and profile keys in `fr.ts`, including the simulation notice.
- Component tests covering every item above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/pro-04-client-discovery-ui`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
