**Task id:** `CMP-03`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `ESC-03`, `CON-02`, `DSP-02`
**Branch:** `feature/cmp-03-api-contract`
**Labels:** `api`, `docs`, `test`

## Goal

Make the HTTP contract explicit and tested, so the web app can be developed against a stable surface and a breaking change is caught in CI rather than in the browser. It is also what a future integration partner will read.

## Requirements

1. Every endpoint documented in OpenAPI: a summary, a description, the response schemas, and **every** error code it can return, referencing the FND-05 envelope.
2. A machine-readable list of every error code the API can emit, with its HTTP status and its French message, generated from the code rather than maintained by hand.
3. A committed OpenAPI snapshot plus a CI check that regenerates it and fails on an undeclared difference. A deliberate contract change means updating the snapshot in the same PR, which makes it visible in review.
4. Contract tests over the documented critical paths, asserting the response **shape** rather than reimplementing the business logic: register, publish a profile, list slots, book, join, end, release, dispute, resolve.
5. A generated TypeScript client or type definitions for the web app from the OpenAPI document, so a contract change surfaces as a type error rather than a runtime surprise.
6. Documented pagination, filtering and error conventions in one place, so a new endpoint has a pattern to follow.
7. The public endpoints (search, slots, profile) are marked as such, and a test asserts they need no authentication while every other endpoint does — reusing the AUT-03 route-coverage test.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- CI check: the generated OpenAPI document matches the committed snapshot.
- Test: every route has a summary and at least one documented response, and every declared error code exists in the error-code registry.
- Test: every error code in the registry has a French message in `fr.ts`.
- Contract test per critical path: the response matches the documented schema, including the error envelope on the failure cases.
- CI check: the generated TypeScript client compiles and the web app type-checks against it.
- Test: an endpoint whose response schema is changed without updating the snapshot fails the check.
- Test: the public endpoints are reachable unauthenticated; all others are not.

## Deliverables

- OpenAPI descriptions across every router, and the error-code registry.
- `apps/api/openapi.snapshot.json` and the CI comparison script.
- `apps/api/tests/contract/` with the critical-path tests.
- The generated client in `apps/web/src/api/generated/` and its generation script.
- `docs/technical_docs/api_conventions.md`.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/cmp-03-api-contract`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
