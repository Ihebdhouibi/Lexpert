**Task id:** `CMP-02`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `FND-05`, `DSP-01`
**Branch:** `feature/cmp-02-logging-guard`
**Labels:** `compliance`, `backend`

## Goal

Make it structurally difficult to log something that should never be logged, and prove in CI that the current code does not. A single logged dispute description or identity document path is a data-protection incident, and 'we were careful' is not a control.

## Requirements

1. A redacting log filter applied to the whole application: known-sensitive field names (password, token, secret, authorization, national id, licence number, dispute description, consultation note, document path, storage key) are replaced with a marker wherever they appear in a log record's arguments or extra fields.
2. A `Sensitive` wrapper type for values that must never be rendered: its `__repr__` and `__str__` return a marker, so it is safe even in an f-string or a traceback. Use it for the JWT secret, provider credentials and document storage keys.
3. Exception handlers must not leak: the error envelope's `details` is built from an allow-list of safe fields, never from the exception's raw arguments or a database error's message. A `psycopg` integrity error can contain row values.
4. Request and response bodies are never logged, at any log level, including debug. If a developer needs a body while debugging, they do it locally and do not commit it.
5. A CI check that greps for the patterns that reintroduce this: logging a request body, logging a whole model instance, an f-string interpolating a known-sensitive attribute into a log call. Keep the check narrow enough not to produce false positives that get it disabled.
6. A documented list of what is considered sensitive, in one place, referenced by both the filter and the register from CMP-01.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Unit test per sensitive field name: a log record containing it is emitted redacted.
- Unit test: `repr()` and `str()` of a `Sensitive` value return the marker, and an f-string interpolation does too.
- Unit test: a traceback containing a `Sensitive` value does not reveal it.
- Integration test: a database integrity error surfaces as the error envelope with no row values in `details`.
- Integration test: a request with a body is logged with no body content, at debug level too.
- Integration test: raising a dispute logs no part of the description (the DSP-01 test extended to assert against the whole captured log stream).
- Integration test: a KYC document upload logs no filename and no storage key.
- The CI check fails on a deliberately added body-logging line and passes on the real tree.
- A full-suite run with log capture, asserting that no captured line matches a set of canary values seeded into the test data. This is the broadest and most valuable of these tests.

## Deliverables

- `lexpert_api/core/redaction.py` with the filter and the `Sensitive` type.
- The error-envelope allow-list in `core/errors.py`.
- The CI check script, wired into the `lint-api` job.
- `apps/api/tests/core/test_redaction.py` and the suite-wide canary test.
- `docs/compliance/sensitive_data.md`.

## Notes

The canary test is the one that will actually catch a future regression: seed distinctive values into test fixtures for every sensitive field, run the whole suite with log capture, and fail if any canary appears. It costs one test and covers every code path the suite exercises.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/cmp-02-logging-guard`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
