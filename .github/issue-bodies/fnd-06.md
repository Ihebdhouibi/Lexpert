**Task id:** `FND-06`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `FND-02`
**Branch:** `feature/fnd-06-web-shell`
**Labels:** `frontend`, `infra`

## Goal

Create the web app's frame: the three portal route trees, a mobile-first layout, the French translation catalogue that all copy goes through, and one API client that understands the error envelope from FND-05. Feature issues then only add screens.

## Requirements

1. React Router with three route trees under a shared layout: `/` (client portal), `/pro` (professional portal), `/admin` (back-office). Placeholder screens are fine.
2. Mobile-first layout: a responsive shell with a header, navigation that collapses on small viewports, and a content area. Most Tunisian users are on a phone, so design the small viewport first and widen up.
3. i18n set up with a **French-only** catalogue (`apps/web/src/i18n/fr.ts`). Every user-facing string in the app resolves through it. Structure keys by feature so the catalogue stays navigable as it grows.
4. A lint rule or unit test that fails when a JSX text node or a `title`/`aria-label`/`placeholder` prop contains a hard-coded non-ASCII-safe literal instead of a catalogue lookup. A pragmatic heuristic is acceptable; the point is that hard-coded copy is caught in CI rather than in review.
5. One typed API client in `apps/web/src/api/`: base URL from `config.ts`, JSON handling, and translation of the `{error: {code, message}}` envelope into a typed `ApiError` carrying the code.
6. TanStack Query (or an equivalent already chosen) for server state, with a `QueryClientProvider` in the shell and sane defaults for retries and staleness.
7. A shared UI primitive set the feature issues reuse: button, input, select, form-field-with-error, spinner, empty state, and a toast or alert for errors. Keep it small; this is not a design system.
8. Formatting helpers used everywhere money and time are shown: TND from integer millimes (`45,500 DT`), and dates in the viewer's timezone with the zone named.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- `npm run build`, `npm run lint`, `npm run format:check`, `npm run typecheck` all pass.
- Unit test: the money formatter renders `45500` as `45,500 DT` and rejects non-integer input.
- Unit test: the date formatter renders a UTC instant in a given timezone and names the zone.
- Unit test: the API client turns a 409 error envelope into an `ApiError` with the correct `code`, and a network failure into a distinguishable error.
- Unit test: an unknown route renders the not-found screen.
- The hard-coded-copy check fails on a component with literal French text and passes on the real tree.
- Manual: at a 375px viewport width, no horizontal scrolling and the navigation is usable.

## Deliverables

- `apps/web/src/app/` with the router and layout.
- `apps/web/src/i18n/fr.ts` and the i18n provider.
- `apps/web/src/api/client.ts` with `ApiError`.
- `apps/web/src/components/` with the shared primitives.
- `apps/web/src/lib/format.ts` for money and dates.
- Unit tests for the formatters, the client and the router.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/fnd-06-web-shell`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
