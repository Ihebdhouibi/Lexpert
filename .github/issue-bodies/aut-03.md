**Task id:** `AUT-03`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `AUT-01`
**Branch:** `feature/aut-03-rbac`
**Labels:** `auth`, `backend`, `api`

## Goal

Give the API one authorization mechanism, used by every protected endpoint, instead of per-endpoint checks that drift. Also establish resource-level ownership, which matters more than role here: a client must not read another client's consultation.

## Requirements

1. FastAPI dependencies: `current_user` (any authenticated user), `require_role(*roles)`, and `require_verified_professional` (role is `PROFESSIONAL` **and** verification status is `APPROVED`).
2. A resource-ownership helper for the pattern that repeats across the app: the actor must be the consultation's client, its professional, or an admin. Return 404 rather than 403 when the actor has no business knowing the resource exists.
3. Admin-only endpoints are grouped under one router with the role dependency applied at the router level, so a new admin endpoint cannot forget it.
4. A test that enumerates every route in the application and asserts each one is either in an explicit public allow-list or carries an authentication dependency. This is the check that catches an unprotected endpoint added six months from now.
5. Consistent failure semantics: 401 with a stable code when unauthenticated, 403 when authenticated but not permitted, 404 when the resource must not be disclosed.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: each dependency admits the permitted roles and rejects the rest.
- Integration test: `require_verified_professional` rejects an approved-role user whose verification is still `SUBMITTED`.
- Integration test: client A requesting client B's resource gets 404, not 403.
- Integration test: an admin can read both clients' resources.
- The route-coverage test fails when an unprotected route is added and passes on the real tree.
- Integration test: a malformed `Authorization` header returns 401 with the documented code, not a 500.

## Deliverables

- `lexpert_api/core/security.py` with the dependencies and the ownership helper.
- The admin router with the role dependency at router level.
- `apps/api/tests/core/test_authorization.py` and `test_route_protection_coverage.py`.
- A `## Authorization` section in the API docs stating which dependency guards which route group.

## Notes

`require_verified_professional` is the mechanical enforcement of the plan's hard rule that an unapproved professional is invisible and unbookable. Every professional-facing write endpoint uses it.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/aut-03-rbac`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
