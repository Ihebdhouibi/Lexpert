**Task id:** `AUT-01`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `FND-05`, `FND-07`
**Branch:** `feature/aut-01-user-auth`
**Labels:** `auth`, `backend`, `database`

## Goal

Let a person create an account as a client or a professional and log in, with admins created out of band. This is the entry point to every other flow, so the token and role model set here is hard to change later.

## Requirements

1. `User` model: id, email (unique, case-insensitive), phone (E.164, unique), password hash, full name, role, `is_active`, `email_verified_at`, `phone_verified_at`, timestamps.
2. Roles: `CLIENT`, `PROFESSIONAL`, `ADMIN`. Registration accepts only `CLIENT` and `PROFESSIONAL`; a request for `ADMIN` is rejected. Admins are created by a management command, never through the public API.
3. Password hashing with Argon2id (or bcrypt if Argon2 proves awkward to install). Minimum policy: at least 10 characters, and rejection of a small list of obvious passwords. Do not invent an elaborate policy; length is what matters.
4. `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`.
5. JWT access token (short TTL from settings) and refresh token (long TTL), both carrying `sub`, `role` and `jti`. Refresh tokens are persisted so logout can revoke them; a revoked or reused refresh token is rejected.
6. Registering a professional creates the user **and** an empty verification file in `DRAFT` (the KYC module's entry point), so KYC-04 has something to submit against.
7. Login must not reveal whether an email exists: the same error code and a comparable response time for an unknown email and a wrong password.
8. Rate-limit login and registration per IP and per email. A simple in-process or database-backed limiter is fine for the MVP; note in the code that it needs to move to shared state when the app runs multi-process.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test: register a client, log in, call `/auth/me`, get the right role.
- Integration test: registering a professional also creates a `DRAFT` verification file.
- Integration test: registering with `role=ADMIN` is rejected with a stable error code.
- Integration test: duplicate email and duplicate phone are both rejected with a conflict code.
- Integration test: email casing is normalised, so `A@b.tn` and `a@b.tn` collide.
- Integration test: an expired access token is rejected; a valid refresh token returns a new pair; the **used** refresh token is then rejected.
- Integration test: after logout, the refresh token no longer works.
- Security test: unknown email and wrong password produce identical error codes.
- Security test: exceeding the login rate limit returns the documented error.
- `grep` the test output and logs to confirm no password or token value is ever logged.

## Deliverables

- `lexpert_api/identity/` with models, schemas, service, router and security primitives.
- Alembic migration for `users` and `refresh_tokens`.
- A `create-admin` management command.
- `apps/api/tests/identity/` covering every validation item.
- New error codes documented in the OpenAPI responses.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/aut-01-user-auth`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
