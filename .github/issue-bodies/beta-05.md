**Task id:** `BETA-05`
**Milestone:** Beta
**Size:** L (3 days or more)
**Depends on:** `CMP-01`, `CMP-02`
**Branch:** `feature/beta-05-retention-deletion`
**Labels:** `compliance`, `backend`, `docs`

## Goal

Complete what CMP-01 deliberately left open: how long each category of personal data is kept, what happens on a deletion request, and how that reconciles with financial and audit records that cannot be deleted. This needs the legal review the feasibility study calls for and cannot be decided from the code.

## Requirements

1. **Gate:** a retention schedule reviewed by a Tunisian data-protection advisor, per category, with its legal basis. Implement the reviewed schedule, not an invented one.
2. A deletion request flow that distinguishes what can be erased (profile, biography, ratings text, uploaded documents past their retention) from what must be retained (ledger entries, audit chain, the fact a consultation occurred), and pseudonymises the retained records rather than deleting them.
3. The audit chain must survive pseudonymisation with its hash verification intact. This is the hard technical constraint in this issue and it must be solved deliberately, not discovered late.
4. Automated retention enforcement: a job deleting KYC documents past their retention and reporting what it did.
5. An INPDP notification or registration package, if the reviewed advice says one is required.
6. A breach-response runbook.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- Test: a deletion request erases every erasable category and pseudonymises the rest.
- Test: the audit chain still verifies after pseudonymisation.
- Test: the ledger still balances after pseudonymisation.
- Test: the retention job deletes only documents past retention, with the clock frozen, and reports its actions.
- Test: a deleted user's data is absent from search, from the professional's earnings view, and from a counterparty's data export.
- The register from CMP-01 updated with the reviewed retention periods.

## Deliverables

- The deletion and pseudonymisation service, and the retention job.
- The reviewed retention schedule in `docs/compliance/`.
- The breach-response runbook.
- Tests as listed above.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/beta-05-retention-deletion`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
