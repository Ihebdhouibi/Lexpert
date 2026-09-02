**Task id:** `BETA-08`
**Milestone:** Beta
**Size:** M (1-2 days)
**Depends on:** `BETA-07`
**Branch:** `chore/beta-08-quality-gates`
**Labels:** `ci`, `test`

## Goal

Ratchet the quality gates now that the codebase can hold them, and find out what the system does under load and under partial failure before a pilot with real professionals does it for us.

## Requirements

1. Raise `fail_under` in steps toward 85%, in its own `chore:` PR, with the escrow, ledger, audit and state-machine modules held to a higher bar than the average.
2. Per-module coverage thresholds so a well-covered average cannot hide an under-tested escrow module.
3. Load testing of the paths that will actually be hit: search, slot computation, booking, and the auto-release job over a realistic backlog.
4. Resilience testing: the payment provider unavailable, the video provider unavailable, the database failing over mid-transaction, and the auto-release job killed halfway. Assert the system's state afterwards is consistent in every case.
5. Fix what the resilience tests find, or document each finding as an accepted risk with a reason. A found-and-ignored inconsistency in a money system is not an acceptable outcome.
6. A documented performance baseline, so a later regression is measurable rather than a matter of opinion.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- CI enforces the raised global and per-module thresholds.
- Load test results documented against the baseline for each path.
- Resilience test: the provider unavailable during booking leaves no held funds and no orphaned consultation.
- Resilience test: the auto-release job killed mid-batch leaves every consultation either fully released or untouched, never partial.
- Resilience test: a database failover mid-transition leaves the ledger balanced and the audit chain gapless.
- Every finding either fixed or recorded as an accepted risk with a rationale.

## Deliverables

- Raised thresholds in `pyproject.toml` and the per-module configuration.
- The load test suite and its baseline document.
- The resilience test suite.
- `docs/technical_docs/performance_baseline.md` and the risk record.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `chore/beta-08-quality-gates`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
