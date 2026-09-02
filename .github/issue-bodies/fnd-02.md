**Task id:** `FND-02`
**Milestone:** MVP
**Size:** S (half a day or less)
**Depends on:** `FND-01`
**Branch:** `feature/fnd-02-config`
**Labels:** `infra`, `backend`

## Goal

Give the API a single typed, validated configuration object loaded from the environment, and give the web app the same for its handful of build-time variables. Every later issue reads configuration through this, never through `os.environ` directly.

## Requirements

1. Add `pydantic-settings`. Define `Settings` in `lexpert_api/core/config.py` covering every variable in the committed `.env.example`, with the `LEXPERT_` prefix.
2. Values that must have no default in any environment: `LEXPERT_DATABASE_URL`, `LEXPERT_JWT_SECRET`. Startup must fail loudly if they are missing.
3. Validate that `LEXPERT_JWT_SECRET` is not the placeholder value from `.env.example`, and that `LEXPERT_PLATFORM_COMMISSION_BPS` is between 0 and 10000.
4. Expose the settings as a cached singleton (`@lru_cache` on a `get_settings()` function) and as a FastAPI dependency, so tests can override it.
5. Web app: read `VITE_API_BASE_URL` through one typed module (`apps/web/src/config.ts`) that throws at startup if it is unset. No component reads `import.meta.env` directly.
6. Keep `.env.example` the single source of truth for the variable list. If this issue adds a variable, add it there too.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test: a complete environment loads and every field has the expected type.
- Unit test: omitting `LEXPERT_DATABASE_URL` raises a validation error mentioning the field name.
- Unit test: `LEXPERT_JWT_SECRET` left at the `.env.example` placeholder is rejected.
- Unit test: `LEXPERT_PLATFORM_COMMISSION_BPS=10001` is rejected.
- Web unit test: `config.ts` throws when `VITE_API_BASE_URL` is absent.
- `grep -rn "os.environ\|os.getenv" apps/api/src` returns nothing outside `core/config.py`.

## Deliverables

- `apps/api/src/lexpert_api/core/config.py` with `Settings` and `get_settings()`.
- `apps/web/src/config.ts`.
- `apps/api/tests/core/test_config.py`.
- Any new variables appended to the root `.env.example`.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/fnd-02-config`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
