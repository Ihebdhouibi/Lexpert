**Task id:** `BETA-10`
**Milestone:** Beta
**Size:** M (1-2 days)
**Depends on:** `BETA-06`, `BETA-07`, `E2E-01`
**Branch:** `feature/beta-10-pilot-readiness`
**Labels:** `admin`, `docs`, `backend`

## Goal

Everything needed to run the supply-first pilot the feasibility study recommends: onboard a curated set of professionals in one city, support them, and measure whether it is working against the KPIs the study names.

## Requirements

1. An admin tool for assisted onboarding, so a professional can be walked through verification by phone during the pilot without an admin ever holding their credentials or acting as them.
2. The KPI dashboard the study asks for: GMV, take rate, no-show rate, dispute rate, professional retention, client repeat rate, and acquisition cost per side where the data exists.
3. Support tooling: look up a user, see their consultations and their audit trail, and act on a specific consultation — every action logged with the acting admin. Support access is a privileged read of sensitive data and must be as auditable as a money movement.
4. Impersonation, if it is built at all, is read-only, time-boxed, consented to by the user, and loudly audited. If that is not achievable, do not build it.
5. Extend the E2E-01 demo seeding to cover the pilot scenarios, rather than building a second seeder. Still entirely synthetic.
6. An operational runbook for the pilot: what to watch daily, what to do when a dispute arrives, and how to handle a professional's payout question.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Test: each KPI matches a hand-computed value over a seeded dataset.
- Test: every support action is recorded with the acting admin and the target.
- Test: assisted onboarding never exposes or sets a professional's credentials.
- Test: impersonation, if present, is read-only and expires, and a write attempt during it is refused.
- Test: the extended seeding produces a working pilot environment and still contains no real personal data.
- The runbook walked through once with the owner, and corrected from that walkthrough.

## Deliverables

- The admin onboarding assistance and support tooling.
- The KPI dashboard and its endpoints.
- The pilot scenarios added to the E2E-01 seeding command.
- `docs/runbooks/pilot_operations.md`.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/beta-10-pilot-readiness`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
