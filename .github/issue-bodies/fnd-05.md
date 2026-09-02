**Task id:** `FND-05`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `FND-03`
**Branch:** `feature/fnd-05-api-skeleton`
**Labels:** `backend`, `api`, `infra`

## Goal

Create the FastAPI application and the modular-monolith package layout from section 3 of the implementation plan, plus the cross-cutting concerns every endpoint needs: one error response shape, request correlation ids, and structured logging. Feature issues then only add routers and services.

## Requirements

1. Create the empty module packages under `lexpert_api/`: `core`, `identity`, `verification`, `profiles`, `scheduling`, `booking`, `escrow`, `consultation`, `disputes`, `notifications`, `admin`. Each gets an `__init__.py` that exports the module's public interface and nothing else.
2. `lexpert_api/main.py` builds the app through an `create_app()` factory (so tests get a fresh app), mounts routers under `/api/v1`, and sets a versioned OpenAPI title and description.
3. A single error envelope for every non-2xx response: `{"error": {"code": "<machine_code>", "message": "<French, user-safe>", "details": {...}}}`. Implement it as exception handlers over a `LexpertError` base with subclasses for not-found, conflict, validation and forbidden.
4. Override FastAPI's default `RequestValidationError` handler so validation failures use the same envelope rather than FastAPI's default shape.
5. Request-id middleware: accept an inbound `X-Request-ID` or generate a UUID, put it in a context variable, echo it on the response, and include it in every log line.
6. Structured JSON logging configured in `core/logging.py`. Log level from settings. **No request or response bodies are logged** — see CMP-02 for why this is a hard rule, and do not weaken it here for debugging convenience.
7. `GET /api/v1/health` returning liveness plus a database round-trip check, and `GET /api/v1/version` returning the app version and git SHA when available.
8. A module-boundary test: an automated check that no module imports another module's internals (only `core` or another module's `__init__` exports).

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- `GET /api/v1/health` returns 200 with the database reachable, and a non-200 with a clear code when it is not.
- Unit test: raising each `LexpertError` subclass from a test route produces the documented envelope and the documented HTTP status.
- Unit test: a request-body validation failure returns the same envelope shape as a domain error, not FastAPI's default.
- Unit test: an inbound `X-Request-ID` is echoed back; when absent, a UUID is generated and echoed.
- Unit test: a log record captured during a request carries the request id.
- The module-boundary test fails when a deliberate cross-module internal import is added, and passes on the real tree.
- `GET /openapi.json` is valid and every documented error response references the envelope schema.

## Deliverables

- `apps/api/src/lexpert_api/main.py` with `create_app()`.
- `core/errors.py`, `core/logging.py`, `core/middleware.py`.
- `__init__.py` for each of the eleven modules.
- `apps/api/tests/core/` covering errors, middleware and logging; `apps/api/tests/test_module_boundaries.py`.

## Notes

The error `message` is shown to users, so it is French. The `code` is consumed by the web app, so it is a stable machine string and never translated. Getting this split right here saves reworking every endpoint later.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/fnd-05-api-skeleton`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
