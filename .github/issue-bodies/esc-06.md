**Task id:** `ESC-06`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `ESC-03`, `ESC-04`
**Branch:** `feature/esc-06-auto-release`
**Labels:** `escrow`, `backend`

## Goal

The mechanism that actually implements the product's promise: one hour after a consultation ends, if nobody disputed it, the funds go to the professional automatically. It runs unattended and moves money, so idempotency and observability are the whole job.

## Requirements

1. When a consultation reaches `SESSION_ENDED`, it transitions to `HOLD_WINDOW` with `hold_window_expires_at = ended_at + LEXPERT_ESCROW_HOLD_WINDOW_MINUTES`, read from settings so the duration is configurable per the feasibility study.
2. A periodic worker selecting consultations in `HOLD_WINDOW` whose expiry has passed and transitioning each to `RELEASED_TO_PRO` via the ESC-03 transition function, with the actor recorded as `SYSTEM`.
3. Each consultation is processed **independently**: one failure must not stop the batch or roll back the others. Failures are logged with the consultation id and retried on the next tick.
4. Idempotent by construction: the transition function's state validation means a second attempt on an already-released consultation is a no-op, not a double release. Prove this with a test.
5. Locked selection (`SELECT ... FOR UPDATE SKIP LOCKED`) so two worker instances never process the same consultation.
6. A bounded retry with a cap on attempts; after the cap, the consultation is flagged for admin attention rather than retried forever, and the flag is visible in the back-office.
7. Runnable both as a scheduled task and as a one-shot CLI command, so it can be triggered by hand in a demo and in tests. The MVP does not need a queue infrastructure; a scheduler plus the CLI is enough.
8. Structured logs per run: how many were eligible, released, failed, and how long it took. This job silently not running is the worst failure mode, so make its silence detectable.
9. A consultation in `UNDER_REVIEW` (disputed) is **never** touched by this job.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Integration test with a frozen clock: a consultation whose window has expired is released; one whose window has not is left alone. Test both sides of the boundary and the exact boundary instant.
- Integration test: a disputed consultation in `UNDER_REVIEW` is not released.
- Integration test: running the job twice releases once; the second run is a no-op and posts no second ledger transaction.
- Integration test: with three eligible consultations, one of which fails, the other two are still released.
- Integration test: the failed one is retried on the next run and succeeds.
- Integration test: after the retry cap it is flagged rather than retried again.
- Concurrency test: two workers over the same eligible set release each consultation exactly once.
- Integration test: each release produces an audit entry with actor `SYSTEM` and a balanced ledger transaction splitting the total into payable and revenue.
- Integration test: changing the hold-window setting affects new consultations but not the expiry already stored on existing ones.
- Unit test: the run summary log contains the documented counters.

## Deliverables

- `lexpert_api/escrow/jobs/auto_release.py` and the CLI entry point.
- The scheduler wiring, and documentation of how it is run locally.
- `apps/api/tests/escrow/test_auto_release.py` covering every item above.
- A `## Hold window and auto-release` section in `docs/technical_docs/escrow_lifecycle.md`.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/esc-06-auto-release`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
