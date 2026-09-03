"""Backlog entries for FND, AUT and KYC."""

from __future__ import annotations

ISSUES: list[dict[str, object]] = [
    # ------------------------------------------------------------------ FND
    {
        "id": "FND-01",
        "title": "Monorepo scaffolding for apps/web and apps/api",
        "milestone": "MVP",
        "labels": ["infra"],
        "size": "S",
        "depends": [],
        "branch": "feature/fnd-01-monorepo-scaffolding",
        "goal": (
            "Create the two-app monorepo layout every later issue assumes, so that both apps "
            "build, lint and run their (empty) test suites from a clean clone. Nothing "
            "functional is added here; this issue exists so that no feature PR has to also "
            "invent the project structure."
        ),
        "requirements": [
            "Create `apps/web` from the Vite React + TypeScript template. Add the scripts CI "
            "depends on: `dev`, `build`, `typecheck` (`tsc --noEmit`), `lint` (`eslint .`), "
            "`format:check` (`prettier --check .`), `test` (`vitest run --coverage`).",
            "Configure ESLint on the flat-config format (`eslint.config.js`) with "
            "`typescript-eslint` and `eslint-plugin-react-hooks`. Prettier is the only "
            "formatter; ESLint handles correctness rules only, so the two never disagree.",
            "Commit `apps/web/package-lock.json` so CI's `npm ci` is reproducible. Node version "
            "is pinned in the repository-root `.nvmrc` (already committed, value `20`).",
            "Create `apps/api` as an installable Python package: `pyproject.toml` with the "
            "package under `apps/api/src/lexpert_api/`, plus an `apps/api/tests/` root.",
            "**Python 3.11**, pinned deliberately -- it is what the rest of the team's stack "
            "runs. Set `requires-python = \">=3.11,<3.12\"` so an install on the wrong "
            "interpreter fails immediately rather than at some later import, and commit a "
            "`.python-version` of `3.11` for pyenv. CI runs 3.11 too, so a local pass means a "
            "CI pass.",
            "Configure `apps/api/pyproject.toml` exactly as specified in the Deliverables "
            "section below: ruff, mypy strict, pytest and coverage with `fail_under = 70`.",
            "Add one trivial passing test per app so the suites are not empty (`vitest` on a "
            "smoke assertion, `pytest` on a package-import assertion).",
            "Run `pre-commit install && pre-commit install --hook-type commit-msg`, then "
            "`pre-commit run --all-files`. If that reformats files, commit the reformat as its "
            "own `chore: apply pre-commit formatting` commit so the noise stays out of the "
            "feature diff.",
        ],
        "validation": [
            "From a clean clone: `cd apps/web && npm ci && npm run build` succeeds.",
            "`npm run lint`, `npm run format:check`, `npm run typecheck` and `npm test` all "
            "succeed in `apps/web`.",
            "From a clean clone: `cd apps/api && pip install -e \".[dev]\"` succeeds, then "
            "`ruff check .`, `ruff format --check .`, `mypy src` and `pytest` all succeed.",
            "`python --version` reports 3.11.x, and installing under 3.12 or 3.10 is refused by "
            "`requires-python`.",
            "`pre-commit run --all-files` passes at the repository root.",
            "`git commit -m \"bad message\"` is rejected by the commit-msg hook; "
            "`git commit -m \"chore: verify hook\"` is accepted.",
        ],
        "deliverables": [
            "`apps/web/` with `package.json`, `package-lock.json`, `eslint.config.js`, "
            "`.prettierrc`, `tsconfig.json`, `vite.config.ts`, one smoke test.",
            "`apps/api/pyproject.toml`, `apps/api/src/lexpert_api/__init__.py`, "
            "`apps/api/tests/test_smoke.py`.",
            "`.python-version` at the repository root, containing `3.11`.",
            "A short `apps/README.md` stating which app is which and how to run each.",
        ],
        "notes": (
            "The `apps/api/pyproject.toml` configuration is fixed, because CI and the ruleset "
            "depend on it:\n\n"
            "```toml\n"
            "[project]\n"
            'requires-python = ">=3.11,<3.12"\n'
            "\n"
            "[project.optional-dependencies]\n"
            'dev = ["pytest>=8.0", "pytest-cov>=5.0", "ruff>=0.16", "mypy>=1.11", "httpx>=0.27"]\n'
            "\n"
            "[tool.ruff]\n"
            "line-length = 100\n"
            'target-version = "py311"\n'
            'src = ["src", "tests"]\n'
            "\n"
            "[tool.ruff.lint]\n"
            'select = ["E", "F", "I", "UP", "B", "SIM"]\n'
            "\n"
            "[tool.mypy]\n"
            'python_version = "3.11"\n'
            "strict = true\n"
            'files = ["src", "tests"]\n'
            "\n"
            "[tool.pytest.ini_options]\n"
            'testpaths = ["tests"]\n'
            'addopts = "-q"\n'
            "\n"
            "[tool.coverage.run]\n"
            'source = ["lexpert_api"]\n'
            "\n"
            "[tool.coverage.report]\n"
            "show_missing = true\n"
            "fail_under = 70\n"
            "```\n\n"
            "Do not raise `fail_under` in this issue. A gate that is red on the first PR gets "
            "disabled instead of respected; it is ratcheted up later in a `chore:` PR."
        ),
    },
    {
        "id": "FND-02",
        "title": "API configuration and secrets handling",
        "milestone": "MVP",
        "labels": ["infra", "backend"],
        "size": "S",
        "depends": ["FND-01"],
        "branch": "feature/fnd-02-config",
        "goal": (
            "Give the API a single typed, validated configuration object loaded from the "
            "environment, and give the web app the same for its handful of build-time "
            "variables. Every later issue reads configuration through this, never through "
            "`os.environ` directly."
        ),
        "requirements": [
            "Add `pydantic-settings`. Define `Settings` in `lexpert_api/core/config.py` covering "
            "every variable in the committed `.env.example`, with the `LEXPERT_` prefix.",
            "Values that must have no default in any environment: `LEXPERT_DATABASE_URL`, "
            "`LEXPERT_JWT_SECRET`. Startup must fail loudly if they are missing.",
            "Validate that `LEXPERT_JWT_SECRET` is not the placeholder value from "
            "`.env.example`, and that `LEXPERT_PLATFORM_COMMISSION_BPS` is between 0 and 10000.",
            "Expose the settings as a cached singleton (`@lru_cache` on a `get_settings()` "
            "function) and as a FastAPI dependency, so tests can override it.",
            "Web app: read `VITE_API_BASE_URL` through one typed module "
            "(`apps/web/src/config.ts`) that throws at startup if it is unset. No component "
            "reads `import.meta.env` directly.",
            "Keep `.env.example` the single source of truth for the variable list. If this issue "
            "adds a variable, add it there too.",
        ],
        "validation": [
            "Unit test: a complete environment loads and every field has the expected type.",
            "Unit test: omitting `LEXPERT_DATABASE_URL` raises a validation error mentioning "
            "the field name.",
            "Unit test: `LEXPERT_JWT_SECRET` left at the `.env.example` placeholder is rejected.",
            "Unit test: `LEXPERT_PLATFORM_COMMISSION_BPS=10001` is rejected.",
            "Web unit test: `config.ts` throws when `VITE_API_BASE_URL` is absent.",
            "`grep -rn \"os.environ\\|os.getenv\" apps/api/src` returns nothing outside "
            "`core/config.py`.",
        ],
        "deliverables": [
            "`apps/api/src/lexpert_api/core/config.py` with `Settings` and `get_settings()`.",
            "`apps/web/src/config.ts`.",
            "`apps/api/tests/core/test_config.py`.",
            "Any new variables appended to the root `.env.example`.",
        ],
    },
    {
        "id": "FND-03",
        "title": "PostgreSQL, SQLAlchemy and Alembic baseline",
        "milestone": "MVP",
        "labels": ["database", "infra", "backend"],
        "size": "M",
        "depends": ["FND-02"],
        "branch": "feature/fnd-03-database-baseline",
        "goal": (
            "Stand up the persistence layer: a local PostgreSQL via Docker Compose, an async "
            "SQLAlchemy session, Alembic migrations, and the test fixtures every later data "
            "issue will use. No domain tables are created here beyond the conventions."
        ),
        "requirements": [
            "`docker-compose.yml` at the repository root with a `postgres:16` service matching "
            "the credentials in `.env.example`, a named volume, and a healthcheck.",
            "Async SQLAlchemy 2.x engine and session factory in "
            "`lexpert_api/core/database.py`, plus a `get_session` FastAPI dependency that "
            "commits on success and rolls back on exception.",
            "A `Base` declarative class with project conventions: `UUID` primary keys defaulting "
            "server-side, `created_at`/`updated_at` timestamptz columns, snake_case table names.",
            "Alembic initialised under `apps/api/migrations/`, configured to read the URL from "
            "`Settings` (not from `alembic.ini`), with `compare_type` and "
            "`compare_server_default` enabled so autogenerate is trustworthy.",
            "One initial migration that creates nothing but establishes the revision chain and "
            "enables the `pgcrypto` extension (for `gen_random_uuid()`).",
            "Pytest fixtures: a session-scoped fixture that creates a disposable test database "
            "and runs migrations against it, and a function-scoped fixture that wraps each test "
            "in a transaction rolled back at teardown.",
            "Database-backed tests must **skip automatically** when PostgreSQL is unreachable, "
            "so `pytest` still passes locally without Docker while CI runs the full set.",
            "A `make`-equivalent entry point (documented commands in `CONTRIBUTING.md` are "
            "enough) for `alembic upgrade head` and `alembic revision --autogenerate`.",
        ],
        "validation": [
            "`docker compose up -d postgres` then `alembic upgrade head` succeeds from a clean "
            "volume, and `alembic downgrade base` reverses it.",
            "`alembic upgrade head && alembic revision --autogenerate -m check` produces an "
            "**empty** migration, proving the models and the schema agree.",
            "A test using the transactional fixture writes a row; a second test does not see it.",
            "With PostgreSQL stopped, `pytest` still exits 0 and reports the database tests as "
            "skipped, not failed.",
            "CI job `test-api` runs the database tests against the `postgres` service and they "
            "are not skipped there.",
        ],
        "deliverables": [
            "`docker-compose.yml`.",
            "`apps/api/src/lexpert_api/core/database.py`, `core/models.py` (the `Base` and "
            "mixins).",
            "`apps/api/migrations/` with `env.py` and the initial revision.",
            "`apps/api/tests/conftest.py` with the database fixtures.",
            "A `## Database` section in `CONTRIBUTING.md` with the migration commands.",
        ],
        "notes": (
            "Use integer columns for money throughout the project (millimes, the thousandth of "
            "a Tunisian dinar). Never `FLOAT` or `REAL`. Add that convention as a comment on "
            "`core/models.py` so it is unmissable when the ledger tables arrive in ESC-02."
        ),
    },
    {
        "id": "FND-04",
        "title": "Make the CI status checks required on the branch ruleset",
        "milestone": "MVP",
        "labels": ["ci", "infra"],
        "size": "S",
        "depends": [],
        "branch": "chore/fnd-04-required-checks",
        "goal": (
            "Finish turning CI into a merge gate. The workflow is live and running; what remains "
            "is adding its six contexts to the branch ruleset as required status checks, so a "
            "red build actually blocks a merge instead of merely being visible."
        ),
        "requirements": [
            "**Owned by the repository owner, not the implementer.** It changes repository "
            "settings, not code.",
            "Already done, recorded here so the remaining work is unambiguous: the `workflow` "
            "OAuth scope was granted; `.github/workflows/ci.yml` is in place and "
            "`.github/workflows-staged/` is gone; the six jobs are `repo-checks`, `secrets`, "
            "`lint-api`, `test-api`, `lint-web` and `test-web`.",
            "Confirm all six contexts have reported on `develop` at least once. A required check "
            "that has never reported blocks every pull request indefinitely in an unexplained "
            "\"Expected\" state, so this check is not optional.",
            "Apply the full ruleset, which carries the required-status-checks rule with "
            "`strict_required_status_checks_policy: true`: "
            "`gh api -X PUT \"repos/:owner/:repo/rulesets/<id>\" --input .github/ruleset.json`.",
            "Delete `.github/ruleset-no-checks.json`; it exists only to bridge the gap before CI "
            "was live, and leaving it invites someone to apply it by mistake.",
            "Verify with a throwaway pull request carrying a deliberately failing check that the "
            "merge is blocked and the GitHub UI names the failing context.",
        ],
        "validation": [
            "`gh api \"repos/:owner/:repo/commits/develop/status\" -q '.statuses[].context'` "
            "lists all six contexts.",
            "`gh api \"repos/:owner/:repo/rulesets/<id>\"` shows a `required_status_checks` rule "
            "with `strict_required_status_checks_policy: true` and exactly those six contexts.",
            "A pull request with a deliberately failing check **cannot** be merged, and the "
            "failing context is named in the UI. Test this with the collaborator's account, not "
            "the owner's -- the owner has the admin bypass, so their own pull request proves "
            "nothing.",
            "`python scripts/check_ruleset_contexts.py` passes.",
            "`.github/ruleset-no-checks.json` no longer exists.",
        ],
        "deliverables": [
            "`.github/ruleset-no-checks.json` removed.",
            "The ruleset updated on the repository (an API action, not a file change).",
            "The blocked-merge verification evidenced on the pull request.",
        ],
        "notes": (
            "Two traps, both from the workflow playbook. First: applying the "
            "required-status-checks rule **before** CI has reported blocks every pull request "
            "indefinitely. Second: contexts are matched as literal strings against job names, so "
            "renaming a job without updating `.github/ruleset.json` in the same change silently "
            "blocks all merges -- `scripts/check_ruleset_contexts.py` runs in the `repo-checks` "
            "job to catch exactly that, and it also rejects a `paths:` filter on "
            "`pull_request`, since a skipped job never reports and produces the same block.\n\n"
            "Note that the four app jobs currently detect a missing `apps/` directory and pass "
            "without doing anything. That is deliberate -- a job-level `if` that evaluates false "
            "never reports its status, which would block merges under the strict policy. They "
            "become real checks as FND-01 creates the apps, and FND-01's own validation requires "
            "them to actually run."
        ),
    },
    {
        "id": "FND-05",
        "title": "API application skeleton with module boundaries and error envelope",
        "milestone": "MVP",
        "labels": ["backend", "api", "infra"],
        "size": "M",
        "depends": ["FND-03"],
        "branch": "feature/fnd-05-api-skeleton",
        "goal": (
            "Create the FastAPI application and the modular-monolith package layout from section "
            "3 of the implementation plan, plus the cross-cutting concerns every endpoint needs: "
            "one error response shape, request correlation ids, and structured logging. Feature "
            "issues then only add routers and services."
        ),
        "requirements": [
            "Create the empty module packages under `lexpert_api/`: `core`, `identity`, "
            "`verification`, `profiles`, `scheduling`, `booking`, `escrow`, `consultation`, "
            "`disputes`, `notifications`, `admin`. Each gets an `__init__.py` that exports the "
            "module's public interface and nothing else.",
            "`lexpert_api/main.py` builds the app through an `create_app()` factory (so tests "
            "get a fresh app), mounts routers under `/api/v1`, and sets a versioned OpenAPI "
            "title and description.",
            "A single error envelope for every non-2xx response: "
            "`{\"error\": {\"code\": \"<machine_code>\", \"message\": \"<French, user-safe>\", "
            "\"details\": {...}}}`. Implement it as exception handlers over a `LexpertError` "
            "base with subclasses for not-found, conflict, validation and forbidden.",
            "Override FastAPI's default `RequestValidationError` handler so validation failures "
            "use the same envelope rather than FastAPI's default shape.",
            "Request-id middleware: accept an inbound `X-Request-ID` or generate a UUID, put it "
            "in a context variable, echo it on the response, and include it in every log line.",
            "Structured JSON logging configured in `core/logging.py`. Log level from settings. "
            "**No request or response bodies are logged** — see CMP-02 for why this is a hard "
            "rule, and do not weaken it here for debugging convenience.",
            "`GET /api/v1/health` returning liveness plus a database round-trip check, and "
            "`GET /api/v1/version` returning the app version and git SHA when available.",
            "A module-boundary test: an automated check that no module imports another module's "
            "internals (only `core` or another module's `__init__` exports).",
        ],
        "validation": [
            "`GET /api/v1/health` returns 200 with the database reachable, and a non-200 with a "
            "clear code when it is not.",
            "Unit test: raising each `LexpertError` subclass from a test route produces the "
            "documented envelope and the documented HTTP status.",
            "Unit test: a request-body validation failure returns the same envelope shape as a "
            "domain error, not FastAPI's default.",
            "Unit test: an inbound `X-Request-ID` is echoed back; when absent, a UUID is "
            "generated and echoed.",
            "Unit test: a log record captured during a request carries the request id.",
            "The module-boundary test fails when a deliberate cross-module internal import is "
            "added, and passes on the real tree.",
            "`GET /openapi.json` is valid and every documented error response references the "
            "envelope schema.",
        ],
        "deliverables": [
            "`apps/api/src/lexpert_api/main.py` with `create_app()`.",
            "`core/errors.py`, `core/logging.py`, `core/middleware.py`.",
            "`__init__.py` for each of the eleven modules.",
            "`apps/api/tests/core/` covering errors, middleware and logging; "
            "`apps/api/tests/test_module_boundaries.py`.",
        ],
        "notes": (
            "The error `message` is shown to users, so it is French. The `code` is consumed by "
            "the web app, so it is a stable machine string and never translated. Getting this "
            "split right here saves reworking every endpoint later."
        ),
    },
    {
        "id": "FND-06",
        "title": "Web app shell: routing, layout, French i18n catalogue and API client",
        "milestone": "MVP",
        "labels": ["frontend", "infra"],
        "size": "M",
        "depends": ["FND-02"],
        "branch": "feature/fnd-06-web-shell",
        "goal": (
            "Create the web app's frame: the three portal route trees, a mobile-first layout, the "
            "French translation catalogue that all copy goes through, and one API client that "
            "understands the error envelope from FND-05. Feature issues then only add screens."
        ),
        "requirements": [
            "React Router with three route trees under a shared layout: `/` (client portal), "
            "`/pro` (professional portal), `/admin` (back-office). Placeholder screens are fine.",
            "Mobile-first layout: a responsive shell with a header, navigation that collapses on "
            "small viewports, and a content area. Most Tunisian users are on a phone, so design "
            "the small viewport first and widen up.",
            "i18n set up with a **French-only** catalogue (`apps/web/src/i18n/fr.ts`). Every "
            "user-facing string in the app resolves through it. Structure keys by feature so the "
            "catalogue stays navigable as it grows.",
            "A lint rule or unit test that fails when a JSX text node or a `title`/`aria-label`/"
            "`placeholder` prop contains a hard-coded non-ASCII-safe literal instead of a "
            "catalogue lookup. A pragmatic heuristic is acceptable; the point is that hard-coded "
            "copy is caught in CI rather than in review.",
            "One typed API client in `apps/web/src/api/`: base URL from `config.ts`, JSON "
            "handling, and translation of the `{error: {code, message}}` envelope into a typed "
            "`ApiError` carrying the code.",
            "TanStack Query (or an equivalent already chosen) for server state, with a "
            "`QueryClientProvider` in the shell and sane defaults for retries and staleness.",
            "A shared UI primitive set the feature issues reuse: button, input, select, "
            "form-field-with-error, spinner, empty state, and a toast or alert for errors. Keep "
            "it small; this is not a design system.",
            "Formatting helpers used everywhere money and time are shown: TND from integer "
            "millimes (`45,500 DT`), and dates in the viewer's timezone with the zone named.",
        ],
        "validation": [
            "`npm run build`, `npm run lint`, `npm run format:check`, `npm run typecheck` all "
            "pass.",
            "Unit test: the money formatter renders `45500` as `45,500 DT` and rejects "
            "non-integer input.",
            "Unit test: the date formatter renders a UTC instant in a given timezone and names "
            "the zone.",
            "Unit test: the API client turns a 409 error envelope into an `ApiError` with the "
            "correct `code`, and a network failure into a distinguishable error.",
            "Unit test: an unknown route renders the not-found screen.",
            "The hard-coded-copy check fails on a component with literal French text and passes "
            "on the real tree.",
            "Manual: at a 375px viewport width, no horizontal scrolling and the navigation is "
            "usable.",
        ],
        "deliverables": [
            "`apps/web/src/app/` with the router and layout.",
            "`apps/web/src/i18n/fr.ts` and the i18n provider.",
            "`apps/web/src/api/client.ts` with `ApiError`.",
            "`apps/web/src/components/` with the shared primitives.",
            "`apps/web/src/lib/format.ts` for money and dates.",
            "Unit tests for the formatters, the client and the router.",
        ],
    },
    {
        "id": "FND-07",
        "title": "Domain reference data: verticals, professions, regulators and statuses",
        "milestone": "MVP",
        "labels": ["backend", "database", "good-first-issue"],
        "size": "S",
        "depends": ["FND-05"],
        "branch": "feature/fnd-07-reference-data",
        "goal": (
            "Define, in one place, the closed vocabularies the rest of the system references: the "
            "three verticals, their regulators, the specialities under each, and the "
            "consultation and verification status enums. Several later issues each need these; "
            "defining them twice guarantees they diverge."
        ),
        "requirements": [
            "A `Vertical` enum with `MEDICAL`, `LEGAL`, `FINANCIAL`, and for each: the "
            "regulator's name and acronym (CNOM, Ordre National des Avocats de Tunisie, OECT) "
            "and its French display label.",
            "A seedable speciality list per vertical (for example medical specialities, areas of "
            "legal practice, areas of financial and fiscal practice). A short, credible starter "
            "list is enough; it is reference data, not a taxonomy project.",
            "Enums for the escrow and consultation lifecycle: the nine states named in feasibility "
            "study section 5.1 -- `BOOKED`, `FUNDS_HELD`, `IN_SESSION`, `SESSION_ENDED`, "
            "`HOLD_WINDOW`, `UNDER_REVIEW`, `RELEASED_TO_PRO`, `REFUNDED`, `CANCELLED` -- "
            "plus the three the request-and-accept handshake adds, which the study does not "
            "model: `PENDING_ACCEPTANCE`, `DECLINED`, `EXPIRED`. Twelve in total; see ESC-03 "
            "for the transitions between them.",
            "An enum for verification status: `DRAFT`, `SUBMITTED`, `UNDER_REVIEW`, "
            "`MORE_INFO_REQUESTED`, `APPROVED`, `REJECTED`.",
            "A Tunisian governorate or city list for the location filter used by PRO-02.",
            "An Alembic migration seeding the reference tables idempotently, so re-running it or "
            "running it on a populated database is safe.",
            "`GET /api/v1/reference` exposing verticals, specialities and cities so the web app "
            "never hard-codes them.",
            "The French labels live in the web i18n catalogue keyed by the enum value, not in the "
            "database, so copy changes do not need a migration.",
        ],
        "validation": [
            "Unit test: every enum member has a French label in `fr.ts`, and every label key "
            "corresponds to a real enum member. This test fails if either side drifts.",
            "Unit test: the consultation status enum contains exactly the twelve states listed "
            "above, no more and no fewer. This test is what stops a state being invented "
            "ad hoc later without a transition being defined for it.",
            "Integration test: running the seed migration twice leaves the same row counts.",
            "Integration test: `GET /api/v1/reference` returns all three verticals, each with a "
            "non-empty speciality list and its regulator.",
        ],
        "deliverables": [
            "`apps/api/src/lexpert_api/core/enums.py`.",
            "Reference models and the seeding migration.",
            "`GET /api/v1/reference` and its router.",
            "French labels added to `apps/web/src/i18n/fr.ts`.",
            "Tests as listed above.",
        ],
    },
    # ------------------------------------------------------------------ AUT
    {
        "id": "AUT-01",
        "title": "User model, registration and JWT login for the three roles",
        "milestone": "MVP",
        "labels": ["auth", "backend", "database"],
        "size": "M",
        "depends": ["FND-05", "FND-07"],
        "branch": "feature/aut-01-user-auth",
        "goal": (
            "Let a person create an account as a client or a professional and log in, with "
            "admins created out of band. This is the entry point to every other flow, so the "
            "token and role model set here is hard to change later."
        ),
        "requirements": [
            "`User` model: id, email (unique, case-insensitive), phone (E.164, unique), password "
            "hash, full name, role, `is_active`, `email_verified_at`, `phone_verified_at`, "
            "timestamps.",
            "Roles: `CLIENT`, `PROFESSIONAL`, `ADMIN`. Registration accepts only `CLIENT` and "
            "`PROFESSIONAL`; a request for `ADMIN` is rejected. Admins are created by a "
            "management command, never through the public API.",
            "Password hashing with Argon2id (or bcrypt if Argon2 proves awkward to install). "
            "Minimum policy: at least 10 characters, and rejection of a small list of obvious "
            "passwords. Do not invent an elaborate policy; length is what matters.",
            "`POST /api/v1/auth/register`, `POST /api/v1/auth/login`, "
            "`POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`, `GET /api/v1/auth/me`.",
            "JWT access token (short TTL from settings) and refresh token (long TTL), both "
            "carrying `sub`, `role` and `jti`. Refresh tokens are persisted so logout can revoke "
            "them; a revoked or reused refresh token is rejected.",
            "Registering a professional creates the user **and** an empty verification file in "
            "`DRAFT` (the KYC module's entry point), so KYC-04 has something to submit against.",
            "Login must not reveal whether an email exists: the same error code and a comparable "
            "response time for an unknown email and a wrong password.",
            "Rate-limit login and registration per IP and per email. A simple in-process or "
            "database-backed limiter is fine for the MVP; note in the code that it needs to move "
            "to shared state when the app runs multi-process.",
        ],
        "validation": [
            "Integration test: register a client, log in, call `/auth/me`, get the right role.",
            "Integration test: registering a professional also creates a `DRAFT` verification "
            "file.",
            "Integration test: registering with `role=ADMIN` is rejected with a stable error "
            "code.",
            "Integration test: duplicate email and duplicate phone are both rejected with a "
            "conflict code.",
            "Integration test: email casing is normalised, so `A@b.tn` and `a@b.tn` collide.",
            "Integration test: an expired access token is rejected; a valid refresh token returns "
            "a new pair; the **used** refresh token is then rejected.",
            "Integration test: after logout, the refresh token no longer works.",
            "Security test: unknown email and wrong password produce identical error codes.",
            "Security test: exceeding the login rate limit returns the documented error.",
            "`grep` the test output and logs to confirm no password or token value is ever "
            "logged.",
        ],
        "deliverables": [
            "`lexpert_api/identity/` with models, schemas, service, router and security "
            "primitives.",
            "Alembic migration for `users` and `refresh_tokens`.",
            "A `create-admin` management command.",
            "`apps/api/tests/identity/` covering every validation item.",
            "New error codes documented in the OpenAPI responses.",
        ],
    },
    {
        "id": "AUT-02",
        "title": "Email and phone verification, and password reset",
        "milestone": "MVP",
        "labels": ["auth", "backend"],
        "size": "M",
        "depends": ["AUT-01"],
        "branch": "feature/aut-02-verification-reset",
        "goal": (
            "Confirm that a new account's email and phone belong to the person registering, and "
            "let someone who has forgotten their password recover it. Phone verification matters "
            "more than usual here: SMS is the channel with the highest open rate in Tunisia and "
            "is what consultation reminders will use."
        ),
        "requirements": [
            "Single-use, expiring tokens for email verification (link) and phone verification "
            "(6-digit code). Store hashes, not the raw values.",
            "`POST /api/v1/auth/verify-email/request`, `POST /api/v1/auth/verify-email/confirm`, "
            "`POST /api/v1/auth/verify-phone/request`, `POST /api/v1/auth/verify-phone/confirm`.",
            "`POST /api/v1/auth/password-reset/request` and "
            "`POST /api/v1/auth/password-reset/confirm`. The request endpoint responds "
            "identically whether or not the email exists.",
            "Confirming a password reset revokes every outstanding refresh token for that user.",
            "Resend throttling with a cooldown, and a cap on attempts per token before it is "
            "invalidated.",
            "Until NOT-01 lands, send through a logging stub that records the message and the "
            "recipient but **not** the token value. Define the interface here so NOT-01 only "
            "swaps the implementation.",
            "A professional whose phone is unverified cannot submit a verification file; a client "
            "whose phone is unverified cannot confirm a booking. Enforce both as service-layer "
            "checks with clear error codes.",
        ],
        "validation": [
            "Integration test: request and confirm email verification; `email_verified_at` is "
            "set.",
            "Integration test: a token cannot be reused, and an expired token is rejected.",
            "Integration test: a wrong code increments the attempt count and the token dies at "
            "the cap.",
            "Integration test: password reset changes the password and invalidates all refresh "
            "tokens.",
            "Integration test: `password-reset/request` returns the same response for a known "
            "and an unknown email.",
            "Integration test: resending inside the cooldown is rejected.",
            "Integration test: an unverified-phone professional gets the documented error when "
            "submitting a verification file.",
            "Test asserting the notification stub was called and that the raw token does not "
            "appear in captured logs.",
        ],
        "deliverables": [
            "Verification and reset token models plus their migration.",
            "The six endpoints and their schemas.",
            "`lexpert_api/notifications/interface.py` with the send interface and the logging "
            "stub.",
            "Tests as listed above.",
        ],
    },
    {
        "id": "AUT-03",
        "title": "Role-based access control and route guards",
        "milestone": "MVP",
        "labels": ["auth", "backend", "api"],
        "size": "M",
        "depends": ["AUT-01"],
        "branch": "feature/aut-03-rbac",
        "goal": (
            "Give the API one authorization mechanism, used by every protected endpoint, instead "
            "of per-endpoint checks that drift. Also establish resource-level ownership, which "
            "matters more than role here: a client must not read another client's consultation."
        ),
        "requirements": [
            "FastAPI dependencies: `current_user` (any authenticated user), "
            "`require_role(*roles)`, and `require_verified_professional` (role is "
            "`PROFESSIONAL` **and** verification status is `APPROVED`).",
            "A resource-ownership helper for the pattern that repeats across the app: the actor "
            "must be the consultation's client, its professional, or an admin. Return 404 rather "
            "than 403 when the actor has no business knowing the resource exists.",
            "Admin-only endpoints are grouped under one router with the role dependency applied "
            "at the router level, so a new admin endpoint cannot forget it.",
            "A test that enumerates every route in the application and asserts each one is "
            "either in an explicit public allow-list or carries an authentication dependency. "
            "This is the check that catches an unprotected endpoint added six months from now.",
            "Consistent failure semantics: 401 with a stable code when unauthenticated, 403 when "
            "authenticated but not permitted, 404 when the resource must not be disclosed.",
        ],
        "validation": [
            "Integration test: each dependency admits the permitted roles and rejects the rest.",
            "Integration test: `require_verified_professional` rejects an approved-role user "
            "whose verification is still `SUBMITTED`.",
            "Integration test: client A requesting client B's resource gets 404, not 403.",
            "Integration test: an admin can read both clients' resources.",
            "The route-coverage test fails when an unprotected route is added and passes on the "
            "real tree.",
            "Integration test: a malformed `Authorization` header returns 401 with the "
            "documented code, not a 500.",
        ],
        "deliverables": [
            "`lexpert_api/core/security.py` with the dependencies and the ownership helper.",
            "The admin router with the role dependency at router level.",
            "`apps/api/tests/core/test_authorization.py` and "
            "`test_route_protection_coverage.py`.",
            "A `## Authorization` section in the API docs stating which dependency guards which "
            "route group.",
        ],
        "notes": (
            "`require_verified_professional` is the mechanical enforcement of the plan's hard "
            "rule that an unapproved professional is invisible and unbookable. Every "
            "professional-facing write endpoint uses it."
        ),
    },
    {
        "id": "AUT-04",
        "title": "Web authentication flows and guarded routes",
        "milestone": "MVP",
        "labels": ["frontend", "auth"],
        "size": "M",
        "depends": ["AUT-02", "AUT-03", "FND-06", "UX-05", "UX-07"],
        "branch": "feature/aut-04-web-auth",
        "goal": (
            "The French screens for registering, logging in, verifying a phone and resetting a "
            "password, plus the client-side session handling and route guards that keep the three "
            "portals apart."
        ),
        "requirements": [
            "Screens, all in French through the i18n catalogue: register (with a client or "
            "professional choice), login, forgot password, reset password, verify phone (code "
            "entry with resend), verify email landing page.",
            "Session handling: the access token in memory, the refresh token in an "
            "`httpOnly`-style persisted slot as far as the API allows, silent refresh on 401 with "
            "a single retry, and a full logout that clears everything.",
            "Route guards: unauthenticated users are redirected to login with a return path; a "
            "client cannot reach `/pro` or `/admin`; a professional cannot reach `/admin`.",
            "A professional who logs in with verification not yet `APPROVED` lands on their "
            "verification status page (KYC-05), not on a dashboard they cannot use.",
            "Form validation with inline French error messages, and mapping of API error `code` "
            "values to French copy from the catalogue. Never render the API's `message` when a "
            "known code has a local translation.",
            "Accessible forms: real labels, `aria-describedby` on errors, focus moved to the "
            "first invalid field on submit, and the whole flow completable by keyboard.",
        ],
        "validation": [
            "Component test per screen: renders, validates, submits, shows the server error.",
            "Test: a 401 on a protected query triggers exactly one silent refresh and one retry, "
            "then logs out if the refresh fails.",
            "Test: guards redirect correctly for each of the three roles, and the return path is "
            "honoured after login.",
            "Test: a professional with `SUBMITTED` verification is routed to the status page.",
            "Test: every rendered string comes from the catalogue (the FND-06 check covers this "
            "and must stay green).",
            "Manual: the whole register-verify-login path is completable by keyboard on a 375px "
            "viewport.",
        ],
        "deliverables": [
            "`apps/web/src/features/auth/` with the six screens.",
            "`apps/web/src/app/guards.tsx` and the session store.",
            "Auth keys added to `fr.ts`.",
            "Component tests for each screen and the guards.",
        ],
    },
    # ------------------------------------------------------------------ KYC
    {
        "id": "KYC-01",
        "title": "KYC-Pro data model and review state machine",
        "milestone": "MVP",
        "labels": ["kyc-pro", "database", "backend"],
        "size": "M",
        "depends": ["AUT-01", "FND-07"],
        "branch": "feature/kyc-01-data-model",
        "goal": (
            "Model the professional verification file that all three verticals share, with the "
            "per-regulator fields kept where they can vary independently, and the review state "
            "machine that governs how a file moves from draft to approved. This is the schema "
            "every other KYC issue builds on."
        ),
        "requirements": [
            "`VerificationFile`: id, user id (unique — one file per professional), vertical, "
            "status, submitted_at, reviewed_at, reviewer id, rejection reason, "
            "more-info message, timestamps.",
            "`VerificationField`: the regulator-specific values, stored as a validated JSON "
            "column or a per-vertical detail table. Choose one and justify the choice in the PR "
            "description; both are defensible, but a mix is not.",
            "`VerificationDocument`: id, file id, document type, storage key, original filename, "
            "content type, byte size, checksum, uploaded_at. **The document bytes never live in "
            "the database.**",
            "Document types as an enum covering what all three verticals need: `NATIONAL_ID`, "
            "`DIPLOMA`, `REGULATOR_CERTIFICATE`, `PROOF_OF_ADDRESS`, `OTHER`.",
            "The review state machine with exactly these legal transitions: `DRAFT -> SUBMITTED`, "
            "`SUBMITTED -> UNDER_REVIEW`, `UNDER_REVIEW -> APPROVED`, "
            "`UNDER_REVIEW -> REJECTED`, `UNDER_REVIEW -> MORE_INFO_REQUESTED`, "
            "`MORE_INFO_REQUESTED -> SUBMITTED`, `REJECTED -> SUBMITTED` (a resubmission after "
            "fixing the file). Every other transition is refused.",
            "Transitions go through one service function that validates the transition, requires "
            "a reason on `REJECTED` and a message on `MORE_INFO_REQUESTED`, and appends a "
            "`VerificationEvent` audit row. Direct status writes are not allowed anywhere else.",
            "An index supporting the admin queue query: files in `SUBMITTED` or `UNDER_REVIEW`, "
            "oldest first.",
        ],
        "validation": [
            "Unit test: a table-driven test over the full transition matrix asserts every legal "
            "transition is allowed and **every** illegal one raises.",
            "Unit test: `REJECTED` without a reason is refused; `MORE_INFO_REQUESTED` without a "
            "message is refused.",
            "Unit test: each transition appends exactly one `VerificationEvent` with the actor, "
            "the from- and to-status, and the timestamp.",
            "Integration test: two files for the same user violate the uniqueness constraint.",
            "Integration test: the admin queue query returns pending files oldest first and "
            "excludes approved and rejected ones.",
            "`alembic upgrade head` then `--autogenerate` produces an empty migration.",
        ],
        "deliverables": [
            "`lexpert_api/verification/models.py`, `state_machine.py`, `service.py`.",
            "The Alembic migration for the four tables.",
            "`apps/api/tests/verification/test_state_machine.py` with the transition matrix.",
            "A transition diagram in `docs/technical_docs/kyc_review_workflow.md`.",
        ],
    },
    {
        "id": "KYC-02",
        "title": "Document upload with private storage",
        "milestone": "MVP",
        "labels": ["kyc-pro", "backend", "compliance"],
        "size": "M",
        "depends": ["KYC-01"],
        "branch": "feature/kyc-02-document-upload",
        "goal": (
            "Let a professional upload the identity and diploma documents their regulator "
            "requires, and let an admin read them — while nobody else can, ever. These are "
            "identity documents; a public URL to one is a data-protection incident."
        ),
        "requirements": [
            "A `DocumentStorage` interface with `put`, `get`, `delete` and "
            "`presigned_read_url`. A local-filesystem implementation for the MVP, rooted at "
            "`LEXPERT_STORAGE_ROOT`, which is git-ignored.",
            "`POST /api/v1/verification/documents` (multipart) and "
            "`DELETE /api/v1/verification/documents/{id}`, both restricted to the owning "
            "professional and only while the file is in `DRAFT` or `MORE_INFO_REQUESTED`.",
            "`GET /api/v1/verification/documents/{id}/url` returning a short-lived, single-use "
            "read URL. Available to the owning professional and to admins. No other role, no "
            "unauthenticated access, and no long-lived or guessable URL.",
            "Validation: allowed content types are PDF, JPEG and PNG; maximum 10 MB per file; "
            "maximum 10 documents per verification file. Detect the real type from the file's "
            "magic bytes, not from the declared `Content-Type` or the extension.",
            "Storage keys are opaque and unguessable (a UUID path), never derived from the "
            "filename or the user id.",
            "Store a SHA-256 checksum and reject an exact duplicate upload within the same "
            "verification file.",
            "Strip EXIF metadata from images on upload — it can carry GPS coordinates.",
            "Deleting a document removes both the row and the stored object, and appends a "
            "`VerificationEvent`.",
        ],
        "validation": [
            "Integration test: upload a PDF, then fetch the read URL and retrieve the bytes.",
            "Integration test: an executable renamed to `.pdf` is rejected by magic-byte "
            "detection.",
            "Integration test: an 11 MB file is rejected; an 11th document is rejected.",
            "Integration test: professional B cannot fetch professional A's document URL "
            "(expect 404).",
            "Integration test: an unauthenticated request for a document URL is rejected.",
            "Integration test: an admin can fetch any document URL.",
            "Integration test: a read URL is rejected after expiry.",
            "Integration test: uploading while the file is `UNDER_REVIEW` is refused.",
            "Integration test: an image with GPS EXIF is stored without it.",
            "Integration test: delete removes the row and the object; a subsequent read is 404.",
            "Manual check: no storage path or filename appears in any log line.",
        ],
        "deliverables": [
            "`lexpert_api/core/storage.py` with the interface and the local backend.",
            "The three document endpoints plus schemas.",
            "`apps/api/tests/verification/test_documents.py` covering every item above.",
            "A note in `docs/technical_docs/` on what changes when storage moves to a real "
            "object store in Beta.",
        ],
        "notes": (
            "`uploads/` and `storage/` are already git-ignored. Test fixtures must be synthetic "
            "documents generated in the test, never real scans of anything."
        ),
    },
    {
        "id": "KYC-03",
        "title": "Per-vertical verification rule sets for CNOM, the Bar and the OECT",
        "milestone": "MVP",
        "labels": ["kyc-pro", "backend", "compliance"],
        "size": "L",
        "depends": ["KYC-01"],
        "branch": "feature/kyc-03-vertical-rules",
        "goal": (
            "Encode what each of the three regulators requires, as three declarative rule sets "
            "behind one interface, so that adding a fourth vertical later is a new rule set "
            "rather than a change to the submission pipeline. This is the issue that makes the "
            "platform genuinely multi-vertical rather than medical-with-extras."
        ),
        "requirements": [
            "A `VerticalRuleSet` interface declaring: required fields with their types and "
            "validation, required document types, and a `validate(file) -> list[Violation]` "
            "method returning every violation rather than raising on the first.",
            "**Medical (CNOM):** CNOM registration number with its documented format, medical "
            "speciality from the FND-07 list, diploma year, place of practice. Required "
            "documents: national ID, diploma, CNOM registration certificate.",
            "**Legal (Ordre National des Avocats de Tunisie):** bar registration number, bar "
            "section (the regional bar), date sworn in, areas of practice. Required documents: "
            "national ID, diploma, bar registration certificate.",
            "**Financial (OECT):** OECT membership number, practice type (expert-comptable or "
            "comptable), areas of practice. Required documents: national ID, diploma, OECT "
            "membership certificate.",
            "Validate identifier **format** only. No regulator publishes a verification API, so "
            "do not pretend to check a number against a registry; that is what the admin review "
            "is for. Where the real format is uncertain, implement a documented permissive check "
            "and leave a `TODO` naming the open question — do not invent a strict format that "
            "rejects real professionals.",
            "Violations carry a machine code and a French message, and name the field or "
            "document type they concern, so KYC-05 can render them inline against the right "
            "input.",
            "A registry mapping vertical to rule set, and a test that fails if a `Vertical` "
            "member has no rule set.",
        ],
        "validation": [
            "Unit test per vertical: a complete, valid file produces no violations.",
            "Unit test per vertical: each individually missing required field produces exactly "
            "one violation naming that field.",
            "Unit test per vertical: each individually missing required document produces "
            "exactly one violation naming that document type.",
            "Unit test: a file with three problems returns three violations, not one.",
            "Unit test: a malformed regulator identifier is rejected with the documented code.",
            "Unit test: submitting a medical file's fields under the legal vertical produces "
            "violations, proving the rule sets are not interchangeable.",
            "Unit test: the registry covers every `Vertical` member.",
            "Every violation code has a French message in `fr.ts` (the FND-07 label test pattern "
            "extended to violation codes).",
        ],
        "deliverables": [
            "`lexpert_api/verification/rules/` with `base.py`, `medical.py`, `legal.py`, "
            "`financial.py`, `registry.py`.",
            "`apps/api/tests/verification/test_rules_*.py`, one file per vertical.",
            "`docs/technical_docs/kyc_vertical_requirements.md` tabulating what each regulator "
            "requires, with the open questions listed explicitly.",
            "Violation codes and French messages in `fr.ts`.",
        ],
        "notes": (
            "The exact identifier formats need confirming with each ordre; the feasibility study "
            "flags all three as to-verify. Implement permissively, document every assumption in "
            "`kyc_vertical_requirements.md`, and raise the open questions on this issue rather "
            "than guessing silently. A rule set that rejects a real doctor is worse than one that "
            "accepts a typo, because the admin review catches the typo."
        ),
    },
    {
        "id": "KYC-04",
        "title": "Verification submission and status API",
        "milestone": "MVP",
        "labels": ["kyc-pro", "api", "backend"],
        "size": "M",
        "depends": ["KYC-02", "KYC-03", "AUT-03"],
        "branch": "feature/kyc-04-submission-api",
        "goal": (
            "The endpoints a professional uses to fill in, submit and track their verification "
            "file. This is where the rule sets from KYC-03 and the state machine from KYC-01 "
            "meet."
        ),
        "requirements": [
            "`GET /api/v1/verification/me` returning the file, its status, its fields, its "
            "documents, the requirements for its vertical, and the current violations — so the "
            "UI can render progress without a second call.",
            "`PATCH /api/v1/verification/me` saving field values as a draft. Permitted only in "
            "`DRAFT` and `MORE_INFO_REQUESTED`. Partial saves are allowed and are not validated "
            "against the rule set.",
            "`POST /api/v1/verification/me/submit` running the full rule set. On violations, "
            "return 422 with the envelope and every violation in `details`, and do **not** change "
            "status. On success, transition to `SUBMITTED`.",
            "Submission additionally requires the professional's phone to be verified (AUT-02) "
            "and their vertical to be set. A vertical cannot be changed once a file has been "
            "submitted.",
            "`GET /api/v1/verification/me/events` returning the audit trail so the professional "
            "can see what happened and when.",
            "Every endpoint is restricted to `role == PROFESSIONAL` and operates only on the "
            "caller's own file. There is no endpoint that takes another user's file id.",
            "A professional resubmitting after `MORE_INFO_REQUESTED` or `REJECTED` keeps their "
            "history; the events are appended, not replaced.",
        ],
        "validation": [
            "Integration test, one per vertical: fill fields, upload documents, submit "
            "successfully, status becomes `SUBMITTED`.",
            "Integration test: submitting an incomplete file returns 422 with all violations and "
            "leaves the status at `DRAFT`.",
            "Integration test: `PATCH` while `UNDER_REVIEW` is refused.",
            "Integration test: submitting with an unverified phone is refused with the documented "
            "code.",
            "Integration test: changing the vertical after submission is refused.",
            "Integration test: a client-role user is refused on every endpoint.",
            "Integration test: the full round trip `SUBMITTED -> MORE_INFO_REQUESTED -> PATCH -> "
            "SUBMITTED` works and the event list shows all four entries.",
            "Integration test: `GET /verification/me` for a professional with no file returns a "
            "sensible empty-draft representation rather than a 404.",
        ],
        "deliverables": [
            "`lexpert_api/verification/router.py` and `schemas.py`.",
            "`apps/api/tests/verification/test_submission_api.py`.",
            "OpenAPI documentation for the five endpoints including the 422 violation shape.",
        ],
    },
    {
        "id": "KYC-05",
        "title": "Professional onboarding wizard",
        "milestone": "MVP",
        "labels": ["frontend", "kyc-pro"],
        "size": "L",
        "depends": ["KYC-04", "AUT-04", "UX-08"],
        "branch": "feature/kyc-05-onboarding-wizard",
        "goal": (
            "The French multi-step form a professional completes to get verified, with the "
            "fields and documents that their chosen vertical actually requires, plus the status "
            "page they return to while waiting. This screen is the platform's first impression "
            "on the supply side, and the feasibility study's cold-start analysis says supply "
            "comes first — so it needs to be genuinely easy."
        ),
        "requirements": [
            "A wizard with clear steps: choose vertical, professional details (fields driven by "
            "the vertical's requirements from the API), documents, review and submit. Steps are "
            "navigable backwards and the current step survives a page reload.",
            "The form is **generated from the requirements returned by the API**, not hard-coded "
            "per vertical. Adding a field in KYC-03 must not require a change here.",
            "Draft autosave via `PATCH`, debounced, with a visible saved indicator. A professional "
            "who closes the tab loses nothing.",
            "Document upload with drag-and-drop and a file picker, per-file progress, client-side "
            "type and size pre-checks matching the server's limits, a thumbnail or filename "
            "chip per uploaded document, and delete.",
            "Submission renders server violations inline against the field or document they "
            "name, plus a summary at the top listing them with anchor links. Do not show a bare "
            "\"submission failed\".",
            "A status page for every non-draft state, in French: `SUBMITTED` and `UNDER_REVIEW` "
            "explain that review is manual and give an expectation; `MORE_INFO_REQUESTED` shows "
            "the admin's message and reopens editing; `REJECTED` shows the reason and offers "
            "resubmission; `APPROVED` links onward to profile setup.",
            "The events timeline from `GET /verification/me/events`, rendered in French with "
            "relative and absolute timestamps.",
            "Mobile-first: the whole wizard is completable on a 375px viewport, including "
            "document upload from a phone camera roll.",
            "Accessibility: each step is a real form with labels, violations are announced via a "
            "live region, and focus moves to the first violation on a failed submit.",
        ],
        "validation": [
            "Component test per vertical: the wizard renders exactly the fields and document "
            "slots that vertical requires and no others.",
            "Test: a field added to the mocked API requirements appears without a code change.",
            "Test: draft autosave fires after the debounce and the indicator updates.",
            "Test: a 422 with three violations renders three inline errors against the correct "
            "inputs plus a three-item summary.",
            "Test: a file over the size limit is rejected client-side with a French message, "
            "before any request is made.",
            "Test: each of the five statuses renders its own screen with the right copy and "
            "actions.",
            "Test: `MORE_INFO_REQUESTED` shows the admin message and re-enables editing.",
            "Test: reloading mid-wizard restores the step and the entered values.",
            "Manual: complete the wizard end to end for all three verticals at a 375px viewport, "
            "keyboard only.",
        ],
        "deliverables": [
            "`apps/web/src/features/professional/onboarding/` with the wizard, the dynamic form "
            "renderer, the uploader and the status screens.",
            "Onboarding keys in `fr.ts`, including copy for all five statuses.",
            "Component tests covering every item above.",
        ],
    },
    {
        "id": "KYC-06",
        "title": "Admin verification review queue and decisions",
        "milestone": "MVP",
        "labels": ["admin", "kyc-pro", "backend"],
        "size": "M",
        "depends": ["KYC-04", "AUT-03"],
        "branch": "feature/kyc-06-admin-review-api",
        "goal": (
            "The API an admin uses to work through submitted verification files and decide them. "
            "Manual review is the compliance control the whole regulated-professions story rests "
            "on, so it has to be recorded properly and impossible to bypass."
        ),
        "requirements": [
            "`GET /api/v1/admin/verification` — a paginated queue, filterable by status and "
            "vertical, sortable by submission date, defaulting to pending files oldest first.",
            "`GET /api/v1/admin/verification/{id}` — the full file: fields, documents with read "
            "URLs, current violations, the applicant's account details, and the event history.",
            "`POST /api/v1/admin/verification/{id}/claim` transitioning `SUBMITTED -> "
            "UNDER_REVIEW` and recording the reviewer, so two admins do not review the same file. "
            "Claiming an already-claimed file is a conflict.",
            "`POST .../approve`, `POST .../reject` (reason required, minimum length enforced), "
            "`POST .../request-info` (message required). All go through the KYC-01 state machine.",
            "Approving sets the professional's verification to `APPROVED`, which is what makes "
            "them visible to PRO-02 search and bookable. Nothing else grants that.",
            "Every decision appends a `VerificationEvent` with the reviewer, the timestamp, the "
            "transition and the reason or message. Events are append-only; there is no edit or "
            "delete endpoint.",
            "Each decision triggers a notification to the professional through the AUT-02 "
            "interface.",
            "The whole router is admin-only via the router-level dependency from AUT-03.",
        ],
        "validation": [
            "Integration test: the queue returns pending files oldest first and honours the "
            "status and vertical filters.",
            "Integration test: a professional-role user is refused on every admin endpoint.",
            "Integration test: claim, then approve; the professional's status is `APPROVED` and "
            "two events exist.",
            "Integration test: a second admin claiming a claimed file gets a conflict.",
            "Integration test: reject without a reason, and with a one-character reason, are both "
            "refused.",
            "Integration test: `request-info` without a message is refused.",
            "Integration test: approving a file that is still `SUBMITTED` (unclaimed) is refused "
            "by the state machine.",
            "Integration test: an approved professional appears in the PRO-02 search query; the "
            "same professional before approval does not.",
            "Integration test: each decision calls the notification interface once.",
            "Integration test: the detail response's document URLs are fetchable by the admin.",
        ],
        "deliverables": [
            "`lexpert_api/admin/verification_router.py` and its schemas.",
            "`apps/api/tests/admin/test_verification_review.py`.",
            "OpenAPI documentation for the six endpoints.",
        ],
    },
    {
        "id": "KYC-07",
        "title": "Admin verification review interface",
        "milestone": "MVP",
        "labels": ["frontend", "admin", "kyc-pro"],
        "size": "M",
        "depends": ["KYC-06", "AUT-04", "UX-08"],
        "branch": "feature/kyc-07-admin-review-ui",
        "goal": (
            "The back-office screens an admin uses to review verification files. Review quality "
            "depends on how easily the reviewer can see the documents next to the claimed "
            "credentials, so the layout is the substance of this issue, not decoration."
        ),
        "requirements": [
            "A queue screen: table of pending files with applicant name, vertical, submission "
            "date and age, plus status and vertical filters and pagination. Oldest first by "
            "default.",
            "A detail screen laid out for comparison: the declared fields on one side, a document "
            "viewer on the other, so the reviewer can read the CNOM number off the certificate "
            "while looking at what was typed. Inline PDF and image viewing; no forced download.",
            "The decision panel: claim, approve, reject with a required reason, request more "
            "information with a required message. Approve and reject both require an explicit "
            "confirmation step, because both are consequential and hard to walk back.",
            "The event history rendered as a timeline with the reviewer's name and timestamps.",
            "Any current rule violations shown prominently — the reviewer should not have to "
            "re-derive what the automated check already found.",
            "Optimistic-free mutations: after a decision, refetch and show the resulting state "
            "rather than assuming success.",
            "A conflict on claim (another admin got there first) shows a clear French message "
            "and refreshes the queue rather than appearing to succeed.",
            "All copy in French through the catalogue.",
        ],
        "validation": [
            "Component test: the queue renders, filters and paginates against a mocked API.",
            "Component test: the detail screen renders fields, documents and violations.",
            "Component test: approve requires confirmation and then calls the endpoint once.",
            "Component test: reject with an empty reason is blocked client-side; with a reason it "
            "submits.",
            "Component test: `request-info` with an empty message is blocked.",
            "Component test: a 409 on claim renders the conflict message and triggers a refetch.",
            "Component test: a PDF and an image document both render inline.",
            "Manual: review a real submitted file end to end in a running local environment for "
            "each of the three verticals.",
        ],
        "deliverables": [
            "`apps/web/src/features/admin/verification/` with the queue, detail and decision "
            "panel.",
            "A reusable document viewer component.",
            "Admin keys in `fr.ts`.",
            "Component tests covering every item above.",
        ],
    },
]
