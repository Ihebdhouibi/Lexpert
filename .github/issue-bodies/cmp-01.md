**Task id:** `CMP-01`
**Milestone:** MVP
**Size:** M (1-2 days)
**Depends on:** `CON-04`, `KYC-02`
**Branch:** `feature/cmp-01-data-protection`
**Labels:** `compliance`, `backend`, `docs`

## Goal

Put the INPDP-facing basics in place: a published privacy policy, an internal register of what personal data the platform holds and why, and a working data-export endpoint. The feasibility study lists an INPDP compliance note as a Phase 1 deliverable; this is its implementation side.

## Requirements

1. A data-processing register in the repository: every category of personal data the platform stores, where it lives, its legal basis, who can access it, and its intended retention. Derive it from the actual schema, not from intent — walk the migrations.
2. Sensitive categories called out explicitly: KYC-Pro identity documents, and the fact that a medical consultation's very existence is health data even though its content is never stored.
3. A versioned French privacy policy and terms of service, served to the web app so the version shown matches the version consented to in CON-04.
4. `GET /api/v1/me/data-export` returning everything the platform holds about the calling user as a structured file: profile, consultations, ratings, consents, notification log entries, and a manifest of their KYC documents.
5. The export excludes the other party's personal data: a client's export names the professional publicly but does not include the professional's private details, and vice versa.
6. Rate-limit the export endpoint and require a fresh authentication (a recent login or a password re-entry), because it returns everything about an account in one response.
7. Deletion is **out of scope here** and belongs to the Beta retention work, because financial and audit records cannot simply be deleted and the retention rules need the legal review the study calls for. State this in the policy honestly rather than promising a deletion the platform cannot yet perform.

## Validation / test checks

Every item below must be satisfied, and the pull request must say how.

- A test that walks the SQLAlchemy models and fails if a model holding personal data is absent from the register. This is what keeps the register true as the schema grows.
- Integration test: the export for a seeded client contains their profile, consultations, ratings and consents.
- Integration test: the export contains a document manifest but not the document bytes.
- Integration test: a client's export contains no private field belonging to the professional they consulted, and the reverse.
- Integration test: the export requires fresh authentication and is rate-limited.
- Integration test: the policy endpoint returns the same version string that CON-04 records against a consent.
- A review checklist item confirming the register was derived from the migrations, with the PR listing any model deliberately excluded and why.

## Deliverables

- `docs/compliance/data_processing_register.md`.
- Versioned French privacy policy and terms, and the endpoint serving them.
- The data-export endpoint.
- `apps/api/tests/compliance/test_data_export.py` and the register-coverage test.
- A `## Data protection` section in `README.md` pointing at the register.

## Notes

This issue produces the artifact a legal advisor reviews. Its value is accuracy, not completeness of coverage: a register that honestly says 'retention undecided, pending legal review' for a category is useful, and one that invents a retention period is worse than useless.

---

## Definition of done

- [ ] Every requirement above is implemented.
- [ ] Every validation check above passes, and the pull request states how.
- [ ] Every deliverable above exists.
- [ ] `pre-commit run --all-files` passes.
- [ ] API: `mypy src` clean, `pytest` passes. Web: `typecheck` clean, tests pass.
- [ ] Coverage stays above the CI gate.
- [ ] Branch is `feature/cmp-01-data-protection`, one pull request into `develop`.
- [ ] The pull request body contains `Closes #<this issue>`.
- [ ] No secrets, credentials, real personal data or real case material in the diff.
- [ ] User-facing strings are French and come from the i18n catalogue.

If a requirement turns out to be wrong or impossible, say so on this issue before implementing something different. Do not change the scope silently in the pull request.

See `CONTRIBUTING.md` for the workflow and `docs/implementation/lexpert_plan.md` for how this issue fits the whole.
