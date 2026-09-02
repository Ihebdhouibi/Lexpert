**Task id:** `FND-03`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `FND-02`
**Branch:** `feature/fnd-03-database-baseline`
**Labels:** `database`, `infra`, `backend`

## Goal

Stand up the persistence layer: a local PostgreSQL via Docker Compose, an async SQLAlchemy session, Alembic migrations, and the test fixtures every later data issue will use. No domain tables are created here beyond the conventions.

## Requirements

1. `docker-compose.yml` at the repository root with a `postgres:16` service matching the credentials in `.env.example`, a named volume, and a healthcheck.
2. Async SQLAlchemy 2.x engine and session factory in `lexpert_api/core/database.py`, plus a `get_session` FastAPI dependency that commits on success and rolls back on exception.
3. A `Base` declarative class with project conventions: `UUID` primary keys defaulting server-side, `created_at`/`updated_at` timestamptz columns, snake_case table names.
4. Alembic initialised under `apps/api/migrations/`, configured to read the URL from `Settings` (not from `alembic.ini`), with `compare_type` and `compare_server_default` enabled so autogenerate is trustworthy.
5. One initial migration that creates nothing but establishes the revision chain and enables the `pgcrypto` extension (for `gen_random_uuid()`).
6. Pytest fixtures: a session-scoped fixture that creates a disposable test database and runs migrations against it, and a function-scoped fixture that wraps each test in a transaction rolled back at teardown.
7. Database-backed tests must **skip automatically** when PostgreSQL is unreachable, so `pytest` still passes locally without Docker while CI runs the full set.
8. A `make`-equivalent entry point (documented commands in `CONTRIBUTING.md` are enough) for `alembic upgrade head` and `alembic revision --autogenerate`.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- `docker compose up -d postgres` then `alembic upgrade head` succeeds from a clean volume, and `alembic downgrade base` reverses it.
- `alembic upgrade head && alembic revision --autogenerate -m check` produces an **empty** migration, proving the models and the schema agree.
- A test using the transactional fixture writes a row; a second test does not see it.
- With PostgreSQL stopped, `pytest` still exits 0 and reports the database tests as skipped, not failed.
- CI job `test-api` runs the database tests against the `postgres` service and they are not skipped there.

## Deliverables

- `docker-compose.yml`.
- `apps/api/src/lexpert_api/core/database.py`, `core/models.py` (the `Base` and mixins).
- `apps/api/migrations/` with `env.py` and the initial revision.
- `apps/api/tests/conftest.py` with the database fixtures.
- A `## Database` section in `CONTRIBUTING.md` with the migration commands.

## Notes

Use integer columns for money throughout the project (millimes, the thousandth of a Tunisian dinar). Never `FLOAT` or `REAL`. Add that convention as a comment on `core/models.py` so it is unmissable when the ledger tables arrive in ESC-02.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/fnd-03-database-baseline`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
