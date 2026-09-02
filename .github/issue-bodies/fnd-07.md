**Task id:** `FND-07`
**Milestone:** MVP
**Size:** S (half a day or less)
**Depends on:** `FND-05`
**Branch:** `feature/fnd-07-reference-data`
**Labels:** `backend`, `database`, `good-first-issue`

## Goal

Define, in one place, the closed vocabularies the rest of the system references: the three verticals, their regulators, the specialities under each, and the consultation and verification status enums. Several later issues each need these; defining them twice guarantees they diverge.

## Requirements

1. A `Vertical` enum with `MEDICAL`, `LEGAL`, `FINANCIAL`, and for each: the regulator's name and acronym (CNOM, Ordre National des Avocats de Tunisie, OECT) and its French display label.
2. A seedable speciality list per vertical (for example medical specialities, areas of legal practice, areas of financial and fiscal practice). A short, credible starter list is enough; it is reference data, not a taxonomy project.
3. Enums for the escrow and consultation lifecycle: the nine states named in feasibility study section 5.1 -- `BOOKED`, `FUNDS_HELD`, `IN_SESSION`, `SESSION_ENDED`, `HOLD_WINDOW`, `UNDER_REVIEW`, `RELEASED_TO_PRO`, `REFUNDED`, `CANCELLED` -- plus the three the request-and-accept handshake adds, which the study does not model: `PENDING_ACCEPTANCE`, `DECLINED`, `EXPIRED`. Twelve in total; see ESC-03 for the transitions between them.
4. An enum for verification status: `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, `MORE_INFO_REQUESTED`, `APPROVED`, `REJECTED`.
5. A Tunisian governorate or city list for the location filter used by PRO-02.
6. An Alembic migration seeding the reference tables idempotently, so re-running it or running it on a populated database is safe.
7. `GET /api/v1/reference` exposing verticals, specialities and cities so the web app never hard-codes them.
8. The French labels live in the web i18n catalogue keyed by the enum value, not in the database, so copy changes do not need a migration.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: every enum member has a French label in `fr.ts`, and every label key corresponds to a real enum member. This test fails if either side drifts.
- Unit test: the consultation status enum contains exactly the twelve states listed above, no more and no fewer. This test is what stops a state being invented ad hoc later without a transition being defined for it.
- Integration test: running the seed migration twice leaves the same row counts.
- Integration test: `GET /api/v1/reference` returns all three verticals, each with a non-empty speciality list and its regulator.

## Deliverables

- `apps/api/src/lexpert_api/core/enums.py`.
- Reference models and the seeding migration.
- `GET /api/v1/reference` and its router.
- French labels added to `apps/web/src/i18n/fr.ts`.
- Tests as listed above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/fnd-07-reference-data`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
