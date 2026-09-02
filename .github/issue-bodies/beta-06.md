**Task id:** `BETA-06`
**Milestone:** Beta
**Size:** M (1-2 days)
**Depends on:** `CMP-02`
**Branch:** `feature/beta-06-observability`
**Labels:** `infra`, `backend`

## Goal

Be able to tell, from outside the system, that it is working — and be told when it is not. The MVP's most dangerous failure is silent: the auto-release job not running, which strands money without any user-visible error until a professional complains.

## Requirements

1. Metrics for the things that matter operationally: consultations by state, auto-release job runs and outcomes, hold-window breaches, provider call latency and error rates, disputes open and their age, notification delivery failures.
2. Alerts on the silent failures specifically: the auto-release job not having run within its expected interval, any consultation past its hold expiry still in `HOLD_WINDOW`, any ledger imbalance, and any reconciliation discrepancy.
3. Distributed tracing across a request, with the FND-05 request id as the correlation key, so a user report maps to a trace.
4. Log shipping and retention that honours the CMP-02 redaction rules. Shipping logs to a third party is itself a data-processing activity and belongs in the CMP-01 register.
5. A health and readiness surface suitable for an orchestrator, distinguishing 'alive' from 'able to serve'.
6. A dashboard covering the escrow lifecycle end to end, because that is what will actually be watched during the pilot.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Test: each metric is emitted on the action it measures.
- Test: a ledger imbalance introduced deliberately triggers the alert condition.
- Test: a stalled auto-release job triggers the alert condition, with the clock frozen.
- Test: a consultation past its hold expiry still in `HOLD_WINDOW` is detected.
- Test: a trace spans a request and carries the request id.
- Test: shipped log records are redacted, verified with the CMP-02 canary values.
- The log-shipping destination added to the CMP-01 register.

## Deliverables

- Metrics instrumentation and the alert rules as code.
- Tracing wiring.
- The dashboard definition, committed.
- Tests as listed above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/beta-06-observability`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
